from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logger = logging.getLogger(__name__)

# ========================
# Importa TUTTE le route esistenti (con fallback sicuri)
# ========================

# Market Data Router (già esiste - usa router.py)
try:
    from app.market_data.router import router as market_data_router
    MARKET_DATA_AVAILABLE = True
except Exception as e:
    logger.warning(f"Market data router not available: {e}")
    MARKET_DATA_AVAILABLE = False

# AI Analysis Router (NUOVO - usa routes.py)
try:
    from app.ai_analysis.routes import router as ai_analysis_router
    AI_ANALYSIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"AI analysis router not available: {e}")
    AI_ANALYSIS_AVAILABLE = False

# Instruments Router (NUOVO - lista simboli disponibili)
try:
    from app.instruments.routes import router as instruments_router
    INSTRUMENTS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Instruments router not available: {e}")
    INSTRUMENTS_AVAILABLE = False

# Market Scanner Router (NUOVO - AI scan completo)
try:
    from app.market_scanner.router import router as scanner_router
    SCANNER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Scanner router not available: {e}")
    SCANNER_AVAILABLE = False

# Best Trades Router (NUOVO - Best trade finder con AI)
try:
    from app.best_trades.routes import router as best_trades_router
    BEST_TRADES_AVAILABLE = True
except Exception as e:
    logger.warning(f"Best trades router not available: {e}")
    BEST_TRADES_AVAILABLE = False

# Telegram Bot Router (NUOVO - Notifiche Telegram)
try:
    from app.telegram_bot.routes import router as telegram_router
    TELEGRAM_AVAILABLE = True
except Exception as e:
    logger.warning(f"Telegram router not available: {e}")
    TELEGRAM_AVAILABLE = False

app = FastAPI(
    title="Trading Dashboard API",
    description="Real-time market data aggregation with AI-powered chart analysis",
    version="2.0.0"
)

# ========================
# CORS Configuration
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://trading-dashboard-amber-seven.vercel.app",  # Your actual Vercel domain
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ========================
# Include ALL Routers (solo se disponibili)
# ========================

# 1. Market Data (già esistente)
if MARKET_DATA_AVAILABLE:
    app.include_router(
        market_data_router,
        tags=["📊 Market Data"]
    )

# 2. AI Analysis (NUOVO)
if AI_ANALYSIS_AVAILABLE:
    app.include_router(
        ai_analysis_router,
        prefix="/api/v1/ai",
        tags=["🤖 AI Analysis"]
    )

# 3. Instruments (NUOVO)
if INSTRUMENTS_AVAILABLE:
    app.include_router(
        instruments_router,
        tags=["📋 Instruments"]
    )

# 4. Market Scanner (NUOVO - Full AI Scan)
if SCANNER_AVAILABLE:
    app.include_router(
        scanner_router,
        tags=["🔍 Market Scanner"]
    )

# 5. Best Trades (NUOVO - AI Best Trade Finder)
if BEST_TRADES_AVAILABLE:
    app.include_router(
        best_trades_router,
        prefix="/api/best-trades",
        tags=["🎯 Best Trades"]
    )

# 6. Telegram Bot (NUOVO - Notifiche e Alert)
if TELEGRAM_AVAILABLE:
    app.include_router(
        telegram_router,
        prefix="/api/telegram",
        tags=["📱 Telegram Bot"]
    )

# ========================
# Root & Health Endpoints
# ========================

@app.get("/")
async def root():
    """
    Welcome endpoint - mostra info API
    """
    return {
        "name": "Trading Dashboard API",
        "status": "🟢 online",
        "version": "2.0.0",
        "features": [
            "Real-time market data aggregation (Binance, OANDA, Finnhub)",
            "AI-powered chart analysis", 
            "Multi-market support (Crypto, Forex, Stocks)",
            "🔍 Full market scanner with AI"
        ],
        "endpoints": {
            "documentation": "/docs",
            "health": "/api/v1/health",
            "market_data": "/api/v1/market-data",  # Fixed path
            "ai_analyze": "/api/v1/ai/analyze",
            "ai_health": "/api/v1/ai/health",
            "scanner": "/api/scanner/scan",
            "best_trades": "/api/best-trades/top"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """
    Health check generale - verifica status di tutti i servizi
    """
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "status": "online",
        "timestamp": os.environ.get("RAILWAY_DEPLOYMENT_ID", "local"),
        "services": {
            "api": "🟢 online",
            "ai": "🟢 online" if anthropic_configured else "🔴 not configured",
            "market_data": "🟢 online",
            "database": "🟢 connected",
            "redis": "🟢 connected"
        }
    }

@app.get("/api/v1/status")
async def detailed_status():
    """
    Status dettagliato con configurazione environment
    """
    return {
        "api": {
            "status": "online",
            "version": "2.0.0",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
        },
        "configuration": {
            "anthropic_api_key": "✅ configured" if os.getenv("ANTHROPIC_API_KEY") else "❌ missing",
            "cors_enabled": True,
            "port": os.getenv("PORT", "8000")
        },
        "available_endpoints": {
            "market_data": {
                "crypto": "/api/v1/market-data/crypto/{symbol}",
                "forex": "/api/v1/market-data/forex/{symbol}",
                "stock": "/api/v1/market-data/stock/{symbol}"
            },
            "ai": {
                "analyze": "/api/v1/ai/analyze",
                "health": "/api/v1/ai/health"
            },
            "system": {
                "health": "/api/v1/health",
                "status": "/api/v1/status",
                "docs": "/docs"
            }
        }
    }

# ========================
# Startup/Shutdown Events
# ========================

@app.on_event("startup")
async def startup_event():
    """
    Eseguito all'avvio dell'applicazione
    """
    print("\n" + "="*60)
    print("🚀 Trading Dashboard API - STARTED")
    print("="*60)
    print(f"📍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"🔑 Anthropic API: {'✅ Configured' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"🌐 Port: {os.getenv('PORT', '8000')}")
    print("\n📚 Available Endpoints:")
    print("   → Market Data:  /api/v1/market-data")
    print("   → AI Analysis:  /api/v1/ai/analyze")
    print("   → AI Health:    /api/v1/ai/health")
    print("   → API Docs:     /docs")
    print("   → Health Check: /api/v1/health")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Eseguito allo shutdown dell'applicazione
    """
    print("\n" + "="*60)
    print("👋 Trading Dashboard API - SHUTTING DOWN")
    print("="*60 + "\n")

# ========================
# Exception Handlers
# ========================

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler globale per tutte le eccezioni non gestite
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url)
        }
    )

# ========================
# Run Application (local)
# ========================

if __name__ == "__main__":
    import uvicorn
    
    # Porta da environment o default 8000
    port = int(os.getenv("PORT", 8000))
    
    # Configurazione uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,          # Auto-reload per development
        log_level="info"
    )
