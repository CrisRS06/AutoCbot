"""
Trading API Routes - Integrated with Exchange Connectors and Risk Management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from models.schemas import (
    TradingSignal,
    OrderSide,
    OrderType
)
from services.trading import TradingService
from services.signal_generator import SignalGeneratorService
from database.session import get_db
from database.models import User
from utils.auth import get_current_user

router = APIRouter()
signal_service = SignalGeneratorService()


def get_trading_service(db: Session = Depends(get_db)) -> TradingService:
    """
    Dependency injection for trading service with database session
    Creates paper trading exchange by default
    """
    return TradingService(db=db, mode="paper")


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
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    validate_risk: bool = True,
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order with optional risk management

    Args:
        symbol: Trading pair (e.g., "BTC/USDT")
        side: Order side (BUY or SELL)
        order_type: Order type (MARKET or LIMIT)
        amount: Order quantity
        price: Limit price (required for limit orders)
        stop_loss: Optional stop-loss price
        take_profit: Optional take-profit price
        validate_risk: Whether to validate against risk rules
    """
    try:
        order = await trading_service.create_order(
            symbol=symbol,
            side=side.value,
            order_type=order_type.value,
            amount=amount,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            validate_risk=validate_risk
        )
        return order
    except ValueError as e:
        # Risk validation failures return 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-order")
async def create_smart_order(
    symbol: str,
    side: OrderSide,
    risk_pct: float = 0.02,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create order with automatic position sizing based on risk

    Args:
        symbol: Trading pair (e.g., "BTC/USDT")
        side: Order side (BUY or SELL)
        risk_pct: Portfolio risk percentage (default 2%)
        stop_loss_pct: Stop-loss percentage
        take_profit_pct: Take-profit percentage

    Returns:
        Order details with position sizing information
    """
    try:
        order = await trading_service.create_smart_order(
            symbol=symbol,
            side=side.value,
            risk_pct=risk_pct,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(
    status: str = "open",
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get orders by status

    Args:
        status: Order status filter ('open', 'closed', 'all')
    """
    try:
        orders = await trading_service.get_orders(status)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_order(
    order_id: str,
    symbol: Optional[str] = None,
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order

    Args:
        order_id: Order ID to cancel
        symbol: Trading symbol (optional)
    """
    try:
        result = await trading_service.cancel_order(order_id, symbol)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Order not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions(
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """Get current open positions"""
    try:
        positions = await trading_service.get_positions()
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance")
async def get_balance(
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """Get account balance"""
    try:
        balance = await trading_service.get_balance()
        return balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio-value")
async def get_portfolio_value(
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """Get total portfolio value in USDT"""
    try:
        value = await trading_service.get_portfolio_value()
        return {"total_value": value, "currency": "USDT"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def get_trades(
    symbol: Optional[str] = None,
    limit: int = 100,
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get trade history

    Args:
        symbol: Optional symbol filter
        limit: Maximum number of trades to return
    """
    try:
        trades = await trading_service.get_trades(symbol=symbol, limit=limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-all")
async def close_all_positions(
    trading_service: TradingService = Depends(get_trading_service),
    current_user: User = Depends(get_current_user)
):
    """Close all open positions (emergency stop)"""
    try:
        result = await trading_service.close_all_positions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
