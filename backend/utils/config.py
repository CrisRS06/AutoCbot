"""
Configuration management for AutoCbot
"""

from pydantic_settings import BaseSettings
from typing import List
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
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

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
    DEFAULT_PAIRS: List[str] = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
    DEFAULT_TIMEFRAME: str = "5m"

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


settings = Settings()
