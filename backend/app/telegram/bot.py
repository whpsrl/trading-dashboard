"""
Telegram Bot Notifier
Sends trading alerts to Telegram channel
"""
import logging
from typing import List, Dict
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram bot"""
        if not bot_token or not chat_id:
            logger.error("❌ Telegram credentials missing!")
            self.bot = None
            self.chat_id = None
        else:
            try:
                self.bot = Bot(token=bot_token)
                self.chat_id = chat_id
                logger.info("✅ Telegram notifier initialized")
            except Exception as e:
                logger.error(f"❌ Telegram init error: {e}")
                self.bot = None
                self.chat_id = None
    
    def is_available(self) -> bool:
        """Check if Telegram is available"""
        return self.bot is not None and self.chat_id is not None
    
    async def send_alert(self, setup: Dict) -> bool:
        """
        Send trading alert for a single setup
        """
        if not self.is_available():
            logger.warning("Telegram not available")
            return False
        
        try:
            # Format message
            direction_emoji = {
                'LONG': '🟢',
                'SHORT': '🔴',
                'NEUTRAL': '⚪'
            }.get(setup.get('direction', 'NEUTRAL'), '⚪')
            
            # Get AI provider (default to Claude for backward compatibility)
            ai_provider = setup.get('ai_provider', 'claude').upper()
            ai_emoji = '🤖' if ai_provider == 'CLAUDE' else '⚡'
            
            message = f"""
{direction_emoji} **TRADING SIGNAL** {direction_emoji}

**Coin:** {setup.get('symbol', 'N/A')}
**Timeframe:** {setup.get('timeframe', 'N/A')}
**Direction:** {setup.get('direction', 'N/A')}
**Confidence:** {setup.get('confidence', 0)}%

💰 **Entry:** ${setup.get('entry', 0):.4f}
🎯 **Take Profit:** ${setup.get('take_profit', 0):.4f}
🛑 **Stop Loss:** ${setup.get('stop_loss', 0):.4f}

📊 **AI Analysis** ({ai_emoji} {ai_provider}):
{setup.get('reasoning', 'No reasoning provided')}

⏰ _Signal generated automatically_
"""
            
            # Send message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Alert sent for {setup.get('symbol')}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    async def send_scan_summary(self, setups: List[Dict]) -> bool:
        """
        Send summary of scan results
        """
        if not self.is_available():
            return False
        
        if not setups:
            message = "🔍 **Market Scan Complete**\n\nNo high-confidence setups found."
        else:
            message = f"🔍 **Market Scan Complete**\n\n✅ Found {len(setups)} high-confidence setup(s)\n\n"
            message += "Sending individual alerts..."
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error sending summary: {e}")
            return False

