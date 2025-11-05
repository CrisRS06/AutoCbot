"""
Market Data Aggregator
Unified service that combines all market data providers
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from cachetools import TTLCache

from .binance_provider import BinanceMarketDataProvider, TimeFrame
from .glassnode_provider import GlassnodeProvider
from .lunarcrush_provider import LunarCrushProvider

logger = logging.getLogger(__name__)


class MarketDataAggregator:
    """
    Aggregates data from multiple sources
    Provides a unified interface for all market data
    """

    def __init__(
        self,
        binance_api_key: str = "",
        binance_api_secret: str = "",
        glassnode_api_key: str = "",
        lunarcrush_api_key: str = "",
        use_cache: bool = True,
        cache_ttl: int = 300  # 5 minutes default
    ):
        """
        Initialize market data aggregator

        Args:
            binance_api_key: Binance API key
            binance_api_secret: Binance API secret
            glassnode_api_key: Glassnode API key
            lunarcrush_api_key: LunarCrush API key
            use_cache: Whether to cache responses
            cache_ttl: Cache time-to-live in seconds
        """
        # Initialize providers
        self.binance = BinanceMarketDataProvider(
            api_key=binance_api_key,
            api_secret=binance_api_secret
        )

        self.glassnode = GlassnodeProvider(api_key=glassnode_api_key)
        self.lunarcrush = LunarCrushProvider(api_key=lunarcrush_api_key)

        # Cache for expensive API calls
        self.use_cache = use_cache
        if use_cache:
            self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        else:
            self.cache = None

        logger.info("Market data aggregator initialized")

    def _cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return "_".join(str(arg) for arg in args)

    async def get_market_overview(self, symbol: str) -> Dict:
        """
        Get comprehensive market overview for a symbol

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Dict with all market data
        """
        cache_key = self._cache_key("market_overview", symbol)

        if self.use_cache and cache_key in self.cache:
            logger.debug(f"Cache hit for market_overview:{symbol}")
            return self.cache[cache_key]

        try:
            # Extract base asset (e.g., "BTC" from "BTC/USDT")
            base_asset = symbol.split('/')[0]

            # Fetch data from all providers in parallel
            tasks = [
                self.binance.get_ticker(symbol),
                self.binance.get_24h_stats(symbol),
                self.lunarcrush.get_social_metrics(base_asset),
            ]

            # Add on-chain metrics for major coins
            if base_asset in ['BTC', 'ETH']:
                tasks.append(self.glassnode.get_market_metrics(base_asset))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Parse results
            ticker = results[0] if not isinstance(results[0], Exception) else {}
            stats_24h = results[1] if not isinstance(results[1], Exception) else {}
            social = results[2] if not isinstance(results[2], Exception) else {}
            onchain = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None

            overview = {
                'symbol': symbol,
                'timestamp': int(datetime.now().timestamp()),
                'price': {
                    'current': ticker.get('last', 0),
                    'bid': ticker.get('bid', 0),
                    'ask': ticker.get('ask', 0),
                    'high_24h': stats_24h.get('high', 0),
                    'low_24h': stats_24h.get('low', 0),
                    'change_24h': stats_24h.get('price_change', 0),
                    'change_pct_24h': stats_24h.get('price_change_percent', 0),
                },
                'volume': {
                    'volume_24h': stats_24h.get('volume', 0),
                    'quote_volume_24h': stats_24h.get('quote_volume', 0),
                },
                'social': social,
                'onchain': onchain,
                'analysis': self._generate_analysis(ticker, social, onchain)
            }

            if self.use_cache:
                self.cache[cache_key] = overview

            return overview

        except Exception as e:
            logger.error(f"Error getting market overview for {symbol}: {e}")
            raise

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.H1,
        days: int = 30
    ) -> Dict:
        """
        Get historical OHLCV data with additional metrics

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            days: Number of days of history

        Returns:
            Dict with historical data and analysis
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()

            # Get OHLCV data
            candles = await self.binance.get_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                limit=min(days * 24, 1000)
            )

            # Calculate technical indicators
            analysis = self._calculate_technical_indicators(candles)

            return {
                'symbol': symbol,
                'timeframe': timeframe.value,
                'candles': candles,
                'candle_count': len(candles),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'technical_analysis': analysis
            }

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise

    async def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Get comprehensive analysis combining all data sources

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Dict with complete analysis
        """
        cache_key = self._cache_key("comprehensive", symbol)

        if self.use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            base_asset = symbol.split('/')[0]

            # Get all data in parallel
            tasks = [
                self.get_market_overview(symbol),
                self.get_historical_data(symbol, TimeFrame.D1, days=30),
                self.lunarcrush.get_social_timeline(base_asset, days=7),
            ]

            if base_asset in ['BTC', 'ETH']:
                tasks.extend([
                    self.glassnode.get_active_addresses(base_asset),
                    self.glassnode.get_network_value(base_asset),
                    self.glassnode.get_exchange_flows(base_asset),
                ])

            results = await asyncio.gather(*tasks, return_exceptions=True)

            market_overview = results[0] if not isinstance(results[0], Exception) else {}
            historical = results[1] if not isinstance(results[1], Exception) else {}
            social_timeline = results[2] if not isinstance(results[2], Exception) else []

            # On-chain data (if available)
            onchain_data = {}
            if len(results) > 3:
                onchain_data = {
                    'active_addresses': results[3] if not isinstance(results[3], Exception) else [],
                    'nvt_ratio': results[4] if len(results) > 4 and not isinstance(results[4], Exception) else [],
                    'exchange_flows': results[5] if len(results) > 5 and not isinstance(results[5], Exception) else {},
                }

            # Generate combined score
            combined_score = self._calculate_combined_score(
                market_overview,
                historical,
                social_timeline,
                onchain_data
            )

            analysis = {
                'symbol': symbol,
                'timestamp': int(datetime.now().timestamp()),
                'market_overview': market_overview,
                'historical_analysis': historical,
                'social_timeline': social_timeline,
                'onchain_metrics': onchain_data,
                'combined_score': combined_score,
                'recommendation': self._generate_recommendation(combined_score)
            }

            if self.use_cache:
                self.cache[cache_key] = analysis

            return analysis

        except Exception as e:
            logger.error(f"Error getting comprehensive analysis for {symbol}: {e}")
            raise

    async def get_trending_analysis(self, limit: int = 10) -> Dict:
        """
        Get analysis of trending coins

        Args:
            limit: Number of trending coins

        Returns:
            Dict with trending coins and analysis
        """
        try:
            # Get trending from social
            trending = await self.lunarcrush.get_trending_coins(limit=limit)

            # Get price data for each trending coin
            trending_with_data = []

            for coin in trending:
                try:
                    symbol = f"{coin['symbol']}/USDT"
                    ticker = await self.binance.get_ticker(symbol)

                    trending_with_data.append({
                        **coin,
                        'price': ticker.get('last', 0),
                        'volume_24h': ticker.get('volume_24h', 0),
                        'change_24h': ticker.get('percentage_24h', 0),
                    })
                except Exception as e:
                    logger.warning(f"Could not get price for {coin['symbol']}: {e}")
                    trending_with_data.append(coin)

            return {
                'timestamp': int(datetime.now().timestamp()),
                'trending_coins': trending_with_data,
                'count': len(trending_with_data)
            }

        except Exception as e:
            logger.error(f"Error getting trending analysis: {e}")
            raise

    async def get_market_sentiment(self) -> Dict:
        """
        Get overall market sentiment

        Returns:
            Dict with market sentiment data
        """
        cache_key = "market_sentiment"

        if self.use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            sentiment = await self.lunarcrush.get_market_sentiment_overview()

            if self.use_cache:
                self.cache[cache_key] = sentiment

            return sentiment

        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            raise

    def _calculate_technical_indicators(self, candles: List[Dict]) -> Dict:
        """
        Calculate basic technical indicators from candles

        Args:
            candles: List of OHLCV candles

        Returns:
            Dict with technical indicators
        """
        if not candles or len(candles) < 2:
            return {}

        closes = [c['close'] for c in candles]
        volumes = [c['volume'] for c in candles]

        # Simple moving averages
        sma_20 = sum(closes[-20:]) / min(20, len(closes))
        sma_50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 50 else sma_20

        # Current price vs SMAs
        current_price = closes[-1]
        trend = "bullish" if current_price > sma_20 > sma_50 else "bearish" if current_price < sma_20 < sma_50 else "neutral"

        # Volume analysis
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        volume_status = "high" if current_volume > avg_volume * 1.5 else "normal"

        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'current_price': current_price,
            'trend': trend,
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'volume_status': volume_status,
            'price_vs_sma20_pct': ((current_price - sma_20) / sma_20 * 100) if sma_20 > 0 else 0,
        }

    def _generate_analysis(self, ticker: Dict, social: Dict, onchain: Optional[Dict]) -> Dict:
        """
        Generate analysis from combined data

        Args:
            ticker: Ticker data
            social: Social sentiment data
            onchain: On-chain metrics

        Returns:
            Analysis dict
        """
        signals = []
        score = 50.0  # Base score

        # Price momentum
        change_24h = ticker.get('percentage_24h', 0)
        if change_24h > 5:
            signals.append("Strong upward momentum")
            score += 10
        elif change_24h < -5:
            signals.append("Strong downward momentum")
            score -= 10

        # Social sentiment
        if social:
            sentiment_score = social.get('sentiment', {}).get('score', 0.5)
            if sentiment_score > 0.6:
                signals.append("Positive social sentiment")
                score += 10
            elif sentiment_score < 0.4:
                signals.append("Negative social sentiment")
                score -= 10

        # On-chain metrics
        if onchain:
            health_score = onchain.get('health_score', 50)
            if health_score > 70:
                signals.append("Strong on-chain fundamentals")
                score += 10
            elif health_score < 30:
                signals.append("Weak on-chain fundamentals")
                score -= 10

        return {
            'score': min(max(score, 0), 100),
            'signals': signals,
            'overall': "bullish" if score > 60 else "bearish" if score < 40 else "neutral"
        }

    def _calculate_combined_score(
        self,
        market_overview: Dict,
        historical: Dict,
        social_timeline: List,
        onchain_data: Dict
    ) -> Dict:
        """
        Calculate combined score from all data sources

        Returns:
            Dict with combined score and breakdown
        """
        scores = {
            'technical': 50.0,
            'social': 50.0,
            'onchain': 50.0,
            'overall': 50.0
        }

        # Technical score from historical analysis
        if historical and 'technical_analysis' in historical:
            tech = historical['technical_analysis']
            if tech.get('trend') == 'bullish':
                scores['technical'] = 70.0
            elif tech.get('trend') == 'bearish':
                scores['technical'] = 30.0

        # Social score
        if market_overview and 'social' in market_overview:
            social = market_overview['social']
            sentiment = social.get('sentiment', {}).get('score', 0.5)
            scores['social'] = sentiment * 100

        # On-chain score
        if onchain_data and 'active_addresses' in onchain_data:
            # Simplified - could be more sophisticated
            scores['onchain'] = 60.0

        # Calculate overall (weighted average)
        scores['overall'] = (
            scores['technical'] * 0.4 +
            scores['social'] * 0.3 +
            scores['onchain'] * 0.3
        )

        return scores

    def _generate_recommendation(self, scores: Dict) -> Dict:
        """
        Generate trading recommendation from scores

        Args:
            scores: Combined scores dict

        Returns:
            Recommendation dict
        """
        overall = scores.get('overall', 50)

        if overall >= 70:
            action = "STRONG BUY"
            confidence = "High"
        elif overall >= 60:
            action = "BUY"
            confidence = "Medium"
        elif overall >= 55:
            action = "WEAK BUY"
            confidence = "Low"
        elif overall >= 45:
            action = "HOLD"
            confidence = "Medium"
        elif overall >= 40:
            action = "WEAK SELL"
            confidence = "Low"
        elif overall >= 30:
            action = "SELL"
            confidence = "Medium"
        else:
            action = "STRONG SELL"
            confidence = "High"

        return {
            'action': action,
            'confidence': confidence,
            'score': overall,
            'reasoning': f"Overall score of {overall:.1f}/100 based on technical, social, and on-chain analysis"
        }

    async def close(self):
        """Close all provider connections"""
        await self.binance.close()
        await self.glassnode.close()
        await self.lunarcrush.close()
        logger.info("Market data aggregator closed")
