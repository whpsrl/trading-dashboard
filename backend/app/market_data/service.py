"""
Market Data Service
Handles crypto market data from Binance/CoinGecko
"""
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        """Initialize market data service"""
        # Try to import ccxt for Binance
        try:
            import ccxt
            self.binance = ccxt.binance()
            logger.info("✅ Binance initialized (ccxt)")
        except ImportError:
            self.binance = None
            logger.warning("⚠️ ccxt not installed - Binance unavailable")
        
        # Redis for caching (optional)
        try:
            import redis
            import os
            redis_url = os.getenv('REDIS_URL')
            self.redis = redis.from_url(redis_url) if redis_url else None
            if self.redis:
                logger.info("✅ Redis cache enabled")
        except:
            self.redis = None
            logger.info("ℹ️ Redis not available")
        
        logger.info("✅ Market data service initialized")
    
    async def get_price(self, symbol: str, exchange: str = "binance") -> Dict:
        """
        Get current price for a crypto pair
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            exchange: Exchange name (binance, coinbase, etc.)
        
        Returns:
            Price data with change, volume, etc.
        """
        try:
            if not self.binance:
                raise Exception("Binance not available - install ccxt")
            
            # Fetch ticker
            ticker = self.binance.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['quoteVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'timestamp': datetime.now().isoformat(),
                'source': 'binance',
                'exchange': exchange
            }
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            # Fallback to CoinGecko if available
            return await self._get_price_coingecko(symbol)
    
    async def _get_price_coingecko(self, symbol: str) -> Dict:
        """Fallback to CoinGecko for price data"""
        try:
            import requests
            
            # Map symbol to CoinGecko ID (simple mapping)
            symbol_map = {
                'BTC/USDT': 'bitcoin',
                'ETH/USDT': 'ethereum',
                'SOL/USDT': 'solana',
                'BNB/USDT': 'binancecoin',
            }
            
            coin_id = symbol_map.get(symbol, 'bitcoin')
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                return {
                    'symbol': symbol,
                    'price': coin_data['usd'],
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'coingecko',
                }
            else:
                raise Exception(f"Coin {coin_id} not found")
                
        except Exception as e:
            logger.error(f"CoinGecko fallback failed: {e}")
            raise
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        exchange: str = "binance"
    ) -> List[List]:
        """
        Get OHLCV candlestick data
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            timeframe: Candle timeframe (1h, 4h, 1d, etc.)
            limit: Number of candles
            exchange: Exchange name
        
        Returns:
            Array of [timestamp, open, high, low, close, volume]
        """
        try:
            if not self.binance:
                raise Exception("Binance not available - install ccxt")
            
            # Fetch OHLCV
            ohlcv = self.binance.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            logger.info(f"✅ Fetched {len(ohlcv)} candles for {symbol} ({timeframe})")
            return ohlcv
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise
    
    async def get_orderbook(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> Dict:
        """Get order book (bids and asks)"""
        try:
            if not self.binance:
                raise Exception("Binance not available")
            
            orderbook = self.binance.fetch_order_book(symbol)
            
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:20],  # Top 20 bids
                'asks': orderbook['asks'][:20],  # Top 20 asks
                'timestamp': orderbook['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            raise
    
    async def get_trades(
        self,
        symbol: str,
        limit: int = 50,
        exchange: str = "binance"
    ) -> List[Dict]:
        """Get recent trades"""
        try:
            if not self.binance:
                raise Exception("Binance not available")
            
            trades = self.binance.fetch_trades(symbol, limit=limit)
            
            return [{
                'id': trade['id'],
                'timestamp': trade['timestamp'],
                'price': trade['price'],
                'amount': trade['amount'],
                'side': trade['side']
            } for trade in trades]
            
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            raise


# Global service instance
market_service = MarketDataService()
