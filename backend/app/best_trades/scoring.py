"""
Trade Scoring System
Sistema di scoring per valutare opportunità di trading
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TradeScorer:
    """
    Valuta opportunità di trading con sistema di scoring multi-fattoriale
    Score range: 0-100
    """
    
    @staticmethod
    def score_rsi(rsi: Optional[float]) -> Dict:
        """
        Score RSI signal
        Oversold (< 30) = bullish signal
        Overbought (> 70) = bearish signal
        """
        if rsi is None:
            return {'score': 0, 'signal': 'neutral', 'reason': 'RSI not available'}
        
        if rsi < 30:
            score = (30 - rsi) * 2  # 0-60 score range
            return {
                'score': min(score, 30),
                'signal': 'bullish',
                'reason': f'RSI oversold at {rsi:.1f}'
            }
        elif rsi > 70:
            score = (rsi - 70) * 2
            return {
                'score': min(score, 30),
                'signal': 'bearish',
                'reason': f'RSI overbought at {rsi:.1f}'
            }
        else:
            return {
                'score': 0,
                'signal': 'neutral',
                'reason': f'RSI neutral at {rsi:.1f}'
            }
    
    @staticmethod
    def score_macd(macd_data: Optional[Dict]) -> Dict:
        """Score MACD crossover and histogram"""
        if not macd_data:
            return {'score': 0, 'signal': 'neutral', 'reason': 'MACD not available'}
        
        macd = macd_data.get('macd', 0)
        signal = macd_data.get('signal', 0)
        histogram = macd_data.get('histogram', 0)
        
        score = 0
        reasons = []
        trade_signal = 'neutral'
        
        # Bullish crossover
        if histogram > 0 and macd > signal:
            score += 20
            trade_signal = 'bullish'
            reasons.append('MACD bullish crossover')
        
        # Bearish crossover
        elif histogram < 0 and macd < signal:
            score += 20
            trade_signal = 'bearish'
            reasons.append('MACD bearish crossover')
        
        # Histogram strength
        if abs(histogram) > 0.1:
            score += 10
            reasons.append(f'Strong histogram ({histogram:.2f})')
        
        return {
            'score': min(score, 30),
            'signal': trade_signal,
            'reason': ', '.join(reasons) if reasons else 'MACD neutral'
        }
    
    @staticmethod
    def score_bollinger(bb_data: Optional[Dict], current_price: float) -> Dict:
        """Score Bollinger Bands position"""
        if not bb_data:
            return {'score': 0, 'signal': 'neutral', 'reason': 'BB not available'}
        
        position = bb_data.get('position', 50)
        bandwidth = bb_data.get('bandwidth', 0)
        
        score = 0
        trade_signal = 'neutral'
        reasons = []
        
        # Touch or break lower band (bullish)
        if position < 10:
            score += 25
            trade_signal = 'bullish'
            reasons.append('Price at lower BB')
        
        # Touch or break upper band (bearish)
        elif position > 90:
            score += 25
            trade_signal = 'bearish'
            reasons.append('Price at upper BB')
        
        # Squeeze (low volatility before breakout)
        if bandwidth < 5:
            score += 10
            reasons.append('BB squeeze detected')
        
        return {
            'score': min(score, 25),
            'signal': trade_signal,
            'reason': ', '.join(reasons) if reasons else 'Price in BB middle'
        }
    
    @staticmethod
    def score_trend(trend_data: Optional[Dict]) -> Dict:
        """Score trend strength and direction"""
        if not trend_data:
            return {'score': 0, 'signal': 'neutral', 'reason': 'Trend data not available'}
        
        direction = trend_data.get('direction', 'neutral')
        strength = trend_data.get('strength', 0)
        consistency = trend_data.get('consistency', 0)
        
        if direction == 'neutral':
            return {
                'score': 0,
                'signal': 'neutral',
                'reason': 'No clear trend'
            }
        
        # Strong consistent trend
        score = (strength * 0.3) + (consistency * 0.2)
        
        trade_signal = 'bullish' if direction == 'uptrend' else 'bearish'
        
        return {
            'score': min(score, 20),
            'signal': trade_signal,
            'reason': f'{direction.capitalize()} (strength: {strength:.0f}, consistency: {consistency:.0f})'
        }
    
    @staticmethod
    def score_volume(volume_data: Optional[Dict]) -> Dict:
        """Score volume confirmation"""
        if not volume_data:
            return {'score': 0, 'signal': 'neutral', 'reason': 'Volume data not available'}
        
        current_vs_avg = volume_data.get('current_vs_avg', 0)
        trend = volume_data.get('trend', 'stable')
        
        score = 0
        reasons = []
        
        # High volume (confirmation)
        if current_vs_avg > 50:
            score += 15
            reasons.append(f'High volume (+{current_vs_avg:.0f}% vs avg)')
        elif current_vs_avg > 20:
            score += 10
            reasons.append(f'Elevated volume (+{current_vs_avg:.0f}%)')
        
        # Volume trend
        if trend == 'increasing':
            score += 5
            reasons.append('Volume increasing')
        
        return {
            'score': min(score, 15),
            'signal': 'confirmation',
            'reason': ', '.join(reasons) if reasons else 'Normal volume'
        }
    
    @staticmethod
    def score_support_resistance(sr_data: Optional[Dict], current_price: float) -> Dict:
        """Score proximity to support/resistance levels"""
        if not sr_data:
            return {'score': 0, 'signal': 'neutral', 'reason': 'S/R data not available'}
        
        support_levels = sr_data.get('support_levels', [])
        resistance_levels = sr_data.get('resistance_levels', [])
        
        score = 0
        trade_signal = 'neutral'
        reasons = []
        
        # Check proximity to support (bullish)
        for support in support_levels:
            distance_pct = abs((current_price - support) / current_price * 100)
            if distance_pct < 2:  # Within 2%
                score += 20
                trade_signal = 'bullish'
                reasons.append(f'Near support at ${support:.2f}')
                break
        
        # Check proximity to resistance (bearish)
        for resistance in resistance_levels:
            distance_pct = abs((current_price - resistance) / current_price * 100)
            if distance_pct < 2:  # Within 2%
                score += 20
                trade_signal = 'bearish'
                reasons.append(f'Near resistance at ${resistance:.2f}')
                break
        
        return {
            'score': min(score, 20),
            'signal': trade_signal,
            'reason': ', '.join(reasons) if reasons else 'No nearby S/R levels'
        }
    
    @staticmethod
    def calculate_total_score(indicators: Dict) -> Dict:
        """
        Calculate total trade score from all indicators
        
        Returns:
            {
                'total_score': 0-100,
                'direction': 'LONG/SHORT/NEUTRAL',
                'confidence': 0-100,
                'components': {...},
                'confluences': [list of confirming factors],
                'warnings': [list of conflicting signals]
            }
        """
        current_price = indicators.get('current_price', 0)
        
        # Score each component
        components = {
            'rsi': TradeScorer.score_rsi(indicators.get('rsi')),
            'macd': TradeScorer.score_macd(indicators.get('macd')),
            'bollinger': TradeScorer.score_bollinger(indicators.get('bollinger_bands'), current_price),
            'trend': TradeScorer.score_trend(indicators.get('trend')),
            'volume': TradeScorer.score_volume(indicators.get('volume_profile')),
            'support_resistance': TradeScorer.score_support_resistance(
                indicators.get('support_resistance'), current_price
            )
        }
        
        # Calculate total score
        total_score = sum(comp['score'] for comp in components.values())
        
        # Determine direction (majority vote weighted by score)
        bullish_score = sum(comp['score'] for comp in components.values() if comp['signal'] == 'bullish')
        bearish_score = sum(comp['score'] for comp in components.values() if comp['signal'] == 'bearish')
        
        if bullish_score > bearish_score and bullish_score > 30:
            direction = 'LONG'
            confidence = min((bullish_score / (bullish_score + bearish_score)) * 100, 100)
        elif bearish_score > bullish_score and bearish_score > 30:
            direction = 'SHORT'
            confidence = min((bearish_score / (bullish_score + bearish_score)) * 100, 100)
        else:
            direction = 'NEUTRAL'
            confidence = 0
        
        # Find confluences (matching signals)
        confluences = []
        warnings = []
        
        for name, comp in components.items():
            if comp['signal'] == direction.lower() and comp['score'] > 0:
                confluences.append(f"{name.upper()}: {comp['reason']}")
            elif comp['signal'] != 'neutral' and comp['signal'] != direction.lower() and comp['score'] > 0:
                warnings.append(f"{name.upper()}: {comp['reason']}")
        
        return {
            'total_score': round(total_score, 1),
            'direction': direction,
            'confidence': round(confidence, 1),
            'components': components,
            'confluences': confluences,
            'warnings': warnings,
            'num_confluences': len(confluences)
        }


# Singleton
trade_scorer = TradeScorer()

