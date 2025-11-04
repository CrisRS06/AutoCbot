"""Trading Service - Demo/Paper Trading Implementation"""

import logging
from typing import List, Dict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class TradingService:
    """Trading service (paper trading for demo)"""

    def __init__(self):
        self.orders: Dict[str, Dict] = {}
        self.positions: Dict[str, Dict] = {}

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: float = None
    ) -> Dict:
        """Create a new order (paper trading)"""
        order_id = str(uuid.uuid4())

        order = {
            "id": order_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "amount": amount,
            "price": price,
            "status": "open",
            "created_at": datetime.now().isoformat()
        }

        self.orders[order_id] = order
        logger.info(f"Created order: {order}")

        return order

    async def get_orders(self, status: str = "open") -> List[Dict]:
        """Get orders by status"""
        return [
            order for order in self.orders.values()
            if order["status"] == status
        ]

    async def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            return {"success": True, "order_id": order_id}
        return {"success": False, "error": "Order not found"}

    async def close_all_positions(self) -> Dict:
        """Close all open positions"""
        closed = []
        for symbol, position in list(self.positions.items()):
            closed.append(symbol)
            del self.positions[symbol]

        return {
            "success": True,
            "closed_positions": closed,
            "count": len(closed)
        }
