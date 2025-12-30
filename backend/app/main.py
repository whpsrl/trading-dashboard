"""
Trading Bot with AI Vision - Main FastAPI Application
"""
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .config import settings
from .scanner import TradingScanner
from .telegram import TelegramNotifier
from .database import init_db
from .database.tracker import trade_tracker
from .scheduler import AutoScanner
from .trade_tracking import TradeTrackerWorker

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
auto_scanner: AutoScanner = None
tracker_worker: TradeTrackerWorker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global scanner, telegram, auto_scanner, tracker_worker
    
    logger.info("🚀 Starting Trading Bot...")
    
    # Initialize database
    init_db()
    
    # Initialize scanner
    scanner = TradingScanner(
        binance_key=settings.BINANCE_API_KEY,
        binance_secret=settings.BINANCE_SECRET,
        claude_key=settings.ANTHROPIC_API_KEY,
        groq_key=settings.GROQ_API_KEY,
        top_n_coins=settings.TOP_N_COINS,
        min_confidence=settings.MIN_CONFIDENCE_SCORE
    )
    
    # Initialize Telegram
    telegram = TelegramNotifier(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        chat_id=settings.TELEGRAM_CHAT_ID
    )
    
    # Initialize auto-scanner (4h scans)
    auto_scanner = AutoScanner(scanner, telegram, trade_tracker)
    auto_scanner.start()
    
    # Initialize trade tracker worker (checks TP/SL every 15min)
    tracker_worker = TradeTrackerWorker(scanner.fetcher)
    asyncio.create_task(tracker_worker.start())
    
    logger.info("✅ All services initialized:")
    logger.info("   📊 4H Auto-scan: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC")
    logger.info("   🔄 Trade Tracker: checks TP/SL every 15 minutes")
    
    yield
    
    logger.info("👋 Shutting down...")
    if auto_scanner:
        auto_scanner.stop()
    if tracker_worker:
        tracker_worker.stop()


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
        "ai_claude_available": scanner.claude.is_available() if scanner else False,
        "ai_groq_available": scanner.groq.is_available() if scanner else False
    }


@app.post("/api/scan")
async def run_scan(top_n: int = 15, ai_provider: str = 'claude'):
    """
    Run market scan and return results + send to Telegram
    
    Args:
        top_n: Number of top crypto pairs to scan (5, 10, 15, or 30)
        ai_provider: AI to use - 'claude' (default) or 'groq'
    """
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    try:
        logger.info(f"🔍 Starting market scan for top {top_n} crypto with {ai_provider.upper()}...")
        
        # Create scan session in database
        scan_id = trade_tracker.create_scan_session(
            scan_type=f'manual_{ai_provider}',
            top_n=top_n,
            timeframes=['15m', '1h', '4h']
        )
        
        # Temporarily override scanner's top_n
        original_top_n = scanner.top_n_coins
        scanner.top_n_coins = top_n
        
        # Scan market with selected AI
        setups = await scanner.scan_market(
            timeframes=['15m', '1h', '4h'],
            max_results=50,  # Allow more results, filter on frontend
            ai_provider=ai_provider
        )
        
        # Restore original
        scanner.top_n_coins = original_top_n
        
        logger.info(f"✅ Scan complete - found {len(setups) if setups else 0} setups")
        
        # Save setups to database
        if setups:
            for setup in setups:
                trade_tracker.save_setup(setup, scan_id=scan_id)
        
        # Complete scan session
        high_conf_count = len([s for s in setups if s.get('confidence', 0) >= 60]) if setups else 0
        trade_tracker.complete_scan_session(
            scan_id=scan_id,
            setups_count=len(setups) if setups else 0,
            high_confidence_count=high_conf_count
        )
        
        # Send to Telegram in background (top 5 only)
        if setups and telegram and telegram.is_available():
            import asyncio
            top_5_setups = sorted(setups, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
            asyncio.create_task(send_telegram_alerts(top_5_setups))
        
        return {
            "success": True,
            "count": len(setups) if setups else 0,
            "setups": setups or [],
            "scan_id": scan_id,
            "message": f"Found {len(setups) if setups else 0} high-confidence setups"
        }
        
    except Exception as e:
        logger.error(f"❌ Scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "setups": []
        }


async def send_telegram_alerts(setups):
    """Send alerts to Telegram (background task)"""
    try:
        await telegram.send_scan_summary(setups)
        for setup in setups:
            await telegram.send_alert(setup)
        logger.info("✅ Telegram alerts sent!")
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")


@app.get("/api/scan/test")
async def test_scan_one_symbol(ai_provider: str = 'claude'):
    """
    Quick test - analyze only BTC/USDT with specified AI
    
    Args:
        ai_provider: 'claude' or 'groq'
    """
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    try:
        logger.info(f"🔍 Test scan: BTC/USDT with {ai_provider.upper()}")
        
        # Fetch BTC data
        logger.info("📊 Fetching BTC/USDT data...")
        ohlcv = await scanner.fetcher.fetch_ohlcv("BTC/USDT", "1h", 100)
        
        if not ohlcv:
            return {"error": "Failed to fetch BTC data", "step": "fetch_ohlcv"}
        
        logger.info(f"✅ Fetched {len(ohlcv)} candles")
        
        # Select AI
        if ai_provider == 'groq':
            if not scanner.groq.is_available():
                return {"error": "Groq not available", "ai_available": False}
            ai_to_use = scanner.groq
        else:
            if not scanner.claude.is_available():
                return {"error": "Claude not available", "ai_available": False}
            ai_to_use = scanner.claude
        
        # AI analysis
        logger.info(f"🤖 Calling {ai_provider.upper()} AI...")
        analysis = await ai_to_use.analyze_setup("BTC/USDT", ohlcv, "1h")
        
        if not analysis:
            return {
                "error": f"{ai_provider.upper()} analysis returned None",
                "ai_available": ai_to_use.is_available(),
                "step": "ai_analysis"
            }
        
        logger.info(f"✅ Analysis complete: {analysis}")
        
        return {
            "success": True,
            "symbol": "BTC/USDT",
            "ai_provider": ai_provider,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"❌ Test scan error: {e}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(error_trace)
        return {
            "error": str(e),
            "traceback": error_trace,
            "ai_provider": ai_provider
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


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics and learning metrics"""
    try:
        stats = trade_tracker.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/results")
async def get_recent_results(limit: int = 20):
    """Get recent scan results"""
    try:
        scans = trade_tracker.get_recent_scans(limit=limit)
        return {
            "success": True,
            "count": len(scans),
            "scans": scans
        }
    except Exception as e:
        logger.error(f"❌ Error getting results: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/results/{scan_id}")
async def get_scan_setups(scan_id: int):
    """Get all setups from a specific scan"""
    try:
        setups = trade_tracker.get_setups_by_scan(scan_id)
        return {
            "success": True,
            "count": len(setups),
            "setups": setups
        }
    except Exception as e:
        logger.error(f"❌ Error getting scan setups: {e}")
        return {
            "success": False,
            "error": str(e)
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

