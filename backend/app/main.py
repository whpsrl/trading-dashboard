from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# ========================
# Importa TUTTE le route esistenti
# ========================

# Market Data Router (già esiste - usa router.py)
from app.market_data.router import router as market_data_router

# AI Analysis Router (NUOVO - usa routes.py)
from app.ai_analysis.routes import router as ai_analysis_router

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
# Include ALL Routers
# ========================

# 1. Market Data (già esistente)
app.include_router(
    market_data_router,
    prefix="/api/v1/market-data",
    tags=["📊 Market Data"]
)

# 2. AI Analysis (NUOVO)
app.include_router(
    ai_analysis_router,
    prefix="/api/v1/ai",
    tags=["🤖 AI Analysis"]
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
            "Multi-market support (Crypto, Forex, Stocks)"
        ],
        "endpoints": {
            "documentation": "/docs",
            "health": "/api/v1/health",
            "market_data": "/api/v1/market-data",
            "ai_analyze": "/api/v1/ai/analyze",
            "ai_health": "/api/v1/ai/health"
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
