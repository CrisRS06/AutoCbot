"""
Settings API Endpoints
Handles user configuration CRUD operations
"""

from fastapi import APIRouter, HTTPException, Depends
from models.settings import UserSettings, settings_storage
from database.models import User
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["settings"])


@router.get("/", response_model=UserSettings)
async def get_settings(current_user: User = Depends(get_current_user)):
    """
    Get current user settings

    Returns:
        UserSettings: Current user configuration
    """
    try:
        settings = settings_storage.load()
        logger.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to load settings")


@router.put("/", response_model=UserSettings)
async def update_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update user settings

    Args:
        settings: New settings configuration

    Returns:
        UserSettings: Saved settings

    Raises:
        HTTPException: If save fails
    """
    try:
        # Validate settings (Pydantic does this automatically)
        # Additional custom validation can go here

        # Save to storage
        success = settings_storage.save(settings)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save settings")

        logger.info("Settings saved successfully")
        return settings

    except ValueError as e:
        logger.error(f"Invalid settings data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid settings: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings")


@router.post("/reset")
async def reset_settings(current_user: User = Depends(get_current_user)):
    """
    Reset settings to defaults

    Returns:
        UserSettings: Default settings
    """
    try:
        default_settings = UserSettings()
        settings_storage.save(default_settings)
        logger.info("Settings reset to defaults")
        return default_settings
    except Exception as e:
        logger.error(f"Failed to reset settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset settings")
