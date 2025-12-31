"""
Automatic commodities scanning scheduler
Runs 30 minutes after 4H candle close to ensure Yahoo Finance data is available
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

logger = logging.getLogger(__name__)


class AutoScannerCommodities:
    """Handles automatic scheduled scans for Commodities (Yahoo Finance)"""
    
    def __init__(self, telegram, trade_tracker):
        self.telegram = telegram
        self.trade_tracker = trade_tracker
        self.scheduler = AsyncIOScheduler()
        logger.info("✅ Auto-scanner Commodities initialized")
    
    async def run_4h_scan(self):
        """Execute 4h commodities scan (30 min after candle close for Yahoo data delay)"""
        try:
            logger.info("🥇 Starting automatic COMMODITIES 4H scan (30min after candle close)...")
            
            from ..market_data.yahoo_fetcher import YahooFetcher
            from ..scanner.scanner import TradingScanner
            from ..config import settings
            
            # Create scan session
            scan_id = self.trade_tracker.create_scan_session(
                scan_type='auto_commodities_4h',
                top_n=3,
                timeframes=['4h'],
                ai_provider=settings.AUTO_SCAN_AI_PROVIDER
            )
            
            # Initialize Yahoo fetcher
            yahoo_fetcher = YahooFetcher()
            commodities = ['GC=F', 'CL=F', 'SI=F']  # Gold, Oil, Silver
            
            # Initialize scanner with Yahoo fetcher
            scanner = TradingScanner(
                binance_key="",
                binance_secret="",
                claude_key=settings.ANTHROPIC_API_KEY,
                groq_key=settings.GROQ_API_KEY,
                top_n_coins=3,
                min_confidence=settings.MIN_CONFIDENCE_SCORE
            )
            
            ai_provider = settings.AUTO_SCAN_AI_PROVIDER
            scanner.set_ai_provider(ai_provider)
            scanner.fetcher = yahoo_fetcher
            
            logger.info(f"   Using AI: {ai_provider.upper()}")
            
            # Scan each commodity
            all_setups = []
            for symbol in commodities:
                try:
                    # Get symbol info
                    symbol_info = yahoo_fetcher.get_symbol_info(symbol)
                    display_name = symbol_info['name'] if symbol_info else symbol
                    
                    logger.info(f"   Analyzing {display_name} ({symbol})...")
                    
                    # Fetch OHLCV data
                    ohlcv = await yahoo_fetcher.fetch_ohlcv(symbol, '4h', limit=100)
                    
                    if not ohlcv or len(ohlcv) < 50:
                        logger.warning(f"⚠️ Insufficient data for {symbol}")
                        continue
                    
                    # Get AI analysis
                    if ai_provider == 'claude':
                        analysis = await scanner.claude.analyze_setup(display_name, ohlcv, '4h')
                    else:
                        analysis = await scanner.groq.analyze_setup(display_name, ohlcv, '4h')
                    
                    if not analysis or analysis.get('confidence', 0) < settings.MIN_CONFIDENCE_SCORE:
                        logger.info(f"   {display_name}: Low confidence, skipping")
                        continue
                    
                    # Get current price
                    current_price = ohlcv[-1][4]
                    
                    # Calculate market strength (simplified)
                    market_strength = {
                        'score': 70,
                        'rating': '⚪ Neutral',
                        'reason': 'Commodity market strength'
                    }
                    
                    # Build setup
                    setup = {
                        'symbol': display_name,
                        'yahoo_symbol': symbol,
                        'timeframe': '4h',
                        'direction': analysis.get('direction', 'NEUTRAL'),
                        'confidence': analysis.get('confidence', 0),
                        'entry': analysis.get('entry', current_price),
                        'stop_loss': analysis.get('stop_loss', current_price * 0.98),
                        'take_profit': analysis.get('take_profit', current_price * 1.02),
                        'reasoning': analysis.get('reasoning', 'No reasoning provided'),
                        'market_strength': market_strength,
                        'ai_provider': ai_provider,
                        'market_type': 'commodity'
                    }
                    
                    all_setups.append(setup)
                    logger.info(f"   ✅ {display_name}: {setup['direction']} @ {setup['confidence']}%")
                    
                    # Save to database
                    self.trade_tracker.save_setup(setup, scan_id=scan_id)
                    
                except Exception as e:
                    logger.error(f"❌ Error analyzing {symbol}: {e}")
                    continue
            
            logger.info(f"✅ Auto commodities scan complete - found {len(all_setups)} setups")
            
            # Send to Telegram if available
            if self.telegram and self.telegram.is_available() and all_setups:
                await self.telegram.send_scan_summary(all_setups, title="🥇 Commodities Scan (Auto)")
                
                for setup in all_setups:
                    await self.telegram.send_alert(setup)
                
                logger.info("📱 Sent commodities alerts to Telegram")
            
            # Complete scan session
            high_conf_count = len([s for s in all_setups if s.get('confidence', 0) >= settings.MIN_CONFIDENCE_SCORE])
            self.trade_tracker.complete_scan_session(
                scan_id=scan_id,
                setups_count=len(all_setups),
                high_confidence_count=high_conf_count
            )
            
            logger.info("✅ Commodities 4H scan complete!")
            
        except Exception as e:
            logger.error(f"❌ Auto commodities scan error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def start(self):
        """Start the scheduler"""
        try:
            # Run every 4 hours, 30 minutes AFTER Binance candle close
            # This accounts for Yahoo Finance 15-20 min data delay
            # Binance candles close at: 03:59, 07:59, 11:59, 15:59, 19:59, 23:59 UTC
            # Commodities scans run at: 04:30, 08:30, 12:30, 16:30, 20:30, 00:30 UTC
            self.scheduler.add_job(
                self.run_4h_scan,
                CronTrigger(hour='0,4,8,12,16,20', minute=30),
                id='scan_commodities_4h',
                name='4H Commodities Scan (+30min delay)',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("✅ Auto-scan Commodities scheduler started (runs 30min after candle close: 04:30, 08:30, 12:30, 16:30, 20:30, 00:30 UTC)")
            
        except Exception as e:
            logger.error(f"❌ Commodities scheduler start error: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("👋 Auto-scan Commodities scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Commodities scheduler stop error: {e}")


# Global instance (will be initialized in main.py)
auto_scanner_commodities: AutoScannerCommodities = None

