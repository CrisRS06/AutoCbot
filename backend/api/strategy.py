"""
Strategy Management API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List

from models.schemas import (
    StrategyConfig,
    BacktestRequest,
    BacktestResult
)
from services.strategy_manager import StrategyManager
from services.backtesting import BacktestingService

router = APIRouter()
strategy_manager = StrategyManager()
backtest_service = BacktestingService()


@router.get("/list", response_model=List[StrategyConfig])
async def list_strategies():
    """List all available strategies"""
    try:
        strategies = await strategy_manager.list_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}", response_model=StrategyConfig)
async def get_strategy(strategy_name: str):
    """Get strategy configuration"""
    try:
        strategy = await strategy_manager.get_strategy(strategy_name)
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_name} not found")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=StrategyConfig)
async def create_strategy(config: StrategyConfig):
    """Create or update a strategy"""
    try:
        strategy = await strategy_manager.save_strategy(config)
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{strategy_name}/toggle")
async def toggle_strategy(strategy_name: str):
    """Enable/disable a strategy"""
    try:
        strategy = await strategy_manager.toggle_strategy(strategy_name)
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_name}")
async def delete_strategy(strategy_name: str):
    """Delete a strategy"""
    try:
        result = await strategy_manager.delete_strategy(strategy_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """Run a backtest"""
    try:
        result = await backtest_service.run_backtest(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest/results")
async def get_backtest_results(limit: int = 10):
    """Get previous backtest results"""
    try:
        results = await backtest_service.get_results(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
