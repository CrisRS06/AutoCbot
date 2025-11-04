"""API routes"""
from fastapi import APIRouter

from .market import router as market_router
from .sentiment import router as sentiment_router
from .trading import router as trading_router
from .portfolio import router as portfolio_router
from .strategy import router as strategy_router

router = APIRouter()

router.include_router(market_router, prefix="/market", tags=["market"])
router.include_router(sentiment_router, prefix="/sentiment", tags=["sentiment"])
router.include_router(trading_router, prefix="/trading", tags=["trading"])
router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
router.include_router(strategy_router, prefix="/strategy", tags=["strategy"])

__all__ = ["router"]
