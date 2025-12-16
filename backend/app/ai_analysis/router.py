"""
AI Analysis Router
Endpoints for Claude-powered market analysis
"""
from fastapi import APIRouter, Query, HTTPException
from app.ai_analysis.service import ai_service
from app.market_data.service import market_service

# Try to import intraday service
try:
    from app.intraday.service import intraday_service
    INTRADAY_AVAILABLE = True
except ImportError:
    INTRADAY_AVAILABLE = False

router = APIRouter()

@router.get("/analyze")
async def analyze_market(
    symbol: str = Query("BTC/USDT", description="Trading pair symbol"),
    timeframe: str = Query("1h", description="Chart timeframe for analysis"),
    asset_type: str = Query("crypto", description="Asset type"),
    exchange: str = Query("binance", description="Exchange name")
):
    """
    Get AI-powered market analysis using Claude Sonnet 4
    
    Analyzes current price, trends, patterns and provides:
    - Sentiment (Bullish/Bearish/Neutral)
    - Trading signals (BUY/SELL/HOLD)
    - Risk assessment
    - Actionable recommendations
    
    Requires ANTHROPIC_API_KEY environment variable
    """
    
    # Check if AI service available
    if not ai_service.is_available():
        return {
            "available": False,
            "message": "AI Analysis not configured. Add ANTHROPIC_API_KEY to enable."
        }
    
    try:
        # Fetch current price
        price_data = await market_service.get_price(symbol, exchange)
        
        # Fetch recent OHLCV for technical analysis
        try:
            if INTRADAY_AVAILABLE and timeframe == "15m":
                ohlcv_data = await intraday_service.get_15min_candles(
                    symbol, asset_type, limit=50
                )
            else:
                ohlcv_data = await market_service.get_ohlcv(
                    symbol, timeframe, limit=50, exchange=exchange
                )
        except:
            ohlcv_data = None
        
        # Get AI analysis
        analysis = await ai_service.analyze_market(
            symbol=symbol,
            current_price=price_data['price'],
            price_change_24h=price_data.get('change_24h', 0),
            volume_24h=price_data.get('volume_24h', 0),
            ohlcv_data=ohlcv_data,
            timeframe=timeframe
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Analysis failed: {str(e)}"
        )


@router.get("/status")
async def ai_status():
    """
    Check if AI analysis is available
    
    Returns status of Claude API integration
    """
    available = ai_service.is_available()
    
    return {
        "available": available,
        "model": "claude-sonnet-4-20250514" if available else None,
        "message": "AI Analysis ready" if available else "ANTHROPIC_API_KEY not configured",
        "cost_estimate": "~$0.03 per analysis" if available else None
    }
