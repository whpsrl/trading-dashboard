"""
Market Data API Router
NOW WITH 15MIN INTRADAY SUPPORT!
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.market_data.service import market_service
from app.intraday.service import intraday_service

# Try to import yahoo service (if exists)
try:
    from app.yahoo_finance.service import yahoo_service
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False

router = APIRouter()

@router.get("/price")
async def get_price(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTC/USDT, AAPL)"),
    asset_type: str = Query("crypto", description="Asset type: crypto, stock, forex, index, commodity"),
    exchange: str = Query("binance", description="Exchange for crypto")
):
    """
    Get current price for any asset type
    
    Supports:
    - Crypto: BTC/USDT, ETH/USDT (via Binance/CoinGecko)
    - Stocks: AAPL, TSLA, GOOGL (via Yahoo Finance if available)
    - Forex, Indices, Commodities (via Yahoo Finance if available)
    """
    try:
        if asset_type == "crypto":
            # Use crypto service
            price_data = await market_service.get_price(symbol, exchange)
        elif YAHOO_AVAILABLE:
            # Use Yahoo Finance for stocks/forex/etc
            price_data = await yahoo_service.get_price(symbol, asset_type)
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Asset type '{asset_type}' not supported. Only crypto available."
            )
        
        return price_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ohlcv")
async def get_ohlcv(
    symbol: str = Query(..., description="Trading pair symbol"),
    timeframe: str = Query("1h", description="Timeframe (15m, 1h, 4h, 1d, 1w)"),
    limit: int = Query(100, description="Number of candles", ge=1, le=1000),
    asset_type: str = Query("crypto", description="Asset type"),
    exchange: str = Query("binance", description="Exchange for crypto")
):
    """
    Get OHLCV candlestick data for any asset
    
    ✨ NEW: Now supports 15min intraday data!
    
    Timeframes:
    - 15m: Intraday (via Binance for crypto, Finnhub for others)
    - 1h, 4h, 1d, 1w: Standard (via existing services)
    
    Returns array of [timestamp, open, high, low, close, volume]
    """
    try:
        # ✨ NEW: 15min timeframe uses intraday service
        if timeframe == "15m":
            ohlcv_data = await intraday_service.get_15min_candles(
                symbol,
                asset_type,
                limit
            )
        else:
            # Standard timeframes: use existing services
            if asset_type == "crypto":
                ohlcv_data = await market_service.get_ohlcv(
                    symbol, timeframe, limit, exchange
                )
            elif YAHOO_AVAILABLE:
                ohlcv_data = await yahoo_service.get_ohlcv(
                    symbol, timeframe, limit, asset_type
                )
            else:
                raise HTTPException(
                    status_code=501,
                    detail=f"Timeframe '{timeframe}' for '{asset_type}' not supported"
                )
        
        return ohlcv_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Trading pair symbol"),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get order book (bids and asks) for a trading pair
    Currently only supports crypto
    """
    try:
        orderbook_data = await market_service.get_orderbook(symbol, exchange)
        return orderbook_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def get_trades(
    symbol: str = Query(..., description="Trading pair symbol"),
    limit: int = Query(50, description="Number of trades", ge=1, le=100),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get recent trades for a trading pair
    Currently only supports crypto
    """
    try:
        trades_data = await market_service.get_trades(symbol, limit, exchange)
        return trades_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_assets(
    query: str = Query(..., description="Search query"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type")
):
    """
    Search for assets by name or symbol
    
    Returns list of matching assets across all types
    """
    # Basic search implementation
    # For full database search, import from assets.database
    
    results = []
    query_lower = query.lower()
    
    # Popular assets for quick results
    popular = [
        {"symbol": "BTC/USDT", "name": "Bitcoin", "type": "crypto"},
        {"symbol": "ETH/USDT", "name": "Ethereum", "type": "crypto"},
        {"symbol": "AAPL", "name": "Apple", "type": "stock"},
        {"symbol": "TSLA", "name": "Tesla", "type": "stock"},
        {"symbol": "GOOGL", "name": "Alphabet", "type": "stock"},
        {"symbol": "MSFT", "name": "Microsoft", "type": "stock"},
        {"symbol": "^GSPC", "name": "S&P 500", "type": "index"},
        {"symbol": "^DJI", "name": "Dow Jones", "type": "index"},
        {"symbol": "GC=F", "name": "Gold", "type": "commodity"},
        {"symbol": "CL=F", "name": "Crude Oil", "type": "commodity"},
        {"symbol": "EUR/USD", "name": "Euro / US Dollar", "type": "forex"},
    ]
    
    for asset in popular:
        # Filter by type if specified
        if asset_type and asset["type"] != asset_type:
            continue
        
        # Match query
        if (query_lower in asset["symbol"].lower() or 
            query_lower in asset["name"].lower()):
            results.append(asset)
    
    return {
        "query": query,
        "asset_type": asset_type,
        "results": results[:20]  # Limit to 20 results
    }


@router.get("/info")
async def get_asset_info(
    symbol: str = Query(..., description="Asset symbol"),
    asset_type: str = Query("stock", description="Asset type")
):
    """
    Get detailed information about an asset
    
    Only available for stocks via Yahoo Finance
    """
    if not YAHOO_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Asset info not available - Yahoo Finance service not configured"
        )
    
    try:
        info = await yahoo_service.get_info(symbol, asset_type)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Frontend-compatible endpoints
# ========================

@router.get("/crypto/{symbol}")
async def get_crypto_data(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe"),
    limit: int = Query(100, description="Number of candles")
):
    """Get crypto OHLCV data - frontend compatible"""
    return await get_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
        asset_type="crypto",
        exchange="binance"
    )


@router.get("/forex/{symbol}")
async def get_forex_data(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe"),
    limit: int = Query(100, description="Number of candles")
):
    """Get forex OHLCV data - frontend compatible"""
    # Convert GBP_JPY to GBP/JPY format if needed
    if '_' in symbol:
        symbol = symbol.replace('_', '/')
    
    return await get_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
        asset_type="forex",
        exchange="yahoo"
    )


@router.get("/stock/{symbol}")
async def get_stock_data(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe"),
    limit: int = Query(100, description="Number of candles")
):
    """Get stock OHLCV data - frontend compatible"""
    return await get_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
        asset_type="stock",
        exchange="yahoo"
    )
