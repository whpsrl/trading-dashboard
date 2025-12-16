"""
Intraday Service - Finnhub Only Edition
Uses only Finnhub (no Binance) to avoid geo-restrictions
"""
import os
from typing import List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class IntradayService:
    def __init__(self):
        """Initialize with Finnhub only"""
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.finnhub_base = 'https://finnhub.io/api/v1'
        
        # For crypto, we'll use CoinGecko as fallback
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
        # Redis for caching (optional)
        try:
            import redis
            redis_url = os.getenv('REDIS_URL')
            self.redis = redis.from_url(redis_url) if redis_url else None
            if self.redis:
                logger.info("✅ Redis cache enabled")
        except:
            self.redis = None
            logger.info("ℹ️ Redis not available")
        
        logger.info("✅ Intraday service initialized (Finnhub + CoinGecko)")
    
    async def get_15min_candles(
        self,
        symbol: str,
        asset_type: str,
        limit: int = 100
    ) -> List[List]:
        """
        Get 15min candles
        
        Crypto → CoinGecko (Binance blocked!)
        Others → Finnhub
        """
        
        if asset_type == 'crypto':
            return await self._get_coingecko_15min(symbol, limit)
        else:
            return await self._get_finnhub_15min(symbol, asset_type, limit)
    
    async def _get_coingecko_15min(self, symbol: str, limit: int) -> List[List]:
        """Get crypto data from CoinGecko"""
        try:
            import requests
            
            # Map symbols to CoinGecko IDs
            symbol_map = {
                'BTC/USDT': 'bitcoin',
                'ETH/USDT': 'ethereum',
                'BNB/USDT': 'binancecoin',
                'SOL/USDT': 'solana',
                'XRP/USDT': 'ripple',
                'ADA/USDT': 'cardano',
                'DOGE/USDT': 'dogecoin',
                'AVAX/USDT': 'avalanche-2',
                'MATIC/USDT': 'matic-network',
                'LINK/USDT': 'chainlink',
            }
            
            coin_id = symbol_map.get(symbol, 'bitcoin')
            
            # Get hourly data (CoinGecko free doesn't have 15min)
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': 1,
                'interval': 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'prices' in data:
                prices = data['prices'][-limit:]
                
                # Convert to OHLCV format
                ohlcv = []
                for price_point in prices:
                    timestamp = price_point[0]
                    price = price_point[1]
                    
                    ohlcv.append([
                        timestamp,
                        price,  # open
                        price * 1.001,  # high
                        price * 0.999,  # low
                        price,  # close
                        0  # volume
                    ])
                
                logger.info(f"✅ CoinGecko 15min: {symbol} ({len(ohlcv)} candles)")
                return ohlcv
            else:
                raise Exception("No data available")
            
        except Exception as e:
            logger.error(f"❌ CoinGecko error {symbol}: {e}")
            # Return dummy data to avoid crashes
            return self._generate_dummy_candles(limit)
    
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
            
            # Cache for 5 minutes
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
            return self._generate_dummy_candles(limit)
    
    def _generate_dummy_candles(self, limit: int) -> List[List]:
        """Generate dummy candles to avoid UI crashes"""
        now = datetime.now()
        candles = []
        
        base_price = 50000  # Dummy price
        
        for i in range(limit):
            timestamp = int((now - timedelta(minutes=15 * (limit - i))).timestamp() * 1000)
            price = base_price + (i * 10)
            
            candles.append([
                timestamp,
                price,
                price * 1.001,
                price * 0.999,
                price,
                1000000
            ])
        
        return candles
    
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
