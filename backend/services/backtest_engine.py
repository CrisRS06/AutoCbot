"""
Complete Backtesting Engine
Implements vectorized backtesting with realistic trade simulation
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from database.models import Strategy, BacktestResult as BacktestResultModel
from services.market_data import MarketDataService
from services.technical_analysis import TechnicalAnalysisService
from utils.metrics import calculate_all_metrics

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Vectorized backtesting engine with realistic trade simulation
    """

    def __init__(
        self,
        strategy: Strategy,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005,  # 0.05%
        db: Session = None
    ):
        """
        Initialize BacktestEngine

        Args:
            strategy: Strategy database model
            start_date: Backtest start date
            end_date: Backtest end date
            initial_capital: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate (0.0005 = 0.05%)
            db: Database session
        """
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.db = db

        # Services
        self.market_data_service = MarketDataService()
        self.ta_service = TechnicalAnalysisService()

        # Results storage
        self.equity_curve: List[Dict] = []
        self.trades: List[Dict] = []
        self.positions: List[Dict] = []

        # State
        self.current_capital = initial_capital
        self.current_position = None  # Dict with entry info

    async def run(self) -> Dict:
        """
        Run the backtest

        Returns:
            Dict with backtest results
        """
        logger.info(f"Starting backtest for strategy: {self.strategy.name}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Initial capital: ${self.initial_capital}")

        try:
            # Get strategy parameters
            params = self.strategy.parameters or {}
            symbols = params.get("symbols", ["BTC/USDT"])
            timeframe = params.get("timeframe", "1h")

            # For now, backtest first symbol only
            # TODO: Multi-symbol backtesting
            symbol = symbols[0] if symbols else "BTC/USDT"

            # Load historical data
            logger.info(f"Loading historical data for {symbol}...")
            df = await self._load_historical_data(symbol, timeframe)

            if df is None or len(df) == 0:
                logger.error("No historical data available")
                return self._create_empty_result()

            logger.info(f"Loaded {len(df)} candles")

            # Calculate indicators
            logger.info("Calculating technical indicators...")
            df = await self._calculate_indicators(df, params)

            # Generate signals
            logger.info("Generating trading signals...")
            df = self._generate_signals(df, params)

            # Simulate trades
            logger.info("Simulating trades...")
            self._simulate_trades(df, params)

            # Calculate metrics
            logger.info("Calculating performance metrics...")
            metrics = self._calculate_metrics()

            # Save to database
            if self.db:
                logger.info("Saving results to database...")
                await self._save_to_database(metrics)

            logger.info(f"Backtest complete. Total trades: {len(self.trades)}")

            return {
                "metrics": metrics,
                "equity_curve": self.equity_curve,
                "trades": self.trades,
                "success": True
            }

        except Exception as e:
            logger.error(f"Backtest failed: {e}", exc_info=True)
            return self._create_empty_result(error=str(e))

    async def _load_historical_data(
        self,
        symbol: str,
        timeframe: str
    ) -> Optional[pd.DataFrame]:
        """
        Load historical market data

        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1h, 4h, 1d)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Calculate number of days needed
            days_diff = (self.end_date - self.start_date).days
            days_to_fetch = days_diff + 30  # Extra for indicators

            # Get historical data from market service
            candles = await self.market_data_service.get_historical_candles(
                symbol=symbol,
                interval=timeframe,
                days=days_to_fetch
            )

            if not candles:
                logger.warning(f"No candles returned for {symbol}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(candles)

            # Ensure we have required columns
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return None

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')

            # Sort by timestamp
            df = df.sort_index()

            # Filter to backtest period
            df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]

            return df

        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return None

    async def _calculate_indicators(
        self,
        df: pd.DataFrame,
        params: Dict
    ) -> pd.DataFrame:
        """
        Calculate technical indicators

        Args:
            df: OHLCV DataFrame
            params: Strategy parameters

        Returns:
            DataFrame with indicators
        """
        try:
            # Get indicator parameters
            indicators_config = params.get("indicators", {})

            # Calculate common indicators
            # SMA
            sma_periods = indicators_config.get("sma_periods", [50, 200])
            for period in sma_periods:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()

            # EMA
            ema_periods = indicators_config.get("ema_periods", [12, 26])
            for period in ema_periods:
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

            # RSI
            rsi_period = indicators_config.get("rsi_period", 14)
            df['rsi'] = self._calculate_rsi(df['close'], rsi_period)

            # MACD
            macd_fast = indicators_config.get("macd_fast", 12)
            macd_slow = indicators_config.get("macd_slow", 26)
            macd_signal = indicators_config.get("macd_signal", 9)

            ema_fast = df['close'].ewm(span=macd_fast, adjust=False).mean()
            ema_slow = df['close'].ewm(span=macd_slow, adjust=False).mean()

            df['macd'] = ema_fast - ema_slow
            df['macd_signal'] = df['macd'].ewm(span=macd_signal, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']

            # Bollinger Bands
            bb_period = indicators_config.get("bb_period", 20)
            bb_std = indicators_config.get("bb_std", 2)

            df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
            rolling_std = df['close'].rolling(window=bb_period).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * rolling_std)
            df['bb_lower'] = df['bb_middle'] - (bb_std * rolling_std)

            # ATR (Average True Range) for stop loss
            atr_period = indicators_config.get("atr_period", 14)
            df['atr'] = self._calculate_atr(df, atr_period)

            # Drop NaN rows from indicator calculation
            df = df.dropna()

            return df

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    def _generate_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Generate buy/sell signals based on strategy logic

        Args:
            df: DataFrame with indicators
            params: Strategy parameters

        Returns:
            DataFrame with signal column
        """
        # Initialize signal column
        df['signal'] = 0  # 0 = no signal, 1 = buy, -1 = sell

        # Get strategy type and conditions
        strategy_type = self.strategy.type.value
        entry_conditions = params.get("entry_conditions", {})
        exit_conditions = params.get("exit_conditions", {})

        # Example: Simple SMA crossover strategy
        if strategy_type == "momentum" or "sma" in entry_conditions:
            # Buy signal: Fast SMA crosses above Slow SMA
            if 'sma_50' in df.columns and 'sma_200' in df.columns:
                df['signal'] = np.where(
                    (df['sma_50'] > df['sma_200']) &
                    (df['sma_50'].shift(1) <= df['sma_200'].shift(1)),
                    1,  # Buy
                    df['signal']
                )

                # Sell signal: Fast SMA crosses below Slow SMA
                df['signal'] = np.where(
                    (df['sma_50'] < df['sma_200']) &
                    (df['sma_50'].shift(1) >= df['sma_200'].shift(1)),
                    -1,  # Sell
                    df['signal']
                )

        # Example: RSI oversold/overbought strategy
        if "rsi" in entry_conditions:
            rsi_oversold = entry_conditions.get("rsi_oversold", 30)
            rsi_overbought = entry_conditions.get("rsi_overbought", 70)

            if 'rsi' in df.columns:
                # Buy on RSI oversold
                df['signal'] = np.where(
                    (df['rsi'] < rsi_oversold) & (df['rsi'].shift(1) >= rsi_oversold),
                    1,
                    df['signal']
                )

                # Sell on RSI overbought
                df['signal'] = np.where(
                    (df['rsi'] > rsi_overbought) & (df['rsi'].shift(1) <= rsi_overbought),
                    -1,
                    df['signal']
                )

        # Example: MACD strategy
        if "macd" in entry_conditions:
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                # Buy on MACD crossover
                df['signal'] = np.where(
                    (df['macd'] > df['macd_signal']) &
                    (df['macd'].shift(1) <= df['macd_signal'].shift(1)),
                    1,
                    df['signal']
                )

                # Sell on MACD crossunder
                df['signal'] = np.where(
                    (df['macd'] < df['macd_signal']) &
                    (df['macd'].shift(1) >= df['macd_signal'].shift(1)),
                    -1,
                    df['signal']
                )

        return df

    def _simulate_trades(self, df: pd.DataFrame, params: Dict):
        """
        Simulate trade execution with realistic conditions

        Args:
            df: DataFrame with signals
            params: Strategy parameters
        """
        # Get risk management parameters
        risk_mgmt = params.get("risk_management", {})
        position_size_pct = risk_mgmt.get("position_size", 1.0)  # 100% of capital
        stop_loss_pct = risk_mgmt.get("stop_loss", 0.02)  # 2%
        take_profit_pct = risk_mgmt.get("take_profit", 0.05)  # 5%

        # Initialize equity tracking
        self.equity_curve = [{"timestamp": df.index[0], "balance": self.initial_capital}]

        # Iterate through candles
        for i, (timestamp, row) in enumerate(df.iterrows()):
            signal = row['signal']
            price = row['close']
            atr = row.get('atr', price * 0.02)  # Fallback to 2% of price

            # Check if we have an open position
            if self.current_position:
                # Check stop loss and take profit
                entry_price = self.current_position['entry_price']
                quantity = self.current_position['quantity']
                side = self.current_position['side']

                # Calculate stop loss and take profit prices
                if side == 'long':
                    stop_loss_price = entry_price * (1 - stop_loss_pct)
                    take_profit_price = entry_price * (1 + take_profit_pct)

                    # Check if stop loss hit
                    if row['low'] <= stop_loss_price:
                        self._close_position(timestamp, stop_loss_price, "stop_loss")
                    # Check if take profit hit
                    elif row['high'] >= take_profit_price:
                        self._close_position(timestamp, take_profit_price, "take_profit")
                    # Check for sell signal
                    elif signal == -1:
                        self._close_position(timestamp, price, "signal")

                # TODO: Implement short positions

            # Check for entry signal (only if no position)
            elif signal == 1 and not self.current_position:
                # Calculate position size
                position_value = self.current_capital * position_size_pct

                # Apply slippage to entry price
                entry_price_with_slippage = price * (1 + self.slippage)

                # Calculate quantity
                quantity = position_value / entry_price_with_slippage

                # Calculate commission
                entry_commission = position_value * self.commission

                # Open position
                self.current_position = {
                    "entry_timestamp": timestamp,
                    "entry_price": entry_price_with_slippage,
                    "quantity": quantity,
                    "side": "long",
                    "entry_commission": entry_commission
                }

                # Deduct commission from capital
                self.current_capital -= entry_commission

                logger.debug(f"Opened long position at {timestamp}: {quantity:.4f} @ ${entry_price_with_slippage:.2f}")

            # Update equity curve
            current_equity = self._calculate_current_equity(price)
            self.equity_curve.append({
                "timestamp": timestamp,
                "balance": current_equity
            })

        # Close any remaining position at end of backtest
        if self.current_position:
            last_price = df.iloc[-1]['close']
            last_timestamp = df.index[-1]
            self._close_position(last_timestamp, last_price, "backtest_end")

    def _close_position(self, timestamp: datetime, exit_price: float, reason: str):
        """Close the current position"""
        if not self.current_position:
            return

        entry_price = self.current_position['entry_price']
        quantity = self.current_position['quantity']
        entry_commission = self.current_position['entry_commission']

        # Apply slippage to exit price
        exit_price_with_slippage = exit_price * (1 - self.slippage)

        # Calculate P&L
        position_value = quantity * exit_price_with_slippage
        exit_commission = position_value * self.commission

        # Return capital
        self.current_capital += position_value - exit_commission

        # Calculate trade P&L (including commissions)
        entry_value = quantity * entry_price
        pnl = (position_value - entry_value) - (entry_commission + exit_commission)
        pnl_pct = pnl / entry_value if entry_value > 0 else 0.0

        # Calculate trade duration
        duration_seconds = (timestamp - self.current_position['entry_timestamp']).total_seconds()

        # Record trade
        trade = {
            "entry_timestamp": self.current_position['entry_timestamp'],
            "exit_timestamp": timestamp,
            "entry_price": entry_price,
            "exit_price": exit_price_with_slippage,
            "quantity": quantity,
            "side": self.current_position['side'],
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "duration_seconds": int(duration_seconds),
            "exit_reason": reason,
            "entry_commission": entry_commission,
            "exit_commission": exit_commission
        }

        self.trades.append(trade)

        logger.debug(
            f"Closed {self.current_position['side']} position at {timestamp}: "
            f"P&L: ${pnl:.2f} ({pnl_pct*100:.2f}%) - Reason: {reason}"
        )

        # Clear position
        self.current_position = None

    def _calculate_current_equity(self, current_price: float) -> float:
        """Calculate current total equity including open positions"""
        equity = self.current_capital

        if self.current_position:
            quantity = self.current_position['quantity']
            position_value = quantity * current_price
            equity += position_value

        return equity

    def _calculate_metrics(self) -> Dict:
        """Calculate all performance metrics"""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return {}

        # Convert equity curve to series
        equity_df = pd.DataFrame(self.equity_curve)
        equity_series = equity_df['balance']

        # Use our metrics module
        metrics = calculate_all_metrics(
            equity_curve=equity_series,
            trades=self.trades,
            initial_capital=self.initial_capital,
            risk_free_rate=0.02,
            periods_per_year=252
        )

        return metrics

    async def _save_to_database(self, metrics: Dict):
        """Save backtest results to database"""
        if not self.db:
            return

        try:
            # Prepare equity curve for JSON storage
            equity_curve_json = [
                {
                    "timestamp": point["timestamp"].isoformat() if hasattr(point["timestamp"], 'isoformat') else str(point["timestamp"]),
                    "balance": float(point["balance"])
                }
                for point in self.equity_curve
            ]

            # Prepare trades for JSON storage
            trades_json = [
                {
                    "entry_timestamp": trade["entry_timestamp"].isoformat() if hasattr(trade["entry_timestamp"], 'isoformat') else str(trade["entry_timestamp"]),
                    "exit_timestamp": trade["exit_timestamp"].isoformat() if hasattr(trade["exit_timestamp"], 'isoformat') else str(trade["exit_timestamp"]),
                    "entry_price": float(trade["entry_price"]),
                    "exit_price": float(trade["exit_price"]),
                    "quantity": float(trade["quantity"]),
                    "side": trade["side"],
                    "pnl": float(trade["pnl"]),
                    "pnl_pct": float(trade["pnl_pct"]),
                    "duration_seconds": int(trade["duration_seconds"]),
                    "exit_reason": trade["exit_reason"]
                }
                for trade in self.trades
            ]

            # Calculate final values
            final_balance = self.equity_curve[-1]["balance"] if self.equity_curve else self.initial_capital
            total_return_pct = metrics.get("total_return_pct", 0.0)

            # Create backtest result record
            result = BacktestResultModel(
                strategy_id=self.strategy.id,
                start_date=self.start_date,
                end_date=self.end_date,
                initial_capital=self.initial_capital,
                final_balance=final_balance,
                total_return=total_return_pct,
                total_trades=metrics.get("total_trades", 0),
                winning_trades=metrics.get("winning_trades", 0),
                losing_trades=metrics.get("losing_trades", 0),
                metrics_json=metrics,
                equity_curve_json=equity_curve_json,
                trades_json=trades_json
            )

            self.db.add(result)
            self.db.commit()

            logger.info(f"Saved backtest result to database (ID: {result.id})")

        except Exception as e:
            logger.error(f"Error saving backtest to database: {e}")
            self.db.rollback()

    def _create_empty_result(self, error: Optional[str] = None) -> Dict:
        """Create empty result dict"""
        return {
            "metrics": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_return": 0.0,
                "total_return_pct": 0.0,
                "sharpe_ratio": 0.0
            },
            "equity_curve": [],
            "trades": [],
            "success": False,
            "error": error
        }
