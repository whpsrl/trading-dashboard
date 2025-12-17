from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from binance.client import Client
from datetime import datetime
import os
import numpy as np
from typing import List, Dict
from collections import Counter

app = FastAPI(title="Trading Dashboard API - Real AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

binance_client = Client()

TIMEFRAME_MAP = {
    "M5": Client.KLINE_INTERVAL_5MINUTE,
    "M15": Client.KLINE_INTERVAL_15MINUTE,
    "H1": Client.KLINE_INTERVAL_1HOUR,
    "H4": Client.KLINE_INTERVAL_4HOUR,
    "D1": Client.KLINE_INTERVAL_1DAY
}

# ==================== CANDLESTICK PATTERN RECOGNITION ====================

def detect_doji(candle):
    """Doji: indecisione, body molto piccolo"""
    body = abs(candle['close'] - candle['open'])
    range_size = candle['high'] - candle['low']
    return body < (range_size * 0.1), "DOJI"

def detect_hammer(candle):
    """Hammer: bullish reversal, long lower wick"""
    body = abs(candle['close'] - candle['open'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    
    if lower_wick > (body * 2) and upper_wick < (body * 0.3):
        return True, "HAMMER"
    return False, None

def detect_shooting_star(candle):
    """Shooting Star: bearish reversal, long upper wick"""
    body = abs(candle['close'] - candle['open'])
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    
    if upper_wick > (body * 2) and lower_wick < (body * 0.3):
        return True, "SHOOTING_STAR"
    return False, None

def detect_engulfing(candles):
    """Bullish/Bearish Engulfing: forte reversal"""
    if len(candles) < 2:
        return False, None
    
    prev = candles[-2]
    curr = candles[-1]
    
    # Bullish Engulfing
    if (prev['close'] < prev['open'] and 
        curr['close'] > curr['open'] and
        curr['open'] < prev['close'] and
        curr['close'] > prev['open']):
        return True, "BULLISH_ENGULFING"
    
    # Bearish Engulfing
    if (prev['close'] > prev['open'] and 
        curr['close'] < curr['open'] and
        curr['open'] > prev['close'] and
        curr['close'] < prev['open']):
        return True, "BEARISH_ENGULFING"
    
    return False, None

def detect_morning_star(candles):
    """Morning Star: strong bullish reversal (3 candles)"""
    if len(candles) < 3:
        return False, None
    
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    
    # First: long bearish
    if c1['close'] >= c1['open']:
        return False, None
    
    # Second: small body (star)
    body2 = abs(c2['close'] - c2['open'])
    range2 = c2['high'] - c2['low']
    if body2 > (range2 * 0.3):
        return False, None
    
    # Third: long bullish
    if c3['close'] > c3['open'] and c3['close'] > (c1['open'] + c1['close']) / 2:
        return True, "MORNING_STAR"
    
    return False, None

def detect_evening_star(candles):
    """Evening Star: strong bearish reversal (3 candles)"""
    if len(candles) < 3:
        return False, None
    
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    
    # First: long bullish
    if c1['close'] <= c1['open']:
        return False, None
    
    # Second: small body (star)
    body2 = abs(c2['close'] - c2['open'])
    range2 = c2['high'] - c2['low']
    if body2 > (range2 * 0.3):
        return False, None
    
    # Third: long bearish
    if c3['close'] < c3['open'] and c3['close'] < (c1['open'] + c1['close']) / 2:
        return True, "EVENING_STAR"
    
    return False, None

def analyze_candlestick_patterns(candles):
    """Analizza tutti i pattern candlestick"""
    patterns = []
    
    if len(candles) >= 1:
        last = candles[-1]
        
        # Single candle patterns
        is_doji, name = detect_doji(last)
        if is_doji:
            patterns.append({"pattern": name, "signal": "NEUTRAL", "strength": 1})
        
        is_hammer, name = detect_hammer(last)
        if is_hammer:
            patterns.append({"pattern": name, "signal": "BULLISH", "strength": 3})
        
        is_star, name = detect_shooting_star(last)
        if is_star:
            patterns.append({"pattern": name, "signal": "BEARISH", "strength": 3})
    
    if len(candles) >= 2:
        # Two candle patterns
        is_engulf, name = detect_engulfing(candles)
        if is_engulf:
            signal = "BULLISH" if "BULLISH" in name else "BEARISH"
            patterns.append({"pattern": name, "signal": signal, "strength": 4})
    
    if len(candles) >= 3:
        # Three candle patterns
        is_morning, name = detect_morning_star(candles)
        if is_morning:
            patterns.append({"pattern": name, "signal": "BULLISH", "strength": 5})
        
        is_evening, name = detect_evening_star(candles)
        if is_evening:
            patterns.append({"pattern": name, "signal": "BEARISH", "strength": 5})
    
    return patterns

# ==================== CHART PATTERN RECOGNITION ====================

def detect_support_resistance(candles, window=20):
    """Identifica livelli di supporto/resistenza"""
    closes = [c['close'] for c in candles[-window:]]
    highs = [c['high'] for c in candles[-window:]]
    lows = [c['low'] for c in candles[-window:]]
    
    # Cluster di prezzi (resistance/support zones)
    price_clusters = {}
    for price in highs + lows:
        rounded = round(price / (price * 0.01)) * (price * 0.01)  # 1% clustering
        price_clusters[rounded] = price_clusters.get(rounded, 0) + 1
    
    # Top 3 livelli
    sorted_levels = sorted(price_clusters.items(), key=lambda x: x[1], reverse=True)[:3]
    
    current_price = candles[-1]['close']
    levels = []
    
    for level, count in sorted_levels:
        if level > current_price:
            levels.append({"type": "RESISTANCE", "price": level, "touches": count})
        else:
            levels.append({"type": "SUPPORT", "price": level, "touches": count})
    
    return levels

def detect_triangle_pattern(candles, lookback=50):
    """Rileva pattern triangolo (ascending/descending/symmetrical)"""
    if len(candles) < lookback:
        return None
    
    recent = candles[-lookback:]
    highs = [c['high'] for c in recent]
    lows = [c['low'] for c in recent]
    
    # Trend delle highs e lows
    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
    
    # Ascending Triangle
    if abs(high_slope) < 0.1 and low_slope > 0.1:
        return {"pattern": "ASCENDING_TRIANGLE", "signal": "BULLISH", "strength": 4}
    
    # Descending Triangle
    if abs(low_slope) < 0.1 and high_slope < -0.1:
        return {"pattern": "DESCENDING_TRIANGLE", "signal": "BEARISH", "strength": 4}
    
    # Symmetrical Triangle
    if high_slope < -0.1 and low_slope > 0.1:
        return {"pattern": "SYMMETRICAL_TRIANGLE", "signal": "NEUTRAL", "strength": 2}
    
    return None

def detect_double_top_bottom(candles, lookback=30, tolerance=0.02):
    """Rileva double top/bottom"""
    if len(candles) < lookback:
        return None
    
    recent = candles[-lookback:]
    highs = [c['high'] for c in recent]
    lows = [c['low'] for c in recent]
    
    # Find peaks and troughs
    peaks = []
    troughs = []
    
    for i in range(2, len(recent)-2):
        # Peak
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            peaks.append((i, highs[i]))
        # Trough
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            troughs.append((i, lows[i]))
    
    # Double Top
    if len(peaks) >= 2:
        last_two_peaks = peaks[-2:]
        if abs(last_two_peaks[0][1] - last_two_peaks[1][1]) / last_two_peaks[0][1] < tolerance:
            return {"pattern": "DOUBLE_TOP", "signal": "BEARISH", "strength": 5}
    
    # Double Bottom
    if len(troughs) >= 2:
        last_two_troughs = troughs[-2:]
        if abs(last_two_troughs[0][1] - last_two_troughs[1][1]) / last_two_troughs[0][1] < tolerance:
            return {"pattern": "DOUBLE_BOTTOM", "signal": "BULLISH", "strength": 5}
    
    return None

# ==================== MACHINE LEARNING PREDICTION ====================

def calculate_features(candles):
    """Estrae features per ML model"""
    closes = np.array([c['close'] for c in candles])
    highs = np.array([c['high'] for c in candles])
    lows = np.array([c['low'] for c in candles])
    volumes = np.array([c['volume'] for c in candles])
    
    features = {}
    
    # Price features
    features['price_change_5'] = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
    features['price_change_10'] = (closes[-1] - closes[-10]) / closes[-10] if len(closes) >= 10 else 0
    features['price_change_20'] = (closes[-1] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0
    
    # Volatility
    if len(closes) >= 10:
        features['volatility'] = np.std(closes[-10:]) / np.mean(closes[-10:])
    else:
        features['volatility'] = 0
    
    # Range
    features['current_range'] = (highs[-1] - lows[-1]) / closes[-1]
    
    # Volume trend
    if len(volumes) >= 5:
        features['volume_trend'] = (volumes[-1] - np.mean(volumes[-5:])) / np.mean(volumes[-5:])
    else:
        features['volume_trend'] = 0
    
    # Moving averages
    if len(closes) >= 20:
        features['sma_20'] = np.mean(closes[-20:])
        features['distance_from_sma20'] = (closes[-1] - features['sma_20']) / features['sma_20']
    else:
        features['distance_from_sma20'] = 0
    
    # Momentum
    if len(closes) >= 10:
        features['momentum'] = closes[-1] - closes[-10]
    else:
        features['momentum'] = 0
    
    return features

def simple_ml_prediction(features):
    """
    Semplice ML model basato su feature weighting
    In produzione: sostituisci con sklearn RandomForest/XGBoost trained model
    """
    score = 0
    
    # Price momentum
    if features['price_change_5'] > 0.02:
        score += 2
    elif features['price_change_5'] < -0.02:
        score -= 2
    
    # Medium term trend
    if features['price_change_20'] > 0.05:
        score += 2
    elif features['price_change_20'] < -0.05:
        score -= 2
    
    # Distance from MA
    if features['distance_from_sma20'] > 0.03:
        score += 1
    elif features['distance_from_sma20'] < -0.03:
        score -= 1
    
    # Volume confirmation
    if features['volume_trend'] > 0.2:
        score += 1
    elif features['volume_trend'] < -0.2:
        score -= 1
    
    # Volatility (high vol = uncertain)
    if features['volatility'] > 0.05:
        score = int(score * 0.7)  # Reduce confidence in high volatility
    
    return score

# ==================== UNIFIED AI PREDICTION ====================

def ai_predict(candles):
    """
    Unified AI prediction combining:
    1. Candlestick patterns
    2. Chart patterns
    3. ML features
    4. Price action
    """
    
    # 1. Candlestick Patterns
    candle_patterns = analyze_candlestick_patterns(candles)
    
    # 2. Chart Patterns
    chart_patterns = []
    
    triangle = detect_triangle_pattern(candles)
    if triangle:
        chart_patterns.append(triangle)
    
    double = detect_double_top_bottom(candles)
    if double:
        chart_patterns.append(double)
    
    # 3. Support/Resistance
    levels = detect_support_resistance(candles)
    
    # 4. ML Features
    features = calculate_features(candles)
    ml_score = simple_ml_prediction(features)
    
    # ==================== SCORING SYSTEM ====================
    
    total_score = ml_score  # Base da ML
    detected_patterns = []
    
    # Add candlestick patterns
    for pattern in candle_patterns:
        detected_patterns.append(pattern['pattern'])
        if pattern['signal'] == 'BULLISH':
            total_score += pattern['strength']
        elif pattern['signal'] == 'BEARISH':
            total_score -= pattern['strength']
    
    # Add chart patterns
    for pattern in chart_patterns:
        detected_patterns.append(pattern['pattern'])
        if pattern['signal'] == 'BULLISH':
            total_score += pattern['strength']
        elif pattern['signal'] == 'BEARISH':
            total_score -= pattern['strength']
    
    # Support/Resistance breakout
    current_price = candles[-1]['close']
    for level in levels:
        if level['type'] == 'RESISTANCE' and current_price > level['price'] * 0.998:
            total_score += 2
            detected_patterns.append("RESISTANCE_BREAKOUT")
        elif level['type'] == 'SUPPORT' and current_price < level['price'] * 1.002:
            total_score -= 2
            detected_patterns.append("SUPPORT_BREAKDOWN")
    
    # ==================== FINAL DECISION ====================
    
    if total_score >= 3:
        direction = "UP"
        confidence = min(total_score * 10 + 50, 95)
    elif total_score <= -3:
        direction = "DOWN"
        confidence = min(abs(total_score) * 10 + 50, 95)
    else:
        direction = "NEUTRAL"
        confidence = 45
    
    return {
        "direction": direction,
        "confidence": round(confidence, 1),
        "score": total_score,
        "ml_score": ml_score,
        "patterns_detected": detected_patterns,
        "candlestick_patterns": candle_patterns,
        "chart_patterns": chart_patterns,
        "support_resistance": levels,
        "features": {
            "price_momentum_5": round(features['price_change_5'] * 100, 2),
            "price_momentum_20": round(features['price_change_20'] * 100, 2),
            "volatility": round(features['volatility'] * 100, 2),
            "volume_trend": round(features['volume_trend'] * 100, 2)
        }
    }

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Trading Dashboard - Real AI",
        "version": "4.0",
        "features": [
            "Candlestick Pattern Recognition",
            "Chart Pattern Detection",
            "Machine Learning Prediction",
            "Support/Resistance Analysis",
            "Multi-timeframe Analysis"
        ]
    }

@app.get("/api/crypto/{symbol}")
async def get_crypto_data(
    symbol: str = "BTCUSDT",
    timeframe: str = "H1",
    limit: int = 100
):
    """Get crypto data with Real AI prediction"""
    try:
        if timeframe not in TIMEFRAME_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timeframe. Use: {', '.join(TIMEFRAME_MAP.keys())}"
            )
        
        interval = TIMEFRAME_MAP[timeframe]
        
        klines = binance_client.get_klines(
            symbol=symbol.upper(),
            interval=interval,
            limit=limit
        )
        
        candles = []
        for k in klines:
            candles.append({
                "time": int(k[0] / 1000),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        
        current_price = float(klines[-1][4])
        
        # Real AI Prediction - with fallback
        try:
            prediction = ai_predict(candles)
        except Exception as e:
            print(f"AI prediction error: {e}")
            prediction = {
                "direction": "NEUTRAL",
                "confidence": 50,
                "score": 0,
                "ml_score": 0,
                "patterns_detected": [],
                "candlestick_patterns": [],
                "chart_patterns": [],
                "support_resistance": [],
                "features": {
                    "price_momentum_5": 0,
                    "price_momentum_20": 0,
                    "volatility": 0,
                    "volume_trend": 0
                }
            }
        
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "current_price": current_price,
            "data": candles,
            "count": len(candles),
            "ai_prediction": prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/price/{symbol}")
async def get_current_price(symbol: str = "BTCUSDT"):
    """Get current price"""
    try:
        ticker = binance_client.get_symbol_ticker(symbol=symbol.upper())
        return {
            "symbol": symbol.upper(),
            "price": float(ticker['price']),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/analyze")
async def analyze_with_ai(request: dict):
    """AI Text Analysis endpoint"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {"analysis": "⚠️ AI Analysis requires ANTHROPIC_API_KEY environment variable"}
        
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        prompt = request.get('prompt', '')
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = message.content[0].text
        
        return {"analysis": analysis}
        
    except ImportError:
        return {"analysis": "⚠️ AI Analysis requires 'anthropic' package (pip install anthropic)"}
    except Exception as e:
        return {"analysis": f"⚠️ AI Analysis error: {str(e)}"}

@app.post("/api/v1/ai/auto-draw")
async def auto_draw_lines(request: dict):
    """AI Auto-Draw endpoint"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {
                "success": False,
                "lines": [],
                "message": "ANTHROPIC_API_KEY not configured"
            }
        
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        symbol = request.get('symbol', 'BTC')
        timeframe = request.get('timeframe', '1h')
        candles = request.get('candles', [])[-50:]
        draw_type = request.get('drawType', 'support_resistance')
        
        if not candles:
            return {"success": False, "lines": [], "message": "No candle data"}
        
        current_price = candles[-1]['close']
        high = max(c['high'] for c in candles)
        low = min(c['low'] for c in candles)
        
        prompt = f"""Analyze {symbol} on {timeframe} and identify key levels for {draw_type}.

Current: ${current_price:.2f}
Range: ${low:.2f} - ${high:.2f}

Return ONLY JSON (no markdown):
{{
  "lines": [
    {{"type": "support", "price": 43200, "strength": "strong", "label": "Key support", "color": "#22c55e"}},
    {{"type": "resistance", "price": 43800, "strength": "strong", "label": "Resistance", "color": "#ef4444"}}
  ]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json, re
        response_text = message.content[0].text.strip()
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if json_match:
            result = json.loads(json_match.group())
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "drawType": draw_type,
                "lines": result.get('lines', [])
            }
        
        return {"success": False, "lines": [], "message": "Failed to parse AI response"}
        
    except ImportError:
        return {"success": False, "lines": [], "message": "anthropic package required"}
    except Exception as e:
        return {"success": False, "lines": [], "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
