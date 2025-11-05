"""
Paper Trading Exchange Connector
Simulates trading without real money for testing strategies
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import random
from decimal import Decimal

from .base_exchange import BaseExchange, OrderSide, OrderType, OrderStatus

logger = logging.getLogger(__name__)


class PaperTradingExchange(BaseExchange):
    """
    Paper trading exchange that simulates trades without real money
    """

    def __init__(self, initial_balance: Dict[str, float] = None):
        """
        Initialize paper trading exchange

        Args:
            initial_balance: Starting balances (e.g., {"USDT": 10000, "BTC": 0.5})
        """
        super().__init__(api_key="", api_secret="", testnet=True)

        # Default initial balance
        if initial_balance is None:
            initial_balance = {"USDT": 10000.0}

        # Account state
        self.balances = initial_balance.copy()
        self.orders = {}  # order_id -> order_dict
        self.trades = []  # List of executed trades
        self.order_counter = 1000

        # Market data cache (symbol -> price)
        self.market_prices = {}

        # Simulation parameters
        self.commission_rate = 0.001  # 0.1% commission
        self.slippage_rate = 0.0005  # 0.05% slippage

        logger.info(f"Paper trading exchange initialized with balance: {initial_balance}")

    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dict with currency and available balance
        """
        # Return only non-zero balances
        return {currency: amount for currency, amount in self.balances.items() if amount > 0}

    async def get_account_info(self) -> Dict:
        """
        Get detailed account information
        """
        return {
            'exchange': 'paper_trading',
            'balances': {
                'free': self.balances.copy(),
                'used': {},  # Not tracking locked balances in paper trading
                'total': self.balances.copy()
            },
            'timestamp': int(datetime.now().timestamp() * 1000),
        }

    async def _get_market_price(self, symbol: str) -> float:
        """
        Get current market price for symbol
        For paper trading, we'll use cached prices or simulate them

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Current market price
        """
        # If we have cached price, use it
        if symbol in self.market_prices:
            # Add small random variation to simulate price movement
            base_price = self.market_prices[symbol]
            variation = random.uniform(-0.01, 0.01)  # ±1% variation
            return base_price * (1 + variation)

        # Otherwise, set default prices for common pairs
        default_prices = {
            "BTC/USDT": 45000.0,
            "ETH/USDT": 2500.0,
            "BNB/USDT": 300.0,
            "SOL/USDT": 100.0,
            "ADA/USDT": 0.5,
            "XRP/USDT": 0.6,
            "DOT/USDT": 7.0,
            "DOGE/USDT": 0.08,
            "MATIC/USDT": 0.9,
            "AVAX/USDT": 35.0,
        }

        if symbol in default_prices:
            self.market_prices[symbol] = default_prices[symbol]
            return default_prices[symbol]

        # Default fallback
        logger.warning(f"No price data for {symbol}, using default price 100.0")
        self.market_prices[symbol] = 100.0
        return 100.0

    def set_market_price(self, symbol: str, price: float):
        """
        Set market price for a symbol (useful for testing)

        Args:
            symbol: Trading pair
            price: Price to set
        """
        self.market_prices[symbol] = price
        logger.debug(f"Set market price for {symbol}: ${price}")

    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float
    ) -> Dict:
        """
        Place a market order (executes immediately in paper trading)

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side (BUY or SELL)
            quantity: Order quantity

        Returns:
            Order details
        """
        try:
            # Get current market price
            price = await self._get_market_price(symbol)

            # Apply slippage
            if side == OrderSide.BUY:
                execution_price = price * (1 + self.slippage_rate)
            else:
                execution_price = price * (1 - self.slippage_rate)

            # Parse symbol (e.g., "BTC/USDT" -> base="BTC", quote="USDT")
            base, quote = symbol.split('/')

            # Calculate cost
            cost = quantity * execution_price
            commission = cost * self.commission_rate

            # Check balance
            if side == OrderSide.BUY:
                # Buying: need quote currency
                total_cost = cost + commission
                if self.balances.get(quote, 0) < total_cost:
                    raise ValueError(f"Insufficient {quote} balance. Need {total_cost}, have {self.balances.get(quote, 0)}")

                # Execute trade
                self.balances[quote] = self.balances.get(quote, 0) - total_cost
                self.balances[base] = self.balances.get(base, 0) + quantity

            else:  # SELL
                # Selling: need base currency
                if self.balances.get(base, 0) < quantity:
                    raise ValueError(f"Insufficient {base} balance. Need {quantity}, have {self.balances.get(base, 0)}")

                # Execute trade
                self.balances[base] = self.balances.get(base, 0) - quantity
                net_proceeds = cost - commission
                self.balances[quote] = self.balances.get(quote, 0) + net_proceeds

            # Create order record
            order_id = str(self.order_counter)
            self.order_counter += 1

            order = {
                'id': order_id,
                'symbol': symbol,
                'type': 'market',
                'side': side.value,
                'price': execution_price,
                'amount': quantity,
                'filled': quantity,
                'remaining': 0,
                'status': 'closed',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'datetime': datetime.now().isoformat(),
                'fee': {
                    'cost': commission,
                    'currency': quote
                }
            }

            self.orders[order_id] = order

            # Record trade
            trade = {
                'id': str(len(self.trades) + 1),
                'order': order_id,
                'symbol': symbol,
                'side': side.value,
                'price': execution_price,
                'amount': quantity,
                'cost': cost,
                'fee': {'cost': commission, 'currency': quote},
                'timestamp': order['timestamp'],
                'datetime': order['datetime']
            }
            self.trades.append(trade)

            logger.info(f"Paper trade executed: {side.value.upper()} {quantity} {symbol} @ ${execution_price}")

            return order

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

        Note: In paper trading, limit orders are immediately executed if price is favorable,
        otherwise they're stored as pending
        """
        try:
            # Get current market price
            market_price = await self._get_market_price(symbol)

            # Check if order would execute immediately
            should_execute = False
            if side == OrderSide.BUY and price >= market_price:
                should_execute = True
            elif side == OrderSide.SELL and price <= market_price:
                should_execute = True

            if should_execute:
                # Execute as market order at limit price
                base, quote = symbol.split('/')
                cost = quantity * price
                commission = cost * self.commission_rate

                # Check balance and execute
                if side == OrderSide.BUY:
                    total_cost = cost + commission
                    if self.balances.get(quote, 0) < total_cost:
                        raise ValueError(f"Insufficient {quote} balance")
                    self.balances[quote] = self.balances.get(quote, 0) - total_cost
                    self.balances[base] = self.balances.get(base, 0) + quantity
                else:
                    if self.balances.get(base, 0) < quantity:
                        raise ValueError(f"Insufficient {base} balance")
                    self.balances[base] = self.balances.get(base, 0) - quantity
                    net_proceeds = cost - commission
                    self.balances[quote] = self.balances.get(quote, 0) + net_proceeds

                order_id = str(self.order_counter)
                self.order_counter += 1

                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'limit',
                    'side': side.value,
                    'price': price,
                    'amount': quantity,
                    'filled': quantity,
                    'remaining': 0,
                    'status': 'closed',
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'fee': {'cost': commission, 'currency': quote}
                }

                self.orders[order_id] = order
                logger.info(f"Paper limit order executed immediately: {side.value.upper()} {quantity} {symbol} @ ${price}")
                return order

            else:
                # Store as pending order
                order_id = str(self.order_counter)
                self.order_counter += 1

                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'limit',
                    'side': side.value,
                    'price': price,
                    'amount': quantity,
                    'filled': 0,
                    'remaining': quantity,
                    'status': 'open',
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'fee': None
                }

                self.orders[order_id] = order
                logger.info(f"Paper limit order placed: {side.value.upper()} {quantity} {symbol} @ ${price}")
                return order

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

        Note: In paper trading, these are stored as pending until triggered
        """
        try:
            order_id = str(self.order_counter)
            self.order_counter += 1

            order = {
                'id': order_id,
                'symbol': symbol,
                'type': 'stop_loss',
                'side': side.value,
                'price': stop_price,
                'amount': quantity,
                'filled': 0,
                'remaining': quantity,
                'status': 'open',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'datetime': datetime.now().isoformat(),
                'stopPrice': stop_price,
                'fee': None
            }

            self.orders[order_id] = order
            logger.info(f"Paper stop-loss order placed: {side.value.upper()} {quantity} {symbol} @ stop ${stop_price}")
            return order

        except Exception as e:
            logger.error(f"Error placing stop-loss order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order
        """
        try:
            if order_id not in self.orders:
                logger.warning(f"Order {order_id} not found")
                return False

            order = self.orders[order_id]

            if order['status'] != 'open':
                logger.warning(f"Order {order_id} is not open (status: {order['status']})")
                return False

            # Cancel the order
            order['status'] = 'canceled'
            logger.info(f"Paper order {order_id} cancelled")
            return True

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """
        Get order status
        """
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")

        return self.orders[order_id]

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders
        """
        open_orders = [
            order for order in self.orders.values()
            if order['status'] == 'open'
        ]

        if symbol:
            open_orders = [o for o in open_orders if o['symbol'] == symbol]

        return open_orders

    async def get_positions(self) -> List[Dict]:
        """
        Get current open positions

        For paper trading, this returns all non-zero non-USDT balances
        """
        positions = []
        for currency, amount in self.balances.items():
            if amount > 0 and currency not in ['USDT', 'USD', 'BUSD']:
                positions.append({
                    'symbol': f'{currency}/USDT',
                    'side': 'long',
                    'quantity': amount,
                    'currency': currency
                })

        return positions

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get trade history
        """
        trades = self.trades.copy()

        if symbol:
            trades = [t for t in trades if t['symbol'] == symbol]

        # Return most recent trades first
        trades.reverse()
        return trades[:limit]

    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information
        """
        price = await self._get_market_price(symbol)

        # Simulate bid/ask spread
        spread = price * 0.0001  # 0.01% spread
        bid = price - spread / 2
        ask = price + spread / 2

        return {
            'symbol': symbol,
            'bid': bid,
            'ask': ask,
            'last': price,
            'open': price * 0.99,  # Simulated
            'high': price * 1.02,  # Simulated
            'low': price * 0.98,   # Simulated
            'volume': 1000000,     # Simulated
            'timestamp': int(datetime.now().timestamp() * 1000),
        }

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book (simulated for paper trading)
        """
        price = await self._get_market_price(symbol)

        # Simulate order book with bids and asks
        bids = []
        asks = []

        for i in range(limit):
            # Bids (buy orders) below market price
            bid_price = price * (1 - (i + 1) * 0.0001)
            bid_quantity = random.uniform(0.1, 2.0)
            bids.append([bid_price, bid_quantity])

            # Asks (sell orders) above market price
            ask_price = price * (1 + (i + 1) * 0.0001)
            ask_quantity = random.uniform(0.1, 2.0)
            asks.append([ask_price, ask_quantity])

        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': int(datetime.now().timestamp() * 1000),
        }

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format
        """
        return symbol

    async def close(self):
        """
        Close exchange connection (no-op for paper trading)
        """
        logger.info("Paper trading exchange closed")

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()

    # Additional helper methods for paper trading

    def reset_account(self, initial_balance: Dict[str, float] = None):
        """
        Reset paper trading account to initial state

        Args:
            initial_balance: New starting balance
        """
        if initial_balance is None:
            initial_balance = {"USDT": 10000.0}

        self.balances = initial_balance.copy()
        self.orders = {}
        self.trades = []
        self.order_counter = 1000

        logger.info(f"Paper trading account reset with balance: {initial_balance}")

    def get_account_summary(self) -> Dict:
        """
        Get comprehensive account summary

        Returns:
            Dict with balance, positions, open orders, trade history
        """
        return {
            'balances': self.balances.copy(),
            'total_trades': len(self.trades),
            'open_orders': len([o for o in self.orders.values() if o['status'] == 'open']),
            'total_orders': len(self.orders),
            'positions': len([b for b in self.balances.values() if b > 0])
        }
