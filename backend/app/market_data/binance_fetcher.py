"""
Binance Data Fetcher
Fetches top 30 crypto pairs by 24h volume and OHLCV data
"""
import ccxt
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class BinanceFetcher:
    def __init__(self, api_key: str = "", secret: str = ""):
        """Initialize Binance client"""
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        logger.info("✅ Binance fetcher initialized")
    
    async def get_top_pairs(self, limit: int = 30) -> List[str]:
        """
        Get top N crypto pairs by 24h volume
        Returns: ['BTC/USDT', 'ETH/USDT', ...]
        """
        try:
            # Fetch all tickers
            tickers = await asyncio.to_thread(self.exchange.fetch_tickers)
            
            # Filter USDT pairs only
            usdt_pairs = {
                symbol: ticker for symbol, ticker in tickers.items()
                if '/USDT' in symbol and ticker.get('quoteVolume')
            }
            
            # Sort by 24h volume (descending)
            sorted_pairs = sorted(
                usdt_pairs.items(),
                key=lambda x: x[1]['quoteVolume'],
                reverse=True
            )
            
            # Get top N
            top_pairs = [pair[0] for pair in sorted_pairs[:limit]]
            
            logger.info(f"📊 Top {limit} pairs by volume: {top_pairs[:5]}...")
            return top_pairs
            
        except Exception as e:
            logger.error(f"❌ Error fetching top pairs: {e}")
            # Fallback to hardcoded top coins
            return [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
                'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT',
                'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'NEAR/USDT',
                'ALGO/USDT', 'FIL/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT',
                'ICP/USDT', 'VET/USDT', 'HBAR/USDT', 'GRT/USDT', 'AAVE/USDT',
                'EOS/USDT', 'FTM/USDT', 'SAND/USDT', 'MANA/USDT', 'AXS/USDT'
            ][:limit]
    
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '15m',
        limit: int = 300
    ) -> Optional[List[List]]:
        """
        Fetch OHLCV candles
        Returns: [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                timeframe,
                limit=limit
            )
            logger.info(f"✅ Fetched {len(ohlcv)} candles for {symbol} {timeframe}")
            return ohlcv
            
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol} {timeframe}: {e}")
            return None
    
    async def fetch_multi_timeframe(
        self,
        symbol: str,
        timeframes: List[str] = ['15m', '1h', '4h']
    ) -> Dict[str, List]:
        """
        Fetch OHLCV for multiple timeframes
        Returns: {'15m': [...], '1h': [...], '4h': [...]}
        """
        results = {}
        
        for tf in timeframes:
            ohlcv = await self.fetch_ohlcv(symbol, tf, limit=300)
            if ohlcv:
                results[tf] = ohlcv
        
        return results

