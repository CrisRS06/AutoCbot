"""
Portfolio Management API Routes
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from datetime import datetime, timedelta

from models.schemas import (
    Position,
    PortfolioSummary
)
from services.portfolio import PortfolioService
from database.models import User
from utils.auth import get_current_user

router = APIRouter()
portfolio_service = PortfolioService()


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(current_user: User = Depends(get_current_user)):
    """Get portfolio summary"""
    try:
        summary = await portfolio_service.get_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[Position])
async def get_open_positions(current_user: User = Depends(get_current_user)):
    """Get all open positions"""
    try:
        positions = await portfolio_service.get_open_positions()
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/position/{symbol}", response_model=Position)
async def get_position(symbol: str, current_user: User = Depends(get_current_user)):
    """Get position for a specific symbol"""
    try:
        position = await portfolio_service.get_position(symbol)
        if not position:
            raise HTTPException(status_code=404, detail=f"No position found for {symbol}")
        return position
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_trade_history(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    current_user: User = Depends(get_current_user)
):
    """Get trade history"""
    try:
        history = await portfolio_service.get_trade_history(days)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics(current_user: User = Depends(get_current_user)):
    """Get detailed performance metrics"""
    try:
        metrics = await portfolio_service.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pnl-chart")
async def get_pnl_chart(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """Get P&L chart data"""
    try:
        chart_data = await portfolio_service.get_pnl_chart_data(days)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
