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
        claude_key=settings.ANTHROPIC_API_KEY,
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


@app.get("/api/scan/test")
async def test_scan_one_symbol():
    """
    Quick test - analyze only BTC/USDT
    """
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    try:
        logger.info("🔍 Test scan: BTC/USDT only")
        
        # Fetch BTC data
        logger.info("📊 Fetching BTC/USDT data...")
        ohlcv = await scanner.fetcher.fetch_ohlcv("BTC/USDT", "1h", 100)
        
        if not ohlcv:
            return {"error": "Failed to fetch BTC data", "step": "fetch_ohlcv"}
        
        logger.info(f"✅ Fetched {len(ohlcv)} candles")
        
        # AI analysis
        logger.info("🤖 Calling Claude AI...")
        analysis = await scanner.ai.analyze_setup("BTC/USDT", ohlcv, "1h")
        
        if not analysis:
            return {
                "error": "AI analysis returned None",
                "ai_available": scanner.ai.is_available(),
                "step": "ai_analysis"
            }
        
        logger.info(f"✅ Analysis complete: {analysis}")
        
        return {
            "success": True,
            "symbol": "BTC/USDT",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"❌ Test scan error: {e}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(error_trace)
        return {
            "error": str(e),
            "traceback": error_trace
        }


async def perform_scan_and_alert():
    """Perform scan and send Telegram alerts"""
    try:
        logger.info("🔍 Starting market scan...")
        logger.info(f"   Scanner: {scanner is not None}")
        logger.info(f"   Telegram: {telegram is not None}")
        
        # Scan market
        setups = await scanner.scan_market(
            timeframes=['15m', '1h', '4h'],
            max_results=settings.MAX_ALERTS_PER_SCAN
        )
        
        logger.info(f"✅ Scan complete - found {len(setups) if setups else 0} setups")
        
        if not setups:
            logger.info("ℹ️  No setups found matching criteria")
            if telegram and telegram.is_available():
                await telegram.send_scan_summary([])
            return
        
        logger.info(f"🎯 Top {len(setups)} setups to send:")
        for s in setups:
            logger.info(f"   - {s.get('symbol')} {s.get('timeframe')} {s.get('direction')} (confidence: {s.get('confidence')}%)")
        
        # Send to Telegram
        if telegram and telegram.is_available():
            logger.info("📱 Sending to Telegram...")
            await telegram.send_scan_summary(setups)
            
            for setup in setups:
                await telegram.send_alert(setup)
            
            logger.info("✅ All alerts sent!")
        else:
            logger.warning("⚠️  Telegram not available")
                
        logger.info("✅ Scan complete!")
        
    except Exception as e:
        logger.error(f"❌ Scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Try to send error to telegram
        if telegram and telegram.is_available():
            try:
                await telegram.bot.send_message(
                    chat_id=telegram.chat_id,
                    text=f"❌ Scan Error:\n{str(e)}"
                )
            except:
                pass


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

