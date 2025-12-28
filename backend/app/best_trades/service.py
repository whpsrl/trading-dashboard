"""
Best Trades AI Service
Combina analisi tecnica con AI per trovare le migliori opportunità di trading
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from ..indicators.technical import technical_indicators
from .scoring import trade_scorer

logger = logging.getLogger(__name__)


class BestTradesService:
    """
    Trova e analizza le migliori opportunità di trading usando:
    1. Analisi tecnica multi-indicatore
    2. Sistema di scoring
    3. AI Claude per validazione e insights
    """
    
    def __init__(self):
        """Initialize with AI client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - AI analysis limited")
            self.client = None
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
                logger.info("✅ Best Trades AI initialized")
            except ImportError:
                logger.error("❌ anthropic package not installed")
                self.client = None
    
    def is_ai_available(self) -> bool:
        """Check if AI is available"""
        return self.client is not None
    
    async def analyze_symbol(
        self,
        symbol: str,
        candles: List[Dict],
        exchange: str = "binance"
    ) -> Optional[Dict]:
        """
        Analizza un singolo simbolo per opportunità di trading
        
        Args:
            symbol: Trading symbol (e.g., BTC/USDT)
            candles: OHLCV candles data
            exchange: Exchange name
        
        Returns:
            Complete trade analysis with score, direction, levels, AI insights
        """
        if not candles or len(candles) < 50:
            logger.warning(f"{symbol}: Not enough candles for analysis")
            return None
        
        try:
            # Step 1: Calculate technical indicators
            indicators = technical_indicators.calculate_all(candles)
            
            if not indicators:
                logger.warning(f"{symbol}: Failed to calculate indicators")
                return None
            
            # Step 2: Calculate trade score
            score_data = trade_scorer.calculate_total_score(indicators)
            
            # Step 3: If score is good, get AI validation
            ai_insights = None
            if score_data['total_score'] >= 60 and self.is_ai_available():
                ai_insights = await self._get_ai_validation(
                    symbol, candles, indicators, score_data
                )
            
            # Step 4: Calculate entry/exit levels
            trade_levels = self._calculate_trade_levels(
                indicators, score_data['direction']
            )
            
            # Step 5: Build complete analysis
            analysis = {
                'symbol': symbol,
                'exchange': exchange,
                'timestamp': datetime.now().isoformat(),
                'score': score_data['total_score'],
                'direction': score_data['direction'],
                'confidence': score_data['confidence'],
                'current_price': indicators['current_price'],
                'indicators': {
                    'rsi': indicators.get('rsi'),
                    'macd': indicators.get('macd'),
                    'trend': indicators.get('trend'),
                    'bollinger_bands': indicators.get('bollinger_bands'),
                    'support_resistance': indicators.get('support_resistance')
                },
                'confluences': score_data['confluences'],
                'warnings': score_data['warnings'],
                'trade_levels': trade_levels,
                'ai_insights': ai_insights,
                'recommendation': self._generate_recommendation(score_data, trade_levels, ai_insights)
            }
            
            logger.info(f"✅ {symbol}: Score {score_data['total_score']:.1f} - {score_data['direction']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def _calculate_trade_levels(self, indicators: Dict, direction: str) -> Dict:
        """
        Calculate entry, stop loss, and target levels based on indicators.
        Targets are realistic and based on actual S/R analysis and trend strength.
        """
        current_price = indicators['current_price']
        atr = indicators.get('atr', current_price * 0.02)  # Default 2% if no ATR
        bb_data = indicators.get('bollinger_bands', {})
        sr_data = indicators.get('support_resistance', {})
        trend_data = indicators.get('trend', {})
        
        # Considera la forza del trend per target più solidi in trend forti
        trend_strength = trend_data.get('strength', 50) if trend_data else 50
        # Multiplier: 1.0 (trend debole) -> 1.5 (trend fortissimo)
        trend_multiplier = 1.0 + (max(trend_strength - 50, 0) / 100)
        
        if direction == 'LONG':
            entry = current_price
            
            # Stop loss: below nearest support or 2 ATR
            support_levels = sr_data.get('support_levels', [])
            if support_levels:
                stop_loss = support_levels[0] - (atr * 0.5)
            else:
                stop_loss = current_price - (atr * 2)
            
            # Targets: basati su resistance REALI identificate nell'analisi
            resistance_levels = sr_data.get('resistance_levels', [])
            
            if resistance_levels and len(resistance_levels) >= 2:
                # Abbiamo almeno 2 resistance chiare: usiamole
                target_1 = resistance_levels[0]
                target_2 = resistance_levels[1]
            elif resistance_levels and len(resistance_levels) == 1:
                # Solo 1 resistance: usala come T1, estendi con Fibonacci per T2
                target_1 = resistance_levels[0]
                move = resistance_levels[0] - entry
                target_2 = entry + (move * 1.618)  # Estensione Fibonacci
            else:
                # Nessuna resistance chiara: usa ATR modulato dal trend
                target_1 = current_price + (atr * 4 * trend_multiplier)
                target_2 = current_price + (atr * 7 * trend_multiplier)
            
        elif direction == 'SHORT':
            entry = current_price
            
            # Stop loss: above nearest resistance or 2 ATR
            resistance_levels = sr_data.get('resistance_levels', [])
            if resistance_levels:
                stop_loss = resistance_levels[0] + (atr * 0.5)
            else:
                stop_loss = current_price + (atr * 2)
            
            # Targets: basati su support REALI identificati nell'analisi
            support_levels = sr_data.get('support_levels', [])
            
            if support_levels and len(support_levels) >= 2:
                # Abbiamo almeno 2 support chiari: usiamoli
                target_1 = support_levels[0]
                target_2 = support_levels[1]
            elif support_levels and len(support_levels) == 1:
                # Solo 1 support: usalo come T1, estendi con Fibonacci per T2
                target_1 = support_levels[0]
                move = entry - support_levels[0]
                target_2 = entry - (move * 1.618)  # Estensione Fibonacci
            else:
                # Nessun support chiaro: usa ATR modulato dal trend
                target_1 = current_price - (atr * 4 * trend_multiplier)
                target_2 = current_price - (atr * 7 * trend_multiplier)
        
        else:  # NEUTRAL
            return {
                'entry': current_price,
                'stop_loss': None,
                'target_1': None,
                'target_2': None,
                'risk_reward_ratio': None,
                'risk_percent': None
            }
        
        # Calculate risk/reward
        risk = abs(entry - stop_loss)
        reward_1 = abs(target_1 - entry)
        reward_2 = abs(target_2 - entry)
        
        risk_reward_1 = reward_1 / risk if risk > 0 else 0
        risk_reward_2 = reward_2 / risk if risk > 0 else 0
        
        risk_percent = (risk / current_price) * 100
        
        return {
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'risk_reward_ratio_t1': round(risk_reward_1, 2),
            'risk_reward_ratio_t2': round(risk_reward_2, 2),
            'risk_percent': round(risk_percent, 2),
            'atr': round(atr, 2)
        }
    
    async def _get_ai_validation(
        self,
        symbol: str,
        candles: List[Dict],
        indicators: Dict,
        score_data: Dict
    ) -> Optional[Dict]:
        """
        Get AI validation and additional insights for high-scoring trades
        """
        if not self.client:
            return None
        
        try:
            # Prepare comprehensive market context for AI
            total_candles = len(candles)
            
            # Analisi su più timeframe
            recent_100 = candles[-100:] if len(candles) >= 100 else candles
            recent_50 = candles[-50:] if len(candles) >= 50 else candles
            recent_20 = candles[-20:]
            
            # Calcoli statistici avanzati
            closes_100 = [c['close'] for c in recent_100]
            highs_100 = [c['high'] for c in recent_100]
            lows_100 = [c['low'] for c in recent_100]
            volumes_100 = [c['volume'] for c in recent_100]
            
            price_change_100 = ((closes_100[-1] - closes_100[0]) / closes_100[0]) * 100
            price_change_50 = ((candles[-1]['close'] - candles[-50]['close']) / candles[-50]['close']) * 100 if len(candles) >= 50 else 0
            price_change_20 = ((candles[-1]['close'] - candles[-20]['close']) / candles[-20]['close']) * 100 if len(candles) >= 20 else 0
            
            volatility = (max(highs_100) - min(lows_100)) / min(lows_100) * 100
            avg_volume = sum(volumes_100) / len(volumes_100)
            current_volume = candles[-1]['volume']
            volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1
            
            # Trova swing highs/lows significativi
            swing_highs = sorted(highs_100, reverse=True)[:5]
            swing_lows = sorted(lows_100)[:5]
            
            prompt = f"""Sei un TRADER PROFESSIONISTA ISTITUZIONALE con 20+ anni di esperienza. Conduci un'analisi APPROFONDITA e DETTAGLIATA di questo asset.

═══════════════════════════════════════════════════════════════
📊 {symbol} - ANALISI ISTITUZIONALE COMPLETA
═══════════════════════════════════════════════════════════════

💰 PREZZO CORRENTE: ${indicators['current_price']:.2f}
🎯 BIAS TECNICO: {score_data['direction']}
⭐ SCORE ALGORITMO: {score_data['total_score']:.1f}/100
💪 CONFIDENCE TECNICA: {score_data['confidence']:.1f}%

═══════════════════════════════════════════════════════════════
📈 ANALISI MULTI-TIMEFRAME - PERFORMANCE STORICA
═══════════════════════════════════════════════════════════════

📊 Variazione 100 periodi: {price_change_100:+.2f}%
📊 Variazione 50 periodi:  {price_change_50:+.2f}%
📊 Variazione 20 periodi:  {price_change_20:+.2f}%

💎 Range totale: ${min(lows_100):.2f} - ${max(highs_100):.2f}
🌊 Volatilità realizzata: {volatility:.1f}%
📍 Posizione nel range: {((indicators['current_price'] - min(lows_100)) / (max(highs_100) - min(lows_100)) * 100):.1f}%

═══════════════════════════════════════════════════════════════
🔬 INDICATORI TECNICI - ANALISI PROFONDA
═══════════════════════════════════════════════════════════════

🎯 **MOMENTUM (RSI)**
   RSI (14): {indicators.get('rsi', 'N/A')}
   ├─ Zona: {'🔥 Extremely Overbought' if indicators.get('rsi', 50) > 80 else '📈 Overbought' if indicators.get('rsi', 50) > 70 else '⚖️ Neutral' if indicators.get('rsi', 50) > 30 else '📉 Oversold' if indicators.get('rsi', 50) > 20 else '❄️ Extremely Oversold'}
   └─ Divergenze? Controllare sui grafici

📊 **MACD - Convergenza/Divergenza**
   MACD Line: {indicators.get('macd', {}).get('macd', 'N/A')}
   Signal Line: {indicators.get('macd', {}).get('signal', 'N/A')}
   Histogram: {indicators.get('macd', {}).get('histogram', 'N/A')}
   └─ Segnale: {'🟢 Bullish crossover' if indicators.get('macd', {}).get('histogram', 0) > 0 else '🔴 Bearish crossover'}

📈 **BOLLINGER BANDS - Volatility & Mean Reversion**
   Upper BB: ${indicators.get('bollinger_bands', {}).get('upper', 0):.2f}
   Middle BB (SMA 20): ${indicators.get('bollinger_bands', {}).get('middle', 0):.2f}
   Lower BB: ${indicators.get('bollinger_bands', {}).get('lower', 0):.2f}
   Position: {indicators.get('bollinger_bands', {}).get('position', 50):.1f}% {'🔥 Vicino alla banda superiore' if indicators.get('bollinger_bands', {}).get('position', 50) > 80 else '❄️ Vicino alla banda inferiore' if indicators.get('bollinger_bands', {}).get('position', 50) < 20 else '⚖️ Nel mezzo'}
   Bandwidth: {indicators.get('bollinger_bands', {}).get('bandwidth', 0):.2f}% {'💥 Alta volatilità' if indicators.get('bollinger_bands', {}).get('bandwidth', 0) > 10 else '😴 Bassa volatilità - possibile breakout imminente' if indicators.get('bollinger_bands', {}).get('bandwidth', 0) < 3 else '📊 Volatilità normale'}

🎢 **TREND ANALYSIS - Direzione e Forza**
   Direction: {indicators.get('trend', {}).get('direction', 'N/A')}
   Strength: {indicators.get('trend', {}).get('strength', 0):.0f}/100 {'💪 TREND FORTE' if indicators.get('trend', {}).get('strength', 0) > 70 else '⚡ Trend moderato' if indicators.get('trend', {}).get('strength', 0) > 40 else '🌫️ Trend debole/laterale'}
   Consistency: {indicators.get('trend', {}).get('consistency', 0):.0f}%

📉 **EMA STACK - Struttura del Trend**
   EMA(20): ${indicators.get('ema_20', 0):.2f}
   EMA(50): ${indicators.get('ema_50', 0):.2f}
   EMA(200): ${indicators.get('ema_200', 0):.2f}
   └─ Allineamento: {'🟢 Bullish stack (20>50>200)' if indicators.get('ema_20', 0) > indicators.get('ema_50', 0) > indicators.get('ema_200', 0) else '🔴 Bearish stack (20<50<200)' if indicators.get('ema_20', 0) < indicators.get('ema_50', 0) < indicators.get('ema_200', 0) else '⚠️ Mixed - possibile cambio trend'}

📊 **VOLUME PROFILE - Smart Money Activity**
   Volume medio 100 periodi: {avg_volume:.0f}
   Volume corrente: {current_volume:.0f}
   Ratio: {volume_ratio:.2f}x {'🔥 Volume esplosivo!' if volume_ratio > 2 else '📈 Volume sopra media' if volume_ratio > 1.2 else '📊 Volume normale' if volume_ratio > 0.8 else '😴 Volume basso - poca convinzione'}
   Trend volumetrico: {indicators.get('volume_profile', {}).get('trend', 'N/A')}

🎯 **SUPPORT & RESISTANCE - Zone Critiche**
   🟢 Supports: {', '.join([f'${s:.2f}' for s in indicators.get('support_resistance', {}).get('support_levels', [])]) or 'Nessun support chiaro identificato'}
   🔴 Resistances: {', '.join([f'${r:.2f}' for r in indicators.get('support_resistance', {}).get('resistance_levels', [])]) or 'Nessuna resistance chiara identificata'}

═══════════════════════════════════════════════════════════════
✅ CONFLUENZE TECNICHE MULTIPLE ({len(score_data['confluences'])})
═══════════════════════════════════════════════════════════════
{chr(10).join(f"✓ {c}" for c in score_data['confluences'])}

{'═══════════════════════════════════════════════════════════════' if score_data['warnings'] else ''}
{'⚠️  SEGNALI CONTRASTANTI - RED FLAGS (' + str(len(score_data['warnings'])) + ')' if score_data['warnings'] else ''}
{'═══════════════════════════════════════════════════════════════' if score_data['warnings'] else ''}
{chr(10).join(f"⚠ {w}" for w in score_data['warnings']) if score_data['warnings'] else ''}

═══════════════════════════════════════════════════════════════
📊 PRICE ACTION ANALYSIS - Swing Highs & Lows
═══════════════════════════════════════════════════════════════

🔺 Top 5 Swing Highs (ultimi 100 candles): {', '.join([f'${h:.2f}' for h in swing_highs])}
🔻 Top 5 Swing Lows (ultimi 100 candles): {', '.join([f'${l:.2f}' for l in swing_lows])}

Ultimi 20 candles per analisi candlestick patterns:
{chr(10).join(f"#{i}: Open:{c['open']:.2f} High:{c['high']:.2f} Low:{c['low']:.2f} Close:{c['close']:.2f} Vol:{c['volume']:.0f}" for i, c in enumerate(recent_20, 1))}

═══════════════════════════════════════════════════════════════
🧠 RICHIESTA ANALISI AI PROFESSIONALE
═══════════════════════════════════════════════════════════════

Come TRADER ISTITUZIONALE, fornisci un'analisi APPROFONDITA e DETTAGLIATA considerando:

1. **VALIDITÀ SETUP**: Questo setup è davvero valido? Analizza il contesto storico, la struttura del mercato, e se ci sono confluenze sufficienti.

2. **TIMING ENTRY**: È il momento ottimale per entrare? Considera: 
   - Posizione rispetto ai livelli chiave
   - Momentum attuale vs trend di fondo
   - Volume e convinzione del mercato
   - Possibili pullback o conferme da attendere

3. **RISK ANALYSIS**: Identifica TUTTI i rischi specifici:
   - Livelli critici che possono invalidare il setup
   - Possibili fake-out o trap
   - Fattori macro che potrebbero influenzare
   - Zone di presa di profitto istituzionale

4. **OPPORTUNITIES**: Quali sono le opportunità concrete?
   - Perché questo setup potrebbe funzionare bene?
   - Quali sono i driver principali?
   - C'è asimmetria rischio/rendimento favorevole?

5. **PRICE TARGETS**: Valuta i target suggeriti:
   - Sono realistici considerando volatilità storica?
   - Ci sono livelli tecnici più appropriati?
   - Il risk/reward è adeguato?

6. **PATTERN RECOGNITION**: Identifica pattern significativi:
   - Candlestick patterns (doji, engulfing, hammer, etc.)
   - Chart patterns (triangoli, flag, testa e spalle, etc.)
   - Pattern di volume (accumulation, distribution)

7. **VOLUME ANALYSIS**: Il volume conferma il movimento?
   - C'è allineamento tra prezzo e volume?
   - Vedi segni di smart money activity?
   - Possibili divergenze prezzo-volume?

8. **MARKET STRUCTURE**: Come si posiziona l'asset nella struttura di mercato?
   - Higher highs/higher lows (uptrend) o lower highs/lower lows (downtrend)?
   - Breakout di struttura o range-bound?
   - Liquidità disponibile sopra/sotto?

Rispondi in formato JSON DETTAGLIATO:
{{
    "valid": true/false,
    "validation_score": 1-10,
    "timing": "immediate|wait_for_pullback|wait_for_confirmation|avoid",
    "risk_factors": ["fattore rischio 1 dettagliato", "fattore rischio 2", "fattore rischio 3+"],
    "opportunities": ["opportunità dettagliata 1", "opportunità 2", "opportunità 3+"],
    "price_targets_realistic": true/false,
    "suggested_targets": {{"t1": prezzo_target_1, "t2": prezzo_target_2, "reasoning": "spiegazione"}},
    "patterns_identified": ["pattern candlestick 1", "chart pattern 2", "volume pattern 3"],
    "volume_confirmation": "strong|moderate|weak|divergence",
    "market_structure": "descrizione struttura di mercato e livelli chiave",
    "recommendation": "Raccomandazione operativa DETTAGLIATA con piano di trading specifico (entry, SL, TP, gestione)",
    "caution": "Avvertenze CRITICHE e scenari alternativi da monitorare",
    "confidence_level": 1-10
}}"""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2500,  # Aumentato per analisi più profonda
                temperature=0.2,  # Più deterministico per analisi professionale
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse AI response
            import json
            import re
            
            content = response.content[0].text
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            ai_data = json.loads(content.strip())
            
            logger.info(f"✅ AI validation for {symbol}: {ai_data.get('validation_score', 'N/A')}/10")
            
            return ai_data
            
        except Exception as e:
            logger.error(f"❌ AI validation error for {symbol}: {e}")
            return None
    
    def _generate_recommendation(
        self,
        score_data: Dict,
        trade_levels: Dict,
        ai_insights: Optional[Dict]
    ) -> str:
        """Generate final trading recommendation"""
        
        score = score_data['total_score']
        direction = score_data['direction']
        confidence = score_data['confidence']
        
        if direction == 'NEUTRAL' or score < 50:
            return "❌ No clear trading opportunity at this time. Wait for better setup."
        
        # Check AI validation if available
        if ai_insights and not ai_insights.get('valid', True):
            return f"⚠️ Technical score is {score:.0f} but AI suggests caution: {ai_insights.get('caution', 'Risk factors identified')}"
        
        if score >= 80:
            strength = "🔥 EXCELLENT"
        elif score >= 70:
            strength = "✅ STRONG"
        elif score >= 60:
            strength = "👍 GOOD"
        else:
            strength = "⚠️ MODERATE"
        
        rec = f"{strength} {direction} opportunity (Score: {score:.0f}, Confidence: {confidence:.0f}%)\n\n"
        
        # Add trade plan
        if trade_levels.get('entry'):
            rec += f"📊 Trade Plan:\n"
            rec += f"Entry: ${trade_levels['entry']:.2f}\n"
            rec += f"Stop Loss: ${trade_levels['stop_loss']:.2f} (Risk: {trade_levels['risk_percent']:.1f}%)\n"
            rec += f"Target 1: ${trade_levels['target_1']:.2f} (R:R {trade_levels['risk_reward_ratio_t1']:.1f}:1)\n"
            rec += f"Target 2: ${trade_levels['target_2']:.2f} (R:R {trade_levels['risk_reward_ratio_t2']:.1f}:1)\n"
        
        # Add AI insight if available
        if ai_insights and ai_insights.get('recommendation'):
            rec += f"\n🤖 AI Insight: {ai_insights['recommendation']}"
        
        return rec
    
    async def scan_for_best_trades(
        self,
        symbols: List[str],
        exchange: str = "binance",
        min_score: float = 60,
        fetch_data_func = None,
        asset_types: Dict[str, str] = None
    ) -> List[Dict]:
        """
        Scan multiple symbols for best trading opportunities
        
        Args:
            symbols: List of trading symbols
            exchange: Exchange name (legacy, now uses asset_types)
            min_score: Minimum score threshold
            fetch_data_func: Async function to fetch OHLCV data
            asset_types: Dict mapping symbol -> asset_type (crypto, stock, forex, etc.)
        
        Returns:
            List of best trade opportunities sorted by score
        """
        logger.info(f"🔍 Scanning {len(symbols)} symbols for best trades (min score: {min_score})...")
        
        results = []
        
        for symbol in symbols:
            try:
                # Determine asset type
                asset_type = 'crypto'  # default
                if asset_types and symbol in asset_types:
                    asset_type = asset_types[symbol]
                
                # Fetch candle data
                if fetch_data_func:
                    candles = await fetch_data_func(symbol, asset_type)
                else:
                    logger.warning(f"{symbol}: No data fetch function provided")
                    continue
                
                if not candles:
                    continue
                
                # Analyze symbol
                analysis = await self.analyze_symbol(symbol, candles, asset_type)
                
                if analysis and analysis['score'] >= min_score:
                    results.append(analysis)
                    logger.info(f"  ✅ {symbol}: {analysis['direction']} @ {analysis['score']:.1f}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ❌ {symbol}: {e}")
                continue
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"🎯 Found {len(results)} trading opportunities")
        
        return results


# Global instance
best_trades_service = BestTradesService()

