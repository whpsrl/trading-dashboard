from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import anthropic
import os
import json
import re

router = APIRouter()

class AnalysisRequest(BaseModel):
    prompt: str

class AnalysisResponse(BaseModel):
    analysis: str

class AutoDrawRequest(BaseModel):
    symbol: str
    timeframe: str
    candles: List[Dict[str, Any]]
    drawType: str  # 'support_resistance', 'trendlines', 'imbalances', 'consolidations'

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chart(request: AnalysisRequest):
    """
    Analizza i dati del grafico usando Claude AI
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]
        )
        
        # Estrai il contenuto della risposta
        analysis_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                analysis_text += block.text
        
        return AnalysisResponse(analysis=analysis_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/auto-draw")
async def auto_draw_lines(request: AutoDrawRequest):
    """
    AI identifica livelli chiave e restituisce coordinate per disegnare linee
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prepare data
        recent_candles = request.candles[-100:]
        price_high = max(c['high'] for c in recent_candles)
        price_low = min(c['low'] for c in recent_candles)
        current_price = recent_candles[-1]['close']
        
        # Create prompt based on draw type
        if request.drawType == 'support_resistance':
            prompt_instruction = """Identifica i 3-5 livelli di SUPPORT e RESISTANCE più importanti.
Per ogni livello restituisci:
- type: "support" o "resistance"
- price: prezzo esatto del livello
- strength: "strong", "medium", "weak"
- label: breve descrizione (es: "Key support", "Resistance zone")"""
        
        elif request.drawType == 'trendlines':
            prompt_instruction = """Identifica 1-2 TRENDLINE principali (rialzista o ribassista).
Per ogni trendline restituisci:
- type: "trendline"
- points: array di 2-3 punti [{time: "ISO date", price: number}, ...]
- label: "Uptrend" o "Downtrend"
- color: colore suggerito"""
        
        elif request.drawType == 'imbalances':
            prompt_instruction = """Identifica 2-4 zone di IMBALANCE/FVG (Fair Value Gap).
Per ogni imbalance restituisci:
- type: "imbalance"
- top: prezzo superiore
- bottom: prezzo inferiore
- time_start: timestamp inizio
- time_end: timestamp fine
- label: "Bullish FVG" o "Bearish FVG"
- color: "rgba(34, 197, 94, 0.2)" per bullish, "rgba(239, 68, 68, 0.2)" per bearish"""
        
        elif request.drawType == 'consolidations':
            prompt_instruction = """Identifica 1-3 zone di CONSOLIDAZIONE (range laterale).
Per ogni consolidation restituisci:
- type: "consolidation"
- top: prezzo superiore del range
- bottom: prezzo inferiore del range
- time_start: timestamp inizio
- time_end: timestamp fine
- label: "Consolidation zone"
- color: "rgba(139, 92, 246, 0.15)" """
        
        else:
            raise HTTPException(status_code=400, detail="Invalid drawType")
        
        prompt = f"""Analizza questo grafico {request.symbol} su timeframe {request.timeframe}.

Prezzo attuale: ${current_price:.2f}
Range: ${price_low:.2f} - ${price_high:.2f}
Ultimi 20 candles: {recent_candles[-20:]}

{prompt_instruction}

Restituisci SOLO un oggetto JSON (senza markdown, senza testo) in questo formato:
{{
  "lines": [
    {{ oggetti come specificato sopra }}
  ]
}}

IMPORTANTE: Rispondi SOLO con il JSON, niente altro."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Clean response
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Parse JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("No JSON found in AI response")
        
        lines_data = json.loads(json_match.group())
        
        return {
            "success": True,
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "drawType": request.drawType,
            "lines": lines_data.get('lines', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-draw failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check per l'endpoint AI"""
    return {"status": "online", "service": "ai-analysis"}
