"""
Market Data Service
Integrates CoinGecko (free tier) and exchange APIs
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache

from models.schemas import MarketPrice, MarketOverview, CandleData
from utils.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """Market data service using CoinGecko Free API"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        self.cache = TTLCache(maxsize=1000, ttl=settings.CACHE_TTL)

        # Symbol mapping (exchange format to CoinGecko IDs)
        self.symbol_map = {
            "BTC/USDT": "bitcoin",
            "ETH/USDT": "ethereum",
            "BNB/USDT": "binancecoin",
            "SOL/USDT": "solana",
            "XRP/USDT": "ripple",
            "ADA/USDT": "cardano",
            "DOGE/USDT": "dogecoin",
            "MATIC/USDT": "matic-network",
            "DOT/USDT": "polkadot",
            "AVAX/USDT": "avalanche-2"
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with caching"""
        cache_key = f"{endpoint}_{str(params)}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.cache[cache_key] = data
                    return data
                else:
                    logger.error(f"API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {}

    def _symbol_to_id(self, symbol: str) -> str:
        """Convert exchange symbol to CoinGecko ID"""
        return self.symbol_map.get(symbol, symbol.lower().split("/")[0])

    async def get_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get current price for a symbol"""
        coin_id = self._symbol_to_id(symbol)

        data = await self._request(
            "simple/price",
            {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
        )

        if coin_id not in data:
            return None

        coin_data = data[coin_id]
        return MarketPrice(
            symbol=symbol,
            price=coin_data.get("usd", 0),
            change_24h=coin_data.get("usd_24h_change", 0),
            volume_24h=coin_data.get("usd_24h_vol", 0),
            timestamp=datetime.now()
        )

    async def get_prices(self, symbols: List[str]) -> List[MarketPrice]:
        """Get prices for multiple symbols"""
        tasks = [self.get_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def get_market_overview(self) -> MarketOverview:
        """Get overall market overview"""
        global_data = await self._request("global")

        if not global_data or "data" not in global_data:
            return MarketOverview(
                total_market_cap=0,
                btc_dominance=0,
                eth_dominance=0,
                defi_market_cap=0,
                total_volume_24h=0
            )

        data = global_data["data"]
        market_cap = data.get("total_market_cap", {})
        volume = data.get("total_volume", {})

        return MarketOverview(
            total_market_cap=market_cap.get("usd", 0),
            btc_dominance=data.get("market_cap_percentage", {}).get("btc", 0),
            eth_dominance=data.get("market_cap_percentage", {}).get("eth", 0),
            defi_market_cap=data.get("defi_market_cap", 0),
            total_volume_24h=volume.get("usd", 0)
        )

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100
    ) -> List[CandleData]:
        """Get historical candle data"""
        coin_id = self._symbol_to_id(symbol)

        # Convert timeframe to days
        days_map = {
            "1m": 1,
            "5m": 1,
            "15m": 1,
            "1h": 7,
            "4h": 30,
            "1d": 90
        }
        days = days_map.get(timeframe, 7)

        data = await self._request(
            f"coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": days}
        )

        if "prices" not in data:
            return []

        prices = data["prices"]
        candles = []

        # Simple OHLC construction from price data
        for i in range(0, len(prices), max(1, len(prices) // limit)):
            if i < len(prices):
                timestamp, price = prices[i]
                candles.append(CandleData(
                    timestamp=int(timestamp),
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=0  # Volume not available in this endpoint
                ))

        return candles[:limit]

    async def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """Get trending cryptocurrencies"""
        data = await self._request("search/trending")

        if "coins" not in data:
            return []

        trending = []
        for item in data["coins"][:limit]:
            coin = item.get("item", {})
            trending.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "thumb": coin.get("thumb")
            })

        return trending

    async def get_gainers_losers(self, limit: int = 10) -> Dict:
        """Get top gainers and losers"""
        data = await self._request(
            "coins/markets",
            {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h"
            }
        )

        if not data:
            return {"gainers": [], "losers": []}

        # Sort by 24h change
        sorted_data = sorted(
            data,
            key=lambda x: x.get("price_change_percentage_24h", 0),
            reverse=True
        )

        gainers = sorted_data[:limit]
        losers = sorted_data[-limit:]

        return {
            "gainers": [
                {
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "price": coin["current_price"],
                    "change_24h": coin.get("price_change_percentage_24h", 0)
                }
                for coin in gainers
            ],
            "losers": [
                {
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "price": coin["current_price"],
                    "change_24h": coin.get("price_change_percentage_24h", 0)
                }
                for coin in losers
            ]
        }

    async def start_price_updates(self):
        """Start background price updates"""
        self.is_running = True
        logger.info("📊 Market data service started")

        while self.is_running:
            try:
                # Update prices for default pairs
                await self.get_prices(settings.DEFAULT_PAIRS)
                await asyncio.sleep(settings.PRICE_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Price update error: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        """Stop the service"""
        self.is_running = False
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("📊 Market data service stopped")
