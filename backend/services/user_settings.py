"""
User Settings Service
Handles per-user settings with encryption for sensitive data
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from database.models import UserSettingsModel
from models.settings import UserSettings
from utils.encryption import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)


class UserSettingsService:
    """Service for managing user settings with encryption"""

    def __init__(self, db: Session):
        self.db = db

    def _encrypt_api_keys(self, settings: UserSettings) -> dict:
        """
        Encrypt sensitive API keys from Pydantic model

        Args:
            settings: UserSettings Pydantic model

        Returns:
            Dictionary with encrypted fields
        """
        return {
            "binance_api_key_encrypted": encrypt_value(settings.binanceApiKey) if settings.binanceApiKey else None,
            "binance_secret_encrypted": encrypt_value(settings.binanceSecret) if settings.binanceSecret else None,
            "coingecko_api_key_encrypted": encrypt_value(settings.coinGeckoApiKey) if settings.coinGeckoApiKey else None,
            "telegram_token_encrypted": encrypt_value(settings.telegramToken) if settings.telegramToken else None,
            "telegram_chat_id_encrypted": encrypt_value(settings.telegramChatId) if settings.telegramChatId else None,
        }

    def _decrypt_api_keys(self, db_settings: UserSettingsModel) -> dict:
        """
        Decrypt sensitive API keys from database model

        Args:
            db_settings: UserSettingsModel database model

        Returns:
            Dictionary with decrypted fields
        """
        return {
            "binanceApiKey": decrypt_value(db_settings.binance_api_key_encrypted) if db_settings.binance_api_key_encrypted else "",
            "binanceSecret": decrypt_value(db_settings.binance_secret_encrypted) if db_settings.binance_secret_encrypted else "",
            "coinGeckoApiKey": decrypt_value(db_settings.coingecko_api_key_encrypted) if db_settings.coingecko_api_key_encrypted else "",
            "telegramToken": decrypt_value(db_settings.telegram_token_encrypted) if db_settings.telegram_token_encrypted else "",
            "telegramChatId": decrypt_value(db_settings.telegram_chat_id_encrypted) if db_settings.telegram_chat_id_encrypted else "",
        }

    def _db_to_pydantic(self, db_settings: UserSettingsModel) -> UserSettings:
        """
        Convert database model to Pydantic model with decryption

        Args:
            db_settings: Database settings model

        Returns:
            UserSettings Pydantic model
        """
        # Decrypt API keys
        decrypted_keys = self._decrypt_api_keys(db_settings)

        return UserSettings(
            binanceApiKey=decrypted_keys["binanceApiKey"],
            binanceSecret=decrypted_keys["binanceSecret"],
            coinGeckoApiKey=decrypted_keys["coinGeckoApiKey"],
            telegramToken=decrypted_keys["telegramToken"],
            telegramChatId=decrypted_keys["telegramChatId"],
            defaultPairs=db_settings.default_pairs,
            defaultTimeframe=db_settings.default_timeframe,
            maxPositionSize=db_settings.max_position_size,
            maxOpenTrades=db_settings.max_open_trades,
            defaultStoploss=db_settings.default_stoploss,
            defaultTakeprofit=db_settings.default_takeprofit,
            enableMlPredictions=db_settings.enable_ml_predictions,
            enablePaperTrading=db_settings.enable_paper_trading,
            dryRun=db_settings.dry_run,
        )

    def get_settings(self, user_id: int) -> UserSettings:
        """
        Get settings for a specific user

        Args:
            user_id: User ID

        Returns:
            UserSettings with decrypted API keys
        """
        try:
            db_settings = self.db.query(UserSettingsModel).filter(
                UserSettingsModel.user_id == user_id
            ).first()

            if db_settings:
                return self._db_to_pydantic(db_settings)
            else:
                # Return default settings if none exist
                logger.info(f"No settings found for user {user_id}, returning defaults")
                return UserSettings()

        except Exception as e:
            logger.error(f"Error loading settings for user {user_id}: {e}")
            # Return default settings on error
            return UserSettings()

    def save_settings(self, user_id: int, settings: UserSettings) -> UserSettings:
        """
        Save or update settings for a specific user

        Args:
            user_id: User ID
            settings: UserSettings to save

        Returns:
            Saved UserSettings

        Raises:
            Exception: If save fails
        """
        try:
            # Check if settings exist
            db_settings = self.db.query(UserSettingsModel).filter(
                UserSettingsModel.user_id == user_id
            ).first()

            # Encrypt API keys
            encrypted_keys = self._encrypt_api_keys(settings)

            if db_settings:
                # Update existing settings
                for key, value in encrypted_keys.items():
                    setattr(db_settings, key, value)

                db_settings.default_pairs = settings.defaultPairs
                db_settings.default_timeframe = settings.defaultTimeframe
                db_settings.max_position_size = settings.maxPositionSize
                db_settings.max_open_trades = settings.maxOpenTrades
                db_settings.default_stoploss = settings.defaultStoploss
                db_settings.default_takeprofit = settings.defaultTakeprofit
                db_settings.enable_ml_predictions = settings.enableMlPredictions
                db_settings.enable_paper_trading = settings.enablePaperTrading
                db_settings.dry_run = settings.dryRun

                logger.info(f"Updated settings for user {user_id}")
            else:
                # Create new settings
                db_settings = UserSettingsModel(
                    user_id=user_id,
                    **encrypted_keys,
                    default_pairs=settings.defaultPairs,
                    default_timeframe=settings.defaultTimeframe,
                    max_position_size=settings.maxPositionSize,
                    max_open_trades=settings.maxOpenTrades,
                    default_stoploss=settings.defaultStoploss,
                    default_takeprofit=settings.defaultTakeprofit,
                    enable_ml_predictions=settings.enableMlPredictions,
                    enable_paper_trading=settings.enablePaperTrading,
                    dry_run=settings.dryRun,
                )
                self.db.add(db_settings)
                logger.info(f"Created new settings for user {user_id}")

            self.db.commit()
            self.db.refresh(db_settings)

            return self._db_to_pydantic(db_settings)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving settings for user {user_id}: {e}")
            raise

    def reset_settings(self, user_id: int) -> UserSettings:
        """
        Reset settings to defaults for a specific user

        Args:
            user_id: User ID

        Returns:
            Default UserSettings
        """
        try:
            default_settings = UserSettings()
            return self.save_settings(user_id, default_settings)
        except Exception as e:
            logger.error(f"Error resetting settings for user {user_id}: {e}")
            raise

    def delete_settings(self, user_id: int) -> bool:
        """
        Delete settings for a specific user

        Args:
            user_id: User ID

        Returns:
            True if deleted successfully
        """
        try:
            db_settings = self.db.query(UserSettingsModel).filter(
                UserSettingsModel.user_id == user_id
            ).first()

            if db_settings:
                self.db.delete(db_settings)
                self.db.commit()
                logger.info(f"Deleted settings for user {user_id}")
                return True
            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting settings for user {user_id}: {e}")
            raise
