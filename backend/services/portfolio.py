"""Portfolio Management Service"""

import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from models.schemas import Position, PortfolioSummary

logger = logging.getLogger(__name__)


class PortfolioService:
    """Portfolio management service"""

    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.balance = 10000.0  # Demo balance

    async def get_summary(self) -> PortfolioSummary:
        """Get portfolio summary"""
        positions_value = sum(p.value_usd for p in self.positions.values())
        total_pnl = sum(p.pnl for p in self.positions.values())

        return PortfolioSummary(
            total_value=self.balance + positions_value,
            available_balance=self.balance,
            positions_value=positions_value,
            total_pnl=total_pnl,
            total_pnl_percentage=(total_pnl / 10000.0 * 100) if total_pnl else 0,
            open_positions=len(self.positions),
            today_pnl=0.0,
            win_rate=0.0
        )

    async def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())

    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol"""
        return self.positions.get(symbol)

    async def get_trade_history(self, days: int = 30) -> List[Dict]:
        """Get trade history"""
        return []

    async def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
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
        """Get P&L chart data"""
        return []
