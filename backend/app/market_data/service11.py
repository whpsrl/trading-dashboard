"""
Market Data Service with Redis Caching
Handles fetching real-time and historical market data from various exchanges
Uses CoinGecko as fallback when exchanges are geo-blocked
Implements Redis caching to avoid rate limits
"""
import ccxt
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
import redis
import os

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        """Initialize exchange connections and Redis cache"""
        self.exchanges = {}
        
        # Initialize Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {str(e)}, continuing without cache")
            self.redis_client = None
        
    def _get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """Get or create exchange instance"""
        if exchange_name not in self.exchanges:
            try:
                exchange_class = getattr(ccxt, exchange_name.lower())
                self.exchanges[exchange_name] = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 10000,
                })
            except Exception as e:
                logger.error(f"Error initializing exchange {exchange_name}: {str(e)}")
                raise
        return self.exchanges[exchange_name]
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info(f"✅ Cache HIT: {cache_key}")
                return json.loads(cached)
            logger.info(f"❌ Cache MISS: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None
    
    def _set_cached_data(self, cache_key: str, data: Dict, ttl: int = 60):
        """Set data in Redis cache with TTL (seconds)"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
            logger.info(f"💾 Cached: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
    
    def _get_price_from_coingecko(self, symbol: str) -> Optional[Dict]:
        """
        Fetch price from CoinGecko as fallback
        Works from any location without geo-restrictions
        Uses Redis cache to avoid rate limits
        """
        # Check cache first (60 second TTL)
        cache_key = f"coingecko:price:{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Convert trading pair to CoinGecko format
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'SOL': 'solana',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'DOGE': 'dogecoin',
                'DOT': 'polkadot',
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2',
            }
            
            base = symbol.split('/')[0] if '/' in symbol else symbol
            coin_id = symbol_map.get(base.upper())
            
            if not coin_id:
                logger.warning(f"Symbol {symbol} not found in CoinGecko map")
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                result = {
                    'symbol': symbol,
                    'price': coin_data.get('usd', 0),
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'coingecko'
                }
                
                # Cache for 60 seconds
                self._set_cached_data(cache_key, result, ttl=60)
                
                return result
            
            return None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("⚠️ CoinGecko rate limit hit! Using cache or fallback")
                # Try to return stale cache if available
                stale_cache = self._get_cached_data(f"coingecko:price:{symbol}:stale")
                if stale_cache:
                    logger.info("✅ Returning stale cache data")
                    return stale_cache
            logger.error(f"Error fetching from CoinGecko: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching from CoinGecko: {str(e)}")
            return None
    
    async def get_price(self, symbol: str, exchange: str = "binance") -> Dict:
        """
        Get current price for a symbol
        Falls back to CoinGecko if exchange is geo-blocked
        Uses Redis caching to avoid rate limits
        """
        # Check cache first (30 second TTL)
        cache_key = f"price:{exchange}:{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Try to get from specified exchange first
            exchange_obj = self._get_exchange(exchange)
            ticker = exchange_obj.fetch_ticker(symbol)
            
            result = {
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['quoteVolume'],
                'change_24h': ticker['percentage'],
                'timestamp': ticker['timestamp'],
                'source': exchange
            }
            
            # Cache for 30 seconds
            self._set_cached_data(cache_key, result, ttl=30)
            
            return result
            
        except ccxt.ExchangeError as e:
            # Check if it's a geo-restriction error
            if '451' in str(e) or 'restricted location' in str(e).lower():
                logger.warning(f"Exchange {exchange} geo-blocked, falling back to CoinGecko")
                coingecko_data = self._get_price_from_coingecko(symbol)
                if coingecko_data:
                    # Also cache this for longer (to reduce CoinGecko calls)
                    self._set_cached_data(cache_key, coingecko_data, ttl=60)
                    # Keep stale copy for emergencies
                    self._set_cached_data(f"{cache_key}:stale", coingecko_data, ttl=300)
                    return coingecko_data
                raise Exception(f"Both {exchange} and CoinGecko failed for {symbol}")
            
            # Other exchange errors
            logger.error(f"Error fetching price from {exchange}: {str(e)}")
            # Try CoinGecko as fallback
            coingecko_data = self._get_price_from_coingecko(symbol)
            if coingecko_data:
                self._set_cached_data(cache_key, coingecko_data, ttl=60)
                return coingecko_data
            raise
            
        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            # Try CoinGecko as last resort
            coingecko_data = self._get_price_from_coingecko(symbol)
            if coingecko_data:
                self._set_cached_data(cache_key, coingecko_data, ttl=60)
                return coingecko_data
            raise
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = "1h",
        limit: int = 100,
        exchange: str = "binance"
    ) -> List[List]:
        """Get OHLCV (candlestick) data with caching"""
        # Check cache (5 minute TTL for OHLCV)
        cache_key = f"ohlcv:{exchange}:{symbol}:{timeframe}:{limit}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            exchange_obj = self._get_exchange(exchange)
            ohlcv = exchange_obj.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Cache for 5 minutes
            self._set_cached_data(cache_key, ohlcv, ttl=300)
            
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {str(e)}")
            raise
    
    async def get_orderbook(self, symbol: str, exchange: str = "binance") -> Dict:
        """Get order book data"""
        try:
            exchange_obj = self._get_exchange(exchange)
            orderbook = exchange_obj.fetch_order_book(symbol)
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:20],  # Top 20 bids
                'asks': orderbook['asks'][:20],  # Top 20 asks
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook: {str(e)}")
            raise
    
    async def get_trades(
        self, 
        symbol: str, 
        limit: int = 50,
        exchange: str = "binance"
    ) -> List[Dict]:
        """Get recent trades"""
        try:
            exchange_obj = self._get_exchange(exchange)
            trades = exchange_obj.fetch_trades(symbol, limit=limit)
            return [{
                'price': trade['price'],
                'amount': trade['amount'],
                'side': trade['side'],
                'timestamp': trade['timestamp']
            } for trade in trades]
        except Exception as e:
            logger.error(f"Error fetching trades: {str(e)}")
            raise

# Global service instance
market_service = MarketDataService()
