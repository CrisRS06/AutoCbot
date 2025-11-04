"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TimeFrame(str, Enum):
    """Supported timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class OrderSide(str, Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


# Market Data Schemas
class CandleData(BaseModel):
    """OHLCV candle data"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketPrice(BaseModel):
    """Current market price"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    timestamp: datetime


class MarketOverview(BaseModel):
    """Market overview data"""
    total_market_cap: float
    btc_dominance: float
    eth_dominance: float
    defi_market_cap: float
    total_volume_24h: float
    fear_greed_index: Optional[int] = None


# Sentiment Schemas
class FearGreedIndex(BaseModel):
    """Fear & Greed Index data"""
    value: int = Field(..., ge=0, le=100)
    value_classification: str
    timestamp: datetime
    time_until_update: Optional[int] = None


class SocialSentiment(BaseModel):
    """Social sentiment data"""
    symbol: str
    sentiment_score: float = Field(..., ge=-1, le=1)
    mentions_24h: int
    sentiment_positive: float
    sentiment_negative: float
    sentiment_neutral: float
    trending_rank: Optional[int] = None


class SentimentAnalysis(BaseModel):
    """Combined sentiment analysis"""
    fear_greed: Optional[FearGreedIndex] = None
    social: Optional[List[SocialSentiment]] = None
    overall_sentiment: str  # bearish, neutral, bullish
    confidence: float = Field(..., ge=0, le=1)


# Fundamental Analysis Schemas
class OnChainMetrics(BaseModel):
    """On-chain metrics"""
    symbol: str
    active_addresses: Optional[int] = None
    transaction_count: Optional[int] = None
    exchange_inflow: Optional[float] = None
    exchange_outflow: Optional[float] = None
    whale_transactions: Optional[int] = None
    timestamp: datetime


class TokenMetrics(BaseModel):
    """Token fundamental metrics"""
    symbol: str
    market_cap: float
    fully_diluted_valuation: Optional[float] = None
    circulating_supply: float
    max_supply: Optional[float] = None
    total_supply: Optional[float] = None
    github_commits: Optional[int] = None
    developer_activity_score: Optional[float] = None


# Technical Analysis Schemas
class TechnicalIndicators(BaseModel):
    """Technical indicators"""
    symbol: str
    timeframe: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    adx: Optional[float] = None
    atr: Optional[float] = None


class TradingSignal(BaseModel):
    """Trading signal"""
    symbol: str
    signal: str  # buy, sell, hold
    confidence: float = Field(..., ge=0, le=1)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: str
    timestamp: datetime
    reasons: List[str]


# Portfolio Schemas
class Position(BaseModel):
    """Open position"""
    id: str
    symbol: str
    side: OrderSide
    entry_price: float
    current_price: float
    amount: float
    value_usd: float
    pnl: float
    pnl_percentage: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime


class PortfolioSummary(BaseModel):
    """Portfolio summary"""
    total_value: float
    available_balance: float
    positions_value: float
    total_pnl: float
    total_pnl_percentage: float
    open_positions: int
    today_pnl: float
    win_rate: float


# Strategy Schemas
class StrategyConfig(BaseModel):
    """Strategy configuration"""
    name: str
    enabled: bool
    pairs: List[str]
    timeframe: TimeFrame
    max_open_trades: int = 5
    stake_amount: float
    stop_loss: float
    take_profit: float
    trailing_stop: bool = False
    use_ml: bool = False
    use_sentiment: bool = False
    min_confidence: float = 0.6


class BacktestRequest(BaseModel):
    """Backtest request"""
    strategy_name: str
    pairs: List[str]
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    commission: float = 0.001


class BacktestResult(BaseModel):
    """Backtest results"""
    strategy: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percentage: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: str
    best_trade: float
    worst_trade: float


# System Status
class SystemStatus(BaseModel):
    """System status"""
    status: str
    uptime: str
    active_strategies: int
    open_positions: int
    services: Dict[str, bool]
    last_update: datetime
