"""
Technical Analysis Service
Calculates technical indicators using pandas/numpy (MVP version without TA-Lib)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from models.schemas import TechnicalIndicators
from services.market_service import MarketDataService

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Technical analysis service using pandas/numpy"""

    def __init__(self):
        self.market_service = MarketDataService()

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal

        return macd, macd_signal, macd_hist

    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std: float = 2.0):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()

        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)

        return upper, sma, lower

    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)

        atr = true_range.rolling(window=period).mean()
        return atr

    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (simplified version)"""
        # Directional movement
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # True range
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)

        # Smoothed indicators
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    async def calculate_indicators(
        self,
        symbol: str,
        timeframe: str = "5m"
    ) -> Optional[TechnicalIndicators]:
        """Calculate technical indicators for a symbol"""
        try:
            # Get candle data
            candles = await self.market_service.get_candles(symbol, timeframe, limit=200)

            if not candles or len(candles) < 50:
                logger.warning(f"Insufficient candle data for {symbol}: {len(candles) if candles else 0} candles")
                return None

            # Convert to DataFrame
            df = pd.DataFrame([c.dict() for c in candles])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)

            # Calculate indicators
            close = df['close']
            high = df['high']
            low = df['low']

            # RSI
            rsi = self.calculate_rsi(close, period=14)

            # MACD
            macd, macd_signal, macd_hist = self.calculate_macd(close, fast=12, slow=26, signal=9)

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close, period=20, std=2.0)

            # Moving Averages
            sma_20 = self.calculate_sma(close, period=20)
            sma_50 = self.calculate_sma(close, period=50)
            sma_200 = self.calculate_sma(close, period=200) if len(close) >= 200 else None

            ema_12 = self.calculate_ema(close, period=12)
            ema_26 = self.calculate_ema(close, period=26)

            # ADX
            adx = self.calculate_adx(high, low, close, period=14)

            # ATR
            atr = self.calculate_atr(high, low, close, period=14)

            # Get latest values (handle NaN)
            def safe_float(series, default=None):
                try:
                    val = series.iloc[-1]
                    return float(val) if not pd.isna(val) else default
                except (IndexError, AttributeError):
                    return default

            indicators = TechnicalIndicators(
                symbol=symbol,
                timeframe=timeframe,
                rsi=safe_float(rsi),
                macd=safe_float(macd),
                macd_signal=safe_float(macd_signal),
                bb_upper=safe_float(bb_upper),
                bb_middle=safe_float(bb_middle),
                bb_lower=safe_float(bb_lower),
                sma_20=safe_float(sma_20),
                sma_50=safe_float(sma_50),
                sma_200=safe_float(sma_200) if sma_200 is not None else None,
                ema_12=safe_float(ema_12),
                ema_26=safe_float(ema_26),
                adx=safe_float(adx),
                atr=safe_float(atr)
            )

            logger.info(f"Calculated indicators for {symbol}: RSI={indicators.rsi:.2f if indicators.rsi else 'N/A'}")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return None
