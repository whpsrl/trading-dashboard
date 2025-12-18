"""
Market Scanner Router
API endpoints for full market scanning
"""
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from app.market_scanner.service import scanner_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scanner", tags=["scanner"])

@router.post("/scan")
async def scan_market(
    timeframe: str = Query("1h", description="Timeframe: 1h, 4h, 1d"),
    min_score: float = Query(7.0, description="Min score (1-10)", ge=1, le=10),
    top_n: int = Query(10, description="Top N results", ge=1, le=30),
    mode: str = Query("top30", description="Scan mode: top30 or all")
):
    """
    🚀 **FULL MARKET SCAN** - Analizza tutte le crypto con AI
    
    **Funzionalità:**
    - Scansiona ~30 top crypto
    - Analisi AI completa con Claude Sonnet 4
    - Filtra solo setup validi (score >= min_score)
    - Ritorna migliori opportunità ordinate per score
    
    **Tempo richiesto:** 2-5 minuti
    
    **Output esempio:**
    ```json
    {
      "total_analyzed": 30,
      "valid_setups": 5,
      "results": [
        {
          "symbol": "SOLUSDT",
          "score": 8.5,
          "direction": "LONG",
          "entry": 145.20,
          "stop_loss": 142.50,
          "target_1": 150.00,
          "target_2": 155.00,
          "risk_reward": 3.2,
          "confluences": ["Breakout", "Volume spike", "RSI oversold"]
        }
      ]
    }
    ```
    """
    
    if not scanner_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Market Scanner not available - ANTHROPIC_API_KEY not configured"
        )
    
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"🚀 Starting market scan: mode={mode}, timeframe={timeframe}, min_score={min_score}")
        
        # Run scan
        results = await scanner_service.scan_market(
            timeframe=timeframe,
            min_score=min_score,
            mode=mode
        )
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Limit results
        top_results = results[:top_n]
        
        response = {
            "success": True,
            "timestamp": start_time.isoformat(),
            "duration_seconds": round(duration, 1),
            "settings": {
                "timeframe": timeframe,
                "min_score": min_score,
                "top_n": top_n
            },
            "total_analyzed": 30,
            "valid_setups": len(results),
            "results": top_results
        }
        
        logger.info(f"✅ Scan complete: {len(results)} setups found in {duration:.1f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Market scan failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Market scan failed: {str(e)}"
        )


@router.get("/status")
async def scanner_status():
    """
    Verifica status e capabilities dello scanner
    """
    available = scanner_service.is_available()
    
    return {
        "status": "online" if available else "unavailable",
        "ai_configured": available,
        "features": [
            "Full AI analysis with Claude Sonnet 4",
            "30+ cryptocurrencies",
            "Multi-timeframe support (1h, 4h, 1d)",
            "Risk/Reward calculation",
            "Technical confluence detection",
            "Pattern recognition"
        ],
        "supported_timeframes": ["1h", "4h", "1d"],
        "avg_scan_duration": "2-5 minutes",
        "max_concurrent": 3
    }


@router.get("/symbols")
async def get_scanned_symbols():
    """
    Lista delle crypto che vengono scansionate
    """
    symbols = await scanner_service.get_crypto_list()
    
    return {
        "count": len(symbols),
        "symbols": symbols
    }
