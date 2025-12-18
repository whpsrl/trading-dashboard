"""
Market Scanner Service
Scansiona tutte le crypto disponibili e trova i migliori setup con AI
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class MarketScannerService:
    def __init__(self):
        """Initialize scanner with AI client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - Scanner disabled")
            self.client = None
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
                logger.info("✅ Market Scanner AI initialized")
            except ImportError:
                logger.error("❌ anthropic package not installed")
                self.client = None
        
        # API base URL - usa Railway production
        self.api_base = os.getenv(
            'API_BASE_URL',
            'https://trading-dashboard-production-79d9.up.railway.app'
        )
    
    def is_available(self) -> bool:
        """Check if scanner is available"""
        return self.client is not None
    
    async def get_crypto_list(self) -> List[str]:
        """Get list of crypto symbols to scan"""
        # Top 30 crypto per market cap
        return [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
            "LINKUSDT", "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT",
            "NEARUSDT", "ALGOUSDT", "ICPUSDT", "FILUSDT", "APTUSDT",
            "ARBUSDT", "OPUSDT", "INJUSDT", "SUIUSDT", "SEIUSDT",
            "TIAUSDT", "RENDERUSDT", "WLDUSDT", "RUNEUSDT", "THETAUSDT"
        ]
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> Optional[Dict]:
        """Fetch OHLCV data for a symbol"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.api_base}/api/crypto/{symbol}"
                params = {
                    "timeframe": timeframe,
                    "limit": limit
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"⚠️ {symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ {symbol} fetch error: {str(e)}")
            return None
    
    def format_candles_for_ai(self, data: Dict, symbol: str) -> str:
        """Format OHLCV data for AI analysis"""
        
        if not data or 'data' not in data:
            return ""
        
        candles = data['data']
        if not candles or len(candles) < 50:
            return ""
        
        # Ultimi 100 candles
        recent = candles[-100:]
        latest = recent[-1]
        oldest = recent[0]
        
        # Calcoli
        closes = [c['close'] for c in recent]
        highs = [c['high'] for c in recent]
        lows = [c['low'] for c in recent]
        volumes = [c['volume'] for c in recent]
        
        price_change_pct = ((latest['close'] - oldest['open']) / oldest['open']) * 100
        
        # Format per AI
        text = f"""# {symbol} - Dati Tecnici

## Snapshot Attuale
Prezzo: ${latest['close']:.2f}
Open: ${latest['open']:.2f} | High: ${latest['high']:.2f} | Low: ${latest['low']:.2f}
Volume: {latest['volume']:.2f}

## Performance Recente (100 candles)
Variazione: {price_change_pct:+.2f}%
High periodo: ${max(highs):.2f}
Low periodo: ${min(lows):.2f}
Volume medio: {sum(volumes)/len(volumes):.2f}

## Ultimi 20 Candles (più recenti in fondo)
"""
        
        for i, c in enumerate(recent[-20:], 1):
            text += f"{i}. O:{c['open']:.2f} H:{c['high']:.2f} L:{c['low']:.2f} C:{c['close']:.2f} V:{c['volume']:.0f}\n"
        
        return text
    
    async def analyze_with_ai(self, symbol: str, candle_data: str) -> Optional[Dict]:
        """Analyze symbol with Claude AI"""
        
        if not self.client or not candle_data:
            return None
        
        prompt = f"""Sei un trader professionista. Analizza {symbol} e determina se c'è un setup valido.

{candle_data}

ANALIZZA:
1. TREND: uptrend/downtrend/ranging?
2. PATTERN: candlestick patterns o chart patterns?
3. LIVELLI: supporti/resistenze chiave?
4. VOLUME: conferma i movimenti?
5. MOMENTUM: forza direzionale?

SETUP VALIDO richiede minimo 3 confluenze tecniche.

Se setup valido, fornisci:
- Direzione: LONG/SHORT
- Entry: prezzo preciso
- Stop Loss: livello + % distanza
- Target 1 e Target 2
- R:R ratio
- Score: 1-10 (minimo 7 per validità)
- Confluenze: lista dei fattori

Se NON valido, rispondi: "NO_SETUP"

IMPORTANTE:
- Sii conservativo
- Score < 7 = NO_SETUP
- R:R minimo 1:2

Formato JSON:
{{
  "valid": true/false,
  "score": 0-10,
  "direction": "LONG/SHORT/NONE",
  "entry": price,
  "stop_loss": price,
  "target_1": price,
  "target_2": price,
  "risk_reward": ratio,
  "confluences": ["motivo1", "motivo2", ...],
  "reasoning": "spiegazione breve"
}}"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Estrai contenuto
            content = response.content[0].text
            
            # Parse JSON
            import json
            import re
            
            # Rimuovi markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            result['symbol'] = symbol
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AI error {symbol}: {str(e)}")
            return None
    
    async def scan_market(
        self,
        timeframe: str = "1h",
        min_score: float = 7.0,
        max_concurrent: int = 3
    ) -> List[Dict]:
        """
        Full market scan with AI analysis
        
        Args:
            timeframe: candlestick timeframe
            min_score: minimum score to include
            max_concurrent: parallel requests limit
        
        Returns:
            List of valid setups sorted by score
        """
        
        if not self.is_available():
            logger.error("❌ Scanner not available - AI not configured")
            return []
        
        logger.info(f"🚀 Starting market scan: timeframe={timeframe}, min_score={min_score}")
        
        symbols = await self.get_crypto_list()
        logger.info(f"📊 Scanning {len(symbols)} cryptocurrencies...")
        
        results = []
        
        # Process in batches
        for i in range(0, len(symbols), max_concurrent):
            batch = symbols[i:i + max_concurrent]
            batch_num = i // max_concurrent + 1
            
            logger.info(f"🔍 Batch {batch_num}: {', '.join(batch)}")
            
            # Fetch data in parallel
            fetch_tasks = [self.fetch_ohlcv(sym, timeframe) for sym in batch]
            batch_data = await asyncio.gather(*fetch_tasks)
            
            # Analyze each
            for symbol, data in zip(batch, batch_data):
                if data:
                    # Format
                    formatted = self.format_candles_for_ai(data, symbol)
                    
                    if formatted:
                        # AI analysis
                        analysis = await self.analyze_with_ai(symbol, formatted)
                        
                        if analysis and analysis.get('valid') and analysis.get('score', 0) >= min_score:
                            results.append(analysis)
                            logger.info(f"  ✅ {symbol}: Score {analysis['score']}/10 - {analysis['direction']}")
                        else:
                            logger.info(f"  ⏭️  {symbol}: No valid setup")
                
                # Rate limiting
                await asyncio.sleep(1)
            
            # Batch delay
            await asyncio.sleep(2)
        
        # Sort by score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"🎯 Scan complete! Found {len(results)} valid setups")
        
        return results


# Global instance
scanner_service = MarketScannerService()
