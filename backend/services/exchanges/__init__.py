"""
Exchange Connectors Package
Provides unified interface for trading on different exchanges
"""

from .base_exchange import BaseExchange, OrderSide, OrderType, OrderStatus
from .binance_connector import BinanceConnector
from .paper_trading_exchange import PaperTradingExchange
from .exchange_factory import (
    ExchangeFactory,
    ExchangeType,
    create_paper_trading_exchange,
    create_binance_exchange
)

__all__ = [
    # Base classes and enums
    "BaseExchange",
    "OrderSide",
    "OrderType",
    "OrderStatus",

    # Exchange implementations
    "BinanceConnector",
    "PaperTradingExchange",

    # Factory
    "ExchangeFactory",
    "ExchangeType",
    "create_paper_trading_exchange",
    "create_binance_exchange",
]
