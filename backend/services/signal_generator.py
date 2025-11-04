"""
Trading Signal Generator
Combines technical, fundamental, and sentiment analysis
"""

import logging
from typing import List, Optional
from datetime import datetime

from models.schemas import TradingSignal
from services.technical_analysis import TechnicalAnalysisService
from services.sentiment import SentimentService
from utils.config import settings

logger = logging.getLogger(__name__)


class SignalGeneratorService:
    """Generates trading signals using multi-layer analysis"""

    def __init__(self):
        self.technical_service = TechnicalAnalysisService()
        self.sentiment_service = SentimentService()

    async def generate_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Generate trading signal for a symbol"""
        try:
            # Get technical indicators
            indicators = await self.technical_service.calculate_indicators(symbol)
            if not indicators:
                return None

            # Get sentiment
            sentiment = await self.sentiment_service.get_fear_greed_index()

            # Signal logic
            reasons = []
            signal = "hold"
            confidence = 0.5

            # Technical analysis
            if indicators.rsi:
                if indicators.rsi < 30:
                    signal = "buy"
                    confidence += 0.2
                    reasons.append("RSI oversold")
                elif indicators.rsi > 70:
                    signal = "sell"
                    confidence += 0.2
                    reasons.append("RSI overbought")

            # Sentiment analysis
            if sentiment.value < 25:
                if signal == "buy":
                    confidence += 0.15
                    reasons.append("Extreme Fear - contrarian buy")
            elif sentiment.value > 75:
                if signal == "sell":
                    confidence += 0.15
                    reasons.append("Extreme Greed - take profits")

            # MACD
            if indicators.macd and indicators.macd_signal:
                if indicators.macd > indicators.macd_signal and signal == "buy":
                    confidence += 0.1
                    reasons.append("MACD bullish crossover")
                elif indicators.macd < indicators.macd_signal and signal == "sell":
                    confidence += 0.1
                    reasons.append("MACD bearish crossover")

            # Calculate entry/exit prices
            current_price = indicators.bb_middle if indicators.bb_middle else 0
            stop_loss = current_price * (1 + settings.DEFAULT_STOPLOSS) if signal == "buy" else current_price * (1 - settings.DEFAULT_STOPLOSS)
            take_profit = current_price * (1 + settings.DEFAULT_TAKEPROFIT) if signal == "buy" else current_price * (1 - settings.DEFAULT_TAKEPROFIT)

            if not reasons:
                reasons = ["No strong signals"]

            return TradingSignal(
                symbol=symbol,
                signal=signal,
                confidence=min(1.0, confidence),
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy="Multi-Layer Analysis",
                timestamp=datetime.now(),
                reasons=reasons
            )

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None

    async def generate_signals(self, symbols: Optional[List[str]] = None) -> List[TradingSignal]:
        """Generate signals for multiple symbols"""
        if not symbols:
            symbols = settings.DEFAULT_PAIRS

        signals = []
        for symbol in symbols:
            signal = await self.generate_signal(symbol)
            if signal:
                signals.append(signal)

        return signals
