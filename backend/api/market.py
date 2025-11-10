"""
Market Data API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models.schemas import (
    MarketPrice,
    MarketOverview,
    CandleData,
    TechnicalIndicators
)
from services.market_service import MarketDataService
from services.technical_analysis import TechnicalAnalysisService

router = APIRouter()
market_service = MarketDataService()
technical_service = TechnicalAnalysisService()


@router.get("/overview", response_model=MarketOverview)
async def get_market_overview():
    """Get overall market overview"""
    try:
        data = await market_service.get_market_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices", response_model=List[MarketPrice])
async def get_current_prices(
    symbols: str = Query(..., description="Comma-separated symbols (e.g., BTC/USDT,ETH/USDT)")
):
    """Get current prices for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        prices = await market_service.get_prices(symbol_list)
        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}", response_model=MarketPrice)
async def get_price(symbol: str):
    """Get current price for a single symbol"""
    try:
        price = await market_service.get_price(symbol)
        if not price:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        return price
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candles/{symbol}", response_model=List[CandleData])
async def get_candles(
    symbol: str,
    timeframe: str = Query("5m", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """Get historical candle data"""
    try:
        candles = await market_service.get_candles(symbol, timeframe, limit)
        return candles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}", response_model=TechnicalIndicators)
async def get_technical_indicators(
    symbol: str,
    timeframe: str = Query("5m", description="Timeframe")
):
    """Get technical indicators for a symbol"""
    try:
        indicators = await technical_service.calculate_indicators(symbol, timeframe)
        return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_coins(limit: int = Query(10, ge=1, le=50)):
    """Get trending cryptocurrencies"""
    try:
        trending = await market_service.get_trending_coins(limit)
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gainers-losers")
async def get_gainers_losers(limit: int = Query(10, ge=1, le=50)):
    """Get top gainers and losers"""
    try:
        data = await market_service.get_gainers_losers(limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
