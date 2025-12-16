"""
Market Data Service - CoinGecko Edition
Uses CoinGecko API (no geo-restrictions) instead of Binance
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        """Initialize with CoinGecko"""
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
        # Mapping common symbols to CoinGecko IDs
        self.symbol_to_id = {
            'BTC/USDT': 'bitcoin',
            'ETH/USDT': 'ethereum',
            'BNB/USDT': 'binancecoin',
            'SOL/USDT': 'solana',
            'XRP/USDT': 'ripple',
            'ADA/USDT': 'cardano',
            'DOGE/USDT': 'dogecoin',
            'AVAX/USDT': 'avalanche-2',
            'TRX/USDT': 'tron',
            'DOT/USDT': 'polkadot',
            'MATIC/USDT': 'matic-network',
            'LINK/USDT': 'chainlink',
            'SHIB/USDT': 'shiba-inu',
            'UNI/USDT': 'uniswap',
            'LTC/USDT': 'litecoin',
            'ATOM/USDT': 'cosmos',
            'XLM/USDT': 'stellar',
            'ETC/USDT': 'ethereum-classic',
            'BCH/USDT': 'bitcoin-cash',
            'FIL/USDT': 'filecoin',
        }
        
        logger.info("✅ Market data service initialized (CoinGecko)")
    
    async def get_price(self, symbol: str, exchange: str = "binance") -> Dict:
        """
        Get current price for crypto using CoinGecko
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            exchange: Ignored (kept for compatibility)
        
        Returns:
            Price data with change, volume, etc.
        """
        try:
            coin_id = self.symbol_to_id.get(symbol, 'bitcoin')
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
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
                    'market_cap': coin_data.get('usd_market_cap', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'coingecko',
                    'exchange': 'coingecko'
                }
            else:
                raise Exception(f"Coin {coin_id} not found")
                
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            # Return dummy data to avoid crashes
            return {
                'symbol': symbol,
                'price': 0,
                'change_24h': 0,
                'volume_24h': 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'error',
                'error': str(e)
            }
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        exchange: str = "binance"
    ) -> List[List]:
        """
        Get OHLCV candlestick data from CoinGecko
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            timeframe: Candle timeframe (1h, 4h, 1d, etc.)
            limit: Number of candles
            exchange: Ignored (kept for compatibility)
        
        Returns:
            Array of [timestamp, open, high, low, close, volume]
        """
        try:
            coin_id = self.symbol_to_id.get(symbol, 'bitcoin')
            
            # Map timeframe to days
            timeframe_to_days = {
                '1h': 1,
                '4h': 4,
                '1d': 30,
                '1w': 90
            }
            days = timeframe_to_days.get(timeframe, 7)
            
            # Get market chart data
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if timeframe in ['1h', '4h'] else 'daily'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'prices' in data:
                prices = data['prices'][-limit:]  # Get last N candles
                
                # Convert to OHLCV format (simplified)
                ohlcv = []
                for price_point in prices:
                    timestamp = price_point[0]
                    price = price_point[1]
                    
                    # Simplified: use same price for OHLC
                    ohlcv.append([
                        timestamp,
                        price,  # open
                        price * 1.001,  # high (slightly above)
                        price * 0.999,  # low (slightly below)
                        price,  # close
                        0  # volume (not available in simple endpoint)
                    ])
                
                logger.info(f"✅ Fetched {len(ohlcv)} candles for {symbol} from CoinGecko")
                return ohlcv
            else:
                raise Exception("No price data available")
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            # Return empty array to avoid crashes
            return []
    
    async def get_orderbook(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> Dict:
        """Get order book - Not available in CoinGecko free tier"""
        return {
            'symbol': symbol,
            'bids': [],
            'asks': [],
            'timestamp': datetime.now().timestamp(),
            'message': 'Order book not available with CoinGecko'
        }
    
    async def get_trades(
        self,
        symbol: str,
        limit: int = 50,
        exchange: str = "binance"
    ) -> List[Dict]:
        """Get recent trades - Not available in CoinGecko free tier"""
        return []


# Global service instance
market_service = MarketDataService()
