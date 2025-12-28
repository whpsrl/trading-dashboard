"""
Technical Indicators Calculator
Calcola indicatori tecnici per analisi di mercato
"""
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calcola indicatori tecnici da dati OHLCV"""
    
    @staticmethod
    def rsi(closes: List[float], period: int = 14) -> Optional[float]:
        """
        Relative Strength Index
        Returns: RSI value (0-100)
        """
        if len(closes) < period + 1:
            return None
        
        closes_arr = np.array(closes)
        deltas = np.diff(closes_arr)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict]:
        """
        Moving Average Convergence Divergence
        Returns: {macd, signal, histogram}
        """
        if len(closes) < slow + signal:
            return None
        
        closes_arr = np.array(closes)
        
        # EMA calculation
        def ema(data, period):
            return data.ewm(span=period, adjust=False).mean()
        
        import pandas as pd
        series = pd.Series(closes_arr)
        
        ema_fast = ema(series, fast)
        ema_slow = ema(series, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }
    
    @staticmethod
    def bollinger_bands(closes: List[float], period: int = 20, std_dev: float = 2.0) -> Optional[Dict]:
        """
        Bollinger Bands
        Returns: {upper, middle, lower, bandwidth, position}
        """
        if len(closes) < period:
            return None
        
        closes_arr = np.array(closes[-period:])
        
        middle = np.mean(closes_arr)
        std = np.std(closes_arr)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        current_price = closes[-1]
        bandwidth = ((upper - lower) / middle) * 100
        
        # Position: 0-100 where 50 is middle
        if upper != lower:
            position = ((current_price - lower) / (upper - lower)) * 100
        else:
            position = 50
        
        return {
            'upper': float(upper),
            'middle': float(middle),
            'lower': float(lower),
            'bandwidth': float(bandwidth),
            'position': float(position)
        }
    
    @staticmethod
    def ema(closes: List[float], period: int) -> Optional[float]:
        """Exponential Moving Average"""
        if len(closes) < period:
            return None
        
        import pandas as pd
        series = pd.Series(closes)
        ema_val = series.ewm(span=period, adjust=False).mean().iloc[-1]
        
        return float(ema_val)
    
    @staticmethod
    def sma(closes: List[float], period: int) -> Optional[float]:
        """Simple Moving Average"""
        if len(closes) < period:
            return None
        
        return float(np.mean(closes[-period:]))
    
    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
        """
        Average True Range (volatility indicator)
        """
        if len(closes) < period + 1:
            return None
        
        tr_list = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr = max(high_low, high_close, low_close)
            tr_list.append(tr)
        
        atr_val = np.mean(tr_list[-period:])
        return float(atr_val)
    
    @staticmethod
    def stochastic(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[Dict]:
        """
        Stochastic Oscillator
        Returns: {k, d}
        """
        if len(closes) < period:
            return None
        
        recent_highs = highs[-period:]
        recent_lows = lows[-period:]
        current_close = closes[-1]
        
        highest_high = max(recent_highs)
        lowest_low = min(recent_lows)
        
        if highest_high == lowest_low:
            k = 50
        else:
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # %D is 3-period SMA of %K (simplified to just K for single calculation)
        d = k
        
        return {
            'k': float(k),
            'd': float(d)
        }
    
    @staticmethod
    def volume_profile(volumes: List[float], period: int = 20) -> Dict:
        """
        Volume analysis
        Returns: {avg_volume, current_vs_avg, trend}
        """
        if len(volumes) < period:
            return {
                'avg_volume': 0,
                'current_vs_avg': 0,
                'trend': 'unknown'
            }
        
        recent_volumes = volumes[-period:]
        avg_volume = np.mean(recent_volumes)
        current_volume = volumes[-1]
        
        if avg_volume > 0:
            current_vs_avg = ((current_volume - avg_volume) / avg_volume) * 100
        else:
            current_vs_avg = 0
        
        # Volume trend
        first_half = np.mean(recent_volumes[:period//2])
        second_half = np.mean(recent_volumes[period//2:])
        
        if second_half > first_half * 1.2:
            trend = 'increasing'
        elif second_half < first_half * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'avg_volume': float(avg_volume),
            'current_vs_avg': float(current_vs_avg),
            'trend': trend
        }
    
    @staticmethod
    def support_resistance(highs: List[float], lows: List[float], closes: List[float], num_levels: int = 3) -> Dict:
        """
        Find support and resistance levels using price clusters
        Returns: {support_levels, resistance_levels}
        """
        if len(closes) < 50:
            return {'support_levels': [], 'resistance_levels': []}
        
        current_price = closes[-1]
        
        # Get recent highs and lows
        recent_highs = highs[-100:]
        recent_lows = lows[-100:]
        
        # Find resistance levels (above current price)
        resistance_candidates = [h for h in recent_highs if h > current_price]
        resistance_levels = []
        
        if resistance_candidates:
            # Cluster similar prices
            resistance_candidates.sort()
            clusters = []
            current_cluster = [resistance_candidates[0]]
            
            for price in resistance_candidates[1:]:
                if price - current_cluster[-1] < current_price * 0.02:  # Within 2%
                    current_cluster.append(price)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [price]
            
            if current_cluster:
                clusters.append(np.mean(current_cluster))
            
            resistance_levels = sorted(clusters)[:num_levels]
        
        # Find support levels (below current price)
        support_candidates = [l for l in recent_lows if l < current_price]
        support_levels = []
        
        if support_candidates:
            support_candidates.sort(reverse=True)
            clusters = []
            current_cluster = [support_candidates[0]]
            
            for price in support_candidates[1:]:
                if current_cluster[-1] - price < current_price * 0.02:  # Within 2%
                    current_cluster.append(price)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [price]
            
            if current_cluster:
                clusters.append(np.mean(current_cluster))
            
            support_levels = sorted(clusters, reverse=True)[:num_levels]
        
        return {
            'support_levels': [float(s) for s in support_levels],
            'resistance_levels': [float(r) for r in resistance_levels]
        }
    
    @staticmethod
    def trend_strength(closes: List[float], period: int = 20) -> Dict:
        """
        Analyze trend strength and direction
        Returns: {direction, strength, consistency}
        """
        if len(closes) < period:
            return {
                'direction': 'neutral',
                'strength': 0,
                'consistency': 0
            }
        
        recent_closes = closes[-period:]
        
        # Linear regression for trend
        x = np.arange(len(recent_closes))
        y = np.array(recent_closes)
        
        # Slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize slope by price
        avg_price = np.mean(recent_closes)
        normalized_slope = (slope / avg_price) * 100
        
        # Direction
        if normalized_slope > 0.5:
            direction = 'uptrend'
        elif normalized_slope < -0.5:
            direction = 'downtrend'
        else:
            direction = 'neutral'
        
        # Strength (0-100)
        strength = min(abs(normalized_slope) * 10, 100)
        
        # Consistency (R-squared)
        y_pred = np.poly1d(np.polyfit(x, y, 1))(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        consistency = max(0, r_squared * 100)
        
        return {
            'direction': direction,
            'strength': float(strength),
            'consistency': float(consistency)
        }
    
    @staticmethod
    def calculate_all(candles: List[Dict]) -> Dict:
        """
        Calculate all technical indicators from OHLCV candles
        
        Args:
            candles: List of {open, high, low, close, volume, timestamp}
        
        Returns:
            Dictionary with all calculated indicators
        """
        if not candles or len(candles) < 50:
            logger.warning("Not enough candles for technical analysis")
            return {}
        
        try:
            # Extract price data
            opens = [c['open'] for c in candles]
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            closes = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            
            current_price = closes[-1]
            
            # Calculate all indicators
            indicators = {
                'current_price': current_price,
                'rsi': TechnicalIndicators.rsi(closes),
                'macd': TechnicalIndicators.macd(closes),
                'bollinger_bands': TechnicalIndicators.bollinger_bands(closes),
                'ema_20': TechnicalIndicators.ema(closes, 20),
                'ema_50': TechnicalIndicators.ema(closes, 50),
                'ema_200': TechnicalIndicators.ema(closes, 200),
                'sma_20': TechnicalIndicators.sma(closes, 20),
                'atr': TechnicalIndicators.atr(highs, lows, closes),
                'stochastic': TechnicalIndicators.stochastic(highs, lows, closes),
                'volume_profile': TechnicalIndicators.volume_profile(volumes),
                'support_resistance': TechnicalIndicators.support_resistance(highs, lows, closes),
                'trend': TechnicalIndicators.trend_strength(closes)
            }
            
            logger.info(f"✅ Calculated all technical indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Error calculating indicators: {e}")
            return {}


# Singleton instance
technical_indicators = TechnicalIndicators()

