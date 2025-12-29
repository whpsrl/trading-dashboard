"""
Trading Scanner
Main scanning logic - coordinates data fetching and AI analysis
"""
import logging
import asyncio
from typing import List, Dict
from ..market_data import BinanceFetcher
from ..ai import ClaudeAnalyzer

logger = logging.getLogger(__name__)


class TradingScanner:
    def __init__(
        self,
        binance_key: str = "",
        binance_secret: str = "",
        claude_key: str = "",
        top_n_coins: int = 30,
        min_confidence: int = 75
    ):
        """Initialize scanner with API clients"""
        self.fetcher = BinanceFetcher(binance_key, binance_secret)
        self.ai = ClaudeAnalyzer(claude_key)
        self.top_n_coins = top_n_coins
        self.min_confidence = min_confidence
        
        logger.info("✅ Trading Scanner initialized")
    
    async def scan_market(
        self,
        timeframes: List[str] = ['15m', '1h', '4h'],
        max_results: int = 3
    ) -> List[Dict]:
        """
        Scan market for best setups
        
        Returns top N setups across all coins and timeframes
        """
        logger.info(f"🔍 Starting market scan...")
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
                    
                    # Filter by confidence
                    if analysis.get('valid') and analysis.get('confidence', 0) >= self.min_confidence:
                        all_setups.append(analysis)
                        logger.info(f"✅ {pair} {tf}: Confidence {analysis['confidence']}% - {analysis['direction']}")
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Error analyzing {pair} {tf}: {e}")
                    continue
        
        # Step 3: Sort by confidence and get top N
        all_setups.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        top_setups = all_setups[:max_results]
        
        logger.info(f"🎯 Found {len(all_setups)} valid setups, returning top {len(top_setups)}")
        
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

