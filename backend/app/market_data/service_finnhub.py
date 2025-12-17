"""
Finnhub service for stocks data with rate limiting
FREE plan: 60 calls/minute
"""
import httpx
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter: max 60 calls per minute"""
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if we can make a call without exceeding rate limit"""
        now = time.time()
        # Remove calls older than time_window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a call"""
        self.calls.append(time.time())
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        while not self.can_make_call():
            time.sleep(0.5)  # Wait 500ms and check again
        self.record_call()


class FinnhubService:
    """Service for fetching stock data from Finnhub"""
    
    def __init__(self):
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
        self.rate_limiter = RateLimiter(max_calls=58, time_window=60)  # 58 to be safe
        
        if not self.api_key:
            logger.warning("⚠️ FINNHUB_API_KEY not set - stock data disabled")
    
    def is_available(self) -> bool:
        """Check if Finnhub is configured"""
        return bool(self.api_key)
    
    async def get_stock_candles(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get stock candlestick data from Finnhub
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            timeframe: '5m', '15m', '1h', '4h', '1d'
            limit: Number of candles to return (max 1000)
        
        Returns:
            List of OHLCV dictionaries
        """
        if not self.is_available():
            raise Exception("Finnhub API key not configured")
        
        # Convert timeframe to Finnhub resolution
        resolution_map = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '4h': '240',
            '1d': 'D',
            '1w': 'W',
            '1M': 'M'
        }
        
        resolution = resolution_map.get(timeframe, '60')
        
        # Calculate time range
        now = int(datetime.now().timestamp())
        
        # Calculate how far back to go based on timeframe and limit
        minutes_per_candle = {
            '1': 1,
            '5': 5,
            '15': 15,
            '30': 30,
            '60': 60,
            '240': 240,
            'D': 1440,
            'W': 10080,
            'M': 43200
        }
        
        minutes_back = minutes_per_candle.get(resolution, 60) * limit
        start_time = now - (minutes_back * 60)
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/candle",
                    params={
                        'symbol': symbol.upper(),
                        'resolution': resolution,
                        'from': start_time,
                        'to': now,
                        'token': self.api_key
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Finnhub API error: {response.status_code} - {response.text}")
                    raise Exception(f"Finnhub API error: {response.status_code}")
                
                data = response.json()
                
                # Check if data is valid
                if data.get('s') == 'no_data':
                    logger.warning(f"No data available for {symbol}")
                    return []
                
                if data.get('s') != 'ok':
                    logger.error(f"Finnhub returned status: {data.get('s')}")
                    return []
                
                # Convert to our format
                candles = []
                timestamps = data.get('t', [])
                opens = data.get('o', [])
                highs = data.get('h', [])
                lows = data.get('l', [])
                closes = data.get('c', [])
                volumes = data.get('v', [])
                
                for i in range(len(timestamps)):
                    candles.append({
                        'timestamp': datetime.fromtimestamp(timestamps[i]).isoformat(),
                        'time': timestamps[i],
                        'open': opens[i],
                        'high': highs[i],
                        'low': lows[i],
                        'close': closes[i],
                        'volume': volumes[i]
                    })
                
                # Return last 'limit' candles
                candles = candles[-limit:] if len(candles) > limit else candles
                
                logger.info(f"✅ Fetched {len(candles)} candles for {symbol} from Finnhub")
                return candles
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub API timeout for {symbol}")
            raise Exception("Finnhub API timeout")
        except Exception as e:
            logger.error(f"Finnhub error: {e}")
            raise


# Global instance
finnhub_service = FinnhubService()
