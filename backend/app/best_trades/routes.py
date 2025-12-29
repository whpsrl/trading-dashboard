"""
Best Trades API Routes
Endpoint per trovare le migliori opportunità di trading
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from .service import best_trades_service
from .ai_only_service import ai_only_service
from ..market_data.unified_service import unified_market_service
from ..market_data.market_universe import get_scan_symbols, SCAN_PRESETS

router = APIRouter()
logger = logging.getLogger(__name__)


class TradeOpportunity(BaseModel):
    symbol: str
    exchange: str
    timestamp: str
    score: float
    direction: str
    confidence: float
    current_price: float
    trade_levels: Dict
    confluences: List[str]
    warnings: List[str]
    recommendation: str
    ai_insights: Optional[Dict] = None


class BestTradesResponse(BaseModel):
    success: bool
    count: int
    opportunities: List[TradeOpportunity]
    scan_time: str
    message: Optional[str] = None


@router.get("/analyze/{symbol}")
async def analyze_single_symbol(
    symbol: str,
    exchange: str = Query("binance", description="Exchange to use"),
    timeframe: str = Query("1h", description="Candle timeframe"),
    limit: int = Query(200, description="Number of candles")
):
    """
    Analizza un singolo simbolo per opportunità di trading
    
    Returns:
        Analisi completa con score, indicatori, livelli di trading, AI insights
    """
    try:
        logger.info(f"🔍 Analyzing {symbol} on {exchange}...")
        
        # Fetch OHLCV data
        ohlcv_data = await market_service.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            exchange=exchange
        )
        
        if not ohlcv_data or len(ohlcv_data) < 50:
            raise HTTPException(
                status_code=404,
                detail=f"Not enough data for {symbol}"
            )
        
        # Convert to candle format
        candles = []
        for candle in ohlcv_data:
            candles.append({
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5] if len(candle) > 5 else 0
            })
        
        # Analyze
        analysis = await best_trades_service.analyze_symbol(
            symbol=symbol,
            candles=candles,
            exchange=exchange
        )
        
        if not analysis:
            raise HTTPException(
                status_code=500,
                detail="Analysis failed"
            )
        
        return {
            "success": True,
            "data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan", response_model=BestTradesResponse)
async def scan_market_for_best_trades(
    preset: str = Query("quick", description="Scan preset: quick/balanced/full"),
    timeframe: str = Query("1h", description="Candle timeframe"),
    min_score: float = Query(60, ge=0, le=100, description="Minimum score threshold")
):
    """
    SIMPLIFIED SCAN - ONLY BINANCE CRYPTO
    
    Presets:
    - quick: 10 crypto (~15 seconds)
    - balanced: 20 crypto (~30 seconds)
    - full: 30 crypto (~45 seconds)
    """
    try:
        from datetime import datetime
        import asyncio
        
        logger.info(f"🚀 Starting {preset} crypto scan: min_score={min_score}")
        
        # TOP 50 CRYPTO BY MARKET CAP (ordinate per importanza)
        TOP_50_MARKETCAP = [
            # Top 10
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
            "ADA/USDT", "DOGE/USDT", "TRX/USDT", "TON/USDT", "LINK/USDT",
            # 11-20
            "AVAX/USDT", "SHIB/USDT", "DOT/USDT", "MATIC/USDT", "LTC/USDT",
            "BCH/USDT", "UNI/USDT", "NEAR/USDT", "ICP/USDT", "APT/USDT",
            # 21-30
            "ATOM/USDT", "FIL/USDT", "ARB/USDT", "OP/USDT", "VET/USDT",
            "IMX/USDT", "HBAR/USDT", "STX/USDT", "ALGO/USDT", "GRT/USDT",
            # 31-40
            "AAVE/USDT", "EOS/USDT", "FTM/USDT", "XTZ/USDT", "SAND/USDT",
            "MANA/USDT", "THETA/USDT", "AXS/USDT", "RUNE/USDT", "KAVA/USDT",
            # 41-50
            "CHZ/USDT", "ZIL/USDT", "ENJ/USDT", "1INCH/USDT", "CRV/USDT",
            "COMP/USDT", "SNX/USDT", "SUSHI/USDT", "YFI/USDT", "BAT/USDT"
        ]
        
        crypto_symbols = {
            'quick': TOP_50_MARKETCAP[:10],      # Top 10 (~15 sec)
            'balanced': TOP_50_MARKETCAP[:20],   # Top 20 (~30 sec)
            'full': TOP_50_MARKETCAP[:25]        # Top 25 (~45 sec, stabile!)
        }
        
        symbols = crypto_symbols.get(preset, crypto_symbols['quick'])
        logger.info(f"📊 Scanning {len(symbols)} crypto...")
        
        # Fetch data function - ONLY BINANCE
        async def fetch_candles(symbol: str, asset_type: str):
            try:
                candles = await unified_market_service.get_candles(
                    symbol=symbol,
                    asset_type='crypto',
                    timeframe=timeframe,
                    limit=200
                )
                return candles
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                return None
        
        # AI-ONLY SCAN - No indicators, pure AI analysis
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get candles
                candles = await unified_market_service.get_candles(
                    symbol=symbol,
                    asset_type='crypto',
                    timeframe=timeframe,
                    limit=200
                )
                
                if not candles:
                    continue
                
                # AI analyzes everything
                analysis = await ai_only_service.analyze_symbol(symbol, candles)
                
                if analysis and analysis.get('score', 0) >= min_score:
                    opportunities.append(analysis)
                    logger.info(f"  ✅ {symbol}: {analysis['direction']} @ {analysis['score']}")
                
            except Exception as e:
                logger.error(f"  ❌ {symbol}: {e}")
                continue
        
        logger.info(f"🎯 Found {len(opportunities)} opportunities")
        
        return BestTradesResponse(
            success=True,
            count=len(opportunities),
            opportunities=opportunities,
            scan_time=datetime.now().isoformat(),
            message=f"Scanned {len(symbols)} crypto - Found {len(opportunities)} opportunities"
        )
        
    except Exception as e:
        logger.error(f"❌ Market scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top")
async def get_top_opportunities(
    limit: int = Query(5, ge=1, le=20, description="Number of top opportunities"),
    exchange: str = Query("binance", description="Exchange"),
    timeframe: str = Query("1h", description="Timeframe")
):
    """
    Get top N trading opportunities (quick scan)
    
    Returns:
        Top opportunities sorted by score
    """
    try:
        # Quick scan of top 20 crypto
        top_symbols = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
            "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "MATIC/USDT",
            "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "NEAR/USDT",
            "ALGO/USDT", "FIL/USDT", "APT/USDT", "ARB/USDT", "OP/USDT"
        ]
        
        async def fetch_candles(symbol: str, exch: str):
            try:
                ohlcv = await market_service.get_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=200,
                    exchange=exch
                )
                
                if not ohlcv:
                    return None
                
                return [
                    {
                        'timestamp': c[0],
                        'open': c[1],
                        'high': c[2],
                        'low': c[3],
                        'close': c[4],
                        'volume': c[5] if len(c) > 5 else 0
                    }
                    for c in ohlcv
                ]
            except:
                return None
        
        opportunities = await best_trades_service.scan_for_best_trades(
            symbols=top_symbols,
            exchange=exchange,
            min_score=50,  # Lower threshold for quick scan
            fetch_data_func=fetch_candles
        )
        
        # Return top N
        top_n = opportunities[:limit]
        
        return {
            "success": True,
            "count": len(top_n),
            "total_scanned": len(top_symbols),
            "opportunities": top_n
        }
        
    except Exception as e:
        logger.error(f"❌ Top opportunities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if best trades service is healthy"""
    return {
        "status": "online",
        "service": "best-trades",
        "ai_available": best_trades_service.is_ai_available()
    }

@router.get("/test-ai")
async def test_ai_single():
    """Test AI analysis on single symbol"""
    try:
        # Test BTC
        candles = await unified_market_service.get_candles("BTC/USDT", "crypto", "1h", 200)
        
        if not candles:
            return {"error": "Failed to get candles"}
        
        analysis = await ai_only_service.analyze_symbol("BTC/USDT", candles)
        
        if not analysis:
            return {"error": "AI returned None", "ai_available": ai_only_service.is_available()}
        
        return {
            "success": True,
            "analysis": analysis,
            "message": "AI test completed"
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "ai_available": ai_only_service.is_available()
        }

@router.get("/test-scan")
async def test_scan():
    """Ultra simple test scan - just return fake data"""
    from datetime import datetime
    return {
        "success": True,
        "count": 1,
        "opportunities": [{
            "symbol": "BTC/USDT",
            "score": 75,
            "direction": "LONG",
            "current_price": 42000
        }],
        "scan_time": datetime.now().isoformat(),
        "message": "Test scan works!"
    }

