"""
Sentiment Analysis Service
Integrates Alternative.me Fear & Greed Index (Free)
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from cachetools import TTLCache

from models.schemas import FearGreedIndex, SentimentAnalysis, SocialSentiment
from utils.config import settings

logger = logging.getLogger(__name__)


class SentimentService:
    """Sentiment analysis service"""

    def __init__(self):
        self.fear_greed_url = "https://api.alternative.me/fng/"
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5 min cache
        self.last_fear_greed: Optional[FearGreedIndex] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _classify_fear_greed(self, value: int) -> str:
        """Classify Fear & Greed value"""
        if value <= 24:
            return "Extreme Fear"
        elif value <= 49:
            return "Fear"
        elif value == 50:
            return "Neutral"
        elif value <= 75:
            return "Greed"
        else:
            return "Extreme Greed"

    async def get_fear_greed_index(self) -> FearGreedIndex:
        """Get current Fear & Greed Index from Alternative.me (Free)"""
        if "fear_greed" in self.cache:
            return self.cache["fear_greed"]

        session = await self._get_session()

        try:
            async with session.get(self.fear_greed_url, params={"limit": 1}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and "data" in data and len(data["data"]) > 0:
                        fg_data = data["data"][0]
                        value = int(fg_data["value"])

                        index = FearGreedIndex(
                            value=value,
                            value_classification=fg_data.get("value_classification", self._classify_fear_greed(value)),
                            timestamp=datetime.fromtimestamp(int(fg_data["timestamp"])),
                            time_until_update=fg_data.get("time_until_update")
                        )

                        self.cache["fear_greed"] = index
                        self.last_fear_greed = index
                        return index

        except Exception as e:
            logger.error(f"Failed to fetch Fear & Greed Index: {e}")

        # Return cached value or default
        return self.last_fear_greed or FearGreedIndex(
            value=50,
            value_classification="Neutral",
            timestamp=datetime.now()
        )

    async def get_social_sentiment(self, symbol: str) -> Optional[SocialSentiment]:
        """
        Get social sentiment for a symbol
        Note: This would require LunarCrush API (paid) or similar service
        For now, returns simulated data for demo purposes
        """
        # Simulated sentiment data for demo
        # In production, integrate with LunarCrush, Santiment, or similar
        return SocialSentiment(
            symbol=symbol,
            sentiment_score=0.0,  # -1 to 1
            mentions_24h=0,
            sentiment_positive=0.33,
            sentiment_negative=0.33,
            sentiment_neutral=0.34,
            trending_rank=None
        )

    def _calculate_overall_sentiment(
        self,
        fear_greed: FearGreedIndex,
        social: Optional[List[SocialSentiment]] = None
    ) -> tuple[str, float]:
        """Calculate overall sentiment and confidence"""
        # Base sentiment from Fear & Greed
        fg_value = fear_greed.value

        if fg_value <= 25:
            sentiment = "bearish"
            confidence = (25 - fg_value) / 25  # 0 to 1
        elif fg_value >= 75:
            sentiment = "bullish"
            confidence = (fg_value - 75) / 25  # 0 to 1
        else:
            sentiment = "neutral"
            confidence = 1 - abs(fg_value - 50) / 25  # Higher confidence near 50

        # Adjust based on social sentiment if available
        if social:
            avg_social_sentiment = sum(s.sentiment_score for s in social) / len(social)
            if avg_social_sentiment > 0.3:
                sentiment = "bullish"
                confidence = min(1.0, confidence + 0.2)
            elif avg_social_sentiment < -0.3:
                sentiment = "bearish"
                confidence = min(1.0, confidence + 0.2)

        return sentiment, min(1.0, confidence)

    async def get_comprehensive_analysis(
        self,
        symbols: Optional[List[str]] = None
    ) -> SentimentAnalysis:
        """Get comprehensive sentiment analysis"""
        # Get Fear & Greed Index
        fear_greed = await self.get_fear_greed_index()

        # Get social sentiment for symbols
        social_sentiments = []
        if symbols:
            for symbol in symbols:
                social = await self.get_social_sentiment(symbol)
                if social:
                    social_sentiments.append(social)

        # Calculate overall sentiment
        overall_sentiment, confidence = self._calculate_overall_sentiment(
            fear_greed,
            social_sentiments if social_sentiments else None
        )

        return SentimentAnalysis(
            fear_greed=fear_greed,
            social=social_sentiments if social_sentiments else None,
            overall_sentiment=overall_sentiment,
            confidence=confidence
        )

    async def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """
        Get trending topics in crypto social media
        Would require integration with social media APIs or crypto-specific services
        Returns simulated data for demo
        """
        return [
            {
                "topic": "Bitcoin",
                "mentions": 0,
                "sentiment": 0.0,
                "rank": i + 1
            }
            for i in range(limit)
        ]

    async def start_periodic_updates(self):
        """Start background sentiment updates"""
        self.is_running = True
        logger.info("😊 Sentiment service started")

        while self.is_running:
            try:
                # Update Fear & Greed Index
                await self.get_fear_greed_index()
                await asyncio.sleep(settings.SENTIMENT_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Sentiment update error: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Stop the service"""
        self.is_running = False
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("😊 Sentiment service stopped")
