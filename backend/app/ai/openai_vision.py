"""
OpenAI GPT-4o Vision Analyzer
Analyzes trading setups using AI vision
"""
import logging
import json
from typing import Dict, Optional, List
from openai import AsyncOpenAI
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


class OpenAIVisionAnalyzer:
    def __init__(self, api_key: str):
        """Initialize OpenAI client"""
        if not api_key:
            logger.error("❌ OpenAI API key not provided!")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("✅ OpenAI Vision analyzer initialized")
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.client is not None
    
    def generate_chart(
        self,
        symbol: str,
        ohlcv: List[List],
        timeframe: str
    ) -> str:
        """
        Generate Plotly chart as base64 image
        Returns: base64 encoded PNG
        """
        try:
            # Create candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=list(range(len(ohlcv))),
                open=[c[1] for c in ohlcv],
                high=[c[2] for c in ohlcv],
                low=[c[3] for c in ohlcv],
                close=[c[4] for c in ohlcv],
                name='Price'
            )])
            
            # Add volume
            fig.add_trace(go.Bar(
                x=list(range(len(ohlcv))),
                y=[c[5] for c in ohlcv],
                name='Volume',
                yaxis='y2',
                opacity=0.3
            ))
            
            # Layout
            fig.update_layout(
                title=f"{symbol} - {timeframe}",
                xaxis_title="Candles",
                yaxis_title="Price",
                yaxis2=dict(
                    title="Volume",
                    overlaying='y',
                    side='right'
                ),
                height=600,
                template='plotly_dark'
            )
            
            # Convert to image bytes
            img_bytes = fig.to_image(format="png", engine="kaleido")
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            logger.info(f"📊 Chart generated for {symbol} {timeframe}")
            return img_base64
            
        except Exception as e:
            logger.error(f"❌ Chart generation error: {e}")
            return ""
    
    async def analyze_setup(
        self,
        symbol: str,
        ohlcv: List[List],
        timeframe: str
    ) -> Optional[Dict]:
        """
        Analyze trading setup using GPT-4o Vision
        
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
            
            # Generate chart
            chart_base64 = self.generate_chart(symbol, ohlcv, timeframe)
            
            if not chart_base64:
                logger.warning("No chart generated, using text analysis")
                # Fallback to text-only analysis
                return await self._analyze_text_only(symbol, ohlcv, timeframe)
            
            # Prepare prompt
            prompt = f"""You are an expert crypto trader analyzing {symbol} on {timeframe} timeframe.

Current price: ${current_price:.2f}

Analyze the chart and provide:
1. Is this a valid trading setup? (true/false)
2. Confidence score (0-100)
3. Direction: LONG, SHORT, or NEUTRAL
4. Entry price
5. Stop loss price
6. Take profit price
7. Two-sentence technical rationale explaining your analysis

Respond in JSON format:
{{
  "valid": true/false,
  "confidence": 0-100,
  "direction": "LONG"|"SHORT"|"NEUTRAL",
  "entry": price,
  "stop_loss": price,
  "take_profit": price,
  "reasoning": "Two sentence explanation"
}}

Be critical - only suggest trades with clear setups."""

            # Call GPT-4o Vision
            logger.info(f"🤖 Calling GPT-4o Vision for {symbol}...")
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{chart_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            # Parse response
            content = response.choices[0].message.content
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
            
            logger.info(f"✅ Analysis complete: {symbol} - Confidence: {result.get('confidence', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AI analysis error for {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _analyze_text_only(
        self,
        symbol: str,
        ohlcv: List[List],
        timeframe: str
    ) -> Optional[Dict]:
        """Fallback: text-only analysis without chart"""
        try:
            current_price = ohlcv[-1][4]
            
            # Prepare candle data text
            recent_candles = ohlcv[-50:]  # Last 50 candles
            candles_text = "\n".join([
                f"#{i}: O:{c[1]:.2f} H:{c[2]:.2f} L:{c[3]:.2f} C:{c[4]:.2f} V:{c[5]:.0f}"
                for i, c in enumerate(recent_candles)
            ])
            
            prompt = f"""Analyze {symbol} on {timeframe} timeframe.

Current price: ${current_price:.2f}

Recent 50 candles (OHLCV):
{candles_text}

Provide JSON analysis:
{{
  "valid": true/false,
  "confidence": 0-100,
  "direction": "LONG"|"SHORT"|"NEUTRAL",
  "entry": price,
  "stop_loss": price,
  "take_profit": price,
  "reasoning": "Two sentence technical rationale"
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result['symbol'] = symbol
            result['timeframe'] = timeframe
            result['current_price'] = current_price
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Text analysis error: {e}")
            return None

