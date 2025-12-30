"""
Groq AI Analyzer (Alternative to Claude)
Ultra-fast inference with Llama models
"""
import logging
import json
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class GroqAnalyzer:
    def __init__(self, api_key: str):
        """Initialize Groq client"""
        if not api_key:
            logger.warning("⚠️  Groq API key not provided - Groq analyzer disabled")
            self.client = None
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
                logger.info("✅ Groq analyzer initialized (llama-3.3-70b-versatile)")
            except ImportError:
                logger.error("❌ Groq package not installed. Run: pip install groq")
                self.client = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Groq is available"""
        return self.client is not None
    
    async def analyze_setup(
        self,
        symbol: str,
        ohlcv: List[List],
        timeframe: str
    ) -> Optional[Dict]:
        """
        Analyze trading setup using Groq Llama
        
        Returns same format as Claude for compatibility
        """
        if not self.is_available():
            logger.warning("Groq not available")
            return None
        
        try:
            # Get current price
            current_price = ohlcv[-1][4]  # Close of last candle
            
            # Prepare last 100 candles
            recent_candles = ohlcv[-100:]
            
            # Format candles as text (compact format for speed)
            candles_text = "\n".join([
                f"#{i}: O:{c[1]:.2f} H:{c[2]:.2f} L:{c[3]:.2f} C:{c[4]:.2f} V:{c[5]:.0f}"
                for i, c in enumerate(recent_candles)
            ])
            
            # Prepare prompt (same as Claude for consistency)
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

            # Call Groq (synchronous, but very fast!)
            logger.info(f"🚀 Calling Groq AI for {symbol}...")
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and accurate
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.info(f"📄 Groq response: {content[:200]}...")
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result['symbol'] = symbol
            result['timeframe'] = timeframe
            result['current_price'] = current_price
            result['ai_provider'] = 'groq'  # Mark as Groq
            
            logger.info(f"✅ Groq analysis complete: {symbol} - Confidence: {result.get('confidence', 0)}%")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Groq analysis error for {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

