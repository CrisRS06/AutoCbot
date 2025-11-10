"""
Settings API Endpoints
Handles user configuration CRUD operations with per-user database storage
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.settings import UserSettings
from database.models import User
from database.session import get_db
from utils.auth import get_current_user
from services.user_settings import UserSettingsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["settings"])


@router.get("/", response_model=UserSettings)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user settings (per-user, with decrypted API keys)

    Returns:
        UserSettings: Current user configuration
    """
    try:
        settings_service = UserSettingsService(db)
        settings = settings_service.get_settings(user_id=current_user.id)
        logger.info(f"Settings loaded successfully for user {current_user.id}")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load settings")


@router.put("/", response_model=UserSettings)
async def update_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user settings (per-user, with encrypted API keys)

    Args:
        settings: New settings configuration

    Returns:
        UserSettings: Saved settings with encrypted API keys

    Raises:
        HTTPException: If save fails
    """
    try:
        settings_service = UserSettingsService(db)
        saved_settings = settings_service.save_settings(user_id=current_user.id, settings=settings)

        logger.info(f"Settings saved successfully for user {current_user.id}")
        return saved_settings

    except ValueError as e:
        logger.error(f"Invalid settings data for user {current_user.id}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid settings: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to save settings for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings")


@router.post("/reset")
async def reset_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset settings to defaults (per-user)

    Returns:
        UserSettings: Default settings
    """
    try:
        settings_service = UserSettingsService(db)
        default_settings = settings_service.reset_settings(user_id=current_user.id)
        logger.info(f"Settings reset to defaults for user {current_user.id}")
        return default_settings
    except Exception as e:
        logger.error(f"Failed to reset settings for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset settings")
