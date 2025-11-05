"""
Binance Exchange Connector
Implements trading operations for Binance exchange using CCXT
"""

import ccxt.async_support as ccxt
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .base_exchange import BaseExchange, OrderSide, OrderType, OrderStatus

logger = logging.getLogger(__name__)


class BinanceConnector(BaseExchange):
    """
    Binance exchange connector using CCXT library
    """

    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        """
        Initialize Binance connector

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet mode (default: False)
        """
        super().__init__(api_key, api_secret, testnet)

        # Initialize CCXT Binance instance
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # spot, margin, future, delivery
            }
        })

        # Set testnet if enabled
        if testnet:
            self.exchange.set_sandbox_mode(True)
            logger.info("Binance connector initialized in TESTNET mode")
        else:
            logger.info("Binance connector initialized in LIVE mode")

    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dict with currency and available balance
        """
        try:
            balance = await self.exchange.fetch_balance()

            # Extract free (available) balances
            free_balances = {}
            for currency, amount in balance['free'].items():
                if amount > 0:
                    free_balances[currency] = float(amount)

            return free_balances

        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise

    async def get_account_info(self) -> Dict:
        """
        Get detailed account information
        """
        try:
            balance = await self.exchange.fetch_balance()

            return {
                'exchange': 'binance',
                'balances': balance,
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'total': balance.get('total', {}),
                'timestamp': balance.get('timestamp'),
            }

        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise

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
            Order details
        """
        try:
            # Convert side to CCXT format
            ccxt_side = side.value  # 'buy' or 'sell'

            order = await self.exchange.create_market_order(
                symbol=symbol,
                side=ccxt_side,
                amount=quantity
            )

            return self._normalize_order(order)

        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise

    async def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        price: float,
        quantity: float
    ) -> Dict:
        """
        Place a limit order
        """
        try:
            ccxt_side = side.value

            order = await self.exchange.create_limit_order(
                symbol=symbol,
                side=ccxt_side,
                amount=quantity,
                price=price
            )

            return self._normalize_order(order)

        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise

    async def place_stop_loss_order(
        self,
        symbol: str,
        side: OrderSide,
        stop_price: float,
        quantity: float
    ) -> Dict:
        """
        Place a stop-loss order
        """
        try:
            ccxt_side = side.value

            # Binance stop loss order
            order = await self.exchange.create_order(
                symbol=symbol,
                type='stop_loss_limit',
                side=ccxt_side,
                amount=quantity,
                price=stop_price,  # Limit price
                params={'stopPrice': stop_price}  # Stop trigger price
            )

            return self._normalize_order(order)

        except Exception as e:
            logger.error(f"Error placing stop-loss order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order
        """
        try:
            await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order {order_id} cancelled successfully")
            return True

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """
        Get order status
        """
        try:
            order = await self.exchange.fetch_order(order_id, symbol)
            return self._normalize_order(order)

        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            raise

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders
        """
        try:
            orders = await self.exchange.fetch_open_orders(symbol)

            return [self._normalize_order(order) for order in orders]

        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    async def get_positions(self) -> List[Dict]:
        """
        Get current open positions

        Note: For spot trading, this returns balances.
        For futures, it returns actual positions.
        """
        try:
            balance = await self.get_balance()

            # Convert balances to position format
            positions = []
            for currency, amount in balance.items():
                if amount > 0 and currency != 'USDT':  # Exclude base currency
                    positions.append({
                        'symbol': f'{currency}/USDT',
                        'side': 'long',
                        'quantity': amount,
                        'currency': currency
                    })

            return positions

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get trade history
        """
        try:
            if symbol:
                trades = await self.exchange.fetch_my_trades(symbol, limit=limit)
            else:
                # Fetch for all symbols (can be slow)
                trades = []
                markets = await self.exchange.fetch_markets()
                for market in markets[:10]:  # Limit to first 10 markets
                    symbol_trades = await self.exchange.fetch_my_trades(
                        market['symbol'],
                        limit=limit
                    )
                    trades.extend(symbol_trades)

            return [self._normalize_trade(trade) for trade in trades]

        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            return []

    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information
        """
        try:
            ticker = await self.exchange.fetch_ticker(symbol)

            return {
                'symbol': symbol,
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'last': ticker.get('last'),
                'open': ticker.get('open'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('baseVolume'),
                'timestamp': ticker.get('timestamp'),
            }

        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book
        """
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit=limit)

            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp'),
            }

        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            raise

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format (BTC/USDT is already correct for CCXT)
        """
        return symbol

    def _normalize_order(self, order: Dict) -> Dict:
        """
        Normalize order response to standard format
        """
        return {
            'id': order.get('id'),
            'symbol': order.get('symbol'),
            'type': order.get('type'),
            'side': order.get('side'),
            'price': order.get('price'),
            'amount': order.get('amount'),
            'filled': order.get('filled', 0),
            'remaining': order.get('remaining', 0),
            'status': order.get('status'),
            'timestamp': order.get('timestamp'),
            'datetime': order.get('datetime'),
            'fee': order.get('fee'),
            'raw': order  # Keep original response
        }

    def _normalize_trade(self, trade: Dict) -> Dict:
        """
        Normalize trade response to standard format
        """
        return {
            'id': trade.get('id'),
            'order_id': trade.get('order'),
            'symbol': trade.get('symbol'),
            'side': trade.get('side'),
            'price': trade.get('price'),
            'amount': trade.get('amount'),
            'cost': trade.get('cost'),
            'fee': trade.get('fee'),
            'timestamp': trade.get('timestamp'),
            'datetime': trade.get('datetime'),
        }

    async def close(self):
        """
        Close exchange connection
        """
        if self.exchange:
            await self.exchange.close()
            logger.info("Binance connection closed")

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
