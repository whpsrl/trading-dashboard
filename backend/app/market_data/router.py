"""Market Data API Endpoints"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List

from app.market_data.service import market_service

router = APIRouter()

@router.get("/price")
async def get_price(symbol: str, exchange: str) -> Dict:
    """
    Get current price for an asset
    
    Examples:
    - /api/market/price?symbol=BTC/USDT&exchange=binance
    - /api/market/price?symbol=EUR/USD&exchange=oanda
    - /api/market/price?symbol=AAPL&exchange=finnhub
    """
    try:
        price_data = await market_service.get_price(symbol, exchange)
        return price_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlcv")
async def get_ohlcv(
    symbol: str,
    exchange: str,
    timeframe: str = "1h",
    limit: int = 100
) -> List[Dict]:
    """
    Get OHLCV candlestick data
    
    Example:
    - /api/market/ohlcv?symbol=BTC/USDT&exchange=binance&timeframe=1h&limit=100
    """
    try:
        candles = await market_service.get_ohlcv(symbol, exchange, timeframe, limit)
        return candles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_connection():
    """Test market data connections"""
    results = {}
    
    # Test Binance
    try:
        btc = await market_service.get_price("BTC/USDT", "binance")
        results['binance'] = {"status": "✅ Connected", "btc_price": btc['price']}
    except Exception as e:
        results['binance'] = {"status": "❌ Error", "error": str(e)}
    
    # Test OANDA (if configured)
    try:
        eur = await market_service.get_price("EUR/USD", "oanda")
        results['oanda'] = {"status": "✅ Connected", "eur_usd": eur['price']}
    except Exception as e:
        results['oanda'] = {"status": "❌ Error", "error": str(e)}
    
    # Test Finnhub (if configured)
    try:
        aapl = await market_service.get_price("AAPL", "finnhub")
        results['finnhub'] = {"status": "✅ Connected", "aapl_price": aapl['price']}
    except Exception as e:
        results['finnhub'] = {"status": "❌ Error", "error": str(e)}
    
    return results
