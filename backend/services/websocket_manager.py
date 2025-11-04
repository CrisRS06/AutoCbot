"""
WebSocket Manager for real-time data streaming
"""

from fastapi import WebSocket
from typing import List, Dict, Set
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        # Store subscriptions per connection
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a connection to a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)
            logger.info(f"Subscribed to {channel}")

    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a connection from a channel"""
        if websocket in self.subscriptions and channel in self.subscriptions[websocket]:
            self.subscriptions[websocket].remove(channel)
            logger.info(f"Unsubscribed from {channel}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict, channel: str = None):
        """Broadcast a message to all connections or specific channel"""
        disconnected = []

        for connection in self.active_connections:
            # Check if connection is subscribed to channel
            if channel and connection in self.subscriptions:
                if channel not in self.subscriptions[connection]:
                    continue

            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_price_update(self, symbol: str, price: float, change: float):
        """Broadcast price update"""
        await self.broadcast({
            "type": "price_update",
            "symbol": symbol,
            "price": price,
            "change_24h": change
        }, channel="prices")

    async def broadcast_signal(self, signal: dict):
        """Broadcast trading signal"""
        await self.broadcast({
            "type": "trading_signal",
            "data": signal
        }, channel="signals")

    async def broadcast_trade(self, trade: dict):
        """Broadcast trade execution"""
        await self.broadcast({
            "type": "trade_executed",
            "data": trade
        }, channel="trades")

    async def broadcast_portfolio_update(self, portfolio: dict):
        """Broadcast portfolio update"""
        await self.broadcast({
            "type": "portfolio_update",
            "data": portfolio
        }, channel="portfolio")
