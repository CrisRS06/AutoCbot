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
    GLASSNODE_API_KEY: str = os.getenv("GLASSNODE_API_KEY", "")

    # Exchange API Keys
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET: str = os.getenv("BINANCE_SECRET", "")
    COINBASE_API_KEY: str = os.getenv("COINBASE_API_KEY", "")
    COINBASE_SECRET: str = os.getenv("COINBASE_SECRET", "")
    COINBASE_PASSPHRASE: str = os.getenv("COINBASE_PASSPHRASE", "")

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

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Redis Cache (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Notifications (optional)
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env (e.g., Freqtrade vars)


settings = Settings()
