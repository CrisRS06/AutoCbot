"""
Market Data Providers Package
Comprehensive market data from multiple sources
"""

from .base_provider import (
    BaseMarketDataProvider,
    OnChainDataProvider,
    SocialSentimentProvider,
    DataSource,
    TimeFrame
)
from .binance_provider import BinanceMarketDataProvider
from .glassnode_provider import GlassnodeProvider
from .lunarcrush_provider import LunarCrushProvider
from .aggregator import MarketDataAggregator

__all__ = [
    # Base classes
    "BaseMarketDataProvider",
    "OnChainDataProvider",
    "SocialSentimentProvider",
    "DataSource",
    "TimeFrame",

    # Providers
    "BinanceMarketDataProvider",
    "GlassnodeProvider",
    "LunarCrushProvider",

    # Aggregator
    "MarketDataAggregator",
]
