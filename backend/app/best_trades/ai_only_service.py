"""
AI-ONLY Trading Analysis Service
L'AI analizza direttamente le candele senza indicatori pre-calcolati
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIOnlyTradingService:
    """
    Servizio che usa SOLO l'AI per l'analisi
    """
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not set!")
            self.client = None
        else:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                logger.info("✅ AI-Only Service initialized with Gemini 2.0")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        return self.client is not None
    
    async def analyze_symbol(self, symbol: str, candles: List[Dict]) -> Optional[Dict]:
        """
        AI analizza direttamente le candele
        """
        if not self.client:
            logger.warning(f"AI not available for {symbol}")
            return None
        
        if not candles or len(candles) < 100:
            logger.warning(f"{symbol}: Not enough candles")
            return None
        
        try:
            # Prepara ultimi 50 candles per l'AI
            recent_candles = candles[-50:]
            current_price = candles[-1]['close']
            
            # Crea prompt per AI
            candles_text = "\n".join([
                f"#{i+1}: O:{c['open']:.2f} H:{c['high']:.2f} L:{c['low']:.2f} C:{c['close']:.2f} Vol:{c['volume']:.0f}"
                for i, c in enumerate(recent_candles)
            ])
            
            prompt = f"""Sei un TRADER PROFESSIONISTA. Analizza {symbol} e fornisci un'analisi COMPLETA.

DATI CANDELE (ultimi 50):
{candles_text}

PREZZO ATTUALE: ${current_price:.2f}

ANALIZZA:
1. Trend principale (uptrend/downtrend/range)
2. Supporti e resistenze chiave
3. Pattern candlestick significativi
4. Volume e momentum
5. Struttura di mercato
6. Setup di trading valido?

RISPONDI IN JSON:
{{
  "valid": true/false,
  "score": 0-100,
  "direction": "LONG"|"SHORT"|"NEUTRAL",
  "confidence": 0-100,
  "current_price": {current_price},
  "entry_price": prezzo_entry_ottimale,
  "stop_loss": prezzo_stoploss,
  "target_1": primo_target,
  "target_2": secondo_target,
  "risk_reward_t1": ratio_rischio_rendimento,
  "timeframe_suggestion": "immediate|wait_pullback|avoid",
  "key_levels": {{"support": [prezzi], "resistance": [prezzi]}},
  "patterns": ["pattern1", "pattern2"],
  "analysis": "Analisi dettagliata in 2-3 frasi",
  "risk_factors": ["rischio1", "rischio2"],
  "why_trade": "Motivo principale per questo trade in 1 frase"
}}

IMPORTANTE: 
- Score basso (<60) se setup non chiaro
- Score alto (80+) solo se setup MOLTO forte
- Sii CRITICO, meglio dire NO che dare falsi segnali"""

            # Chiama AI
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            # Parse risposta
            import json
            content = response.text
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            ai_result = json.loads(content.strip())
            
            # Aggiungi info aggiuntive
            ai_result['symbol'] = symbol
            ai_result['timestamp'] = datetime.now().isoformat()
            ai_result['exchange'] = 'binance'
            
            logger.info(f"✅ AI analysis for {symbol}: Score {ai_result.get('score', 0)}, Direction {ai_result.get('direction', 'N/A')}")
            
            return ai_result
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed for {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None


# Singleton
ai_only_service = AIOnlyTradingService()

