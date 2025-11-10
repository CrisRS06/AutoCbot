"""
Backtesting Service - Complete implementation with real backtesting engine
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.schemas import BacktestRequest, BacktestResult
from database.models import BacktestResult as BacktestResultModel, Strategy
from services.backtest_engine import BacktestEngine

logger = logging.getLogger(__name__)


class BacktestingService:
    """
    Backtesting service with complete backtesting engine
    """

    def __init__(self, db: Session = None):
        """
        Initialize BacktestingService

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def run_backtest(self, request: BacktestRequest, user_id: int) -> BacktestResult:
        """
        Run a complete backtest using the BacktestEngine for a specific user

        Args:
            request: BacktestRequest with strategy name and parameters
            user_id: User ID to verify strategy ownership

        Returns:
            BacktestResult with real metrics
        """
        logger.info(f"Running backtest for strategy: {request.strategy_name} (user {user_id})")

        if not self.db:
            logger.error("No database session available")
            return self._create_empty_result(request.strategy_name)

        try:
            # Get strategy from database (must belong to user)
            strategy = self.db.query(Strategy).filter(
                Strategy.name == request.strategy_name,
                Strategy.user_id == user_id
            ).first()

            if not strategy:
                logger.error(f"Strategy not found or doesn't belong to user: {request.strategy_name}")
                return self._create_empty_result(request.strategy_name)

            # Parse dates (default to last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            # Override with request parameters if provided
            if hasattr(request, 'start_date') and request.start_date:
                start_date = request.start_date
            if hasattr(request, 'end_date') and request.end_date:
                end_date = request.end_date

            # Get backtest parameters
            initial_capital = getattr(request, 'initial_capital', 10000.0)
            commission = getattr(request, 'commission', 0.001)
            slippage = getattr(request, 'slippage', 0.0005)

            # Create backtest engine
            engine = BacktestEngine(
                strategy=strategy,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                commission=commission,
                slippage=slippage,
                db=self.db
            )

            # Run backtest
            result_data = await engine.run()

            if not result_data.get("success"):
                error = result_data.get("error", "Unknown error")
                logger.error(f"Backtest failed: {error}")
                return self._create_empty_result(request.strategy_name)

            # Extract metrics
            metrics = result_data.get("metrics", {})

            # Calculate average trade duration
            trades = result_data.get("trades", [])
            avg_duration_seconds = 0
            if trades:
                total_duration = sum(t.get("duration_seconds", 0) for t in trades)
                avg_duration_seconds = total_duration / len(trades)

            # Format duration as human-readable string
            avg_duration_str = self._format_duration(avg_duration_seconds)

            # Create result schema
            result = BacktestResult(
                strategy=request.strategy_name,
                total_trades=metrics.get("total_trades", 0),
                winning_trades=metrics.get("winning_trades", 0),
                losing_trades=metrics.get("losing_trades", 0),
                win_rate=metrics.get("win_rate", 0.0),
                total_pnl=metrics.get("net_profit", 0.0),
                total_pnl_percentage=metrics.get("total_return_pct", 0.0),
                sharpe_ratio=metrics.get("sharpe_ratio", 0.0),
                max_drawdown=metrics.get("max_drawdown", 0.0),
                avg_trade_duration=avg_duration_str,
                best_trade=metrics.get("largest_win", 0.0),
                worst_trade=metrics.get("largest_loss", 0.0)
            )

            logger.info(
                f"Backtest completed successfully: {metrics.get('total_trades', 0)} trades, "
                f"{metrics.get('win_rate', 0)*100:.1f}% win rate, "
                f"{metrics.get('total_return_pct', 0)*100:.2f}% total return"
            )

            return result

        except Exception as e:
            logger.error(f"Error running backtest: {e}", exc_info=True)
            return self._create_empty_result(request.strategy_name)

    async def get_results(self, user_id: int, limit: int = 10) -> List[BacktestResult]:
        """
        Get previous backtest results from database for a specific user

        Args:
            user_id: User ID to filter results
            limit: Maximum number of results to return

        Returns:
            List of BacktestResult objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            # Get recent backtest results from database (only for user's strategies)
            results = self.db.query(BacktestResultModel).join(Strategy).filter(
                Strategy.user_id == user_id
            ).order_by(
                BacktestResultModel.created_at.desc()
            ).limit(limit).all()

            # Convert to schema format
            backtest_results = []
            for result in results:
                strategy = result.strategy
                metrics = result.metrics_json or {}

                # Calculate average trade duration from trades
                avg_duration_str = "0h"
                if result.trades_json:
                    total_duration = sum(
                        t.get("duration_seconds", 0) for t in result.trades_json
                    )
                    avg_duration = total_duration / len(result.trades_json) if result.trades_json else 0
                    avg_duration_str = self._format_duration(avg_duration)

                # Extract best/worst trades
                best_trade = 0.0
                worst_trade = 0.0
                if result.trades_json:
                    trade_pnls = [t.get("pnl", 0) for t in result.trades_json]
                    if trade_pnls:
                        best_trade = max(trade_pnls)
                        worst_trade = min(trade_pnls)

                backtest_results.append(BacktestResult(
                    strategy=strategy.name if strategy else "Unknown",
                    total_trades=result.total_trades,
                    winning_trades=result.winning_trades,
                    losing_trades=result.losing_trades,
                    win_rate=metrics.get("win_rate", 0.0),
                    total_pnl=metrics.get("net_profit", 0.0),
                    total_pnl_percentage=result.total_return,
                    sharpe_ratio=metrics.get("sharpe_ratio", 0.0),
                    max_drawdown=metrics.get("max_drawdown", 0.0),
                    avg_trade_duration=avg_duration_str,
                    best_trade=best_trade,
                    worst_trade=worst_trade
                ))

            return backtest_results

        except Exception as e:
            logger.error(f"Error retrieving backtest results: {e}")
            return []

    async def get_backtest_by_id(self, backtest_id: int, user_id: int) -> Dict:
        """
        Get detailed backtest result by ID for a specific user

        Args:
            backtest_id: Backtest database ID
            user_id: User ID to verify ownership

        Returns:
            Dict with detailed backtest information
        """
        if not self.db:
            return {}

        try:
            # Get backtest result (must belong to user's strategy)
            result = self.db.query(BacktestResultModel).join(Strategy).filter(
                BacktestResultModel.id == backtest_id,
                Strategy.user_id == user_id
            ).first()

            if not result:
                return {}

            return {
                "id": result.id,
                "strategy_name": result.strategy.name if result.strategy else "Unknown",
                "start_date": result.start_date.isoformat(),
                "end_date": result.end_date.isoformat(),
                "initial_capital": result.initial_capital,
                "final_balance": result.final_balance,
                "total_return": result.total_return,
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "metrics": result.metrics_json,
                "equity_curve": result.equity_curve_json,
                "trades": result.trades_json,
                "created_at": result.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error retrieving backtest {backtest_id}: {e}")
            return {}

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable string

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "2h 30m", "5d 4h")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            return f"{days}d {hours}h" if hours > 0 else f"{days}d"

    def _create_empty_result(self, strategy_name: str) -> BacktestResult:
        """
        Create empty result with zeros

        Args:
            strategy_name: Name of strategy

        Returns:
            BacktestResult with zero values
        """
        return BacktestResult(
            strategy=strategy_name,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_pnl=0.0,
            total_pnl_percentage=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            avg_trade_duration="0h",
            best_trade=0.0,
            worst_trade=0.0
        )
