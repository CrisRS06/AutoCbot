"""
Settings Models and Storage
Handles user configuration persistence
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import json
import os
from pathlib import Path


class UserSettings(BaseModel):
    """User configuration settings"""

    # API Keys
    binanceApiKey: str = ""
    binanceSecret: str = ""
    coinGeckoApiKey: str = ""
    telegramToken: str = ""
    telegramChatId: str = ""

    # Trading Parameters
    defaultPairs: str = "BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT"
    defaultTimeframe: str = "5m"
    maxPositionSize: float = Field(default=0.1, ge=0, le=1)
    maxOpenTrades: int = Field(default=5, ge=1, le=20)

    # Risk Management
    defaultStoploss: float = Field(default=-0.05, le=0)
    defaultTakeprofit: float = Field(default=0.03, ge=0)

    # Features
    enableMlPredictions: bool = True
    enablePaperTrading: bool = True
    dryRun: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "binanceApiKey": "",
                "binanceSecret": "",
                "defaultPairs": "BTC/USDT,ETH/USDT",
                "defaultTimeframe": "5m",
                "maxPositionSize": 0.1,
                "maxOpenTrades": 5,
                "defaultStoploss": -0.05,
                "defaultTakeprofit": 0.03,
                "enableMlPredictions": True,
                "dryRun": True
            }
        }


class SettingsStorage:
    """Handles settings persistence to JSON file"""

    def __init__(self, storage_path: str = "data/user_settings.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> UserSettings:
        """Load settings from file, return defaults if not found"""
        if not self.storage_path.exists():
            return UserSettings()

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return UserSettings(**data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return UserSettings()

    def save(self, settings: UserSettings) -> bool:
        """Save settings to file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(settings.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False


# Global settings storage instance
settings_storage = SettingsStorage()
