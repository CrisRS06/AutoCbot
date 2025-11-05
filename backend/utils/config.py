"""
Configuration management for AutoCbot
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./autocbot.db"

    # API Keys (use free tiers)
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    MESSARI_API_KEY: str = os.getenv("MESSARI_API_KEY", "")
    LUNARCRUSH_API_KEY: str = os.getenv("LUNARCRUSH_API_KEY", "")
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET: str = os.getenv("BINANCE_SECRET", "")

    # Data Sources Configuration
    USE_COINGECKO: bool = True
    USE_ALTERNATIVE_ME: bool = True  # Free Fear & Greed Index
    USE_MESSARI: bool = True  # Free tier
    USE_LUNARCRUSH: bool = False  # Requires paid plan

    # Trading Configuration
    DEFAULT_PAIRS: Union[List[str], str] = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
    DEFAULT_TIMEFRAME: str = "5m"

    @field_validator('DEFAULT_PAIRS', mode='before')
    @classmethod
    def parse_default_pairs(cls, v):
        """Parse DEFAULT_PAIRS from comma-separated string or list"""
        if isinstance(v, str):
            return [pair.strip() for pair in v.split(',') if pair.strip()]
        return v

    # Cache Settings
    CACHE_TTL: int = 60  # seconds
    PRICE_UPDATE_INTERVAL: int = 5  # seconds
    SENTIMENT_UPDATE_INTERVAL: int = 300  # 5 minutes

    # Risk Management
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    MAX_OPEN_TRADES: int = 5
    DEFAULT_STOPLOSS: float = -0.05  # 5%
    DEFAULT_TAKEPROFIT: float = 0.03  # 3%

    # Feature Flags
    ENABLE_ML_PREDICTIONS: bool = True
    ENABLE_BACKTESTING: bool = True
    ENABLE_PAPER_TRADING: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env (e.g., Freqtrade vars)


settings = Settings()
