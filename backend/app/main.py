"""
Trading Dashboard API
Main application with all features enabled
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from app.market_data.router import router as market_router

# Try to import AI router
try:
    from app.ai_analysis.router import router as ai_router
    AI_AVAILABLE = True
    logger.info("✅ AI Analysis router loaded")
except ImportError:
    AI_AVAILABLE = False
    logger.warning("⚠️ AI Analysis not available")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Trading Dashboard API starting...")
    logger.info("📊 Market Data: ENABLED")
    logger.info(f"🤖 AI Analysis: {'ENABLED' if AI_AVAILABLE else 'DISABLED'}")
    yield
    logger.info("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Trading Dashboard API",
    description="Real-time market data with AI-powered analysis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    market_router,
    prefix="/api/market",
    tags=["Market Data"]
)

if AI_AVAILABLE:
    app.include_router(
        ai_router,
        prefix="/api/ai",
        tags=["AI Analysis"]
    )

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Trading Dashboard API",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "market_data": True,
            "intraday_15min": True,
            "ai_analysis": AI_AVAILABLE
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "now"
    }
