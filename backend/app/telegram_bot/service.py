"""
Telegram Bot Service
Invia notifiche e risponde a comandi per best trades
"""
import os
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Bot Telegram per notifiche best trades
    """
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️ Telegram not configured - notifications disabled")
        else:
            logger.info(f"✅ Telegram Bot initialized - Chat ID: {self.chat_id}")
    
    def is_available(self) -> bool:
        """Check if Telegram is configured"""
        return bool(self.bot_token and self.chat_id)
    
    def format_opportunity_message(self, opp: Dict) -> str:
        """
        Format trading opportunity as Telegram message
        """
        # Emoji per direction
        direction_emoji = "📈" if opp['direction'] == 'LONG' else "📉" if opp['direction'] == 'SHORT' else "➡️"
        
        # Score color (emoji)
        if opp['score'] >= 80:
            score_emoji = "🔥"
        elif opp['score'] >= 70:
            score_emoji = "✅"
        elif opp['score'] >= 60:
            score_emoji = "👍"
        else:
            score_emoji = "⚠️"
        
        # Category emoji
        symbol = opp['symbol']
        if 'USDT' in symbol or '/' in symbol:
            category = "🪙 CRYPTO"
        elif opp.get('exchange') == 'forex':
            category = "💱 FOREX"
        elif symbol in ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI']:
            category = "📊 INDEX"
        elif symbol in ['GLD', 'SLV', 'USO', 'UNG']:
            category = "🥇 COMMODITY"
        else:
            category = "📈 STOCK"
        
        message = f"""
{category}
━━━━━━━━━━━━━━━━━━━━

{score_emoji} **{symbol}**

⭐ **Score:** {opp['score']:.0f}/100
{direction_emoji} **Direction:** {opp['direction']}
💪 **Confidence:** {opp['confidence']:.0f}%

💰 **Trade Plan:**
├ Entry: ${opp['current_price']:.2f}
├ Stop Loss: ${opp['trade_levels']['stop_loss']:.2f}
├ Target 1: ${opp['trade_levels']['target_1']:.2f} (R:R {opp['trade_levels']['risk_reward_ratio_t1']:.1f}:1)
└ Target 2: ${opp['trade_levels']['target_2']:.2f} (R:R {opp['trade_levels']['risk_reward_ratio_t2']:.1f}:1)

✅ **Confluences ({len(opp['confluences'])}):**
{chr(10).join(f'  • {c}' for c in opp['confluences'][:3])}
"""
        
        # Add AI insights if available
        if opp.get('ai_insights') and opp['ai_insights'].get('valid'):
            ai = opp['ai_insights']
            message += f"""
🤖 **AI Validation:** {ai.get('validation_score', 0)}/10
💡 {ai.get('recommendation', '')[:150]}...
"""
        
        return message.strip()
    
    def format_scan_summary(self, opportunities: List[Dict], preset: str, total_scanned: int) -> str:
        """
        Format scan summary message
        """
        # Group by category
        crypto = [o for o in opportunities if 'USDT' in o['symbol']]
        stocks = [o for o in opportunities if o['symbol'] not in ['SPY', 'QQQ', 'DIA', 'IWM'] and 'USDT' not in o['symbol'] and '/' not in o['symbol']]
        indices = [o for o in opportunities if o['symbol'] in ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI']]
        commodities = [o for o in opportunities if o['symbol'] in ['GLD', 'SLV', 'USO', 'UNG', 'CORN', 'WEAT']]
        forex = [o for o in opportunities if o.get('exchange') == 'forex' or ('/' in o['symbol'] and 'USDT' not in o['symbol'])]
        
        message = f"""
🎯 **MARKET SCAN COMPLETE**
━━━━━━━━━━━━━━━━━━━━

📊 Preset: **{preset.upper()}**
🔍 Assets Scanned: **{total_scanned}**
✅ Opportunities Found: **{len(opportunities)}**

**By Category:**
🪙 Crypto: {len(crypto)}
📈 Stocks: {len(stocks)}
📊 Indices: {len(indices)}
🥇 Commodities: {len(commodities)}
💱 Forex: {len(forex)}

**Top 3 Opportunities:**
"""
        
        # Add top 3
        for i, opp in enumerate(opportunities[:3], 1):
            direction_emoji = "📈" if opp['direction'] == 'LONG' else "📉"
            message += f"{i}. {opp['symbol']} - {direction_emoji} {opp['direction']} (Score: {opp['score']:.0f})\n"
        
        return message.strip()
    
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send message to Telegram chat
        """
        if not self.is_available():
            logger.warning("Telegram not configured, skipping message")
            return False
        
        try:
            import httpx
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    logger.info("✅ Telegram message sent")
                    return True
                else:
                    logger.error(f"❌ Telegram error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    async def send_opportunities(self, opportunities: List[Dict], max_messages: int = 5):
        """
        Send multiple opportunities (respects rate limits)
        """
        if not opportunities:
            return
        
        sent = 0
        for opp in opportunities[:max_messages]:
            message = self.format_opportunity_message(opp)
            success = await self.send_message(message)
            
            if success:
                sent += 1
                # Telegram rate limit: ~30 msg/sec, we use 1 msg/sec to be safe
                await asyncio.sleep(1)
            else:
                break
        
        logger.info(f"📤 Sent {sent}/{len(opportunities)} opportunities to Telegram")
    
    async def send_scan_complete(self, opportunities: List[Dict], preset: str, total_scanned: int):
        """
        Send scan complete summary
        """
        summary = self.format_scan_summary(opportunities, preset, total_scanned)
        await self.send_message(summary)
        
        # Send top opportunities
        if opportunities:
            await asyncio.sleep(1)
            await self.send_opportunities(opportunities, max_messages=3)
    
    async def send_alert(self, title: str, message: str):
        """
        Send generic alert
        """
        text = f"🔔 **{title}**\n\n{message}"
        await self.send_message(text)
    
    async def test_connection(self) -> Dict:
        """
        Test Telegram connection
        """
        if not self.is_available():
            return {
                'success': False,
                'message': 'Telegram not configured'
            }
        
        try:
            import httpx
            
            url = f"{self.base_url}/getMe"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_info = data.get('result', {})
                    
                    return {
                        'success': True,
                        'bot_username': bot_info.get('username'),
                        'bot_name': bot_info.get('first_name'),
                        'chat_id': self.chat_id
                    }
                else:
                    return {
                        'success': False,
                        'message': f'API Error: {response.status_code}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


# Global instance
telegram_bot = TelegramBotService()

