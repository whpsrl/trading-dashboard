"""
Market Data API Router
Endpoints for fetching market data, prices, OHLCV, orderbooks, etc.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.market_data.service import market_service

router = APIRouter()

@router.get("/price")
async def get_price(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTC/USDT)"),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get current price for a trading pair
    
    Returns real-time price data with 24h change, volume, etc.
    Falls back to CoinGecko if exchange is geo-blocked.
    """
    try:
        price_data = await market_service.get_price(symbol, exchange)
        return price_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlcv")
async def get_ohlcv(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTC/USDT)"),
    timeframe: str = Query("1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w)"),
    limit: int = Query(100, description="Number of candles to return", ge=1, le=1000),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get OHLCV (candlestick) data for charting
    
    Returns array of [timestamp, open, high, low, close, volume]
    """
    try:
        ohlcv_data = await market_service.get_ohlcv(symbol, timeframe, limit, exchange)
        return ohlcv_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTC/USDT)"),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get order book (bids and asks) for a trading pair
    
    Returns top 20 bids and asks with price and quantity
    """
    try:
        orderbook_data = await market_service.get_orderbook(symbol, exchange)
        return orderbook_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trades(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTC/USDT)"),
    limit: int = Query(50, description="Number of trades to return", ge=1, le=100),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get recent trades for a trading pair
    
    Returns list of recent trades with price, amount, side, timestamp
    """
    try:
        trades_data = await market_service.get_trades(symbol, limit, exchange)
        return trades_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
