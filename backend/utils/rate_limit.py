"""
Rate Limiting Utilities
Implements anti-abuse rate limiting using SlowAPI
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


# Rate limit configuration
# Format: "number/time_unit" (e.g., "5/minute", "100/hour")
RATE_LIMITS = {
    "auth": "5/minute",           # Authentication endpoints (login, register)
    "auth_strict": "3/minute",    # Password change, sensitive operations
    "data": "100/minute",         # Data retrieval endpoints
    "mutation": "30/minute",      # Create/Update/Delete operations
    "trading": "60/minute",       # Trading-related endpoints
    "default": "60/minute",       # Default for unclassified endpoints
}


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting

    Uses IP address as identifier. In production, consider using:
    - User ID from JWT token (for authenticated requests)
    - API key (for API clients)
    - X-Forwarded-For header (for proxied requests)

    Args:
        request: FastAPI request object

    Returns:
        Unique identifier string
    """
    # Try to get user from token first (more accurate for authenticated endpoints)
    try:
        # Check if request has state with user info
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
    except:
        pass

    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["60/minute"],  # Global default
    storage_uri="memory://",  # Use memory storage for MVP (consider Redis for production)
    strategy="fixed-window",  # Fixed window strategy
    headers_enabled=True,  # Add rate limit headers to responses
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse with 429 status code
    """
    logger.warning(
        f"Rate limit exceeded for {get_identifier(request)} on {request.url.path}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "detail": str(exc.detail) if hasattr(exc, "detail") else None,
        },
        headers=getattr(exc, "headers", {}),
    )


# Convenience decorators for common rate limits
def auth_rate_limit():
    """Rate limit for authentication endpoints"""
    return limiter.limit(RATE_LIMITS["auth"])


def auth_strict_rate_limit():
    """Strict rate limit for sensitive auth operations"""
    return limiter.limit(RATE_LIMITS["auth_strict"])


def data_rate_limit():
    """Rate limit for data retrieval endpoints"""
    return limiter.limit(RATE_LIMITS["data"])


def mutation_rate_limit():
    """Rate limit for create/update/delete operations"""
    return limiter.limit(RATE_LIMITS["mutation"])


def trading_rate_limit():
    """Rate limit for trading-related endpoints"""
    return limiter.limit(RATE_LIMITS["trading"])
