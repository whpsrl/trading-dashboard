"""
Yahoo Finance data fetcher for Commodities, Forex, Indices, Stocks
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class YahooFetcher:
    """Fetches market data from Yahoo Finance"""
    
    # Commodity symbols on Yahoo Finance
    COMMODITIES = {
        'GOLD': {'symbol': 'GC=F', 'name': 'Gold Futures', 'emoji': '🥇'},
        'OIL': {'symbol': 'CL=F', 'name': 'Crude Oil WTI', 'emoji': '🛢️'},
        'SILVER': {'symbol': 'SI=F', 'name': 'Silver Futures', 'emoji': '🥈'},
        'WHEAT': {'symbol': 'ZW=F', 'name': 'Wheat Futures', 'emoji': '🌾'},
    }
    
    # Forex pairs
    FOREX = {
        'EURUSD': {'symbol': 'EURUSD=X', 'name': 'EUR/USD', 'emoji': '💱'},
        'GBPUSD': {'symbol': 'GBPUSD=X', 'name': 'GBP/USD', 'emoji': '💱'},
        'USDJPY': {'symbol': 'USDJPY=X', 'name': 'USD/JPY', 'emoji': '💱'},
    }
    
    # Indices - Top 8 Global
    INDICES = {
        'SPX': {'symbol': '^GSPC', 'name': 'S&P 500', 'emoji': '🇺🇸'},
        'DJI': {'symbol': '^DJI', 'name': 'Dow Jones', 'emoji': '🇺🇸'},
        'NDX': {'symbol': '^IXIC', 'name': 'NASDAQ', 'emoji': '🇺🇸'},
        'DAX': {'symbol': '^GDAXI', 'name': 'DAX 40', 'emoji': '🇩🇪'},
        'FTSE': {'symbol': '^FTSE', 'name': 'FTSE 100', 'emoji': '🇬🇧'},
        'MIB': {'symbol': 'FTSEMIB.MI', 'name': 'FTSE MIB', 'emoji': '🇮🇹'},
        'N225': {'symbol': '^N225', 'name': 'Nikkei 225', 'emoji': '🇯🇵'},
        'HSI': {'symbol': '^HSI', 'name': 'Hang Seng', 'emoji': '🇭🇰'},
    }
    
    # Timeframe mapping (Yahoo format)
    TIMEFRAME_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '4h': '1h',  # Yahoo doesn't have 4h, we'll aggregate 1h data
        '1d': '1d',
    }
    
    def __init__(self):
        logger.info("✅ YahooFetcher initialized")
    
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = '4h', 
        limit: int = 100
    ) -> Optional[List]:
        """
        Fetch OHLCV data from Yahoo Finance
        Returns data in Binance-compatible format: [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            # Import yfinance here to avoid issues if not installed
            import yfinance as yf
            import pandas as pd
            
            logger.info(f"📊 Fetching {symbol} data from Yahoo Finance (TF: {timeframe})")
            
            # Get Yahoo timeframe
            yahoo_tf = self.TIMEFRAME_MAP.get(timeframe, '1h')
            
            # Calculate period based on limit and timeframe
            if timeframe == '4h':
                # For 4h, fetch 4x more 1h candles
                period_days = max(7, (limit * 4) // 24 + 1)
            elif timeframe == '1h':
                period_days = max(7, limit // 24 + 1)
            else:
                period_days = 30  # Default 1 month
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            df = await asyncio.to_thread(
                ticker.history,
                period=f'{period_days}d',
                interval=yahoo_tf
            )
            
            if df.empty:
                logger.warning(f"⚠️ No data returned for {symbol}")
                return None
            
            # If 4h timeframe, aggregate 1h data
            if timeframe == '4h':
                df = self._aggregate_to_4h(df)
            
            # Limit to requested number of candles
            df = df.tail(limit)
            
            # Convert to Binance-compatible format
            ohlcv = []
            for idx, row in df.iterrows():
                timestamp = int(idx.timestamp() * 1000)  # Convert to milliseconds
                ohlcv.append([
                    timestamp,
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    float(row['Volume'])
                ])
            
            logger.info(f"✅ Fetched {len(ohlcv)} candles for {symbol}")
            return ohlcv
            
        except ImportError:
            logger.error("❌ yfinance not installed. Run: pip install yfinance")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol} from Yahoo: {e}")
            return None
    
    def _aggregate_to_4h(self, df):
        """Aggregate 1h data to 4h candles"""
        try:
            import pandas as pd
            
            # Resample to 4h
            df_4h = df.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })
            
            # Remove rows with NaN (incomplete candles)
            df_4h = df_4h.dropna()
            
            return df_4h
        except Exception as e:
            logger.error(f"❌ Error aggregating to 4h: {e}")
            return df
    
    async def get_top_symbols(self, market_type: str = 'commodities', limit: int = 10) -> List[str]:
        """
        Get top symbols for a market type
        """
        if market_type == 'commodities':
            symbols = [v['symbol'] for v in self.COMMODITIES.values()]
        elif market_type == 'forex':
            symbols = [v['symbol'] for v in self.FOREX.values()]
        elif market_type == 'indices':
            symbols = [v['symbol'] for v in self.INDICES.values()]
        else:
            logger.warning(f"⚠️ Unknown market type: {market_type}")
            return []
        
        return symbols[:limit]
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information (name, emoji, etc.)"""
        # Check in all markets
        for market_dict in [self.COMMODITIES, self.FOREX, self.INDICES]:
            for key, info in market_dict.items():
                if info['symbol'] == symbol:
                    return info
        return None
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current/latest price for a symbol"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = await asyncio.to_thread(ticker.history, period='1d', interval='1m')
            
            if data.empty:
                return None
            
            return float(data['Close'].iloc[-1])
            
        except Exception as e:
            logger.error(f"❌ Error getting price for {symbol}: {e}")
            return None

