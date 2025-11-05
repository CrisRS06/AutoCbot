"""
Base Market Data Provider
Abstract base class for all market data providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """Supported data sources"""
    BINANCE = "binance"
    GLASSNODE = "glassnode"
    LUNARCRUSH = "lunarcrush"
    COINGECKO = "coingecko"


class TimeFrame(str, Enum):
    """Supported timeframes for OHLCV data"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class BaseMarketDataProvider(ABC):
    """
    Abstract base class for market data providers
    Defines the interface that all providers must implement
    """

    def __init__(self, api_key: str = "", api_secret: str = ""):
        """
        Initialize market data provider

        Args:
            api_key: API key for the service
            api_secret: API secret (if required)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.source = None

    @abstractmethod
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.H1,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            timeframe: Candle timeframe
            start_date: Start date for historical data
            end_date: End date for historical data
            limit: Maximum number of candles to return

        Returns:
            List of OHLCV dicts with keys: timestamp, open, high, low, close, volume
        """
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information

        Args:
            symbol: Trading pair symbol

        Returns:
            Dict with ticker data: last, bid, ask, volume, change_24h, etc.
        """
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """
        Get order book data

        Args:
            symbol: Trading pair symbol
            depth: Number of bids/asks to return

        Returns:
            Dict with bids and asks
        """
        pass

    async def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols

        Returns:
            List of symbol strings
        """
        # Default implementation - override in subclasses
        return []

    async def close(self):
        """
        Close connections and cleanup resources
        """
        logger.info(f"{self.__class__.__name__} closed")


class OnChainDataProvider(ABC):
    """
    Abstract base class for on-chain data providers (e.g., Glassnode)
    """

    def __init__(self, api_key: str = ""):
        """
        Initialize on-chain data provider

        Args:
            api_key: API key for the service
        """
        self.api_key = api_key

    @abstractmethod
    async def get_active_addresses(
        self,
        asset: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get active addresses metric

        Args:
            asset: Asset symbol (e.g., "BTC")
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with timestamp and value
        """
        pass

    @abstractmethod
    async def get_network_value(
        self,
        asset: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get network value to transactions (NVT) ratio

        Args:
            asset: Asset symbol
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with timestamp and NVT value
        """
        pass

    @abstractmethod
    async def get_exchange_flows(
        self,
        asset: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get exchange inflows and outflows

        Args:
            asset: Asset symbol
            start_date: Start date
            end_date: End date

        Returns:
            Dict with inflow and outflow data
        """
        pass

    @abstractmethod
    async def get_holder_distribution(self, asset: str) -> Dict:
        """
        Get holder distribution metrics

        Args:
            asset: Asset symbol

        Returns:
            Dict with distribution data
        """
        pass


class SocialSentimentProvider(ABC):
    """
    Abstract base class for social sentiment data providers (e.g., LunarCrush)
    """

    def __init__(self, api_key: str = ""):
        """
        Initialize social sentiment provider

        Args:
            api_key: API key for the service
        """
        self.api_key = api_key

    @abstractmethod
    async def get_social_metrics(self, symbol: str) -> Dict:
        """
        Get social media metrics for a symbol

        Args:
            symbol: Asset symbol

        Returns:
            Dict with social metrics: sentiment, mentions, engagement, etc.
        """
        pass

    @abstractmethod
    async def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """
        Get trending coins based on social activity

        Args:
            limit: Number of coins to return

        Returns:
            List of dicts with coin data and metrics
        """
        pass

    @abstractmethod
    async def get_influencer_activity(self, symbol: str) -> List[Dict]:
        """
        Get influencer activity for a symbol

        Args:
            symbol: Asset symbol

        Returns:
            List of influential posts/mentions
        """
        pass
