"""
Trade Tracker Worker
Automatically checks open trades for TP/SL hits
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from ..database.models import TradeSetup
from ..database.connection import SessionLocal
from ..market_data import BinanceFetcher

logger = logging.getLogger(__name__)


class TradeTrackerWorker:
    """Worker that monitors open trades and updates outcomes"""
    
    def __init__(self, binance_fetcher: BinanceFetcher, telegram_notifier=None, trade_tracker=None):
        self.fetcher = binance_fetcher
        self.telegram = telegram_notifier
        self.trade_tracker = trade_tracker
        self.running = False
        logger.info("✅ Trade Tracker Worker initialized")
    
    async def start(self):
        """Start the tracking worker"""
        self.running = True
        logger.info("🔄 Trade Tracker Worker started (checks every 15 min)")
        
        while self.running:
            try:
                await self.check_all_open_trades()
                
                # Wait 15 minutes before next check
                await asyncio.sleep(900)  # 15 minutes
                
            except Exception as e:
                logger.error(f"❌ Tracker worker error: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        logger.info("🛑 Trade Tracker Worker stopped")
    
    async def check_all_open_trades(self):
        """Check all open trades for TP/SL hits"""
        # Check if system is enabled
        from app.admin.system_controller import system_controller
        if not system_controller.is_enabled:
            logger.debug("🔴 SYSTEM DISABLED - Skipping trade tracking")
            return
        
        db = SessionLocal()
        try:
            # Get all open trades
            open_trades = db.query(TradeSetup).filter(
                TradeSetup.status == 'open'
            ).all()
            
            if not open_trades:
                logger.debug("No open trades to check")
                return
            
            logger.info(f"🔍 Checking {len(open_trades)} open trades...")
            
            checked = 0
            updated = 0
            
            for trade in open_trades:
                try:
                    # Check if trade should be closed
                    outcome = await self.check_trade_outcome(trade)
                    
                    if outcome:
                        # Update trade in database
                        trade.status = outcome['status']
                        trade.closed_at = datetime.utcnow()
                        trade.exit_price = outcome['exit_price']
                        trade.profit_loss_pct = outcome['profit_loss_pct']
                        
                        db.commit()
                        updated += 1
                        
                        logger.info(f"{'✅' if outcome['status'] == 'hit_tp' else '❌'} {trade.symbol} {trade.timeframe}: {outcome['status']} | P/L: {outcome['profit_loss_pct']:.2f}%")
                        
                        # Send Telegram notification
                        if self.telegram and self.telegram.is_available() and self.trade_tracker:
                            try:
                                # Get updated stats
                                stats = self.trade_tracker.get_stats()
                                
                                # Prepare trade data for notification
                                trade_data = {
                                    'symbol': trade.symbol,
                                    'timeframe': trade.timeframe,
                                    'direction': trade.direction,
                                    'entry_price': trade.entry_price,
                                    'exit_price': trade.exit_price,
                                    'current_price': trade.current_price,
                                    'status': trade.status,
                                    'profit_loss_pct': trade.profit_loss_pct,
                                    'created_at': trade.created_at.isoformat() if trade.created_at else None,
                                    'closed_at': trade.closed_at.isoformat() if trade.closed_at else None
                                }
                                
                                # Send notification
                                await self.telegram.send_trade_close_alert(trade_data, stats)
                                
                            except Exception as e:
                                logger.error(f"❌ Error sending Telegram notification: {e}")
                    
                    checked += 1
                    
                    # Small delay between checks
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ Error checking trade #{trade.id}: {e}")
                    continue
            
            if updated > 0:
                logger.info(f"📊 Trade check complete: {checked} checked, {updated} closed")
            
        except Exception as e:
            logger.error(f"❌ Error in check_all_open_trades: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def check_trade_outcome(self, trade: TradeSetup) -> dict:
        """
        Check if a trade has hit TP, SL, or expired
        
        Returns None if still open, or dict with outcome
        """
        try:
            # Check if trade is too old (48 hours = expired)
            age_hours = (datetime.utcnow() - trade.created_at).total_seconds() / 3600
            
            if age_hours > 48:
                # Trade expired without hitting TP/SL
                return {
                    'status': 'expired',
                    'exit_price': trade.current_price,
                    'profit_loss_pct': 0.0
                }
            
            # Fetch current price
            current_price = await self.get_current_price(trade.symbol)
            
            if not current_price:
                return None
            
            # Check TP/SL
            if trade.direction == 'LONG':
                # Long trade
                if current_price >= trade.take_profit:
                    # Hit TP
                    profit_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    return {
                        'status': 'hit_tp',
                        'exit_price': current_price,
                        'profit_loss_pct': profit_pct
                    }
                elif current_price <= trade.stop_loss:
                    # Hit SL
                    loss_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    return {
                        'status': 'hit_sl',
                        'exit_price': current_price,
                        'profit_loss_pct': loss_pct
                    }
            
            elif trade.direction == 'SHORT':
                # Short trade
                if current_price <= trade.take_profit:
                    # Hit TP
                    profit_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                    return {
                        'status': 'hit_tp',
                        'exit_price': current_price,
                        'profit_loss_pct': profit_pct
                    }
                elif current_price >= trade.stop_loss:
                    # Hit SL
                    loss_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                    return {
                        'status': 'hit_sl',
                        'exit_price': current_price,
                        'profit_loss_pct': loss_pct
                    }
            
            # Still open
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking outcome for trade #{trade.id}: {e}")
            return None
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            # Fetch latest candle
            ohlcv = await self.fetcher.fetch_ohlcv(symbol, '1m', limit=1)
            
            if ohlcv and len(ohlcv) > 0:
                return ohlcv[0][4]  # Close price
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching price for {symbol}: {e}")
            return None

