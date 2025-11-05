"""
Binance Market Data Provider
Provides historical and real-time market data from Binance
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import ccxt
import asyncio

from .base_provider import BaseMarketDataProvider, DataSource, TimeFrame

logger = logging.getLogger(__name__)


class BinanceMarketDataProvider(BaseMarketDataProvider):
    """
    Binance market data provider using CCXT
    Provides OHLCV, ticker, and orderbook data
    """

    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        """
        Initialize Binance market data provider

        Args:
            api_key: Binance API key (optional for public endpoints)
            api_secret: Binance API secret (optional for public endpoints)
            testnet: Use testnet
        """
        super().__init__(api_key, api_secret)
        self.source = DataSource.BINANCE
        self.testnet = testnet

        # Initialize CCXT Binance client
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # spot, future, margin
            }
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)

        logger.info(f"Binance market data provider initialized (testnet: {testnet})")

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.H1,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        Get OHLCV data from Binance

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            timeframe: Candle timeframe
            start_date: Start date (defaults to limit candles ago)
            end_date: End date (defaults to now)
            limit: Max candles (default 500, max 1000)

        Returns:
            List of OHLCV dicts
        """
        try:
            # Limit to max 1000 (Binance limit)
            limit = min(limit, 1000)

            # Convert datetime to milliseconds timestamp
            since = None
            if start_date:
                since = int(start_date.timestamp() * 1000)

            # Fetch OHLCV data
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                timeframe.value,
                since=since,
                limit=limit
            )

            # Convert to dict format
            result = []
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle

                # Filter by end_date if provided
                if end_date and datetime.fromtimestamp(timestamp / 1000) > end_date:
                    break

                result.append({
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                    'open': float(open_price),
                    'high': float(high),
                    'low': float(low),
                    'close': float(close),
                    'volume': float(volume)
                })

            logger.info(f"Fetched {len(result)} candles for {symbol} ({timeframe.value})")
            return result

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise

    async def get_ohlcv_range(
        self,
        symbol: str,
        timeframe: TimeFrame,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get OHLCV data for a date range (handles pagination for large ranges)

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            start_date: Start date
            end_date: End date

        Returns:
            List of all OHLCV dicts in range
        """
        try:
            all_candles = []
            current_date = start_date

            # Determine candle duration in milliseconds
            timeframe_ms = {
                TimeFrame.M1: 60 * 1000,
                TimeFrame.M5: 5 * 60 * 1000,
                TimeFrame.M15: 15 * 60 * 1000,
                TimeFrame.M30: 30 * 60 * 1000,
                TimeFrame.H1: 60 * 60 * 1000,
                TimeFrame.H4: 4 * 60 * 60 * 1000,
                TimeFrame.D1: 24 * 60 * 60 * 1000,
                TimeFrame.W1: 7 * 24 * 60 * 60 * 1000,
            }

            candle_duration = timeframe_ms.get(timeframe, 60 * 60 * 1000)
            batch_size = 1000  # Binance limit

            while current_date < end_date:
                # Fetch batch
                candles = await self.get_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=current_date,
                    limit=batch_size
                )

                if not candles:
                    break

                # Add to results
                for candle in candles:
                    candle_time = datetime.fromtimestamp(candle['timestamp'] / 1000)
                    if candle_time <= end_date:
                        all_candles.append(candle)

                # Move to next batch
                last_timestamp = candles[-1]['timestamp']
                current_date = datetime.fromtimestamp(last_timestamp / 1000) + timedelta(milliseconds=candle_duration)

                # Rate limiting
                await asyncio.sleep(0.1)

            logger.info(f"Fetched {len(all_candles)} total candles for {symbol} from {start_date} to {end_date}")
            return all_candles

        except Exception as e:
            logger.error(f"Error fetching OHLCV range: {e}")
            raise

    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information

        Args:
            symbol: Trading pair

        Returns:
            Dict with ticker data
        """
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)

            return {
                'symbol': symbol,
                'last': float(ticker.get('last', 0)),
                'bid': float(ticker.get('bid', 0)),
                'ask': float(ticker.get('ask', 0)),
                'high_24h': float(ticker.get('high', 0)),
                'low_24h': float(ticker.get('low', 0)),
                'volume_24h': float(ticker.get('baseVolume', 0)),
                'quote_volume_24h': float(ticker.get('quoteVolume', 0)),
                'change_24h': float(ticker.get('change', 0)),
                'percentage_24h': float(ticker.get('percentage', 0)),
                'timestamp': ticker.get('timestamp'),
                'datetime': ticker.get('datetime')
            }

        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    async def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """
        Get order book data

        Args:
            symbol: Trading pair
            depth: Number of bids/asks

        Returns:
            Dict with bids and asks
        """
        try:
            orderbook = await asyncio.to_thread(
                self.exchange.fetch_order_book,
                symbol,
                limit=depth
            )

            return {
                'symbol': symbol,
                'bids': [[float(price), float(amount)] for price, amount in orderbook.get('bids', [])],
                'asks': [[float(price), float(amount)] for price, amount in orderbook.get('asks', [])],
                'timestamp': orderbook.get('timestamp'),
                'datetime': orderbook.get('datetime')
            }

        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            raise

    async def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols on Binance

        Returns:
            List of symbol strings
        """
        try:
            markets = await asyncio.to_thread(self.exchange.load_markets)

            # Filter for active spot markets
            symbols = [
                symbol for symbol, market in markets.items()
                if market.get('active', False) and market.get('spot', False)
            ]

            logger.info(f"Found {len(symbols)} available symbols on Binance")
            return sorted(symbols)

        except Exception as e:
            logger.error(f"Error fetching available symbols: {e}")
            return []

    async def get_24h_stats(self, symbol: str) -> Dict:
        """
        Get 24-hour statistics

        Args:
            symbol: Trading pair

        Returns:
            Dict with 24h stats
        """
        try:
            ticker = await self.get_ticker(symbol)

            return {
                'symbol': symbol,
                'price_change': ticker.get('change_24h', 0),
                'price_change_percent': ticker.get('percentage_24h', 0),
                'high': ticker.get('high_24h', 0),
                'low': ticker.get('low_24h', 0),
                'volume': ticker.get('volume_24h', 0),
                'quote_volume': ticker.get('quote_volume_24h', 0),
                'last_price': ticker.get('last', 0)
            }

        except Exception as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            raise

    async def get_klines_with_volume_profile(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.H1,
        limit: int = 100
    ) -> Dict:
        """
        Get OHLCV data with volume profile analysis

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            limit: Number of candles

        Returns:
            Dict with candles and volume profile
        """
        try:
            candles = await self.get_ohlcv(symbol, timeframe, limit=limit)

            if not candles:
                return {'candles': [], 'volume_profile': {}}

            # Calculate volume profile
            total_volume = sum(c['volume'] for c in candles)
            avg_volume = total_volume / len(candles) if candles else 0

            # Find high volume nodes (volume > 1.5x average)
            high_volume_candles = [
                c for c in candles
                if c['volume'] > avg_volume * 1.5
            ]

            volume_profile = {
                'total_volume': total_volume,
                'avg_volume': avg_volume,
                'max_volume': max(c['volume'] for c in candles) if candles else 0,
                'min_volume': min(c['volume'] for c in candles) if candles else 0,
                'high_volume_nodes': len(high_volume_candles),
                'high_volume_levels': [
                    {
                        'price': c['close'],
                        'volume': c['volume'],
                        'timestamp': c['timestamp']
                    }
                    for c in high_volume_candles
                ]
            }

            return {
                'candles': candles,
                'volume_profile': volume_profile
            }

        except Exception as e:
            logger.error(f"Error fetching volume profile for {symbol}: {e}")
            raise

    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """
        Get recent trades

        Args:
            symbol: Trading pair
            limit: Number of trades

        Returns:
            List of trade dicts
        """
        try:
            trades = await asyncio.to_thread(
                self.exchange.fetch_trades,
                symbol,
                limit=limit
            )

            return [
                {
                    'id': trade.get('id'),
                    'timestamp': trade.get('timestamp'),
                    'datetime': trade.get('datetime'),
                    'symbol': trade.get('symbol'),
                    'side': trade.get('side'),
                    'price': float(trade.get('price', 0)),
                    'amount': float(trade.get('amount', 0)),
                    'cost': float(trade.get('cost', 0))
                }
                for trade in trades
            ]

        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            raise

    async def close(self):
        """Close exchange connection"""
        if hasattr(self.exchange, 'close'):
            await asyncio.to_thread(self.exchange.close)
        logger.info("Binance market data provider closed")
