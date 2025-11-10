"""API routes"""
from fastapi import APIRouter

from .auth import router as auth_router
from .market import router as market_router
from .sentiment import router as sentiment_router
from .trading import router as trading_router
from .portfolio import router as portfolio_router
from .strategy import router as strategy_router
from .settings import router as settings_router

router = APIRouter()

# Authentication router (public - no auth required for auth endpoints)
router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Public data routers (market data and sentiment are public)
router.include_router(market_router, prefix="/market", tags=["market"])
router.include_router(sentiment_router, prefix="/sentiment", tags=["sentiment"])

# Protected routers (TODO: Add authentication dependencies to individual endpoints)
router.include_router(trading_router, prefix="/trading", tags=["trading"])
router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
router.include_router(strategy_router, prefix="/strategy", tags=["strategy"])
router.include_router(settings_router, prefix="/settings", tags=["settings"])

__all__ = ["router"]
