"""
Best Trades API Routes
Endpoint per trovare le migliori opportunità di trading
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from .service import best_trades_service
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
    Scansiona il mercato per trovare le migliori opportunità di trading
    
    Presets:
    - quick: ~55 simboli (Crypto + Top Stocks + Indices) - ~30 sec
    - balanced: ~80 simboli (Più stocks + commodities + forex) - ~60 sec  
    - full: ~150 simboli (Coverage completo) - ~2 min
    
    Returns:
        List of best trade opportunities sorted by score
    """
    try:
        from datetime import datetime
        import asyncio
        
        logger.info(f"🚀 Starting {preset} market scan: min_score={min_score}")
        
        # Get symbols for preset
        scan_data = get_scan_symbols(preset)
        metadata = scan_data['metadata']
        
        logger.info(f"📊 Scanning {metadata['total_symbols']} assets across all markets...")
        logger.info(f"⏱️  Estimated time: {metadata['estimated_time']} seconds")
        logger.info(f"📡 Finnhub calls needed: {metadata['finnhub_calls']}")
        
        # Prepare symbols and types
        all_symbols = []
        asset_type_map = {}
        
        for market_type in ['crypto', 'stocks', 'indices', 'commodities', 'forex']:
            for item in scan_data[market_type]:
                symbol = item['symbol']
                asset_type = item['type']
                all_symbols.append(symbol)
                asset_type_map[symbol] = asset_type
        
        # Fetch data function
        async def fetch_candles(symbol: str, asset_type: str):
            try:
                candles = await unified_market_service.get_candles(
                    symbol=symbol,
                    asset_type=asset_type,
                    timeframe=timeframe,
                    limit=200
                )
                return candles
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                return None
        
        # Scan for opportunities
        opportunities = await best_trades_service.scan_for_best_trades(
            symbols=all_symbols,
            exchange="multi",  # Not used anymore
            min_score=min_score,
            fetch_data_func=fetch_candles,
            asset_types=asset_type_map
        )
        
        # Get rate limit status
        rate_status = unified_market_service.get_rate_limit_status()
        
        logger.info(f"🎯 Found {len(opportunities)} opportunities")
        logger.info(f"📊 Rate limits: Finnhub {rate_status['finnhub']['percentage']}%, OANDA {rate_status['oanda']['percentage']}%")
        
        return BestTradesResponse(
            success=True,
            count=len(opportunities),
            opportunities=opportunities,
            scan_time=datetime.now().isoformat(),
            message=f"Scanned {metadata['total_symbols']} assets - Found {len(opportunities)} opportunities"
        )
        
    except Exception as e:
        logger.error(f"❌ Market scan error: {e}")
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

