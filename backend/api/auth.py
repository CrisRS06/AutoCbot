"""
Authentication API endpoints
Handles user registration, login, token refresh, and user management
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from database.session import get_db
from database.models import User, TokenBlacklist
from utils.auth import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_token
)
from utils.config import settings
from utils.rate_limit import auth_rate_limit, auth_strict_rate_limit, limiter

router = APIRouter(tags=["authentication"])
security = HTTPBearer()


# ========== Pydantic Schemas ==========

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "trader@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user information response"""
    id: int
    email: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str


# ========== Endpoints ==========

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Rate limit: 5 registration attempts per minute
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account

    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 characters recommended)

    Returns newly created user information (without password)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Rate limit: 5 login attempts per minute (anti-brute-force)
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login and receive access and refresh tokens

    - **email**: User's email address
    - **password**: User's password

    Returns access token (30 min expiry) and refresh token (7 day expiry)
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")  # Rate limit: 10 token refresh attempts per minute
async def refresh_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token

    Provide a valid refresh token in the Authorization header.
    Returns new access and refresh tokens.
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type - refresh token required"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information

    Requires valid access token in Authorization header.
    Returns user details (id, email, active status, superuser status).
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user by blacklisting the access token

    Adds the current access token to the blacklist to prevent reuse.
    Note: Refresh tokens should also be discarded client-side.

    Requires valid access token in Authorization header.
    """
    try:
        # Extract and decode token
        token = credentials.credentials
        payload = verify_token(token)

        token_jti = payload.get("jti")
        token_type = payload.get("type", "access")
        exp_timestamp = payload.get("exp")

        if not token_jti:
            # Old tokens without JTI - just return success
            return {"message": "Successfully logged out. Please discard your tokens."}

        # Convert expiration to datetime
        expires_at = datetime.utcfromtimestamp(exp_timestamp) if exp_timestamp else datetime.utcnow()

        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            token_jti=token_jti,
            user_id=current_user.id,
            token_type=token_type,
            expires_at=expires_at,
            reason="logout"
        )

        db.add(blacklisted_token)
        db.commit()

        return {"message": "Successfully logged out. Token has been revoked."}

    except Exception as e:
        db.rollback()
        # Even if blacklist fails, return success to avoid blocking logout
        return {"message": "Successfully logged out. Please discard your tokens."}


@router.put("/change-password", response_model=MessageResponse)
@limiter.limit("3/minute")  # Rate limit: 3 password change attempts per minute (strict)
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password

    Requires current password for verification.
    """
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Update to new password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Password changed successfully"}
