"""
Claude AI Analyzer
Analyzes trading setups using Anthropic Claude
"""
import logging
import json
from typing import Dict, Optional, List
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    def __init__(self, api_key: str):
        """Initialize Claude client"""
        if not api_key:
            logger.error("❌ Anthropic API key not provided!")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=api_key)
            logger.info("✅ Claude analyzer initialized")
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.client is not None
    
    async def analyze_setup(
        self,
        symbol: str,
        ohlcv: List[List],
        timeframe: str
    ) -> Optional[Dict]:
        """
        Analyze trading setup using Claude
        
        Returns:
        {
            'valid': bool,
            'confidence': 0-100,
            'direction': 'LONG'|'SHORT'|'NEUTRAL',
            'entry': float,
            'stop_loss': float,
            'take_profit': float,
            'reasoning': 'AI 2-sentence rationale'
        }
        """
        if not self.is_available():
            logger.warning("AI not available")
            return None
        
        try:
            # Get current price
            current_price = ohlcv[-1][4]  # Close of last candle
            
            # Prepare last 100 candles for analysis
            recent_candles = ohlcv[-100:]
            
            # Format candles as text
            candles_text = "\n".join([
                f"#{i}: Open:{c[1]:.2f} High:{c[2]:.2f} Low:{c[3]:.2f} Close:{c[4]:.2f} Volume:{c[5]:.0f}"
                for i, c in enumerate(recent_candles)
            ])
            
            # Prepare prompt
            prompt = f"""You are an expert institutional crypto trader analyzing {symbol} on {timeframe} timeframe.

Current price: ${current_price:.2f}

Last 100 candles (OHLCV data):
{candles_text}

Analyze this data and provide a trading recommendation in JSON format:

{{
  "valid": true/false,
  "confidence": 0-100,
  "direction": "LONG"|"SHORT"|"NEUTRAL",
  "entry": price,
  "stop_loss": price,
  "take_profit": price,
  "reasoning": "Two sentence technical rationale explaining your analysis"
}}

Consider:
- Trend direction and strength
- Support and resistance levels
- Volume patterns
- Price action and momentum
- Risk/reward ratio

Be critical - only recommend trades with clear, high-probability setups. 
If the setup is unclear or risky, set valid to false and confidence below 60."""

            # Call Claude
            logger.info(f"🤖 Calling Claude AI for {symbol}...")
            
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text
            logger.info(f"📄 AI response: {content[:200]}...")
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result['symbol'] = symbol
            result['timeframe'] = timeframe
            result['current_price'] = current_price
            
            logger.info(f"✅ Analysis complete: {symbol} - Confidence: {result.get('confidence', 0)}%")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AI analysis error for {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

