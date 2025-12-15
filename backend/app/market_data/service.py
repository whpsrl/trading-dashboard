"""Market Data Service - Binance, OANDA, Finnhub"""
import ccxt
import requests
from typing import Dict, List
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class MarketDataService:
    """Unified market data aggregator"""
    
    def __init__(self):
        # Binance
        self.binance = ccxt.binance({
            'enableRateLimit': True
        })
        
        # OANDA
        self.oanda_token = settings.OANDA_API_TOKEN
        self.oanda_url = "https://api-fxpractice.oanda.com"
        
        # Finnhub
        self.finnhub_key = settings.FINNHUB_API_KEY
    
    async def get_price(self, symbol: str, exchange: str) -> Dict:
        """Get current price"""
        try:
            if exchange == "binance":
                return await self._get_binance_price(symbol)
            elif exchange == "oanda":
                return await self._get_oanda_price(symbol)
            elif exchange == "finnhub":
                return await self._get_finnhub_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            raise
    
    async def _get_binance_price(self, symbol: str) -> Dict:
        """Get crypto price from Binance"""
        ticker = self.binance.fetch_ticker(symbol)
        return {
            "symbol": symbol,
            "exchange": "binance",
            "price": ticker['last'],
            "volume_24h": ticker['quoteVolume'],
            "change_24h": ticker['percentage'],
            "timestamp": ticker['timestamp']
        }
    
    async def _get_oanda_price(self, pair: str) -> Dict:
        """Get forex price from OANDA"""
        oanda_pair = pair.replace('/', '_')
        
        headers = {'Authorization': f'Bearer {self.oanda_token}'}
        url = f"{self.oanda_url}/v3/instruments/{oanda_pair}/candles"
        params = {'count': 1, 'granularity': 'M1'}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        candle = response.json()['candles'][0]
        return {
            "symbol": pair,
            "exchange": "oanda",
            "price": float(candle['mid']['c']),
            "timestamp": candle['time']
        }
    
    async def _get_finnhub_price(self, symbol: str) -> Dict:
        """Get stock price from Finnhub"""
        url = 'https://finnhub.io/api/v1/quote'
        params = {'symbol': symbol, 'token': self.finnhub_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            "symbol": symbol,
            "exchange": "finnhub",
            "price": data['c'],
            "change": data['d'],
            "change_percent": data['dp'],
            "timestamp": data['t'] * 1000
        }
    
    async def get_ohlcv(self, symbol: str, exchange: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """Get OHLCV candlestick data"""
        try:
            if exchange == "binance":
                ohlcv = self.binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                return [{
                    'timestamp': c[0],
                    'open': c[1],
                    'high': c[2],
                    'low': c[3],
                    'close': c[4],
                    'volume': c[5]
                } for c in ohlcv]
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            raise

# Singleton instance
market_service = MarketDataService()
