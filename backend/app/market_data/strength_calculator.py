"""
Market Strength Calculator
Calculates relative strength score for crypto pairs
"""
import logging
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class MarketStrengthCalculator:
    """Calculate market strength score (0-100) for crypto pairs"""
    
    def __init__(self):
        self.cached_rankings = {}
        logger.info("✅ Market Strength Calculator initialized")
    
    def calculate_strength(
        self,
        symbol: str,
        current_price: float,
        volume_24h: float,
        price_change_24h: float,
        ohlcv_data: List[List],
        market_ranking: int = None
    ) -> Dict:
        """
        Calculate comprehensive market strength score
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            current_price: Current price
            volume_24h: 24h volume in quote currency
            price_change_24h: % change in 24h
            ohlcv_data: Recent OHLCV candles for RSI calculation
            market_ranking: Position in market cap ranking (1-30)
        
        Returns:
            {
                'strength_score': 0-100,
                'strength_level': 'Very Strong' | 'Strong' | 'Neutral' | 'Weak' | 'Very Weak',
                'volume_strength': 0-100,
                'momentum_strength': 0-100,
                'ranking_strength': 0-100,
                'rsi': 0-100
            }
        """
        try:
            scores = []
            
            # 1. Volume Strength (25% weight)
            volume_score = self._calculate_volume_strength(volume_24h, ohlcv_data)
            scores.append(volume_score * 0.25)
            
            # 2. Momentum Strength (30% weight)
            momentum_score = self._calculate_momentum_strength(price_change_24h)
            scores.append(momentum_score * 0.30)
            
            # 3. Market Ranking Strength (20% weight)
            if market_ranking:
                ranking_score = self._calculate_ranking_strength(market_ranking)
                scores.append(ranking_score * 0.20)
            else:
                scores.append(50 * 0.20)  # Neutral if no ranking
            
            # 4. RSI Strength (25% weight)
            rsi = self._calculate_rsi(ohlcv_data)
            rsi_score = self._normalize_rsi_to_strength(rsi)
            scores.append(rsi_score * 0.25)
            
            # Calculate final score
            final_score = sum(scores)
            
            # Determine level
            strength_level = self._get_strength_level(final_score)
            
            result = {
                'strength_score': round(final_score, 1),
                'strength_level': strength_level,
                'volume_strength': round(volume_score, 1),
                'momentum_strength': round(momentum_score, 1),
                'ranking_strength': round(ranking_score if market_ranking else 50, 1),
                'rsi': round(rsi, 1)
            }
            
            logger.info(f"💪 {symbol} Strength: {result['strength_score']}/100 ({strength_level})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Strength calculation error for {symbol}: {e}")
            return {
                'strength_score': 50,
                'strength_level': 'Neutral',
                'volume_strength': 50,
                'momentum_strength': 50,
                'ranking_strength': 50,
                'rsi': 50
            }
    
    def _calculate_volume_strength(self, volume_24h: float, ohlcv_data: List[List]) -> float:
        """Calculate volume strength vs recent average"""
        try:
            if not ohlcv_data or len(ohlcv_data) < 20:
                return 50
            
            # Get last 20 candles volumes
            recent_volumes = [candle[5] for candle in ohlcv_data[-20:]]
            avg_volume = np.mean(recent_volumes)
            
            if avg_volume == 0:
                return 50
            
            # Volume ratio
            volume_ratio = volume_24h / avg_volume
            
            # Map to 0-100 (ratio 0.5 = 0, ratio 1.0 = 50, ratio 2.0 = 100)
            score = min(100, max(0, (volume_ratio - 0.5) * 100))
            
            return score
            
        except:
            return 50
    
    def _calculate_momentum_strength(self, price_change_24h: float) -> float:
        """Calculate momentum strength from price change"""
        try:
            # Map -10% to +10% change to 0-100 scale
            # -10% = 0, 0% = 50, +10% = 100
            score = 50 + (price_change_24h * 5)
            
            return min(100, max(0, score))
            
        except:
            return 50
    
    def _calculate_ranking_strength(self, ranking: int) -> float:
        """Calculate strength from market cap ranking"""
        try:
            # Top 1-5: 90-100
            # 6-10: 80-90
            # 11-20: 60-80
            # 21-30: 40-60
            # 30+: 0-40
            
            if ranking <= 5:
                return 90 + (5 - ranking) * 2
            elif ranking <= 10:
                return 80 + (10 - ranking)
            elif ranking <= 20:
                return 60 + (20 - ranking)
            elif ranking <= 30:
                return 40 + (30 - ranking) * 2
            else:
                return max(0, 40 - (ranking - 30))
                
        except:
            return 50
    
    def _calculate_rsi(self, ohlcv_data: List[List], period: int = 14) -> float:
        """Calculate RSI from OHLCV data"""
        try:
            if not ohlcv_data or len(ohlcv_data) < period + 1:
                return 50
            
            # Get closing prices
            closes = [candle[4] for candle in ohlcv_data[-period-1:]]
            
            # Calculate price changes
            deltas = np.diff(closes)
            
            # Separate gains and losses
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calculate average gain and loss
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            
            if avg_loss == 0:
                return 100
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except:
            return 50
    
    def _normalize_rsi_to_strength(self, rsi: float) -> float:
        """
        Convert RSI to strength score
        RSI 30-70 = neutral (50)
        RSI < 30 = weak (oversold, potential bounce = moderate strength)
        RSI > 70 = strong (overbought, momentum = high strength)
        """
        if rsi > 70:
            # Overbought = strong momentum
            return 70 + (rsi - 70)  # 70-100
        elif rsi < 30:
            # Oversold = potential reversal (moderate strength)
            return 30 + rsi  # 30-60
        else:
            # Neutral zone
            return 40 + (rsi - 30) * 0.5  # 40-60
    
    def _get_strength_level(self, score: float) -> str:
        """Convert score to descriptive level"""
        if score >= 80:
            return 'Very Strong'
        elif score >= 65:
            return 'Strong'
        elif score >= 45:
            return 'Neutral'
        elif score >= 30:
            return 'Weak'
        else:
            return 'Very Weak'


# Global instance
strength_calculator = MarketStrengthCalculator()

