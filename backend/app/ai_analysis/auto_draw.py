"""
AI Auto-Draw endpoint
Returns coordinates for drawing lines on the chart
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class AutoDrawRequest(BaseModel):
    symbol: str
    timeframe: str
    candles: List[Dict[str, Any]]  # [{time, open, high, low, close, volume}, ...]


class LineCoordinate(BaseModel):
    type: str  # "support", "resistance", "trendline", "consolidation", "imbalance"
    coords: Dict[str, Any]  # Different for each type
    color: str
    label: str


@router.post("/auto-draw")
async def auto_draw_analysis(request: AutoDrawRequest):
    """
    Analyze chart and return coordinates for drawing lines
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise HTTPException(status_code=503, detail="AI service not configured")
        
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Prepare candle data for AI
        recent_candles = request.candles[-100:]  # Last 100 candles
        
        price_high = max(c['high'] for c in recent_candles)
        price_low = min(c['low'] for c in recent_candles)
        current_price = recent_candles[-1]['close']
        
        # Create AI prompt
        prompt = f"""Analyze this {request.symbol} chart on {request.timeframe} timeframe and identify key levels to draw.

Current Price: ${current_price:.2f}
Price Range: ${price_low:.2f} - ${price_high:.2f}

Recent {len(recent_candles)} candles data:
{recent_candles[-20:]}

Identify and return ONLY a JSON object (no markdown, no text before/after) with these drawing instructions:

{{
  "lines": [
    {{
      "type": "support",
      "price": 2920.50,
      "strength": "strong",
      "label": "Key support",
      "color": "#22c55e"
    }},
    {{
      "type": "resistance", 
      "price": 3150.00,
      "strength": "strong",
      "label": "Resistance zone",
      "color": "#ef4444"
    }},
    {{
      "type": "trendline",
      "points": [
        {{"time": "2024-12-15T00:00:00", "price": 3100}},
        {{"time": "2024-12-17T12:00:00", "price": 2950}}
      ],
      "label": "Downtrend",
      "color": "#3b82f6"
    }},
    {{
      "type": "imbalance",
      "top": 2980,
      "bottom": 2950,
      "time_start": "2024-12-16T08:00:00",
      "time_end": "2024-12-16T16:00:00",
      "label": "FVG bullish",
      "color": "rgba(34, 197, 94, 0.2)"
    }}
  ]
}}

Rules:
- Find 2-4 strong support/resistance levels
- Identify 1-2 trendlines if clear trend exists
- Mark 1-3 imbalance zones (FVG) if present
- Use ONLY these types: "support", "resistance", "trendline", "imbalance"
- Return ONLY JSON, no explanations"""

        # Call Claude
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON
        import json
        import re
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Find JSON object
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        lines_data = json.loads(json_match.group())
        
        logger.info(f"✅ Auto-draw analysis completed for {request.symbol}: {len(lines_data.get('lines', []))} lines")
        
        return {
            "success": True,
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "lines": lines_data.get('lines', [])
        }
        
    except Exception as e:
        logger.error(f"❌ Auto-draw error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
