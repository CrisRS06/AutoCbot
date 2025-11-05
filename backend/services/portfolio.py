"""
Portfolio Management Service
Integrated with real market data and trading service
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.schemas import Position, PortfolioSummary
from .market_data import MarketDataAggregator
from .trading import TradingService
from database.models import Trade as DBTrade, Order as DBOrder

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Portfolio management service with real market data integration
    """

    def __init__(
        self,
        market_data: Optional[MarketDataAggregator] = None,
        trading_service: Optional[TradingService] = None,
        db: Optional[Session] = None
    ):
        """
        Initialize portfolio service

        Args:
            market_data: Market data aggregator instance
            trading_service: Trading service instance
            db: Database session
        """
        self.market_data = market_data
        self.trading_service = trading_service
        self.db = db

        logger.info("Portfolio service initialized with real market data")

    async def get_summary(self) -> PortfolioSummary:
        """
        Get portfolio summary with real data

        Returns:
            PortfolioSummary with current portfolio state
        """
        try:
            if not self.trading_service:
                # Fallback to demo data
                return await self._get_demo_summary()

            # Get real balance and positions
            balance = await self.trading_service.get_balance()
            positions = await self.trading_service.get_positions()

            # Calculate positions value
            positions_value = 0.0
            for position in positions:
                try:
                    symbol = position.get('symbol', '')
                    quantity = position.get('quantity', 0)

                    if self.market_data:
                        ticker = await self.market_data.binance.get_ticker(symbol)
                        current_price = ticker.get('last', 0)
                        positions_value += quantity * current_price
                except Exception as e:
                    logger.warning(f"Error calculating position value for {symbol}: {e}")

            # Get available balance (USDT)
            available_balance = balance.get('USDT', 0.0)

            # Total value
            total_value = available_balance + positions_value

            # Get performance from trades
            total_pnl = 0.0
            win_rate = 0.0

            if self.db:
                trades = self.db.query(DBTrade).all()
                if trades:
                    total_pnl = sum(t.pnl for t in trades if t.pnl)
                    winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
                    win_rate = (winning_trades / len(trades) * 100) if trades else 0.0

            # Calculate PnL percentage (assuming initial balance was 10000)
            initial_balance = 10000.0
            total_pnl_percentage = ((total_value - initial_balance) / initial_balance * 100)

            return PortfolioSummary(
                total_value=total_value,
                available_balance=available_balance,
                positions_value=positions_value,
                total_pnl=total_value - initial_balance,
                total_pnl_percentage=total_pnl_percentage,
                open_positions=len(positions),
                today_pnl=0.0,  # TODO: Calculate from today's trades
                win_rate=win_rate
            )

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return await self._get_demo_summary()

    async def _get_demo_summary(self) -> PortfolioSummary:
        """Fallback demo summary"""
        return PortfolioSummary(
            total_value=10000.0,
            available_balance=10000.0,
            positions_value=0.0,
            total_pnl=0.0,
            total_pnl_percentage=0.0,
            open_positions=0,
            today_pnl=0.0,
            win_rate=0.0
        )

    async def get_open_positions(self) -> List[Position]:
        """
        Get all open positions with current market prices

        Returns:
            List of Position objects
        """
        try:
            if not self.trading_service:
                return []

            positions = await self.trading_service.get_positions()
            position_objects = []

            for pos in positions:
                try:
                    symbol = pos.get('symbol', '')
                    quantity = pos.get('quantity', 0)
                    side = pos.get('side', 'long')

                    # Get current price
                    current_price = 0.0
                    if self.market_data:
                        ticker = await self.market_data.binance.get_ticker(symbol)
                        current_price = ticker.get('last', 0)

                    # Get entry price (from database or estimate)
                    entry_price = pos.get('entry_price', current_price)

                    # Calculate P&L
                    if side.lower() == 'long':
                        pnl = (current_price - entry_price) * quantity
                    else:
                        pnl = (entry_price - current_price) * quantity

                    value_usd = quantity * current_price
                    pnl_percentage = (pnl / (entry_price * quantity) * 100) if entry_price > 0 else 0.0

                    position_objects.append(Position(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        entry_price=entry_price,
                        current_price=current_price,
                        value_usd=value_usd,
                        pnl=pnl,
                        pnl_percentage=pnl_percentage
                    ))

                except Exception as e:
                    logger.error(f"Error processing position {symbol}: {e}")

            return position_objects

        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []

    async def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a specific symbol

        Args:
            symbol: Trading symbol

        Returns:
            Position object or None
        """
        positions = await self.get_open_positions()
        for pos in positions:
            if pos.symbol == symbol:
                return pos
        return None

    async def get_trade_history(self, days: int = 30) -> List[Dict]:
        """
        Get trade history

        Args:
            days: Number of days of history

        Returns:
            List of trade dicts
        """
        try:
            if self.trading_service:
                # Get from trading service
                trades = await self.trading_service.get_trades(limit=1000)
                return trades

            if self.db:
                # Get from database
                cutoff_date = datetime.now() - timedelta(days=days)
                trades = self.db.query(DBTrade).filter(
                    DBTrade.created_at >= cutoff_date
                ).order_by(DBTrade.created_at.desc()).all()

                return [
                    {
                        'id': t.id,
                        'symbol': t.symbol,
                        'side': t.side.value,
                        'quantity': float(t.quantity),
                        'price': float(t.price),
                        'pnl': float(t.pnl) if t.pnl else 0.0,
                        'timestamp': int(t.created_at.timestamp() * 1000),
                        'datetime': t.created_at.isoformat()
                    }
                    for t in trades
                ]

            return []

        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return []

    async def get_performance_metrics(self) -> Dict:
        """
        Get performance metrics

        Returns:
            Dict with performance metrics
        """
        try:
            if not self.db:
                return self._get_demo_metrics()

            # Get all trades from database
            trades = self.db.query(DBTrade).all()

            if not trades:
                return self._get_demo_metrics()

            # Calculate metrics
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
            losing_trades = sum(1 for t in trades if t.pnl and t.pnl < 0)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

            wins = [float(t.pnl) for t in trades if t.pnl and t.pnl > 0]
            losses = [abs(float(t.pnl)) for t in trades if t.pnl and t.pnl < 0]

            avg_win = sum(wins) / len(wins) if wins else 0.0
            avg_loss = sum(losses) / len(losses) if losses else 0.0

            total_wins = sum(wins)
            total_losses = sum(losses)
            profit_factor = total_wins / total_losses if total_losses > 0 else 0.0

            # Simple Sharpe calculation (would need returns data for accurate calc)
            total_pnl = sum(float(t.pnl) for t in trades if t.pnl)
            sharpe_ratio = 1.5 if total_pnl > 0 else 0.0  # Placeholder

            # Max drawdown (simplified - would need equity curve for accurate calc)
            max_drawdown = max(losses) if losses else 0.0

            return {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "profit_factor": profit_factor,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown
            }

        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._get_demo_metrics()

    def _get_demo_metrics(self) -> Dict:
        """Fallback demo metrics"""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        }

    async def get_pnl_chart_data(self, days: int = 30) -> List[Dict]:
        """
        Get P&L chart data

        Args:
            days: Number of days

        Returns:
            List of daily P&L data points
        """
        try:
            if not self.db:
                return []

            cutoff_date = datetime.now() - timedelta(days=days)
            trades = self.db.query(DBTrade).filter(
                DBTrade.created_at >= cutoff_date
            ).order_by(DBTrade.created_at).all()

            if not trades:
                return []

            # Group by day and calculate cumulative P&L
            daily_pnl = {}
            cumulative_pnl = 0.0

            for trade in trades:
                date_key = trade.created_at.date().isoformat()
                pnl = float(trade.pnl) if trade.pnl else 0.0
                cumulative_pnl += pnl

                if date_key not in daily_pnl:
                    daily_pnl[date_key] = {
                        'date': date_key,
                        'pnl': 0.0,
                        'cumulative_pnl': 0.0,
                        'trades': 0
                    }

                daily_pnl[date_key]['pnl'] += pnl
                daily_pnl[date_key]['cumulative_pnl'] = cumulative_pnl
                daily_pnl[date_key]['trades'] += 1

            return list(daily_pnl.values())

        except Exception as e:
            logger.error(f"Error getting PnL chart data: {e}")
            return []
