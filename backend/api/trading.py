"""
Trading API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List

from models.schemas import (
    TradingSignal,
    OrderSide,
    OrderType
)
from services.trading import TradingService
from services.signal_generator import SignalGeneratorService

router = APIRouter()
trading_service = TradingService()
signal_service = SignalGeneratorService()


@router.get("/signals", response_model=List[TradingSignal])
async def get_trading_signals(symbols: str = None):
    """Get current trading signals"""
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]

        signals = await signal_service.generate_signals(symbol_list)
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signal/{symbol}", response_model=TradingSignal)
async def get_signal(symbol: str):
    """Get trading signal for a specific symbol"""
    try:
        signal = await signal_service.generate_signal(symbol)
        if not signal:
            raise HTTPException(status_code=404, detail=f"No signal available for {symbol}")
        return signal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order")
async def create_order(
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    amount: float,
    price: float = None
):
    """Create a new order"""
    try:
        order = await trading_service.create_order(
            symbol=symbol,
            side=side.value,
            order_type=order_type.value,
            amount=amount,
            price=price
        )
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(status: str = "open"):
    """Get orders"""
    try:
        orders = await trading_service.get_orders(status)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an order"""
    try:
        result = await trading_service.cancel_order(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-all")
async def close_all_positions():
    """Close all open positions (emergency stop)"""
    try:
        result = await trading_service.close_all_positions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
