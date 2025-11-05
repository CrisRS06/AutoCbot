"""
Base Exchange Interface
Defines the standard interface that all exchange connectors must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class BaseExchange(ABC):
    """
    Abstract base class for all exchange implementations

    This interface ensures consistency across different exchange connectors
    """

    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        """
        Initialize exchange connector

        Args:
            api_key: Exchange API key
            api_secret: Exchange API secret
            testnet: Use testnet/sandbox mode
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.name = self.__class__.__name__

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dict with currency as key and available balance as value
            Example: {"USDT": 10000.0, "BTC": 0.5}
        """
        pass

    @abstractmethod
    async def get_account_info(self) -> Dict:
        """
        Get detailed account information

        Returns:
            Dict with account details including balances, fees, permissions, etc.
        """
        pass

    @abstractmethod
    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float
    ) -> Dict:
        """
        Place a market order

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side (BUY or SELL)
            quantity: Order quantity

        Returns:
            Dict with order details
        """
        pass

    @abstractmethod
    async def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        price: float,
        quantity: float
    ) -> Dict:
        """
        Place a limit order

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side (BUY or SELL)
            price: Limit price
            quantity: Order quantity

        Returns:
            Dict with order details
        """
        pass

    @abstractmethod
    async def place_stop_loss_order(
        self,
        symbol: str,
        side: OrderSide,
        stop_price: float,
        quantity: float
    ) -> Dict:
        """
        Place a stop-loss order

        Args:
            symbol: Trading pair
            side: Order side (BUY or SELL)
            stop_price: Stop price trigger
            quantity: Order quantity

        Returns:
            Dict with order details
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order

        Args:
            order_id: Exchange order ID
            symbol: Trading pair

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """
        Get order status

        Args:
            order_id: Exchange order ID
            symbol: Trading pair

        Returns:
            Dict with order details and status
        """
        pass

    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders

        Args:
            symbol: Trading pair (optional, None returns all)

        Returns:
            List of open orders
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """
        Get current open positions

        Returns:
            List of position dicts
        """
        pass

    @abstractmethod
    async def get_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get trade history

        Args:
            symbol: Trading pair (optional)
            limit: Maximum number of trades to return

        Returns:
            List of executed trades
        """
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information

        Args:
            symbol: Trading pair

        Returns:
            Dict with ticker data (bid, ask, last, volume, etc.)
        """
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book

        Args:
            symbol: Trading pair
            limit: Depth limit

        Returns:
            Dict with bids and asks
        """
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format (e.g., BTC/USDT -> BTCUSDT for Binance)

        Args:
            symbol: Symbol in standard format (BTC/USDT)

        Returns:
            Symbol in exchange-specific format
        """
        # Default implementation (override in subclasses if needed)
        return symbol

    def denormalize_symbol(self, symbol: str) -> str:
        """
        Convert exchange-specific symbol to standard format

        Args:
            symbol: Symbol in exchange format (e.g., BTCUSDT)

        Returns:
            Symbol in standard format (BTC/USDT)
        """
        # Default implementation (override in subclasses if needed)
        return symbol

    async def test_connection(self) -> bool:
        """
        Test connection to exchange

        Returns:
            True if connection successful
        """
        try:
            await self.get_account_info()
            return True
        except Exception:
            return False

    def __repr__(self):
        mode = "testnet" if self.testnet else "live"
        return f"<{self.name} ({mode})>"
