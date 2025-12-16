"""
Intraday Service - 15min Candles
Binance (crypto) + Finnhub (stocks/forex/commodities)
"""
import os
from typing import List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class IntradayService:
    def __init__(self):
        """Initialize Binance and Finnhub"""
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.finnhub_base = 'https://finnhub.io/api/v1'
        
        # Try to import ccxt for Binance
        try:
            import ccxt
            self.binance = ccxt.binance()
            logger.info("✅ Binance initialized (ccxt)")
        except ImportError:
            self.binance = None
            logger.warning("⚠️ ccxt not installed - crypto 15min unavailable")
        
        # Redis for caching (optional)
        try:
            import redis
            redis_url = os.getenv('REDIS_URL')
            self.redis = redis.from_url(redis_url) if redis_url else None
            if self.redis:
                logger.info("✅ Redis cache enabled")
        except:
            self.redis = None
            logger.info("ℹ️ Redis not available - no caching")
        
        logger.info("✅ Intraday service initialized")
    
    async def get_15min_candles(
        self,
        symbol: str,
        asset_type: str,
        limit: int = 100
    ) -> List[List]:
        """
        Get 15min candles
        
        Crypto → Binance
        Others → Finnhub
        """
        if asset_type == 'crypto':
            return await self._get_binance_15min(symbol, limit)
        else:
            return await self._get_finnhub_15min(symbol, asset_type, limit)
    
    async def _get_binance_15min(self, symbol: str, limit: int) -> List[List]:
        """Get 15min crypto from Binance"""
        if not self.binance:
            raise Exception("Binance not available - install ccxt")
        
        try:
            # BTC/USDT → BTCUSDT
            binance_symbol = symbol.replace('/', '')
            
            # Fetch OHLCV
            ohlcv = self.binance.fetch_ohlcv(
                binance_symbol,
                timeframe='15m',
                limit=limit
            )
            
            logger.info(f"✅ Binance 15min: {symbol} ({len(ohlcv)} candles)")
            return ohlcv
            
        except Exception as e:
            logger.error(f"❌ Binance error {symbol}: {e}")
            raise
    
    async def _get_finnhub_15min(
        self,
        symbol: str,
        asset_type: str,
        limit: int
    ) -> List[List]:
        """Get 15min from Finnhub with cache"""
        
        # Check cache (5 min TTL)
        cache_key = f"finnhub:15m:{symbol}"
        if self.redis:
            try:
                import json
                cached = self.redis.get(cache_key)
                if cached:
                    logger.info(f"✅ Cache HIT: {symbol}")
                    return json.loads(cached)
            except:
                pass
        
        # Fetch from Finnhub
        logger.info(f"🌐 Fetching {symbol} from Finnhub...")
        
        try:
            import requests
            
            # Convert symbol
            finnhub_symbol = self._convert_symbol(symbol, asset_type)
            
            # Time range
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=15 * limit)
            
            # API call
            url = f"{self.finnhub_base}/stock/candle"
            params = {
                'symbol': finnhub_symbol,
                'resolution': '15',
                'from': int(start_time.timestamp()),
                'to': int(end_time.timestamp()),
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('s') != 'ok':
                raise Exception(f"Finnhub error: {data.get('s', 'unknown')}")
            
            # Convert to format: [timestamp_ms, open, high, low, close, volume]
            ohlcv = []
            for i in range(len(data['t'])):
                ohlcv.append([
                    data['t'][i] * 1000,  # ms
                    data['o'][i],
                    data['h'][i],
                    data['l'][i],
                    data['c'][i],
                    data['v'][i]
                ])
            
            # Cache 5 minutes
            if self.redis:
                try:
                    import json
                    self.redis.setex(cache_key, 300, json.dumps(ohlcv))
                except:
                    pass
            
            logger.info(f"✅ Finnhub 15min: {symbol} ({len(ohlcv)} candles)")
            return ohlcv
            
        except Exception as e:
            logger.error(f"❌ Finnhub error {symbol}: {e}")
            raise
    
    def _convert_symbol(self, symbol: str, asset_type: str) -> str:
        """Convert to Finnhub format"""
        
        if asset_type == 'stock':
            return symbol  # AAPL → AAPL
        
        elif asset_type == 'forex':
            # EUR/USD → OANDA:EUR_USD
            base, quote = symbol.split('/')
            return f"OANDA:{base}_{quote}"
        
        elif asset_type == 'commodity':
            # Map common commodities
            commodity_map = {
                'GC=F': 'COMEX:GC1!',  # Gold
                'CL=F': 'NYMEX:CL1!',  # Oil
                'SI=F': 'COMEX:SI1!',  # Silver
                'NG=F': 'NYMEX:NG1!',  # Natural Gas
            }
            return commodity_map.get(symbol, symbol)
        
        elif asset_type == 'index':
            # Map indices
            index_map = {
                '^GSPC': '.SPX',
                '^DJI': '.DJI',
                '^IXIC': '.IXIC',
            }
            return index_map.get(symbol, symbol)
        
        return symbol


# Global instance
intraday_service = IntradayService()
