"""
Unified Market Data Service
Gestisce CRYPTO, STOCKS, FOREX con rate limiting intelligente
"""
import asyncio
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import ccxt

from .service_finnhub import finnhub_service

logger = logging.getLogger(__name__)


class RateLimitManager:
    """Gestisce rate limits per tutte le API"""
    
    def __init__(self):
        # Finnhub: 60 req/min (usiamo 55 per sicurezza)
        self.finnhub_calls = []
        self.finnhub_max = 55
        self.finnhub_window = 60
        
        # OANDA: ~100 req/20sec (usiamo 80 per sicurezza)
        self.oanda_calls = []
        self.oanda_max = 80
        self.oanda_window = 20
    
    def can_call_finnhub(self) -> bool:
        """Check if we can call Finnhub"""
        now = time.time()
        self.finnhub_calls = [t for t in self.finnhub_calls if now - t < self.finnhub_window]
        return len(self.finnhub_calls) < self.finnhub_max
    
    async def wait_finnhub(self):
        """Wait if needed before calling Finnhub"""
        while not self.can_call_finnhub():
            await asyncio.sleep(0.5)
        self.finnhub_calls.append(time.time())
    
    def can_call_oanda(self) -> bool:
        """Check if we can call OANDA"""
        now = time.time()
        self.oanda_calls = [t for t in self.oanda_calls if now - t < self.oanda_window]
        return len(self.oanda_calls) < self.oanda_max
    
    async def wait_oanda(self):
        """Wait if needed before calling OANDA"""
        while not self.can_call_oanda():
            await asyncio.sleep(0.2)
        self.oanda_calls.append(time.time())


class UnifiedMarketDataService:
    """
    Servizio unificato per dati di mercato multi-asset
    FREE + REAL-TIME con rate limiting intelligente
    """
    
    def __init__(self):
        # Rate limit manager
        self.rate_limiter = RateLimitManager()
        
        # Binance (Crypto) - CCXT
        try:
            self.binance = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            logger.info("✅ Binance initialized")
        except Exception as e:
            logger.error(f"❌ Binance init error: {e}")
            self.binance = None
        
        # Finnhub (Stocks/Indices/Commodities)
        self.finnhub = finnhub_service
        
        # OANDA (Forex)
        import os
        self.oanda_token = os.getenv('OANDA_API_TOKEN', '')
        self.oanda_url = "https://api-fxpractice.oanda.com"
        
        # Cache per ridurre chiamate
        self.cache = {}
        self.cache_ttl = 60  # 60 secondi
        
        logger.info("✅ Unified Market Data Service initialized")
    
    def _get_cache_key(self, source: str, symbol: str, timeframe: str) -> str:
        """Generate cache key"""
        return f"{source}:{symbol}:{timeframe}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Set cache"""
        self.cache[key] = (data, time.time())
    
    async def get_crypto_candles(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> List[Dict]:
        """
        Get crypto candles from Binance
        NO RATE LIMIT issues (Binance is generous)
        """
        if not self.binance:
            logger.error("Binance not available")
            return []
        
        # Check cache
        cache_key = self._get_cache_key('binance', symbol, timeframe)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info(f"📦 Cache hit: {symbol}")
            return cached
        
        try:
            # Binance CCXT fetch
            ohlcv = self.binance.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            candles = [
                {
                    'timestamp': c[0],
                    'open': c[1],
                    'high': c[2],
                    'low': c[3],
                    'close': c[4],
                    'volume': c[5]
                }
                for c in ohlcv
            ]
            
            # Cache result
            self._set_cache(cache_key, candles)
            
            logger.info(f"✅ Binance: {symbol} - {len(candles)} candles")
            return candles
            
        except Exception as e:
            logger.error(f"❌ Binance error {symbol}: {e}")
            return []
    
    async def get_stock_candles(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> List[Dict]:
        """
        Get stock candles from Finnhub
        RATE LIMITED: 60 req/min
        """
        if not self.finnhub.is_available():
            logger.error("Finnhub not available")
            return []
        
        # Check cache
        cache_key = self._get_cache_key('finnhub', symbol, timeframe)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info(f"📦 Cache hit: {symbol}")
            return cached
        
        try:
            # Wait for rate limit
            await self.rate_limiter.wait_finnhub()
            
            # Fetch from Finnhub
            candles = await self.finnhub.get_stock_candles(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if not candles:
                return []
            
            # Convert to standard format
            result = [
                {
                    'timestamp': c['time'] * 1000,  # to milliseconds
                    'open': c['open'],
                    'high': c['high'],
                    'low': c['low'],
                    'close': c['close'],
                    'volume': c['volume']
                }
                for c in candles
            ]
            
            # Cache result
            self._set_cache(cache_key, result)
            
            logger.info(f"✅ Finnhub: {symbol} - {len(result)} candles")
            return result
            
        except Exception as e:
            logger.error(f"❌ Finnhub error {symbol}: {e}")
            return []
    
    async def get_forex_candles(
        self,
        pair: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> List[Dict]:
        """
        Get forex candles from OANDA
        RATE LIMITED: ~100 req/20sec
        """
        if not self.oanda_token:
            logger.error("OANDA not configured")
            return []
        
        # Check cache
        cache_key = self._get_cache_key('oanda', pair, timeframe)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info(f"📦 Cache hit: {pair}")
            return cached
        
        try:
            # Wait for rate limit
            await self.rate_limiter.wait_oanda()
            
            # Convert pair format: EUR/USD -> EUR_USD
            oanda_pair = pair.replace('/', '_')
            
            # Map timeframe to OANDA granularity
            granularity_map = {
                '5m': 'M5',
                '15m': 'M15',
                '30m': 'M30',
                '1h': 'H1',
                '4h': 'H4',
                '1d': 'D',
            }
            granularity = granularity_map.get(timeframe, 'H1')
            
            import httpx
            
            headers = {'Authorization': f'Bearer {self.oanda_token}'}
            url = f"{self.oanda_url}/v3/instruments/{oanda_pair}/candles"
            params = {
                'count': limit,
                'granularity': granularity,
                'price': 'M'  # Mid prices
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    logger.error(f"OANDA error: {response.status_code}")
                    return []
                
                data = response.json()
                candles_data = data.get('candles', [])
                
                candles = [
                    {
                        'timestamp': int(datetime.fromisoformat(c['time'].replace('Z', '+00:00')).timestamp() * 1000),
                        'open': float(c['mid']['o']),
                        'high': float(c['mid']['h']),
                        'low': float(c['mid']['l']),
                        'close': float(c['mid']['c']),
                        'volume': c.get('volume', 0)
                    }
                    for c in candles_data
                    if c.get('complete', True)  # Solo candele complete
                ]
                
                # Cache result
                self._set_cache(cache_key, candles)
                
                logger.info(f"✅ OANDA: {pair} - {len(candles)} candles")
                return candles
                
        except Exception as e:
            logger.error(f"❌ OANDA error {pair}: {e}")
            return []
    
    async def get_candles(
        self,
        symbol: str,
        asset_type: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> List[Dict]:
        """
        Unified method to get candles for any asset type
        
        Args:
            symbol: Asset symbol
            asset_type: 'crypto', 'stock', 'forex', 'index', 'commodity'
            timeframe: Candle timeframe
            limit: Number of candles
        """
        if asset_type == 'crypto':
            return await self.get_crypto_candles(symbol, timeframe, limit)
        
        elif asset_type in ['stock', 'index', 'commodity', 'etf']:
            # All use Finnhub
            return await self.get_stock_candles(symbol, timeframe, limit)
        
        elif asset_type == 'forex':
            return await self.get_forex_candles(symbol, timeframe, limit)
        
        else:
            logger.error(f"Unknown asset type: {asset_type}")
            return []
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit usage"""
        now = time.time()
        
        finnhub_recent = len([
            t for t in self.rate_limiter.finnhub_calls 
            if now - t < self.rate_limiter.finnhub_window
        ])
        
        oanda_recent = len([
            t for t in self.rate_limiter.oanda_calls 
            if now - t < self.rate_limiter.oanda_window
        ])
        
        return {
            'finnhub': {
                'used': finnhub_recent,
                'max': self.rate_limiter.finnhub_max,
                'percentage': round((finnhub_recent / self.rate_limiter.finnhub_max) * 100, 1),
                'window_seconds': self.rate_limiter.finnhub_window
            },
            'oanda': {
                'used': oanda_recent,
                'max': self.rate_limiter.oanda_max,
                'percentage': round((oanda_recent / self.rate_limiter.oanda_max) * 100, 1),
                'window_seconds': self.rate_limiter.oanda_window
            },
            'cache_entries': len(self.cache)
        }


# Global instance
unified_market_service = UnifiedMarketDataService()

