"""Trading Dashboard API - Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Trading Dashboard API")
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("👋 Shutting down")

# Initialize FastAPI
app = FastAPI(
    title="Trading Dashboard API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Trading Dashboard API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Import routers
from app.market_data.router import router as market_router

# Include routers
app.include_router(market_router, prefix="/api/market", tags=["Market Data"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
