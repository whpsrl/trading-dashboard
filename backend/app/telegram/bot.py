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
            self.topics = {}
        else:
            try:
                self.bot = Bot(token=bot_token)
                self.chat_id = chat_id
                
                # Define Telegram Topics (Forum Thread IDs)
                # These need to be configured after creating topics in your Telegram group
                self.topics = {
                    'crypto_signals': None,      # Will be set via config
                    'commodities_signals': None,
                    'indices_signals': None,
                    'news_articles': None,
                    'education': None,
                    'general': None
                }
                
                logger.info("✅ Telegram notifier initialized with Topics support")
            except Exception as e:
                logger.error(f"❌ Telegram init error: {e}")
                self.bot = None
                self.chat_id = None
                self.topics = {}
    
    def is_available(self) -> bool:
        """Check if Telegram is available"""
        return self.bot is not None and self.chat_id is not None
    
    def set_topic_id(self, topic_name: str, thread_id: int):
        """Set a topic thread ID"""
        if topic_name in self.topics:
            self.topics[topic_name] = thread_id
            logger.info(f"✅ Set topic '{topic_name}' to thread ID: {thread_id}")
        else:
            logger.warning(f"⚠️ Unknown topic: {topic_name}")
    
    def get_topic_id(self, topic_name: str) -> int:
        """Get a topic thread ID (returns None if not set)"""
        return self.topics.get(topic_name)
    
    async def send_alert(self, setup: Dict, topic: str = 'crypto_signals') -> bool:
        """
        Send trading alert for a single setup
        
        Args:
            setup: Trade setup dictionary
            topic: Topic name ('crypto_signals', 'commodities_signals', 'indices_signals')
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
            
            # Get market strength
            strength_data = setup.get('market_strength', {})
            strength_score = strength_data.get('strength_score', 50)
            strength_level = strength_data.get('strength_level', 'Neutral')
            
            # Strength emoji
            if strength_score >= 80:
                strength_emoji = '🟢🟢🟢'
            elif strength_score >= 65:
                strength_emoji = '🟢🟢'
            elif strength_score >= 45:
                strength_emoji = '⚪'
            elif strength_score >= 30:
                strength_emoji = '🔴'
            else:
                strength_emoji = '🔴🔴'
            
            message = f"""
{direction_emoji} **TRADING SIGNAL** {direction_emoji}

**Coin:** {setup.get('symbol', 'N/A')}
**Timeframe:** {setup.get('timeframe', 'N/A')}
**Direction:** {setup.get('direction', 'N/A')}
**Confidence:** {setup.get('confidence', 0)}%

💪 **Market Strength:** {strength_emoji} **{strength_score}/100** ({strength_level})

💰 **Entry:** ${setup.get('entry', 0):.4f}
🎯 **Take Profit:** ${setup.get('take_profit', 0):.4f}
🛑 **Stop Loss:** ${setup.get('stop_loss', 0):.4f}

📊 **AI Analysis** ({ai_emoji} {ai_provider}):
{setup.get('reasoning', 'No reasoning provided')}

⏰ _Signal generated automatically_
"""
            
            # Get topic thread ID
            topic_id = self.get_topic_id(topic)
            
            # Send message (to topic if ID is set)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                message_thread_id=topic_id  # None = general chat, int = specific topic
            )
            
            logger.info(f"✅ Alert sent for {setup.get('symbol')} to topic '{topic}'")
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
    
    async def send_trade_close_alert(self, trade: Dict, stats: Dict) -> bool:
        """
        Send alert when a trade closes (TP/SL hit)
        
        Args:
            trade: Trade details with outcome
            stats: Current performance stats
        """
        if not self.is_available():
            return False
        
        try:
            # Determine if WIN or LOSS
            is_win = trade['status'] == 'hit_tp'
            is_expired = trade['status'] == 'expired'
            
            # Emoji and title
            if is_win:
                status_emoji = '✅'
                status_text = 'TRADE CLOSED - WIN'
            elif is_expired:
                status_emoji = '⏰'
                status_text = 'TRADE EXPIRED'
            else:
                status_emoji = '❌'
                status_text = 'TRADE CLOSED - LOSS'
            
            # Direction emoji
            direction_emoji = '🟢' if trade['direction'] == 'LONG' else '🔴'
            
            # P/L formatting
            profit_loss = trade.get('profit_loss_pct', 0)
            if profit_loss > 0:
                pl_text = f"+{profit_loss:.2f}% 💰"
                pl_color = "green"
            elif profit_loss < 0:
                pl_text = f"{profit_loss:.2f}% 📉"
                pl_color = "red"
            else:
                pl_text = "0.00% ⚪"
                pl_color = "gray"
            
            # Win Rate emoji
            win_rate = stats.get('win_rate', 0)
            if win_rate >= 70:
                wr_emoji = '🔥'
            elif win_rate >= 60:
                wr_emoji = '✨'
            elif win_rate >= 50:
                wr_emoji = '📊'
            else:
                wr_emoji = '⚠️'
            
            message = f"""
{status_emoji} **{status_text}** {status_emoji}

{direction_emoji} **{trade['symbol']}** - {trade['timeframe']} - {trade['direction']}

💰 **Entry:** ${trade['entry_price']:.4f}
🏁 **Exit:** ${trade.get('exit_price', trade['current_price']):.4f}
📈 **Result:** {pl_text}

⏱ **Duration:** {self._format_duration(trade.get('created_at'), trade.get('closed_at'))}

━━━━━━━━━━━━━━━━━━
📊 **CURRENT PERFORMANCE**

{wr_emoji} **Win Rate:** {win_rate:.1f}% ({stats.get('tracked_trades', 0)} trades)
💰 **Avg Profit:** +{stats.get('avg_profit', 0):.2f}%
🛑 **Avg Loss:** -{stats.get('avg_loss', 0):.2f}%
🧠 **Learning Score:** {stats.get('learning_score', 0):.1f}/100

⏰ _Auto-learning active_
"""
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Trade close alert sent for {trade['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending trade close alert: {e}")
            return False
    
    def _format_duration(self, created_at, closed_at) -> str:
        """Format trade duration"""
        try:
            if not created_at or not closed_at:
                return "N/A"
            
            from datetime import datetime
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if isinstance(closed_at, str):
                closed_at = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
            
            duration = closed_at - created_at
            hours = duration.total_seconds() / 3600
            
            if hours < 1:
                return f"{int(hours * 60)}m"
            elif hours < 24:
                return f"{hours:.1f}h"
            else:
                days = hours / 24
                return f"{days:.1f}d"
        except:
            return "N/A"
    
    async def send_article(self, article: Dict, topic: str = 'news_articles') -> Dict:
        """
        Send news article to Telegram topic
        
        Args:
            article: Article dictionary with content, sources, etc.
            topic: Topic name (default: 'news_articles')
        
        Returns:
            Dict with success status and message_id if sent
        """
        if not self.is_available():
            logger.warning("Telegram not available")
            return {'success': False, 'error': 'Telegram not available'}
        
        try:
            content = article.get('content', '')
            
            # If content is too long, truncate and add "Read more" link
            MAX_LENGTH = 4000  # Telegram limit is 4096
            if len(content) > MAX_LENGTH:
                content = content[:MAX_LENGTH] + "\n\n... [Read more on dashboard]"
            
            # Get topic thread ID
            topic_id = self.get_topic_id(topic)
            
            # Send message
            message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=content,
                parse_mode='HTML',  # Use HTML for better formatting
                message_thread_id=topic_id,
                disable_web_page_preview=False  # Show link previews
            )
            
            logger.info(f"✅ Article sent to topic '{topic}' - Message ID: {message.message_id}")
            
            return {
                'success': True,
                'message_id': message.message_id,
                'topic': topic,
                'topic_id': topic_id
            }
            
        except TelegramError as e:
            logger.error(f"❌ Telegram send error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"❌ Unexpected error sending article: {e}")
            return {'success': False, 'error': str(e)}

