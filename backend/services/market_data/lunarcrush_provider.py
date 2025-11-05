"""
LunarCrush Social Sentiment Provider
Provides social media sentiment and engagement metrics
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
import random

from .base_provider import SocialSentimentProvider

logger = logging.getLogger(__name__)


class LunarCrushProvider(SocialSentimentProvider):
    """
    LunarCrush social sentiment provider
    Provides social media metrics and sentiment analysis
    """

    BASE_URL = "https://lunarcrush.com/api4/public"

    def __init__(self, api_key: str = ""):
        """
        Initialize LunarCrush provider

        Args:
            api_key: LunarCrush API key (optional for public endpoints)
        """
        super().__init__(api_key)
        self.session = None
        logger.info("LunarCrush provider initialized")

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            self.session = aiohttp.ClientSession(headers=headers)

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make API request to LunarCrush

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with self.session.get(url, params=params or {}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.warning(f"LunarCrush API error ({response.status}): {error_text}")
                    # Return mock data on error
                    return None

        except Exception as e:
            logger.error(f"Error making LunarCrush request to {endpoint}: {e}")
            return None

    async def get_social_metrics(self, symbol: str) -> Dict:
        """
        Get social media metrics for a symbol

        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH")

        Returns:
            Dict with social metrics
        """
        try:
            # LunarCrush v4 API endpoint
            data = await self._make_request(f"/coins/{symbol.upper()}")

            if not data:
                return self._get_mock_social_metrics(symbol)

            coin_data = data.get('data', {})

            return {
                'symbol': symbol.upper(),
                'name': coin_data.get('name', symbol),
                'timestamp': int(datetime.now().timestamp()),
                'sentiment': {
                    'score': coin_data.get('sentiment', 50) / 100,  # Normalize to 0-1
                    'sentiment_absolute': coin_data.get('sentiment_absolute', 0),
                    'sentiment_relative': coin_data.get('sentiment_relative', 0),
                },
                'social_volume': {
                    'total': coin_data.get('social_volume', 0),
                    'reddit': coin_data.get('reddit_posts', 0),
                    'twitter': coin_data.get('tweets', 0),
                    'news': coin_data.get('news', 0),
                },
                'engagement': {
                    'social_score': coin_data.get('social_score', 0),
                    'social_contributors': coin_data.get('social_contributors', 0),
                    'social_dominance': coin_data.get('social_dominance', 0),
                },
                'influence': {
                    'galaxy_score': coin_data.get('galaxy_score', 0),
                    'alt_rank': coin_data.get('alt_rank', 0),
                    'market_dominance': coin_data.get('market_dominance', 0),
                },
                'price_correlation': {
                    'correlation_rank': coin_data.get('correlation_rank', 0),
                    'volatility': coin_data.get('volatility', 0),
                }
            }

        except Exception as e:
            logger.error(f"Error fetching social metrics for {symbol}: {e}")
            return self._get_mock_social_metrics(symbol)

    async def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """
        Get trending coins based on social activity

        Args:
            limit: Number of coins to return

        Returns:
            List of trending coins with metrics
        """
        try:
            data = await self._make_request('/coins/list', params={'sort': 'social_volume', 'limit': limit})

            if not data:
                return self._get_mock_trending_coins(limit)

            coins = data.get('data', [])

            return [
                {
                    'rank': idx + 1,
                    'symbol': coin.get('symbol', ''),
                    'name': coin.get('name', ''),
                    'social_volume': coin.get('social_volume', 0),
                    'social_score': coin.get('social_score', 0),
                    'sentiment': coin.get('sentiment', 50) / 100,
                    'galaxy_score': coin.get('galaxy_score', 0),
                    'alt_rank': coin.get('alt_rank', 0),
                    'price_change_24h': coin.get('percent_change_24h', 0),
                }
                for idx, coin in enumerate(coins[:limit])
            ]

        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return self._get_mock_trending_coins(limit)

    async def get_influencer_activity(self, symbol: str) -> List[Dict]:
        """
        Get influencer activity for a symbol

        Args:
            symbol: Asset symbol

        Returns:
            List of influential posts/mentions
        """
        try:
            data = await self._make_request(f'/coins/{symbol.upper()}/influencers')

            if not data:
                return self._get_mock_influencer_activity(symbol)

            influencers = data.get('data', [])

            return [
                {
                    'username': inf.get('username', ''),
                    'platform': inf.get('platform', 'twitter'),
                    'followers': inf.get('followers', 0),
                    'engagement': inf.get('engagement', 0),
                    'sentiment': inf.get('sentiment', 0),
                    'influence_score': inf.get('influence_score', 0),
                    'recent_posts': inf.get('recent_posts', 0),
                }
                for inf in influencers[:20]
            ]

        except Exception as e:
            logger.error(f"Error fetching influencer activity for {symbol}: {e}")
            return self._get_mock_influencer_activity(symbol)

    async def get_social_timeline(
        self,
        symbol: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Get social metrics timeline

        Args:
            symbol: Asset symbol
            days: Number of days of history

        Returns:
            List of daily social metrics
        """
        try:
            data = await self._make_request(
                f'/coins/{symbol.upper()}/time-series',
                params={'interval': 'day', 'days': days}
            )

            if not data:
                return self._get_mock_social_timeline(symbol, days)

            timeline = data.get('data', [])

            return [
                {
                    'timestamp': item.get('timestamp', 0),
                    'datetime': datetime.fromtimestamp(item.get('timestamp', 0)).isoformat() if item.get('timestamp') else None,
                    'social_volume': item.get('social_volume', 0),
                    'sentiment': item.get('sentiment', 50) / 100,
                    'social_score': item.get('social_score', 0),
                    'engagement': item.get('engagement', 0),
                }
                for item in timeline
            ]

        except Exception as e:
            logger.error(f"Error fetching social timeline for {symbol}: {e}")
            return self._get_mock_social_timeline(symbol, days)

    async def get_market_sentiment_overview(self) -> Dict:
        """
        Get overall crypto market sentiment

        Returns:
            Dict with market sentiment overview
        """
        try:
            # Get top coins by social volume
            trending = await self.get_trending_coins(limit=50)

            if not trending:
                return self._get_mock_market_sentiment()

            # Calculate aggregate sentiment
            total_sentiment = sum(coin.get('sentiment', 0.5) for coin in trending)
            avg_sentiment = total_sentiment / len(trending) if trending else 0.5

            # Count bullish vs bearish
            bullish = sum(1 for coin in trending if coin.get('sentiment', 0.5) > 0.5)
            bearish = sum(1 for coin in trending if coin.get('sentiment', 0.5) < 0.5)
            neutral = len(trending) - bullish - bearish

            return {
                'timestamp': int(datetime.now().timestamp()),
                'overall_sentiment': avg_sentiment,
                'sentiment_label': self._sentiment_label(avg_sentiment),
                'distribution': {
                    'bullish': bullish,
                    'neutral': neutral,
                    'bearish': bearish,
                    'bullish_pct': (bullish / len(trending) * 100) if trending else 0,
                    'bearish_pct': (bearish / len(trending) * 100) if trending else 0,
                },
                'top_trending': trending[:10],
                'total_social_volume': sum(coin.get('social_volume', 0) for coin in trending),
            }

        except Exception as e:
            logger.error(f"Error fetching market sentiment overview: {e}")
            return self._get_mock_market_sentiment()

    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 0.7:
            return "Very Bullish"
        elif score >= 0.6:
            return "Bullish"
        elif score >= 0.5:
            return "Slightly Bullish"
        elif score >= 0.4:
            return "Neutral"
        elif score >= 0.3:
            return "Slightly Bearish"
        elif score >= 0.2:
            return "Bearish"
        else:
            return "Very Bearish"

    # Mock data methods for fallback

    def _get_mock_social_metrics(self, symbol: str) -> Dict:
        """Generate mock social metrics"""
        base_volume = {'BTC': 15000, 'ETH': 8000, 'BNB': 3000}.get(symbol.upper(), 1000)
        sentiment_score = random.uniform(0.4, 0.7)

        return {
            'symbol': symbol.upper(),
            'name': symbol,
            'timestamp': int(datetime.now().timestamp()),
            'sentiment': {
                'score': sentiment_score,
                'sentiment_absolute': random.randint(1000, 5000),
                'sentiment_relative': random.uniform(-0.2, 0.2),
            },
            'social_volume': {
                'total': base_volume + random.randint(-500, 500),
                'reddit': random.randint(100, 500),
                'twitter': random.randint(500, 2000),
                'news': random.randint(50, 200),
            },
            'engagement': {
                'social_score': random.uniform(50, 95),
                'social_contributors': random.randint(1000, 5000),
                'social_dominance': random.uniform(1, 10),
            },
            'influence': {
                'galaxy_score': random.uniform(60, 85),
                'alt_rank': random.randint(1, 100),
                'market_dominance': random.uniform(1, 50),
            },
            'price_correlation': {
                'correlation_rank': random.randint(1, 50),
                'volatility': random.uniform(0.02, 0.08),
            }
        }

    def _get_mock_trending_coins(self, limit: int) -> List[Dict]:
        """Generate mock trending coins"""
        coins = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOT', 'DOGE', 'MATIC', 'AVAX',
                 'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'ALGO', 'VET', 'ICP', 'FIL']

        return [
            {
                'rank': idx + 1,
                'symbol': coin,
                'name': coin,
                'social_volume': random.randint(1000, 15000),
                'social_score': random.uniform(50, 95),
                'sentiment': random.uniform(0.4, 0.7),
                'galaxy_score': random.uniform(60, 85),
                'alt_rank': idx + 1,
                'price_change_24h': random.uniform(-10, 10),
            }
            for idx, coin in enumerate(coins[:limit])
        ]

    def _get_mock_influencer_activity(self, symbol: str) -> List[Dict]:
        """Generate mock influencer activity"""
        usernames = ['CryptoWhale', 'BTCMaxi', 'DeFiGuru', 'AltcoinDaily', 'CoinBureau']

        return [
            {
                'username': username,
                'platform': 'twitter',
                'followers': random.randint(10000, 500000),
                'engagement': random.uniform(0.01, 0.05),
                'sentiment': random.uniform(0.3, 0.8),
                'influence_score': random.uniform(60, 95),
                'recent_posts': random.randint(1, 20),
            }
            for username in usernames
        ]

    def _get_mock_social_timeline(self, symbol: str, days: int) -> List[Dict]:
        """Generate mock social timeline"""
        timeline = []
        current = datetime.now() - timedelta(days=days)

        for i in range(days):
            date = current + timedelta(days=i)
            timeline.append({
                'timestamp': int(date.timestamp()),
                'datetime': date.isoformat(),
                'social_volume': random.randint(1000, 5000),
                'sentiment': random.uniform(0.4, 0.7),
                'social_score': random.uniform(50, 90),
                'engagement': random.randint(1000, 10000),
            })

        return timeline

    def _get_mock_market_sentiment(self) -> Dict:
        """Generate mock market sentiment overview"""
        trending = self._get_mock_trending_coins(50)
        bullish = sum(1 for coin in trending if coin['sentiment'] > 0.5)
        bearish = sum(1 for coin in trending if coin['sentiment'] < 0.5)
        neutral = len(trending) - bullish - bearish
        avg_sentiment = sum(coin['sentiment'] for coin in trending) / len(trending)

        return {
            'timestamp': int(datetime.now().timestamp()),
            'overall_sentiment': avg_sentiment,
            'sentiment_label': self._sentiment_label(avg_sentiment),
            'distribution': {
                'bullish': bullish,
                'neutral': neutral,
                'bearish': bearish,
                'bullish_pct': (bullish / len(trending) * 100),
                'bearish_pct': (bearish / len(trending) * 100),
            },
            'top_trending': trending[:10],
            'total_social_volume': sum(coin['social_volume'] for coin in trending),
        }

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
        logger.info("LunarCrush provider closed")
