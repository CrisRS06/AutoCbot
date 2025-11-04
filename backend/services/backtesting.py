"""Backtesting Service"""

import logging
from typing import List, Dict
from models.schemas import BacktestRequest, BacktestResult

logger = logging.getLogger(__name__)


class BacktestingService:
    """Backtesting service"""

    def __init__(self):
        self.results: List[BacktestResult] = []

    async def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        """Run a backtest"""
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

        self.results.append(result)
        return result

    async def get_results(self, limit: int = 10) -> List[BacktestResult]:
        """Get previous backtest results"""
        return self.results[-limit:]
