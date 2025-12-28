"""
Telegram notifications for trade results and signals
"""
import os
import logging
import httpx
from typing import Optional, Dict

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_trade_signal(analysis: Dict) -> bool:
    """
    Send new trade signal to Telegram when opportunity is found
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured")
        return False
    
    try:
        # Get data
        symbol = analysis.get('symbol', 'N/A')
        direction = analysis.get('direction', 'NEUTRAL')
        score = analysis.get('score', 0)
        confidence = analysis.get('confidence', 0)
        current_price = analysis.get('current_price', 0)
        
        trade_levels = analysis.get('trade_levels', {})
        entry = trade_levels.get('entry', current_price)
        stop_loss = trade_levels.get('stop_loss')
        target_1 = trade_levels.get('target_1')
        target_2 = trade_levels.get('target_2')
        rr_t1 = trade_levels.get('risk_reward_ratio_t1', 0)
        rr_t2 = trade_levels.get('risk_reward_ratio_t2', 0)
        
        ai_validation = analysis.get('ai_insights') or analysis.get('ai_validation')
        ai_rec = ai_validation.get('recommendation', 'N/A') if ai_validation else 'N/A'
        ai_timing = ai_validation.get('timing', 'N/A') if ai_validation else 'N/A'
        
        confluences = analysis.get('confluences', [])
        warnings = analysis.get('warnings', [])
        
        # Direction emoji
        if direction == 'LONG':
            dir_emoji = "🟢"
            dir_text = "LONG"
        elif direction == 'SHORT':
            dir_emoji = "🔴"
            dir_text = "SHORT"
        else:
            dir_emoji = "⚪"
            dir_text = "NEUTRAL"
        
        # Score emoji
        if score >= 80:
            score_emoji = "🔥🔥🔥"
        elif score >= 70:
            score_emoji = "🔥🔥"
        elif score >= 60:
            score_emoji = "🔥"
        else:
            score_emoji = "⭐"
        
        # Build message
        message = f"""
{score_emoji} **NUOVO SEGNALE TRADING** {score_emoji}

━━━━━━━━━━━━━━━━━━━━
{dir_emoji} **{symbol}** - {dir_text}
━━━━━━━━━━━━━━━━━━━━

⭐ **Score**: {score:.1f}/100
💪 **Confidence**: {confidence:.1f}%
🤖 **AI Timing**: {ai_timing}

━━━━━━━━━━━━━━━━━━━━
📊 **LIVELLI DI TRADING**
━━━━━━━━━━━━━━━━━━━━

💰 **Entry**: ${entry:.2f}
🛑 **Stop Loss**: ${stop_loss:.2f if stop_loss else 0}
🎯 **Target 1**: ${target_1:.2f if target_1 else 0} (R:R {rr_t1:.1f}x)
🎯 **Target 2**: ${target_2:.2f if target_2 else 0} (R:R {rr_t2:.1f}x)

━━━━━━━━━━━━━━━━━━━━
✅ **CONFLUENZE** ({len(confluences)})
━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f"• {c}" for c in confluences[:5]])}

{f'''━━━━━━━━━━━━━━━━━━━━
⚠️ **ATTENZIONE** ({len(warnings)})
━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f"• {w}" for w in warnings[:3]])}
''' if warnings else ''}
━━━━━━━━━━━━━━━━━━━━
🧠 **ANALISI AI**
━━━━━━━━━━━━━━━━━━━━
{ai_rec[:300]}...

━━━━━━━━━━━━━━━━━━━━
⏰ Trade tracciato automaticamente!
Riceverai aggiornamenti quando raggiunge target o SL.
"""
        
        # Send message
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Signal sent for {symbol}")
                return True
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return False
    
    except Exception as e:
        logger.error(f"❌ Error sending signal: {e}")
        return False


async def send_trade_result_notification(trade) -> bool:
    """
    Send notification when a trade completes (hits target or stop loss)
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured")
        return False
    
    try:
        # Determine result emoji and message
        if trade.status.value == "hit_target_2":
            emoji = "🎯🎯"
            status_text = "TARGET 2 RAGGIUNTO!"
            result_color = "🟢"
        elif trade.status.value == "hit_target_1":
            emoji = "🎯"
            status_text = "TARGET 1 RAGGIUNTO!"
            result_color = "🟢"
        elif trade.status.value == "stopped":
            emoji = "🛑"
            status_text = "STOP LOSS COLPITO"
            result_color = "🔴"
        elif trade.status.value == "expired":
            emoji = "⏰"
            status_text = "TRADE SCADUTO"
            result_color = "⚪"
        else:
            return False
        
        # Calculate profit/loss
        pl = trade.profit_loss_percent or 0
        pl_text = f"+{pl:.2f}%" if pl > 0 else f"{pl:.2f}%"
        pl_emoji = "📈" if pl > 0 else "📉" if pl < 0 else "➖"
        
        # Build message
        message = f"""
{emoji} **{status_text}** {emoji}

━━━━━━━━━━━━━━━━━━━━
{result_color} **{trade.symbol}** - {trade.direction.value}
━━━━━━━━━━━━━━━━━━━━

💰 **Entry**: ${trade.entry_price:.2f}
💸 **Exit**: ${trade.exit_price:.2f}

{pl_emoji} **P/L**: {pl_text}
📊 **R:R Realizzato**: {trade.risk_reward_realized:.2f}x
⏱️ **Durata**: {trade.duration_minutes} minuti

📈 **Score Tecnico**: {trade.technical_score:.1f}/100
🤖 **AI Confidence**: {trade.ai_validation_score or 'N/A'}/10
⏰ **Timeframe**: {trade.timeframe}

━━━━━━━━━━━━━━━━━━━━
{trade.ai_recommendation[:200] if trade.ai_recommendation else ''}...
━━━━━━━━━━━━━━━━━━━━

🔗 Trade ID: #{trade.id}
"""
        
        # Send message
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram notification sent for trade #{trade.id}")
                return True
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return False
    
    except Exception as e:
        logger.error(f"❌ Error sending Telegram notification: {e}")
        return False


async def send_learning_summary(stats: dict) -> bool:
    """
    Send periodic learning summary to Telegram
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        message = f"""
📊 **REPORT APPRENDIMENTO AI** 📊

━━━━━━━━━━━━━━━━━━━━
🎯 **STATISTICHE GENERALI**
━━━━━━━━━━━━━━━━━━━━

📈 Trade Totali: {stats.get('total_trades', 0)}
✅ Trade Vincenti: {stats.get('winning_trades', 0)}
❌ Trade Perdenti: {stats.get('losing_trades', 0)}
🎯 Win Rate: {stats.get('win_rate', 0):.1f}%

💰 Profitto Medio: +{stats.get('avg_profit', 0):.2f}%
📉 Loss Medio: {stats.get('avg_loss', 0):.2f}%
📊 Profit Factor: {stats.get('profit_factor', 0):.2f}
⚖️ R:R Medio: {stats.get('avg_rr', 0):.2f}x

━━━━━━━━━━━━━━━━━━━━
🏆 **TOP PERFORMING**
━━━━━━━━━━━━━━━━━━━━

{stats.get('best_market', 'N/A')}
{stats.get('best_timeframe', 'N/A')}
{stats.get('best_setup', 'N/A')}

━━━━━━━━━━━━━━━━━━━━
🧠 **INSIGHTS AI**
━━━━━━━━━━━━━━━━━━━━

{chr(10).join(stats.get('insights', [])[:3])}

━━━━━━━━━━━━━━━━━━━━
L'AI continua ad imparare! 🚀
"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10.0
            )
            
            return response.status_code == 200
    
    except Exception as e:
        logger.error(f"❌ Error sending learning summary: {e}")
        return False

