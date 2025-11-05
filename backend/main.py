"""
AutoCbot Main API Server
FastAPI backend for AI-powered crypto trading
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, List
import asyncio

from api import router
from services.market_data import MarketDataService
from services.sentiment import SentimentService
from services.fundamental import FundamentalService
from services.websocket_manager import WebSocketManager
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
market_data_service: MarketDataService = None
sentiment_service: SentimentService = None
fundamental_service: FundamentalService = None
ws_manager: WebSocketManager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global market_data_service, sentiment_service, fundamental_service

    logger.info("🚀 Starting AutoCbot Backend...")

    # Initialize database
    logger.info("📊 Initializing database...")
    try:
        from database.session import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # Initialize services
    market_data_service = MarketDataService()
    sentiment_service = SentimentService()
    fundamental_service = FundamentalService()

    # Start background tasks
    asyncio.create_task(market_data_service.start_price_updates())
    asyncio.create_task(sentiment_service.start_periodic_updates())

    logger.info("✅ All services initialized")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Shutting down AutoCbot Backend...")
    await market_data_service.stop()
    await sentiment_service.stop()
    logger.info("👋 Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AutoCbot API",
    description="AI-Powered Crypto Trading System - The Ultimate Stack",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AutoCbot API",
        "version": "1.0.0",
        "status": "operational",
        "description": "AI-Powered Crypto Trading System"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "market_data": market_data_service.is_running if market_data_service else False,
            "sentiment": sentiment_service.is_running if sentiment_service else False,
            "fundamental": fundamental_service.is_running if fundamental_service else False
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            # Handle subscription requests
            if data.startswith("subscribe:"):
                channel = data.split(":")[1]
                await ws_manager.subscribe(websocket, channel)
            elif data.startswith("unsubscribe:"):
                channel = data.split(":")[1]
                await ws_manager.unsubscribe(websocket, channel)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
