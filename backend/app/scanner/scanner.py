"""
Trading Scanner
Main scanning logic - coordinates data fetching and AI analysis
"""
import logging
import asyncio
from typing import List, Dict
from ..market_data import BinanceFetcher, strength_calculator
from ..ai import ClaudeAnalyzer, GroqAnalyzer

logger = logging.getLogger(__name__)


class TradingScanner:
    def __init__(
        self,
        binance_key: str = "",
        binance_secret: str = "",
        claude_key: str = "",
        groq_key: str = "",
        top_n_coins: int = 15,
        min_confidence: int = 60
    ):
        """Initialize scanner with API clients"""
        self.fetcher = BinanceFetcher(binance_key, binance_secret)
        
        # Initialize both AI providers
        self.claude = ClaudeAnalyzer(claude_key)
        self.groq = GroqAnalyzer(groq_key)
        
        # Default to Claude (backward compatibility)
        self.ai = self.claude
        self.current_provider = 'claude'
        
        self.top_n_coins = top_n_coins
        self.min_confidence = min_confidence
        
        logger.info(f"✅ Trading Scanner initialized (Claude: {self.claude.is_available()}, Groq: {self.groq.is_available()})")
    
    def set_ai_provider(self, provider: str = 'claude'):
        """Switch between AI providers"""
        if provider == 'groq' and self.groq.is_available():
            self.ai = self.groq
            self.current_provider = 'groq'
            logger.info("🚀 Switched to Groq AI")
        elif provider == 'claude' and self.claude.is_available():
            self.ai = self.claude
            self.current_provider = 'claude'
            logger.info("🤖 Switched to Claude AI")
        else:
            logger.warning(f"⚠️  AI provider '{provider}' not available, keeping {self.current_provider}")
    
    async def scan_market(
        self,
        timeframes: List[str] = ['15m', '1h', '4h'],
        max_results: int = 3,
        ai_provider: str = None
    ) -> List[Dict]:
        """
        Scan market for best setups
        
        Returns top N setups across all coins and timeframes
        """
        # Temporarily switch AI provider if requested
        original_provider = self.current_provider
        if ai_provider:
            self.set_ai_provider(ai_provider)
        
        logger.info(f"🔍 Starting market scan...")
        logger.info(f"   AI Provider: {self.current_provider.upper()}")
        logger.info(f"   Coins: Top {self.top_n_coins}")
        logger.info(f"   Timeframes: {timeframes}")
        logger.info(f"   Min confidence: {self.min_confidence}")
        
        # Step 1: Get top pairs
        pairs = await self.fetcher.get_top_pairs(limit=self.top_n_coins)
        logger.info(f"📊 Analyzing {len(pairs)} pairs")
        
        # Step 2: Analyze each pair on each timeframe
        all_setups = []
        
        for pair in pairs:
            for tf in timeframes:
                try:
                    # Fetch OHLCV
                    ohlcv = await self.fetcher.fetch_ohlcv(pair, tf, limit=300)
                    
                    if not ohlcv or len(ohlcv) < 100:
                        logger.warning(f"⚠️  Insufficient data for {pair} {tf}")
                        continue
                    
                    # AI Analysis
                    analysis = await self.ai.analyze_setup(pair, ohlcv, tf)
                    
                    if not analysis:
                        continue
                    
                    # Calculate Market Strength
                    try:
                        # Get 24h data from first candle stats
                        volume_24h = sum([c[5] for c in ohlcv[-24:]]) if len(ohlcv) >= 24 else ohlcv[-1][5]
                        price_24h_ago = ohlcv[-24][4] if len(ohlcv) >= 24 else ohlcv[0][4]
                        price_change_24h = ((analysis['current_price'] - price_24h_ago) / price_24h_ago) * 100
                        
                        strength_data = strength_calculator.calculate_strength(
                            symbol=pair,
                            current_price=analysis['current_price'],
                            volume_24h=volume_24h,
                            price_change_24h=price_change_24h,
                            ohlcv_data=ohlcv,
                            market_ranking=pairs.index(pair) + 1 if pair in pairs else None
                        )
                        
                        # Add strength to analysis
                        analysis['market_strength'] = strength_data
                        
                    except Exception as e:
                        logger.warning(f"⚠️  Could not calculate strength for {pair}: {e}")
                        analysis['market_strength'] = {
                            'strength_score': 50,
                            'strength_level': 'Neutral'
                        }
                    
                    # Filter by confidence
                    if analysis.get('valid') and analysis.get('confidence', 0) >= self.min_confidence:
                        all_setups.append(analysis)
                        strength_emoji = '🟢' if strength_data['strength_score'] >= 65 else '⚪' if strength_data['strength_score'] >= 45 else '🔴'
                        logger.info(f"✅ {pair} {tf}: Conf {analysis['confidence']}% | Strength {strength_emoji} {strength_data['strength_score']}/100 - {analysis['direction']}")
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Error analyzing {pair} {tf}: {e}")
                    continue
        
        # Step 3: Sort by confidence and get top N
        all_setups.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        top_setups = all_setups[:max_results]
        
        logger.info(f"🎯 Found {len(all_setups)} valid setups, returning top {len(top_setups)}")
        
        # Restore original provider if it was changed
        if ai_provider and ai_provider != original_provider:
            self.set_ai_provider(original_provider)
        
        return top_setups
    
    async def quick_scan(self, symbol: str, timeframe: str = '15m') -> Dict:
        """
        Quick scan for a single symbol
        """
        logger.info(f"🔍 Quick scan: {symbol} {timeframe}")
        
        ohlcv = await self.fetcher.fetch_ohlcv(symbol, timeframe, limit=300)
        
        if not ohlcv:
            return {"error": "Failed to fetch data"}
        
        analysis = await self.ai.analyze_setup(symbol, ohlcv, timeframe)
        
        return analysis or {"error": "Analysis failed"}

