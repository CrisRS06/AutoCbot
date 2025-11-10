"""
Strategy Management API Routes - Database-backed version
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.schemas import (
    StrategyConfig,
    BacktestRequest,
    BacktestResult
)
from services.strategy_manager import StrategyManager
from services.backtesting import BacktestingService
from database.session import get_db
from database.models import User
from utils.auth import get_current_user

router = APIRouter()


@router.get("/list", response_model=List[StrategyConfig])
async def list_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available strategies"""
    try:
        strategy_manager = StrategyManager(db=db)
        strategies = await strategy_manager.list_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}", response_model=StrategyConfig)
async def get_strategy(
    strategy_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get strategy configuration"""
    try:
        strategy_manager = StrategyManager(db=db)
        strategy = await strategy_manager.get_strategy(strategy_name)
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_name} not found")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=StrategyConfig)
async def create_strategy(
    config: StrategyConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a strategy"""
    try:
        strategy_manager = StrategyManager(db=db)
        strategy = await strategy_manager.save_strategy(config)
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{strategy_name}/toggle")
async def toggle_strategy(
    strategy_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable/disable a strategy"""
    try:
        strategy_manager = StrategyManager(db=db)
        strategy = await strategy_manager.toggle_strategy(strategy_name)
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_name}")
async def delete_strategy(
    strategy_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a strategy"""
    try:
        strategy_manager = StrategyManager(db=db)
        result = await strategy_manager.delete_strategy(strategy_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run a backtest"""
    try:
        backtest_service = BacktestingService(db=db)
        result = await backtest_service.run_backtest(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest/results")
async def get_backtest_results(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get previous backtest results"""
    try:
        backtest_service = BacktestingService(db=db)
        results = await backtest_service.get_results(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest/{backtest_id}")
async def get_backtest_details(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed backtest result by ID"""
    try:
        backtest_service = BacktestingService(db=db)
        result = await backtest_service.get_backtest_by_id(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="Backtest not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
