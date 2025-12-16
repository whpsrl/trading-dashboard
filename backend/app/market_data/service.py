"""
Market Data Service
Handles fetching real-time and historical market data from various exchanges
Uses CoinGecko as fallback when exchanges are geo-blocked
"""
import ccxt
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        """Initialize exchange connections"""
        self.exchanges = {}
        
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
    
    def _get_price_from_coingecko(self, symbol: str) -> Optional[Dict]:
        """
        Fetch price from CoinGecko as fallback
        Works from any location without geo-restrictions
        """
        try:
            # Convert trading pair to CoinGecko format
            # BTC/USDT -> bitcoin, ETH/USDT -> ethereum, etc.
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
                return {
                    'symbol': symbol,
                    'price': coin_data.get('usd', 0),
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'coingecko'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching from CoinGecko: {str(e)}")
            return None
    
    async def get_price(self, symbol: str, exchange: str = "binance") -> Dict:
        """
        Get current price for a symbol
        Falls back to CoinGecko if exchange is geo-blocked
        """
        try:
            # Try to get from specified exchange first
            exchange_obj = self._get_exchange(exchange)
            ticker = exchange_obj.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['quoteVolume'],
                'change_24h': ticker['percentage'],
                'timestamp': ticker['timestamp'],
                'source': exchange
            }
            
        except ccxt.ExchangeError as e:
            # Check if it's a geo-restriction error
            if '451' in str(e) or 'restricted location' in str(e).lower():
                logger.warning(f"Exchange {exchange} geo-blocked, falling back to CoinGecko")
                coingecko_data = self._get_price_from_coingecko(symbol)
                if coingecko_data:
                    return coingecko_data
                raise Exception(f"Both {exchange} and CoinGecko failed for {symbol}")
            
            # Other exchange errors
            logger.error(f"Error fetching price from {exchange}: {str(e)}")
            # Try CoinGecko as fallback
            coingecko_data = self._get_price_from_coingecko(symbol)
            if coingecko_data:
                return coingecko_data
            raise
            
        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            # Try CoinGecko as last resort
            coingecko_data = self._get_price_from_coingecko(symbol)
            if coingecko_data:
                return coingecko_data
            raise
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = "1h",
        limit: int = 100,
        exchange: str = "binance"
    ) -> List[List]:
        """Get OHLCV (candlestick) data"""
        try:
            exchange_obj = self._get_exchange(exchange)
            ohlcv = exchange_obj.fetch_ohlcv(symbol, timeframe, limit=limit)
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
