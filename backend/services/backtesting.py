"""
Backtesting Service - Database-backed version
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.schemas import BacktestRequest, BacktestResult
from database.models import BacktestResult as BacktestResultModel, Strategy

logger = logging.getLogger(__name__)


class BacktestingService:
    """
    Backtesting service with database persistence

    Note: This is currently returning mock data.
    Real backtesting logic will be implemented in Phase 2.
    """

    def __init__(self, db: Session = None):
        """
        Initialize BacktestingService

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        """
        Run a backtest (currently returns mock data)

        Args:
            request: BacktestRequest with strategy name and parameters

        Returns:
            BacktestResult with mock metrics
        """
        logger.info(f"Running backtest for strategy: {request.strategy_name}")

        # TODO: Phase 2 - Implement real backtesting logic
        # For now, return mock data but save to database

        # Simulated backtest result
        result = BacktestResult(
            strategy=request.strategy_name,
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

        # Save to database if db session is available
        if self.db:
            try:
                # Get strategy from database
                strategy = self.db.query(Strategy).filter(
                    Strategy.name == request.strategy_name
                ).first()

                if strategy:
                    # Create backtest result record
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)  # Default 30 days

                    backtest_record = BacktestResultModel(
                        strategy_id=strategy.id,
                        start_date=start_date,
                        end_date=end_date,
                        initial_capital=10000.0,
                        final_balance=10000.0,  # Mock
                        total_return=0.0,
                        total_trades=0,
                        winning_trades=0,
                        losing_trades=0,
                        metrics_json={
                            "win_rate": 0.0,
                            "profit_factor": 0.0,
                            "sharpe_ratio": 0.0,
                            "max_drawdown": 0.0,
                        },
                        equity_curve_json=[],
                        trades_json=[]
                    )

                    self.db.add(backtest_record)
                    self.db.commit()
                    logger.info(f"Saved backtest result to database for strategy: {request.strategy_name}")

            except Exception as e:
                logger.error(f"Error saving backtest result: {e}")
                self.db.rollback()

        return result

    async def get_results(self, limit: int = 10) -> List[BacktestResult]:
        """
        Get previous backtest results from database

        Args:
            limit: Maximum number of results to return

        Returns:
            List of BacktestResult objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            # Get recent backtest results from database
            results = self.db.query(BacktestResultModel).order_by(
                BacktestResultModel.created_at.desc()
            ).limit(limit).all()

            # Convert to schema format
            backtest_results = []
            for result in results:
                strategy = result.strategy
                metrics = result.metrics_json or {}

                backtest_results.append(BacktestResult(
                    strategy=strategy.name if strategy else "Unknown",
                    total_trades=result.total_trades,
                    winning_trades=result.winning_trades,
                    losing_trades=result.losing_trades,
                    win_rate=metrics.get("win_rate", 0.0),
                    total_pnl=result.final_balance - result.initial_capital,
                    total_pnl_percentage=result.total_return,
                    sharpe_ratio=metrics.get("sharpe_ratio", 0.0),
                    max_drawdown=metrics.get("max_drawdown", 0.0),
                    avg_trade_duration="0h",  # TODO: Calculate from trades_json
                    best_trade=0.0,  # TODO: Extract from trades_json
                    worst_trade=0.0  # TODO: Extract from trades_json
                ))

            return backtest_results

        except Exception as e:
            logger.error(f"Error retrieving backtest results: {e}")
            return []

    async def get_backtest_by_id(self, backtest_id: int) -> Dict:
        """
        Get detailed backtest result by ID

        Args:
            backtest_id: Backtest database ID

        Returns:
            Dict with detailed backtest information
        """
        if not self.db:
            return {}

        try:
            result = self.db.query(BacktestResultModel).filter(
                BacktestResultModel.id == backtest_id
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
