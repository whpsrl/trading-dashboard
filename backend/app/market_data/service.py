"""
Smart 15min Intraday Data Strategy
Combines Binance (crypto) + Finnhub (stocks/forex/commodities)
"""
import os
from typing import Dict, List
import ccxt  # For Binance
import requests  # For Finnhub
from datetime import datetime, timedelta
import redis
import json

class IntradayDataService:
    def __init__(self):
        """Initialize Binance and Finnhub"""
        # Binance for crypto (GRATIS)
        self.binance = ccxt.binance()
        
        # Finnhub for stocks/forex/commodities (GRATIS)
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'your_free_key_here')
        self.finnhub_base = 'https://finnhub.io/api/v1'
        
        # Redis for caching
        redis_url = os.getenv('REDIS_URL')
        self.redis = redis.from_url(redis_url) if redis_url else None
        
        print("✅ Intraday service initialized (Binance + Finnhub)")
    
    async def get_15min_candles(
        self,
        symbol: str,
        asset_type: str,
        limit: int = 100
    ) -> List[List]:
        """
        Get 15min candles intelligently
        
        Crypto → Binance (always fresh, free)
        Others → Finnhub (with smart caching)
        """
        
        if asset_type == 'crypto':
            return await self._get_binance_15min(symbol, limit)
        else:
            return await self._get_finnhub_15min(symbol, asset_type, limit)
    
    async def _get_binance_15min(self, symbol: str, limit: int) -> List[List]:
        """
        Get 15min crypto data from Binance
        
        FREE, UNLIMITED, EXCELLENT quality!
        """
        try:
            # Binance symbol format: BTC/USDT → BTCUSDT
            binance_symbol = symbol.replace('/', '')
            
            # Fetch OHLCV
            ohlcv = self.binance.fetch_ohlcv(
                binance_symbol,
                timeframe='15m',
                limit=limit
            )
            
            # Format: [timestamp, open, high, low, close, volume]
            return ohlcv
            
        except Exception as e:
            print(f"Binance 15min error for {symbol}: {e}")
            raise
    
    async def _get_finnhub_15min(
        self,
        symbol: str,
        asset_type: str,
        limit: int
    ) -> List[List]:
        """
        Get 15min data from Finnhub with smart caching
        
        Strategy:
        - Check cache first (5 min TTL)
        - If cache miss, fetch from Finnhub
        - Cache result for 5 minutes
        - This reduces API calls by ~95%
        """
        
        # Check cache
        cache_key = f"finnhub:15m:{symbol}"
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"✅ Cache HIT: {symbol} (15min)")
                return json.loads(cached)
        
        # Cache miss - fetch from Finnhub
        print(f"🌐 Fetching {symbol} from Finnhub...")
        
        try:
            # Convert symbol to Finnhub format
            finnhub_symbol = self._convert_to_finnhub_symbol(symbol, asset_type)
            
            # Calculate time range (last 100 candles × 15min)
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=15 * limit)
            
            # Finnhub candle endpoint
            url = f"{self.finnhub_base}/stock/candle"
            params = {
                'symbol': finnhub_symbol,
                'resolution': '15',  # 15 minute candles
                'from': int(start_time.timestamp()),
                'to': int(end_time.timestamp()),
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('s') != 'ok':
                raise Exception(f"Finnhub error: {data}")
            
            # Convert to our format: [timestamp, open, high, low, close, volume]
            ohlcv = []
            for i in range(len(data['t'])):
                ohlcv.append([
                    data['t'][i] * 1000,  # timestamp in ms
                    data['o'][i],          # open
                    data['h'][i],          # high
                    data['l'][i],          # low
                    data['c'][i],          # close
                    data['v'][i]           # volume
                ])
            
            # Cache for 5 minutes
            if self.redis:
                self.redis.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(ohlcv)
                )
            
            return ohlcv
            
        except Exception as e:
            print(f"Finnhub 15min error for {symbol}: {e}")
            raise
    
    def _convert_to_finnhub_symbol(self, symbol: str, asset_type: str) -> str:
        """Convert our symbol format to Finnhub format"""
        
        if asset_type == 'stock':
            return symbol  # AAPL → AAPL
        
        elif asset_type == 'forex':
            # EUR/USD → OANDA:EUR_USD
            base, quote = symbol.split('/')
            return f"OANDA:{base}_{quote}"
        
        elif asset_type == 'commodity':
            # Gold futures mapping
            commodity_map = {
                'GC=F': 'COMEX:GC1!',  # Gold
                'CL=F': 'NYMEX:CL1!',  # Crude Oil
                'SI=F': 'COMEX:SI1!',  # Silver
            }
            return commodity_map.get(symbol, symbol)
        
        elif asset_type == 'index':
            # ^GSPC → .SPX (Finnhub uses different format)
            index_map = {
                '^GSPC': '.SPX',
                '^DJI': '.DJI',
                '^IXIC': '.IXIC',
            }
            return index_map.get(symbol, symbol)
        
        return symbol
    
    async def get_watchlist_updates(self, watchlist: List[Dict]) -> Dict:
        """
        Update entire watchlist efficiently
        
        Called every 15 minutes for user's watchlist
        
        Returns: {symbol: price_data}
        """
        results = {}
        
        for asset in watchlist:
            try:
                candles = await self.get_15min_candles(
                    asset['symbol'],
                    asset['type'],
                    limit=1  # Only need latest candle
                )
                
                if candles:
                    latest = candles[-1]
                    results[asset['symbol']] = {
                        'price': latest[4],  # close
                        'high': latest[2],
                        'low': latest[3],
                        'volume': latest[5],
                        'timestamp': latest[0]
                    }
            except Exception as e:
                print(f"Error updating {asset['symbol']}: {e}")
                continue
        
        return results


# Global service instance
intraday_service = IntradayDataService()


# USAGE EXAMPLE:
"""
# Crypto (Binance - always fresh):
btc_candles = await intraday_service.get_15min_candles('BTC/USDT', 'crypto', 100)

# Stock (Finnhub - cached 5min):
aapl_candles = await intraday_service.get_15min_candles('AAPL', 'stock', 100)

# Watchlist update (every 15min):
watchlist = [
    {'symbol': 'BTC/USDT', 'type': 'crypto'},
    {'symbol': 'AAPL', 'type': 'stock'},
    {'symbol': 'EUR/USD', 'type': 'forex'},
]
updates = await intraday_service.get_watchlist_updates(watchlist)
"""
