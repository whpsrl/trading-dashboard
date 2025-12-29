"""
Trading Bot with AI Vision - Main FastAPI Application
"""
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .config import settings
from .scanner import TradingScanner
from .telegram import TelegramNotifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
scanner: TradingScanner = None
telegram: TelegramNotifier = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global scanner, telegram
    
    logger.info("🚀 Starting Trading Bot...")
    
    # Initialize scanner
    scanner = TradingScanner(
        binance_key=settings.BINANCE_API_KEY,
        binance_secret=settings.BINANCE_SECRET,
        openai_key=settings.OPENAI_API_KEY,
        top_n_coins=settings.TOP_N_COINS,
        min_confidence=settings.MIN_CONFIDENCE_SCORE
    )
    
    # Initialize Telegram
    telegram = TelegramNotifier(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        chat_id=settings.TELEGRAM_CHAT_ID
    )
    
    logger.info("✅ All services initialized")
    
    yield
    
    logger.info("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AI Trading Bot",
    description="Trading bot with GPT-4o Vision analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "AI Trading Bot",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """Detailed health check"""
    return {
        "status": "online",
        "scanner_available": scanner is not None,
        "telegram_available": telegram.is_available() if telegram else False,
        "ai_available": scanner.ai.is_available() if scanner else False
    }


@app.post("/api/scan")
async def run_scan(background_tasks: BackgroundTasks):
    """
    Run market scan and send alerts to Telegram
    """
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    # Run scan in background
    background_tasks.add_task(perform_scan_and_alert)
    
    return {
        "status": "started",
        "message": "Market scan started in background"
    }


async def perform_scan_and_alert():
    """Perform scan and send Telegram alerts"""
    try:
        logger.info("🔍 Starting market scan...")
        
        # Scan market
        setups = await scanner.scan_market(
            timeframes=['15m', '1h', '4h'],
            max_results=settings.MAX_ALERTS_PER_SCAN
        )
        
        if not setups:
            logger.info("No setups found")
            if telegram and telegram.is_available():
                await telegram.send_scan_summary([])
            return
        
        logger.info(f"🎯 Found {len(setups)} top setups")
        
        # Send to Telegram
        if telegram and telegram.is_available():
            await telegram.send_scan_summary(setups)
            
            for setup in setups:
                await telegram.send_alert(setup)
                
        logger.info("✅ Scan complete and alerts sent!")
        
    except Exception as e:
        logger.error(f"❌ Scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())


@app.get("/api/scan/quick/{symbol}")
async def quick_scan(symbol: str, timeframe: str = '15m'):
    """
    Quick scan for a single symbol
    """
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    result = await scanner.quick_scan(symbol, timeframe)
    
    return {
        "success": bool(result and not result.get('error')),
        "data": result
    }


@app.get("/api/test/telegram")
async def test_telegram():
    """Test Telegram connection"""
    if not telegram or not telegram.is_available():
        return {"error": "Telegram not configured"}
    
    test_setup = {
        'symbol': 'BTC/USDT',
        'timeframe': '15m',
        'direction': 'LONG',
        'confidence': 85,
        'entry': 42000.0,
        'take_profit': 43000.0,
        'stop_loss': 41500.0,
        'reasoning': 'This is a test alert. Strong support at current level with bullish momentum.'
    }
    
    success = await telegram.send_alert(test_setup)
    
    return {
        "success": success,
        "message": "Test alert sent" if success else "Failed to send alert"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

