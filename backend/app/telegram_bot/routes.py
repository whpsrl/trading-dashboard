"""
Telegram Bot Routes
Webhook e comandi per il bot
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import logging

from .service import telegram_bot
from ..best_trades.service import best_trades_service
from ..market_data.unified_service import unified_market_service
from ..market_data.market_universe import get_scan_symbols

router = APIRouter()
logger = logging.getLogger(__name__)


class TelegramMessage(BaseModel):
    text: str
    parse_mode: Optional[str] = "Markdown"


@router.get("/test")
async def test_telegram():
    """Test Telegram bot connection"""
    result = await telegram_bot.test_connection()
    
    if result['success']:
        # Send test message
        await telegram_bot.send_message("🤖 Bot connected successfully!\n\nUse /scan to find best trades.")
        
        return {
            "success": True,
            "message": "Telegram bot working",
            "bot_info": result
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('message', 'Connection failed'))


@router.post("/send")
async def send_telegram_message(message: TelegramMessage):
    """Send custom message to Telegram"""
    if not telegram_bot.is_available():
        raise HTTPException(status_code=503, detail="Telegram not configured")
    
    success = await telegram_bot.send_message(message.text, message.parse_mode)
    
    if success:
        return {"success": True, "message": "Message sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/notify/scan")
async def notify_scan_complete(
    background_tasks: BackgroundTasks,
    preset: str = Query("quick", description="Scan preset"),
    min_score: float = Query(70, description="Only notify if score >= this")
):
    """
    Trigger scan and send results to Telegram
    Runs in background
    """
    if not telegram_bot.is_available():
        raise HTTPException(status_code=503, detail="Telegram not configured")
    
    async def do_scan():
        try:
            logger.info(f"🚀 Starting Telegram scan: {preset}")
            
            # Get symbols for preset
            scan_data = get_scan_symbols(preset)
            metadata = scan_data['metadata']
            
            # Prepare symbols
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
                    return await unified_market_service.get_candles(
                        symbol=symbol,
                        asset_type=asset_type,
                        timeframe='1h',
                        limit=200
                    )
                except:
                    return None
            
            # Scan
            opportunities = await best_trades_service.scan_for_best_trades(
                symbols=all_symbols,
                min_score=min_score,
                fetch_data_func=fetch_candles,
                asset_types=asset_type_map
            )
            
            logger.info(f"✅ Scan complete: {len(opportunities)} opportunities found")
            
            # Send to Telegram
            await telegram_bot.send_scan_complete(
                opportunities=opportunities,
                preset=preset,
                total_scanned=metadata['total_symbols']
            )
            
        except Exception as e:
            logger.error(f"❌ Scan error: {e}")
            await telegram_bot.send_alert(
                "Scan Error",
                f"Failed to complete scan: {str(e)}"
            )
    
    # Run in background
    background_tasks.add_task(do_scan)
    
    return {
        "success": True,
        "message": f"Scan started ({preset}). Results will be sent to Telegram."
    }


@router.post("/notify/opportunity")
async def notify_single_opportunity(symbol: str, asset_type: str = "crypto"):
    """
    Analyze single symbol and send to Telegram if score is good
    """
    if not telegram_bot.is_available():
        raise HTTPException(status_code=503, detail="Telegram not configured")
    
    try:
        # Fetch candles
        candles = await unified_market_service.get_candles(
            symbol=symbol,
            asset_type=asset_type,
            timeframe='1h',
            limit=200
        )
        
        if not candles:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Analyze
        analysis = await best_trades_service.analyze_symbol(
            symbol=symbol,
            candles=candles,
            exchange=asset_type
        )
        
        if not analysis:
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        # Send if score >= 60
        if analysis['score'] >= 60:
            message = telegram_bot.format_opportunity_message(analysis)
            await telegram_bot.send_message(message)
            
            return {
                "success": True,
                "message": "Opportunity sent to Telegram",
                "score": analysis['score']
            }
        else:
            return {
                "success": False,
                "message": f"Score too low ({analysis['score']:.0f}). Not sent.",
                "score": analysis['score']
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def telegram_status():
    """Get Telegram bot status"""
    if not telegram_bot.is_available():
        return {
            "configured": False,
            "message": "Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
        }
    
    test_result = await telegram_bot.test_connection()
    
    return {
        "configured": True,
        "connected": test_result['success'],
        "bot_info": test_result if test_result['success'] else None,
        "error": test_result.get('message') if not test_result['success'] else None
    }

