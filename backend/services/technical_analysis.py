"""
Technical Analysis Service
Calculates technical indicators
"""

import pandas as pd
import talib
from typing import Dict, Optional
import logging

from models.schemas import TechnicalIndicators
from services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Technical analysis service"""

    def __init__(self):
        self.market_service = MarketDataService()

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
                return None

            # Convert to DataFrame
            df = pd.DataFrame([c.dict() for c in candles])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)

            # Calculate indicators
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values

            # RSI
            rsi = talib.RSI(close, timeperiod=14)

            # MACD
            macd, macd_signal, macd_hist = talib.MACD(
                close,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(
                close,
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2
            )

            # Moving Averages
            sma_20 = talib.SMA(close, timeperiod=20)
            sma_50 = talib.SMA(close, timeperiod=50)
            sma_200 = talib.SMA(close, timeperiod=200) if len(close) >= 200 else None

            ema_12 = talib.EMA(close, timeperiod=12)
            ema_26 = talib.EMA(close, timeperiod=26)

            # ADX
            adx = talib.ADX(high, low, close, timeperiod=14)

            # ATR
            atr = talib.ATR(high, low, close, timeperiod=14)

            # Get latest values
            indicators = TechnicalIndicators(
                symbol=symbol,
                timeframe=timeframe,
                rsi=float(rsi[-1]) if not pd.isna(rsi[-1]) else None,
                macd=float(macd[-1]) if not pd.isna(macd[-1]) else None,
                macd_signal=float(macd_signal[-1]) if not pd.isna(macd_signal[-1]) else None,
                bb_upper=float(bb_upper[-1]) if not pd.isna(bb_upper[-1]) else None,
                bb_middle=float(bb_middle[-1]) if not pd.isna(bb_middle[-1]) else None,
                bb_lower=float(bb_lower[-1]) if not pd.isna(bb_lower[-1]) else None,
                sma_20=float(sma_20[-1]) if not pd.isna(sma_20[-1]) else None,
                sma_50=float(sma_50[-1]) if not pd.isna(sma_50[-1]) else None,
                sma_200=float(sma_200[-1]) if sma_200 is not None and not pd.isna(sma_200[-1]) else None,
                ema_12=float(ema_12[-1]) if not pd.isna(ema_12[-1]) else None,
                ema_26=float(ema_26[-1]) if not pd.isna(ema_26[-1]) else None,
                adx=float(adx[-1]) if not pd.isna(adx[-1]) else None,
                atr=float(atr[-1]) if not pd.isna(atr[-1]) else None
            )

            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return None
