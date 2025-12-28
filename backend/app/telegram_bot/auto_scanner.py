"""
Automatic market scanning scheduler
Scans markets every hour and sends signals to Telegram
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from ..best_trades.service import BestTradesService
from ..market_data.unified_service import UnifiedMarketDataService
from ..market_data.market_universe import MARKET_UNIVERSE
from .notifications import send_trade_signal

logger = logging.getLogger(__name__)


class AutoScanner:
    """
    Automatic scanner that runs every hour
    """
    
    def __init__(self):
        self.best_trades_service = BestTradesService()
        self.market_service = UnifiedMarketDataService()
        self.is_running = False
    
    async def scan_all_markets(self, min_score: float = 65) -> List[Dict]:
        """
        Scan all markets and return opportunities
        """
        logger.info("🔍 Starting automatic market scan...")
        
        opportunities = []
        
        # Crypto - Binance (50+ assets, no limits)
        crypto_symbols = MARKET_UNIVERSE['crypto'][:50]
        logger.info(f"📊 Scanning {len(crypto_symbols)} crypto assets...")
        crypto_results = await self._scan_symbols(crypto_symbols, 'crypto', '1h', min_score)
        opportunities.extend(crypto_results)
        
        # Small delay between market types
        await asyncio.sleep(2)
        
        # Stocks - Finnhub (40-50 assets)
        stock_symbols = MARKET_UNIVERSE['stocks'][:45]
        logger.info(f"📊 Scanning {len(stock_symbols)} stocks...")
        stock_results = await self._scan_symbols_with_rate_limit(
            stock_symbols, 'stocks', '1h', min_score, delay=1.2
        )
        opportunities.extend(stock_results)
        
        await asyncio.sleep(2)
        
        # Indices - Finnhub (10-15 assets)
        indices_symbols = MARKET_UNIVERSE['indices'][:12]
        logger.info(f"📊 Scanning {len(indices_symbols)} indices...")
        indices_results = await self._scan_symbols_with_rate_limit(
            indices_symbols, 'indices', '1h', min_score, delay=1.2
        )
        opportunities.extend(indices_results)
        
        await asyncio.sleep(2)
        
        # Commodities - Finnhub (8-10 assets)
        commodities_symbols = MARKET_UNIVERSE['commodities'][:8]
        logger.info(f"📊 Scanning {len(commodities_symbols)} commodities...")
        commodities_results = await self._scan_symbols_with_rate_limit(
            commodities_symbols, 'commodities', '1h', min_score, delay=1.2
        )
        opportunities.extend(commodities_results)
        
        await asyncio.sleep(2)
        
        # Forex - OANDA (15-20 coppie)
        forex_symbols = MARKET_UNIVERSE['forex'][:18]
        logger.info(f"📊 Scanning {len(forex_symbols)} forex pairs...")
        forex_results = await self._scan_symbols_with_rate_limit(
            forex_symbols, 'forex', '1h', min_score, delay=1.5
        )
        opportunities.extend(forex_results)
        
        # Sort by score
        opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"✅ Scan completed! Found {len(opportunities)} opportunities")
        
        return opportunities
    
    async def _scan_symbols(
        self, 
        symbols: List[Dict], 
        market_type: str, 
        timeframe: str,
        min_score: float
    ) -> List[Dict]:
        """
        Scan a list of symbols (for markets without rate limits like Binance)
        """
        results = []
        
        for symbol_info in symbols:
            try:
                symbol = symbol_info['symbol']
                exchange = symbol_info.get('exchange', 'binance')
                
                # Get market data
                candles = await self.market_service.get_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=200,
                    market_type=market_type
                )
                
                if not candles or len(candles) < 50:
                    continue
                
                # Analyze
                analysis = await self.best_trades_service.analyze_symbol(
                    symbol=symbol,
                    candles=candles,
                    exchange=exchange
                )
                
                if analysis and analysis.get('score', 0) >= min_score:
                    analysis['market_type'] = market_type
                    results.append(analysis)
                    logger.info(f"✅ {symbol}: {analysis['score']:.1f} - {analysis['direction']}")
                
                # Small delay
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error scanning {symbol_info.get('symbol', '?')}: {e}")
                continue
        
        return results
    
    async def _scan_symbols_with_rate_limit(
        self,
        symbols: List[Dict],
        market_type: str,
        timeframe: str,
        min_score: float,
        delay: float = 1.2
    ) -> List[Dict]:
        """
        Scan symbols with rate limiting (for Finnhub, OANDA)
        """
        results = []
        
        for symbol_info in symbols:
            try:
                symbol = symbol_info['symbol']
                exchange = symbol_info.get('exchange', 'finnhub')
                
                # Get market data
                candles = await self.market_service.get_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=200,
                    market_type=market_type
                )
                
                if not candles or len(candles) < 50:
                    await asyncio.sleep(delay)
                    continue
                
                # Analyze
                analysis = await self.best_trades_service.analyze_symbol(
                    symbol=symbol,
                    candles=candles,
                    exchange=exchange
                )
                
                if analysis and analysis.get('score', 0) >= min_score:
                    analysis['market_type'] = market_type
                    results.append(analysis)
                    logger.info(f"✅ {symbol}: {analysis['score']:.1f} - {analysis['direction']}")
                
                # Rate limit delay
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"❌ Error scanning {symbol_info.get('symbol', '?')}: {e}")
                await asyncio.sleep(delay)
                continue
        
        return results
    
    async def scan_and_notify(self, min_score: float = 70):
        """
        Scan markets and send top opportunities to Telegram
        """
        logger.info("🚀 Starting scan and notify...")
        
        opportunities = await self.scan_all_markets(min_score=min_score)
        
        if not opportunities:
            logger.info("📭 No opportunities found")
            return
        
        # Send top 5 to Telegram
        top_opportunities = opportunities[:5]
        
        logger.info(f"📱 Sending {len(top_opportunities)} signals to Telegram...")
        
        for opp in top_opportunities:
            try:
                await send_trade_signal(opp)
                await asyncio.sleep(2)  # Delay between messages
            except Exception as e:
                logger.error(f"❌ Error sending signal: {e}")
        
        logger.info("✅ Scan and notify completed!")
    
    async def start_hourly_scan(self, min_score: float = 70):
        """
        Start scanning every hour
        """
        logger.info("🕐 Starting hourly automatic scanner...")
        self.is_running = True
        
        while self.is_running:
            try:
                current_time = datetime.now()
                logger.info(f"⏰ [{current_time.strftime('%H:%M')}] Starting hourly scan...")
                
                await self.scan_and_notify(min_score=min_score)
                
                # Wait 1 hour
                logger.info("😴 Sleeping for 1 hour...")
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"❌ Error in hourly scan: {e}")
                await asyncio.sleep(3600)
    
    def stop(self):
        """
        Stop the scanner
        """
        logger.info("🛑 Stopping automatic scanner...")
        self.is_running = False


# Global scanner instance
auto_scanner = AutoScanner()

