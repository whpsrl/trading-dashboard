"""
Automatic hourly scanning scheduler
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

logger = logging.getLogger(__name__)


class AutoScanner:
    """Handles automatic scheduled scans"""
    
    def __init__(self, scanner, telegram, trade_tracker):
        self.scanner = scanner
        self.telegram = telegram
        self.trade_tracker = trade_tracker
        self.scheduler = AsyncIOScheduler()
        logger.info("✅ Auto-scanner initialized")
    
    async def run_4h_scan(self):
        """Execute 4h scan (synchronized with candle close)"""
        try:
            logger.info("🕐 Starting automatic 4H scan (candle close)...")
            
            # Create scan session
            scan_id = self.trade_tracker.create_scan_session(
                scan_type='auto_4h',
                top_n=15,
                timeframes=['4h']
            )
            
            # Scan market - ONLY 4H timeframe
            # Use configured AI provider for auto-scans
            from ..config import settings
            ai_provider = settings.AUTO_SCAN_AI_PROVIDER
            
            logger.info(f"   Using AI: {ai_provider.upper()}")
            
            setups = await self.scanner.scan_market(
                timeframes=['4h'],
                max_results=50,
                ai_provider=ai_provider
            )
            
            logger.info(f"✅ Auto scan complete - found {len(setups) if setups else 0} setups")
            
            # Save setups to database
            if setups:
                for setup in setups:
                    self.trade_tracker.save_setup(setup, scan_id=scan_id)
                
                # Send top 5 to Telegram
                if self.telegram and self.telegram.is_available():
                    top_5 = sorted(setups, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
                    await self.telegram.send_scan_summary(top_5)
                    
                    for setup in top_5:
                        await self.telegram.send_alert(setup)
                    
                    logger.info("📱 Sent top 5 setups to Telegram")
            
            # Complete scan session
            high_conf_count = len([s for s in setups if s.get('confidence', 0) >= 60]) if setups else 0
            self.trade_tracker.complete_scan_session(
                scan_id=scan_id,
                setups_count=len(setups) if setups else 0,
                high_confidence_count=high_conf_count
            )
            
            logger.info("✅ Hourly scan complete!")
            
        except Exception as e:
            logger.error(f"❌ Auto scan error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def start(self):
        """Start the scheduler"""
        try:
            # Run every 4 hours at Binance 4H candle close: 03:00, 07:00, 11:00, 15:00, 19:00, 23:00 UTC
            # (04:00, 08:00, 12:00, 16:00, 20:00, 00:00 Italy time)
            self.scheduler.add_job(
                self.run_4h_scan,
                CronTrigger(hour='3,7,11,15,19,23', minute=0),
                id='scan_4h',
                name='4H Market Scan (Candle Close)',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("✅ Auto-scan scheduler started (runs every 4h at Binance candle close: 03:00, 07:00, 11:00, 15:00, 19:00, 23:00 UTC)")
            
        except Exception as e:
            logger.error(f"❌ Scheduler start error: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("👋 Auto-scan scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Scheduler stop error: {e}")


# Global instance (will be initialized in main.py)
auto_scanner: AutoScanner = None

