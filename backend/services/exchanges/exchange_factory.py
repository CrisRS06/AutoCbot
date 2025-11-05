"""
Exchange Factory
Factory pattern for creating exchange connector instances
"""

import logging
from typing import Dict, Optional
from enum import Enum

from .base_exchange import BaseExchange
from .binance_connector import BinanceConnector
from .paper_trading_exchange import PaperTradingExchange

logger = logging.getLogger(__name__)


class ExchangeType(str, Enum):
    """Supported exchange types"""
    BINANCE = "binance"
    BINANCE_TESTNET = "binance_testnet"
    PAPER_TRADING = "paper_trading"


class ExchangeFactory:
    """
    Factory for creating exchange connector instances
    """

    _instances: Dict[str, BaseExchange] = {}  # Singleton instances

    @classmethod
    def create_exchange(
        cls,
        exchange_type: ExchangeType,
        api_key: str = "",
        api_secret: str = "",
        testnet: bool = False,
        initial_balance: Optional[Dict[str, float]] = None,
        use_singleton: bool = True
    ) -> BaseExchange:
        """
        Create an exchange connector instance

        Args:
            exchange_type: Type of exchange to create
            api_key: API key for the exchange
            api_secret: API secret for the exchange
            testnet: Whether to use testnet mode
            initial_balance: Initial balance for paper trading (only for paper trading)
            use_singleton: Whether to reuse existing instance (default: True)

        Returns:
            Exchange connector instance

        Raises:
            ValueError: If exchange type is not supported
        """
        # Create cache key for singleton pattern
        cache_key = f"{exchange_type}_{api_key[:8] if api_key else 'none'}_{testnet}"

        # Return existing instance if using singleton
        if use_singleton and cache_key in cls._instances:
            logger.debug(f"Returning existing {exchange_type} instance")
            return cls._instances[cache_key]

        # Create new instance based on type
        exchange = None

        if exchange_type == ExchangeType.PAPER_TRADING:
            if initial_balance is None:
                initial_balance = {"USDT": 10000.0}
            exchange = PaperTradingExchange(initial_balance=initial_balance)
            logger.info(f"Created paper trading exchange with balance: {initial_balance}")

        elif exchange_type == ExchangeType.BINANCE:
            if not api_key or not api_secret:
                raise ValueError("API key and secret required for Binance")
            exchange = BinanceConnector(
                api_key=api_key,
                api_secret=api_secret,
                testnet=False
            )
            logger.info("Created Binance live exchange connector")

        elif exchange_type == ExchangeType.BINANCE_TESTNET:
            if not api_key or not api_secret:
                raise ValueError("API key and secret required for Binance Testnet")
            exchange = BinanceConnector(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True
            )
            logger.info("Created Binance testnet exchange connector")

        else:
            raise ValueError(f"Unsupported exchange type: {exchange_type}")

        # Cache instance if using singleton
        if use_singleton:
            cls._instances[cache_key] = exchange

        return exchange

    @classmethod
    def create_from_config(cls, config: Dict) -> BaseExchange:
        """
        Create exchange from configuration dictionary

        Args:
            config: Configuration dictionary with keys:
                - type: Exchange type (binance, binance_testnet, paper_trading)
                - api_key: API key (optional for paper trading)
                - api_secret: API secret (optional for paper trading)
                - testnet: Boolean for testnet mode
                - initial_balance: Dict for paper trading initial balance

        Returns:
            Exchange connector instance

        Example:
            config = {
                "type": "binance",
                "api_key": "your_api_key",
                "api_secret": "your_api_secret",
                "testnet": False
            }
            exchange = ExchangeFactory.create_from_config(config)
        """
        exchange_type_str = config.get("type", "paper_trading").lower()

        # Map string to enum
        try:
            if exchange_type_str == "binance":
                if config.get("testnet", False):
                    exchange_type = ExchangeType.BINANCE_TESTNET
                else:
                    exchange_type = ExchangeType.BINANCE
            elif exchange_type_str in ["paper_trading", "paper", "demo"]:
                exchange_type = ExchangeType.PAPER_TRADING
            else:
                raise ValueError(f"Unknown exchange type: {exchange_type_str}")

            return cls.create_exchange(
                exchange_type=exchange_type,
                api_key=config.get("api_key", ""),
                api_secret=config.get("api_secret", ""),
                testnet=config.get("testnet", False),
                initial_balance=config.get("initial_balance"),
                use_singleton=config.get("use_singleton", True)
            )

        except Exception as e:
            logger.error(f"Error creating exchange from config: {e}")
            raise

    @classmethod
    def get_instance(cls, exchange_type: ExchangeType, api_key: str = "") -> Optional[BaseExchange]:
        """
        Get existing exchange instance if it exists

        Args:
            exchange_type: Type of exchange
            api_key: API key (first 8 chars used for cache key)

        Returns:
            Exchange instance or None if not found
        """
        cache_key = f"{exchange_type}_{api_key[:8] if api_key else 'none'}_False"
        return cls._instances.get(cache_key)

    @classmethod
    async def close_all(cls):
        """
        Close all exchange connections
        """
        logger.info("Closing all exchange connections...")
        for exchange in cls._instances.values():
            try:
                await exchange.close()
            except Exception as e:
                logger.error(f"Error closing exchange: {e}")

        cls._instances.clear()
        logger.info("All exchange connections closed")

    @classmethod
    def clear_cache(cls):
        """
        Clear cached exchange instances
        (Note: Does not close connections, use close_all() for that)
        """
        cls._instances.clear()
        logger.info("Exchange instance cache cleared")

    @classmethod
    def list_active_exchanges(cls) -> Dict[str, str]:
        """
        List all active exchange instances

        Returns:
            Dict with cache_key -> exchange type
        """
        return {
            key: type(exchange).__name__
            for key, exchange in cls._instances.items()
        }


# Convenience functions for common use cases

def create_paper_trading_exchange(initial_balance: Optional[Dict[str, float]] = None) -> PaperTradingExchange:
    """
    Convenience function to create a paper trading exchange

    Args:
        initial_balance: Initial balance (default: {"USDT": 10000.0})

    Returns:
        PaperTradingExchange instance
    """
    return ExchangeFactory.create_exchange(
        exchange_type=ExchangeType.PAPER_TRADING,
        initial_balance=initial_balance,
        use_singleton=False  # Don't cache paper trading by default
    )


def create_binance_exchange(
    api_key: str,
    api_secret: str,
    testnet: bool = False
) -> BinanceConnector:
    """
    Convenience function to create a Binance exchange

    Args:
        api_key: Binance API key
        api_secret: Binance API secret
        testnet: Use testnet mode

    Returns:
        BinanceConnector instance
    """
    exchange_type = ExchangeType.BINANCE_TESTNET if testnet else ExchangeType.BINANCE

    return ExchangeFactory.create_exchange(
        exchange_type=exchange_type,
        api_key=api_key,
        api_secret=api_secret,
        testnet=testnet
    )
