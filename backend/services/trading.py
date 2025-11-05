"""
Trading Service - Complete Implementation
Supports both paper trading and live trading with risk management
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .exchanges import (
    BaseExchange,
    ExchangeFactory,
    ExchangeType,
    OrderSide,
    OrderStatus
)
from .risk_manager import RiskManager, RiskLimits
from database.models import Order, Trade, Position
from database.models import OrderSide as DBOrderSide, OrderType as DBOrderType, OrderStatus as DBOrderStatus

logger = logging.getLogger(__name__)


class TradingService:
    """
    Trading service with exchange integration and risk management
    Supports both paper trading and live trading
    """

    def __init__(
        self,
        exchange: Optional[BaseExchange] = None,
        risk_manager: Optional[RiskManager] = None,
        db: Optional[Session] = None,
        mode: str = "paper"
    ):
        """
        Initialize Trading Service

        Args:
            exchange: Exchange connector instance (creates paper trading if None)
            risk_manager: Risk manager instance (creates default if None)
            db: Database session for persistence
            mode: Trading mode ('paper' or 'live')
        """
        self.mode = mode
        self.db = db

        # Initialize exchange
        if exchange is None:
            logger.info("No exchange provided, creating paper trading exchange")
            self.exchange = ExchangeFactory.create_exchange(
                exchange_type=ExchangeType.PAPER_TRADING,
                initial_balance={"USDT": 10000.0},
                use_singleton=False
            )
        else:
            self.exchange = exchange

        # Initialize risk manager
        self.risk_manager = risk_manager or RiskManager()

        logger.info(f"Trading service initialized in {mode} mode")

    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dict with currency balances
        """
        try:
            balance = await self.exchange.get_balance()
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise

    async def get_portfolio_value(self) -> float:
        """
        Calculate total portfolio value in USDT

        Returns:
            Total portfolio value
        """
        try:
            balance = await self.get_balance()

            # Start with USDT/stablecoin balance
            total_value = balance.get('USDT', 0.0)
            total_value += balance.get('USD', 0.0)
            total_value += balance.get('BUSD', 0.0)

            # Add value of other holdings
            for currency, amount in balance.items():
                if currency not in ['USDT', 'USD', 'BUSD'] and amount > 0:
                    try:
                        symbol = f"{currency}/USDT"
                        ticker = await self.exchange.get_ticker(symbol)
                        price = ticker.get('last', 0)
                        total_value += amount * price
                    except Exception as e:
                        logger.warning(f"Could not get price for {currency}: {e}")

            return total_value

        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return 0.0

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        validate_risk: bool = True
    ) -> Dict:
        """
        Create a new order with risk management

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market' or 'limit')
            amount: Order quantity
            price: Limit price (required for limit orders)
            stop_loss: Optional stop-loss price
            take_profit: Optional take-profit price
            validate_risk: Whether to validate against risk rules

        Returns:
            Order details
        """
        try:
            # Convert side string to OrderSide enum
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL

            # Get current market price
            ticker = await self.exchange.get_ticker(symbol)
            market_price = ticker.get('last', 0)

            # Use market price if no price provided
            entry_price = price if price else market_price

            # Validate risk if enabled
            if validate_risk:
                portfolio_value = await self.get_portfolio_value()
                balance = await self.get_balance()
                available_balance = balance.get('USDT', 0)
                open_positions = await self.get_positions()

                # Prepare open positions for risk assessment
                position_list = [
                    {
                        'value': p.get('quantity', 0) * p.get('entry_price', 0),
                        'risk_amount': p.get('quantity', 0) * abs(p.get('entry_price', 0) - p.get('stop_loss', entry_price)) if p.get('stop_loss') else 0
                    }
                    for p in open_positions
                ]

                # Validate trade
                approved, reason = self.risk_manager.validate_trade(
                    entry_price=entry_price,
                    stop_loss_price=stop_loss,
                    take_profit_price=take_profit,
                    quantity=amount,
                    portfolio_value=portfolio_value,
                    available_balance=available_balance,
                    open_positions=position_list
                )

                if not approved:
                    logger.warning(f"Trade rejected by risk manager: {reason}")
                    raise ValueError(f"Risk validation failed: {reason}")

            # Place order based on type
            if order_type.lower() == 'market':
                order = await self.exchange.place_market_order(
                    symbol=symbol,
                    side=order_side,
                    quantity=amount
                )
            elif order_type.lower() == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = await self.exchange.place_limit_order(
                    symbol=symbol,
                    side=order_side,
                    price=price,
                    quantity=amount
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            # Place stop-loss order if provided
            if stop_loss and order.get('status') == 'closed':
                try:
                    # For filled orders, place stop-loss
                    stop_side = OrderSide.SELL if order_side == OrderSide.BUY else OrderSide.BUY
                    stop_order = await self.exchange.place_stop_loss_order(
                        symbol=symbol,
                        side=stop_side,
                        stop_price=stop_loss,
                        quantity=amount
                    )
                    order['stop_loss_order_id'] = stop_order.get('id')
                    logger.info(f"Stop-loss order placed: {stop_order.get('id')}")
                except Exception as e:
                    logger.error(f"Error placing stop-loss order: {e}")

            # Place take-profit order if provided
            if take_profit and order.get('status') == 'closed':
                try:
                    # For filled orders, place take-profit limit order
                    tp_side = OrderSide.SELL if order_side == OrderSide.BUY else OrderSide.BUY
                    tp_order = await self.exchange.place_limit_order(
                        symbol=symbol,
                        side=tp_side,
                        price=take_profit,
                        quantity=amount
                    )
                    order['take_profit_order_id'] = tp_order.get('id')
                    logger.info(f"Take-profit order placed: {tp_order.get('id')}")
                except Exception as e:
                    logger.error(f"Error placing take-profit order: {e}")

            # Save to database if session available
            if self.db and order.get('status') == 'closed':
                await self._save_order_to_db(order)

            logger.info(f"Order created: {order.get('id')} - {side.upper()} {amount} {symbol}")
            return order

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def create_smart_order(
        self,
        symbol: str,
        side: str,
        risk_pct: float = 0.02,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> Dict:
        """
        Create order with automatic position sizing based on risk

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            risk_pct: Portfolio risk percentage (default 2%)
            stop_loss_pct: Stop-loss percentage (default from risk manager)
            take_profit_pct: Take-profit percentage (default from risk manager)

        Returns:
            Order details with position sizing information
        """
        try:
            # Get current market price
            ticker = await self.exchange.get_ticker(symbol)
            entry_price = ticker.get('last', 0)

            # Calculate stop-loss and take-profit
            stop_loss_price = self.risk_manager.calculate_stop_loss(
                entry_price=entry_price,
                side=side,
                stop_loss_pct=stop_loss_pct
            )

            take_profit_price = self.risk_manager.calculate_take_profit(
                entry_price=entry_price,
                side=side,
                take_profit_pct=take_profit_pct
            )

            # Get portfolio value
            portfolio_value = await self.get_portfolio_value()

            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                portfolio_value=portfolio_value,
                risk_pct=risk_pct,
                take_profit_price=take_profit_price
            )

            if not position_size.approved:
                raise ValueError(f"Position sizing rejected: {position_size.rejection_reason}")

            # Create order with calculated quantity
            order = await self.create_order(
                symbol=symbol,
                side=side,
                order_type='market',
                amount=position_size.quantity,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price,
                validate_risk=True
            )

            # Add position sizing info to response
            order['position_sizing'] = {
                'quantity': position_size.quantity,
                'entry_price': position_size.entry_price,
                'stop_loss': position_size.stop_loss_price,
                'take_profit': position_size.take_profit_price,
                'position_value': position_size.position_value,
                'risk_amount': position_size.risk_amount,
                'risk_pct': position_size.risk_pct,
                'risk_reward_ratio': position_size.risk_reward_ratio
            }

            return order

        except Exception as e:
            logger.error(f"Error creating smart order: {e}")
            raise

    async def get_orders(self, status: str = "open") -> List[Dict]:
        """
        Get orders by status

        Args:
            status: Order status filter ('open', 'closed', 'all')

        Returns:
            List of orders
        """
        try:
            if status == "open":
                orders = await self.exchange.get_open_orders()
                return orders
            elif status == "all":
                # For paper trading, get from exchange
                # For live trading, might need to query database
                return await self.exchange.get_open_orders()
            else:
                # Filter by status
                all_orders = await self.exchange.get_open_orders()
                return [o for o in all_orders if o.get('status') == status]

        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []

    async def cancel_order(self, order_id: str, symbol: str = None) -> Dict:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel
            symbol: Trading symbol (optional, may be required by some exchanges)

        Returns:
            Result dict with success status
        """
        try:
            # Try to get symbol from open orders if not provided
            if not symbol:
                open_orders = await self.get_orders("open")
                for order in open_orders:
                    if order.get('id') == order_id:
                        symbol = order.get('symbol')
                        break

            if not symbol:
                return {"success": False, "error": "Symbol required for order cancellation"}

            success = await self.exchange.cancel_order(order_id, symbol)

            return {
                "success": success,
                "order_id": order_id,
                "message": "Order cancelled successfully" if success else "Failed to cancel order"
            }

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_positions(self) -> List[Dict]:
        """
        Get current open positions

        Returns:
            List of positions
        """
        try:
            positions = await self.exchange.get_positions()
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def close_all_positions(self) -> Dict:
        """
        Close all open positions (emergency stop)

        Returns:
            Result dict with closed positions
        """
        try:
            positions = await self.get_positions()
            closed = []
            errors = []

            for position in positions:
                try:
                    symbol = position.get('symbol')
                    quantity = position.get('quantity', 0)
                    side_str = position.get('side', 'long')

                    # Determine order side (opposite of position)
                    if side_str.lower() == 'long':
                        order_side = 'sell'
                    else:
                        order_side = 'buy'

                    # Close position with market order
                    order = await self.create_order(
                        symbol=symbol,
                        side=order_side,
                        order_type='market',
                        amount=quantity,
                        validate_risk=False  # Skip risk validation for emergency close
                    )

                    closed.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'order_id': order.get('id')
                    })

                    logger.info(f"Closed position: {symbol}")

                except Exception as e:
                    logger.error(f"Error closing position {position.get('symbol')}: {e}")
                    errors.append({
                        'symbol': position.get('symbol'),
                        'error': str(e)
                    })

            return {
                "success": True,
                "closed_positions": closed,
                "count": len(closed),
                "errors": errors if errors else None
            }

        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            raise

    async def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get trade history

        Args:
            symbol: Optional symbol filter
            limit: Maximum number of trades to return

        Returns:
            List of trades
        """
        try:
            trades = await self.exchange.get_trades(symbol=symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            return []

    async def _save_order_to_db(self, order: Dict):
        """
        Save order to database

        Args:
            order: Order dict from exchange
        """
        if not self.db:
            return

        try:
            # Map order to database model
            db_order = Order(
                exchange_order_id=order.get('id'),
                symbol=order.get('symbol'),
                side=DBOrderSide.BUY if order.get('side') == 'buy' else DBOrderSide.SELL,
                type=DBOrderType.MARKET if order.get('type') == 'market' else DBOrderType.LIMIT,
                status=DBOrderStatus.FILLED if order.get('status') == 'closed' else DBOrderStatus.OPEN,
                quantity=order.get('amount', 0),
                price=order.get('price'),
                filled_quantity=order.get('filled', 0),
                average_price=order.get('price'),
                commission=order.get('fee', {}).get('cost', 0) if order.get('fee') else 0
            )

            self.db.add(db_order)
            self.db.commit()
            logger.debug(f"Order saved to database: {order.get('id')}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving order to database: {e}")

    async def close(self):
        """Close exchange connection"""
        if self.exchange:
            await self.exchange.close()
            logger.info("Trading service closed")
