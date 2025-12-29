"""
ULTRA SIMPLE SCAN - Start from scratch
ONLY Binance crypto, basic technical analysis, AI validation
NO complex services, NO tracking, NO multi-market
"""
import os
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import ccxt.async_support as ccxt

logger = logging.getLogger(__name__)

# Initialize Binance
binance = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

async def get_crypto_price(symbol: str) -> Optional[float]:
    """Get current price from Binance"""
    try:
        ticker = await binance.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None

async def get_crypto_candles(symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[List[Dict]]:
    """Get OHLCV candles from Binance"""
    try:
        ohlcv = await binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        candles = []
        for candle in ohlcv:
            candles.append({
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            })
        return candles
    except Exception as e:
        logger.error(f"Error fetching candles for {symbol}: {e}")
        return None

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate RSI"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_simple_score(candles: List[Dict]) -> Dict:
    """Calculate a simple technical score"""
    if not candles or len(candles) < 20:
        return None
    
    closes = [c['close'] for c in candles]
    current_price = closes[-1]
    
    # RSI
    rsi = calculate_rsi(closes)
    if rsi is None:
        return None
    
    # Simple trend (SMA)
    sma_20 = sum(closes[-20:]) / 20
    sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
    
    # Scoring
    score = 50  # Base score
    direction = "NEUTRAL"
    confluences = []
    
    # RSI signals
    if rsi < 30:
        score += 20
        direction = "LONG"
        confluences.append("RSI oversold")
    elif rsi > 70:
        score += 20
        direction = "SHORT"
        confluences.append("RSI overbought")
    
    # Trend signals
    if current_price > sma_20 > sma_50:
        score += 15
        if direction == "NEUTRAL":
            direction = "LONG"
        confluences.append("Uptrend")
    elif current_price < sma_20 < sma_50:
        score += 15
        if direction == "NEUTRAL":
            direction = "SHORT"
        confluences.append("Downtrend")
    
    # Volume check
    recent_volume = sum([c['volume'] for c in candles[-5:]]) / 5
    avg_volume = sum([c['volume'] for c in candles]) / len(candles)
    if recent_volume > avg_volume * 1.5:
        score += 10
        confluences.append("High volume")
    
    return {
        'score': min(score, 100),
        'direction': direction,
        'rsi': round(rsi, 2),
        'current_price': current_price,
        'confluences': confluences
    }

async def get_ai_analysis(symbol: str, score_data: Dict) -> Optional[str]:
    """Get AI analysis from Claude"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None
        
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        prompt = f"""Quick crypto analysis:
Symbol: {symbol}
Direction: {score_data['direction']}
Score: {score_data['score']}/100
Price: ${score_data['current_price']}
RSI: {score_data['rsi']}

Give a brief (2-3 sentences) trading insight."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        return None

async def scan_crypto_simple(symbols: List[str], min_score: float = 60) -> List[Dict]:
    """
    ULTRA SIMPLE SCAN
    - Get candles from Binance
    - Calculate basic technical score
    - Add AI for high scores
    """
    logger.info(f"🚀 Starting simple scan of {len(symbols)} crypto...")
    
    opportunities = []
    
    for symbol in symbols:
        try:
            logger.info(f"  Analyzing {symbol}...")
            
            # Get candles
            candles = await get_crypto_candles(symbol, '1h', 100)
            if not candles:
                continue
            
            # Calculate score
            score_data = calculate_simple_score(candles)
            if not score_data or score_data['score'] < min_score:
                continue
            
            # AI analysis for high scores (75+)
            ai_insight = None
            if score_data['score'] >= 75:
                ai_insight = await get_ai_analysis(symbol, score_data)
            
            # Build opportunity
            opp = {
                'symbol': symbol,
                'exchange': 'binance',
                'score': score_data['score'],
                'direction': score_data['direction'],
                'current_price': score_data['current_price'],
                'rsi': score_data['rsi'],
                'confluences': score_data['confluences'],
                'ai_insight': ai_insight,
                'timestamp': datetime.now().isoformat()
            }
            
            opportunities.append(opp)
            logger.info(f"  ✅ {symbol}: {score_data['direction']} @ {score_data['score']}")
            
            # Small delay
            await asyncio.sleep(0.3)
            
        except Exception as e:
            logger.error(f"  ❌ {symbol}: {e}")
            continue
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    logger.info(f"🎯 Found {len(opportunities)} opportunities")
    return opportunities

