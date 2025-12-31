"""
API routes for Commodities scanning
"""
import logging
from fastapi import APIRouter, Query
from typing import List, Dict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/scan")
async def scan_commodities(
    ai_provider: str = Query("claude", pattern="^(claude|groq)$")
):
    """
    Scan top 3 commodities (Gold, Oil, Silver) on 4H timeframe
    """
    try:
        from ..market_data.yahoo_fetcher import YahooFetcher
        from ..scanner.scanner import TradingScanner
        from ..config import settings
        from ..database.tracker import TradeTracker
        
        logger.info(f"🥇 Starting commodities scan with {ai_provider.upper()} AI...")
        
        # Initialize fetcher
        yahoo_fetcher = YahooFetcher()
        
        # Get commodity symbols
        commodities = ['GC=F', 'CL=F', 'SI=F']  # Gold, Oil, Silver
        
        # Initialize scanner with Yahoo fetcher
        scanner = TradingScanner(
            binance_key="",  # Not needed for Yahoo
            binance_secret="",
            claude_key=settings.ANTHROPIC_API_KEY,
            groq_key=settings.GROQ_API_KEY,
            top_n_coins=3,  # Fixed to 3 commodities
            min_confidence=settings.MIN_CONFIDENCE_SCORE,
            default_ai_provider=ai_provider
        )
        
        # Replace Binance fetcher with Yahoo fetcher
        scanner.fetcher = yahoo_fetcher
        
        # Create scan session in database
        trade_tracker = TradeTracker()
        scan_id = trade_tracker.create_scan_session(
            scan_type='manual_commodities',
            top_n=3,
            timeframes=['4h'],
            ai_provider=ai_provider
        )
        
        # Scan each commodity
        all_setups = []
        for symbol in commodities:
            try:
                # Get symbol info
                symbol_info = yahoo_fetcher.get_symbol_info(symbol)
                display_name = symbol_info['name'] if symbol_info else symbol
                
                logger.info(f"   Analyzing {display_name} ({symbol})...")
                
                # Fetch OHLCV data
                ohlcv = await yahoo_fetcher.fetch_ohlcv(symbol, '4h', limit=100)
                
                if not ohlcv or len(ohlcv) < 50:
                    logger.warning(f"⚠️ Insufficient data for {symbol}")
                    continue
                
                # Get AI analysis
                if ai_provider == 'claude':
                    analysis = await scanner.claude_ai.analyze_setup(display_name, ohlcv, '4h')
                else:
                    analysis = await scanner.groq_ai.analyze_setup(display_name, ohlcv, '4h')
                
                if not analysis or analysis.get('confidence', 0) < settings.MIN_CONFIDENCE_SCORE:
                    logger.info(f"   {display_name}: Low confidence, skipping")
                    continue
                
                # Get current price
                current_price = ohlcv[-1][4]  # Close price of last candle
                
                # Calculate market strength (simplified for commodities)
                market_strength = {
                    'score': 70,  # Default score for commodities
                    'rating': '⚪ Neutral',
                    'reason': 'Commodity market strength'
                }
                
                # Build setup
                setup = {
                    'symbol': display_name,
                    'yahoo_symbol': symbol,
                    'timeframe': '4h',
                    'direction': analysis.get('direction', 'NEUTRAL'),
                    'confidence': analysis.get('confidence', 0),
                    'entry': analysis.get('entry', current_price),
                    'stop_loss': analysis.get('stop_loss', current_price * 0.98),
                    'take_profit': analysis.get('take_profit', current_price * 1.02),
                    'reasoning': analysis.get('reasoning', 'No reasoning provided'),
                    'market_strength': market_strength,
                    'ai_provider': ai_provider,
                    'market_type': 'commodity'
                }
                
                all_setups.append(setup)
                logger.info(f"   ✅ {display_name}: {setup['direction']} @ {setup['confidence']}%")
                
                # Save to database
                trade_tracker.save_setup(setup, scan_id=scan_id)
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {symbol}: {e}")
                continue
        
        # Complete scan session
        high_conf_count = len([s for s in all_setups if s.get('confidence', 0) >= settings.MIN_CONFIDENCE_SCORE])
        trade_tracker.complete_scan_session(
            scan_id=scan_id,
            setups_count=len(all_setups),
            high_confidence_count=high_conf_count
        )
        
        logger.info(f"✅ Commodities scan complete - found {len(all_setups)} setups")
        
        # Send to Telegram if available
        try:
            from ..telegram.bot import TelegramNotifier
            from ..config import settings
            
            telegram = TelegramNotifier(
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                chat_id=settings.TELEGRAM_CHAT_ID
            )
            
            if telegram.is_available() and all_setups:
                import asyncio
                asyncio.create_task(telegram.send_scan_summary(all_setups, title="🥇 Commodities Scan"))
                for setup in all_setups:
                    asyncio.create_task(telegram.send_alert(setup))
                logger.info("📱 Sent commodities alerts to Telegram")
        except Exception as e:
            logger.warning(f"⚠️ Could not send Telegram alerts: {e}")
        
        return {
            "success": True,
            "count": len(all_setups),
            "setups": all_setups,
            "message": f"Found {len(all_setups)} commodity setups"
        }
        
    except Exception as e:
        logger.error(f"❌ Commodities scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "setups": []
        }


@router.get("/list")
async def list_commodities():
    """
    Get list of available commodities
    """
    from ..market_data.yahoo_fetcher import YahooFetcher
    
    fetcher = YahooFetcher()
    
    commodities = [
        {
            "key": key,
            "symbol": info['symbol'],
            "name": info['name'],
            "emoji": info['emoji']
        }
        for key, info in fetcher.COMMODITIES.items()
    ]
    
    return {
        "success": True,
        "commodities": commodities
    }

