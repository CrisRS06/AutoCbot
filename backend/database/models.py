"""
SQLAlchemy ORM Models for AutoCbot
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base


# Enums
class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class StrategyType(str, enum.Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    ARBITRAGE = "arbitrage"
    GRID = "grid"
    DCA = "dca"
    CUSTOM = "custom"


# Models
class User(Base):
    """User model for authentication and settings"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Required for MVP security
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Settings stored as JSON
    settings_json = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettingsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class TokenBlacklist(Base):
    """Blacklisted JWT tokens for logout/revocation"""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String(255), nullable=False, unique=True, index=True)  # JWT ID claim
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_type = Column(String(20), nullable=False)  # "access" or "refresh"

    # Expiration tracking
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Timestamps
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(255), nullable=True)  # "logout", "security", "expired"

    # Indexes
    __table_args__ = (
        Index('idx_token_jti_expires', 'token_jti', 'expires_at'),
    )

    def __repr__(self):
        return f"<TokenBlacklist(jti={self.token_jti}, user_id={self.user_id})>"


class UserSettingsModel(Base):
    """Per-user settings with encrypted sensitive data"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # API Keys (ENCRYPTED)
    binance_api_key_encrypted = Column(Text, nullable=True)
    binance_secret_encrypted = Column(Text, nullable=True)
    coingecko_api_key_encrypted = Column(Text, nullable=True)
    telegram_token_encrypted = Column(Text, nullable=True)
    telegram_chat_id_encrypted = Column(Text, nullable=True)

    # Trading Parameters
    default_pairs = Column(String(500), default="BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT")
    default_timeframe = Column(String(10), default="5m")
    max_position_size = Column(Float, default=0.1)  # 10% of portfolio
    max_open_trades = Column(Integer, default=5)

    # Risk Management
    default_stoploss = Column(Float, default=-0.05)  # -5%
    default_takeprofit = Column(Float, default=0.03)  # 3%

    # Feature Flags (per-user)
    enable_ml_predictions = Column(Boolean, default=True)
    enable_paper_trading = Column(Boolean, default=True)
    dry_run = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettingsModel(user_id={self.user_id})>"


class Strategy(Base):
    """Trading strategy configuration"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Strategy metadata
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(StrategyType), default=StrategyType.CUSTOM)

    # Strategy configuration stored as JSON
    parameters = Column(JSON, nullable=False)
    # Example parameters structure:
    # {
    #   "symbols": ["BTC/USDT", "ETH/USDT"],
    #   "timeframe": "1h",
    #   "indicators": {
    #     "sma_period": 50,
    #     "rsi_period": 14,
    #     "rsi_overbought": 70,
    #     "rsi_oversold": 30
    #   },
    #   "entry_conditions": [...],
    #   "exit_conditions": [...],
    #   "risk_management": {
    #     "position_size": 0.1,
    #     "stop_loss": 0.02,
    #     "take_profit": 0.05
    #   }
    # }

    # Status
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)  # Soft delete

    # Performance metrics (updated periodically)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_run_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="strategies")
    backtest_results = relationship("BacktestResult", back_populates="strategy", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="strategy", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="strategy", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="strategy", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_strategy_active', 'is_active', 'is_deleted'),
    )

    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', active={self.is_active})>"


class BacktestResult(Base):
    """Backtest results for a strategy"""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    # Backtest parameters
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Float, default=10000.0)

    # Results summary
    final_balance = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)  # Percentage
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)

    # Metrics stored as JSON
    metrics_json = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "win_rate": 0.65,
    #   "profit_factor": 1.85,
    #   "sharpe_ratio": 1.42,
    #   "sortino_ratio": 1.89,
    #   "max_drawdown": -0.15,
    #   "max_drawdown_duration": 7,
    #   "avg_win": 125.50,
    #   "avg_loss": -75.30,
    #   "largest_win": 500.00,
    #   "largest_loss": -250.00,
    #   "expectancy": 45.20,
    #   "calmar_ratio": 0.95,
    #   "recovery_factor": 2.1
    # }

    # Equity curve and trades stored as JSON
    equity_curve_json = Column(JSON, nullable=True)
    # Structure: [{"timestamp": "2024-01-01T00:00:00", "balance": 10500.0}, ...]

    trades_json = Column(JSON, nullable=True)
    # Structure: List of trade objects

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    strategy = relationship("Strategy", back_populates="backtest_results")

    # Indexes
    __table_args__ = (
        Index('idx_backtest_strategy_date', 'strategy_id', 'created_at'),
    )

    def __repr__(self):
        return f"<BacktestResult(id={self.id}, strategy_id={self.strategy_id}, return={self.total_return:.2f}%)>"


class Trade(Base):
    """Completed trade record"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    # Trade details
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(SQLEnum(OrderSide), nullable=False)

    # Prices and quantities
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)

    # P&L
    pnl = Column(Float, nullable=False)
    pnl_percentage = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)

    # Trade metadata
    entry_reason = Column(String(255), nullable=True)
    exit_reason = Column(String(255), nullable=True)

    # Timestamps
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Integer, nullable=True)

    # Relationships
    strategy = relationship("Strategy", back_populates="trades")

    # Indexes
    __table_args__ = (
        Index('idx_trade_strategy_symbol', 'strategy_id', 'symbol'),
        Index('idx_trade_closed_at', 'closed_at'),
    )

    def __repr__(self):
        return f"<Trade(id={self.id}, {self.side.value} {self.symbol}, pnl={self.pnl:.2f})>"


class Position(Base):
    """Open position"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    # Position details
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(SQLEnum(OrderSide), nullable=False)

    # Entry details
    entry_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)

    # Current state
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_percentage = Column(Float, default=0.0)

    # Stop loss / Take profit
    stop_loss_price = Column(Float, nullable=True)
    take_profit_price = Column(Float, nullable=True)

    # Metadata
    entry_reason = Column(String(255), nullable=True)

    # Timestamps
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy", back_populates="positions")

    # Indexes
    __table_args__ = (
        Index('idx_position_strategy_symbol', 'strategy_id', 'symbol'),
    )

    def __repr__(self):
        return f"<Position(id={self.id}, {self.side.value} {self.symbol} @ {self.entry_price})>"


class Order(Base):
    """Order (pending, filled, or cancelled)"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    # Exchange order ID
    exchange_order_id = Column(String(255), nullable=True, index=True)

    # Order details
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(SQLEnum(OrderSide), nullable=False)
    type = Column(SQLEnum(OrderType), nullable=False)

    # Price and quantity
    price = Column(Float, nullable=True)  # Null for market orders
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)

    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)

    # Metadata
    reason = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    strategy = relationship("Strategy", back_populates="orders")

    # Indexes
    __table_args__ = (
        Index('idx_order_strategy_status', 'strategy_id', 'status'),
        Index('idx_order_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, {self.side.value} {self.symbol}, status={self.status.value})>"


class PerformanceSnapshot(Base):
    """Periodic snapshot of portfolio performance"""
    __tablename__ = "performance_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    # Snapshot data
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Portfolio metrics
    total_balance = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_pnl_percentage = Column(Float, nullable=False)
    active_positions_count = Column(Integer, default=0)

    # Detailed metrics stored as JSON
    metrics_json = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "daily_pnl": 150.0,
    #   "weekly_pnl": 850.0,
    #   "monthly_pnl": 3200.0,
    #   "win_rate_7d": 0.68,
    #   "sharpe_30d": 1.5,
    #   "max_drawdown_30d": -0.08
    # }

    # Indexes
    __table_args__ = (
        Index('idx_snapshot_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<PerformanceSnapshot(timestamp={self.timestamp}, balance={self.total_balance:.2f})>"


class MarketDataCache(Base):
    """Cache for market data (OHLCV candles and indicators)"""
    __tablename__ = "market_data_cache"

    id = Column(Integer, primary_key=True, index=True)

    # Cache key
    symbol = Column(String(50), nullable=False, index=True)
    interval = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d, etc.
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    # Pre-calculated indicators stored as JSON
    indicators_json = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "sma_50": 45000.0,
    #   "sma_200": 42000.0,
    #   "rsi": 65.5,
    #   "macd": 150.2,
    #   "macd_signal": 145.8,
    #   "bb_upper": 46000.0,
    #   "bb_middle": 45000.0,
    #   "bb_lower": 44000.0
    # }

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_market_data_symbol_interval_timestamp', 'symbol', 'interval', 'timestamp', unique=True),
        Index('idx_market_data_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<MarketDataCache(symbol={self.symbol}, interval={self.interval}, timestamp={self.timestamp})>"
