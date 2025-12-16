"""
AI Analysis Service
Uses Claude Sonnet 4 to analyze market data
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAnalysisService:
    def __init__(self):
        """Initialize Claude API client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - AI analysis disabled")
            self.client = None
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
                logger.info("✅ Claude AI initialized")
            except ImportError:
                logger.error("❌ anthropic package not installed")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.client is not None
    
    async def analyze_market(
        self,
        symbol: str,
        current_price: float,
        price_change_24h: float,
        volume_24h: float = None,
        ohlcv_data: List[List] = None,
        timeframe: str = "1h"
    ) -> Dict:
        """
        Analyze market data using Claude AI
        
        Returns sentiment, signals, risk assessment, recommendations
        """
        if not self.client:
            return {
                "available": False,
                "message": "AI Analysis not available - ANTHROPIC_API_KEY not configured"
            }
        
        try:
            # Prepare market summary
            market_summary = self._prepare_summary(
                symbol, current_price, price_change_24h, volume_24h, ohlcv_data, timeframe
            )
            
            # Create prompt for Claude
            prompt = f"""Analyze this market data and provide trading insights:

{market_summary}

Provide a JSON response with:
{{
    "sentiment": "Bullish|Bearish|Neutral",
    "confidence": 0-100,
    "trend": "Strong Uptrend|Uptrend|Sideways|Downtrend|Strong Downtrend",
    "signals": [
        {{"type": "BUY|SELL|HOLD", "strength": "Strong|Moderate|Weak", "reason": "..."}}
    ],
    "technical_analysis": "...",
    "risk_level": "Low|Medium|High",
    "key_points": ["...", "..."],
    "recommendation": "..."
}}

Be concise and actionable."""

            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = {
                    "sentiment": "Neutral",
                    "confidence": 50,
                    "trend": "Analysis in progress",
                    "signals": [],
                    "technical_analysis": response_text,
                    "risk_level": "Medium",
                    "key_points": [],
                    "recommendation": "See full analysis"
                }
            
            logger.info(f"✅ AI analysis completed for {symbol}")
            
            return {
                "available": True,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis_data
            }
            
        except Exception as e:
            logger.error(f"❌ AI Analysis error: {e}")
            return {
                "available": True,
                "error": str(e),
                "message": "AI analysis temporarily unavailable"
            }
    
    def _prepare_summary(
        self,
        symbol: str,
        current_price: float,
        price_change_24h: float,
        volume_24h: Optional[float],
        ohlcv_data: Optional[List[List]],
        timeframe: str
    ) -> str:
        """Prepare market data summary for Claude"""
        
        summary = f"""
Symbol: {symbol}
Current Price: ${current_price:,.2f}
24h Change: {price_change_24h:+.2f}%
Timeframe: {timeframe}
"""
        
        if volume_24h:
            summary += f"24h Volume: ${volume_24h / 1e9:.2f}B\n"
        
        if ohlcv_data and len(ohlcv_data) > 0:
            recent_candles = ohlcv_data[-10:]
            
            highs = [c[2] for c in recent_candles]
            lows = [c[3] for c in recent_candles]
            closes = [c[4] for c in recent_candles]
            
            summary += f"""
Recent Range (last 10 candles):
- High: ${max(highs):,.2f}
- Low: ${min(lows):,.2f}

Recent Price Action:
"""
            for i, candle in enumerate(recent_candles[-5:], 1):
                open_p, high, low, close = candle[1:5]
                candle_type = "🟢 Bullish" if close > open_p else "🔴 Bearish"
                change = ((close - open_p) / open_p) * 100
                summary += f"Candle {i}: {candle_type} ({change:+.2f}%)\n"
        
        return summary


# Global AI service instance
ai_service = AIAnalysisService()
