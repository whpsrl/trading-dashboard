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
        Calculate entry, stop loss, and target levels based on indicators
        """
        current_price = indicators['current_price']
        atr = indicators.get('atr', current_price * 0.02)  # Default 2% if no ATR
        bb_data = indicators.get('bollinger_bands', {})
        sr_data = indicators.get('support_resistance', {})
        
        if direction == 'LONG':
            # Entry: current price or near support
            entry = current_price
            
            # Stop loss: below nearest support or 2 ATR
            support_levels = sr_data.get('support_levels', [])
            if support_levels:
                stop_loss = support_levels[0] - (atr * 0.5)
            else:
                stop_loss = current_price - (atr * 2)
            
            # Targets: resistance levels or ATR multiples
            resistance_levels = sr_data.get('resistance_levels', [])
            if resistance_levels:
                target_1 = resistance_levels[0]
                target_2 = resistance_levels[1] if len(resistance_levels) > 1 else target_1 * 1.05
            else:
                target_1 = current_price + (atr * 3)
                target_2 = current_price + (atr * 5)
            
        elif direction == 'SHORT':
            # Entry: current price or near resistance
            entry = current_price
            
            # Stop loss: above nearest resistance or 2 ATR
            resistance_levels = sr_data.get('resistance_levels', [])
            if resistance_levels:
                stop_loss = resistance_levels[0] + (atr * 0.5)
            else:
                stop_loss = current_price + (atr * 2)
            
            # Targets: support levels or ATR multiples
            support_levels = sr_data.get('support_levels', [])
            if support_levels:
                target_1 = support_levels[0]
                target_2 = support_levels[1] if len(support_levels) > 1 else target_1 * 0.95
            else:
                target_1 = current_price - (atr * 3)
                target_2 = current_price - (atr * 5)
        
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
            # Prepare market context for AI
            recent_candles = candles[-20:]
            
            prompt = f"""Sei un trader esperto. Analizza questo setup di trading:

**{symbol}**
Prezzo attuale: ${indicators['current_price']:.2f}
Direzione: {score_data['direction']}
Score tecnico: {score_data['total_score']:.1f}/100

**Indicatori Tecnici:**
- RSI: {indicators.get('rsi', 'N/A')}
- Trend: {indicators.get('trend', {}).get('direction', 'N/A')} (forza: {indicators.get('trend', {}).get('strength', 0):.0f})
- MACD: {indicators.get('macd', {})}

**Confluenze trovate:**
{chr(10).join(f"- {c}" for c in score_data['confluences'])}

**Ultimi 10 candles:**
{chr(10).join(f"C: {c['close']:.2f} | H: {c['high']:.2f} | L: {c['low']:.2f} | V: {c['volume']:.0f}" for c in recent_candles[-10:])}

**DOMANDE:**
1. Confermi che questo è un setup valido?
2. Ci sono fattori di rischio non considerati?
3. Qual è la tua valutazione complessiva (1-10)?
4. Consigli specifici per questo trade?

Rispondi in formato JSON:
{{
    "valid": true/false,
    "validation_score": 1-10,
    "risk_factors": ["fattore1", "fattore2"],
    "opportunities": ["opportunità1", "opportunità2"],
    "recommendation": "Tuo consiglio specifico",
    "caution": "Avvertenze importanti"
}}"""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
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
        fetch_data_func = None
    ) -> List[Dict]:
        """
        Scan multiple symbols for best trading opportunities
        
        Args:
            symbols: List of trading symbols
            exchange: Exchange name
            min_score: Minimum score threshold
            fetch_data_func: Async function to fetch OHLCV data
        
        Returns:
            List of best trade opportunities sorted by score
        """
        logger.info(f"🔍 Scanning {len(symbols)} symbols for best trades (min score: {min_score})...")
        
        results = []
        
        for symbol in symbols:
            try:
                # Fetch candle data
                if fetch_data_func:
                    candles = await fetch_data_func(symbol, exchange)
                else:
                    logger.warning(f"{symbol}: No data fetch function provided")
                    continue
                
                if not candles:
                    continue
                
                # Analyze symbol
                analysis = await self.analyze_symbol(symbol, candles, exchange)
                
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

