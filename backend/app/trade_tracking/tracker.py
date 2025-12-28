"""
Trade tracking service - monitors recommended trades and records results
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ..database import (
    Trade,
    TradeStatus,
    TradeDirection,
    MarketType,
    get_db_session
)
from ..market_data.unified_service import UnifiedMarketDataService

logger = logging.getLogger(__name__)


class TradeTracker:
    """
    Tracks active trades and updates their status based on market prices
    """
    
    def __init__(self):
        self.market_service = UnifiedMarketDataService()
        self.is_running = False
    
    def save_trade(
        self,
        symbol: str,
        market_type: str,
        timeframe: str,
        direction: str,
        entry_price: float,
        stop_loss: Optional[float],
        target_1: Optional[float],
        target_2: Optional[float],
        technical_score: float,
        confidence: float,
        ai_validation: Optional[Dict] = None,
        indicators: Optional[Dict] = None,
        confluences: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Save a new trade recommendation to track
        """
        db = get_db_session()
        if not db:
            logger.warning("Database not available - cannot save trade")
            return None
        
        try:
            trade = Trade(
                symbol=symbol,
                market_type=MarketType(market_type.lower()),
                timeframe=timeframe,
                direction=TradeDirection(direction),
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                technical_score=technical_score,
                confidence=confidence,
                ai_validation_score=ai_validation.get('validation_score') if ai_validation else None,
                ai_recommendation=ai_validation.get('recommendation') if ai_validation else None,
                indicators_snapshot=indicators,
                confluences=confluences,
                warnings=warnings,
                status=TradeStatus.PENDING,
                highest_price=entry_price if direction == 'LONG' else None,
                lowest_price=entry_price if direction == 'SHORT' else None
            )
            
            db.add(trade)
            db.commit()
            db.refresh(trade)
            
            logger.info(f"✅ Trade saved: {symbol} {direction} at ${entry_price}")
            return trade.id
            
        except Exception as e:
            logger.error(f"❌ Error saving trade: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    async def check_active_trades(self):
        """
        Check all active trades and update their status
        """
        db = get_db_session()
        if not db:
            return
        
        try:
            # Get all pending trades
            active_trades = db.query(Trade).filter(
                Trade.status == TradeStatus.PENDING
            ).all()
            
            logger.info(f"🔍 Checking {len(active_trades)} active trades...")
            
            for trade in active_trades:
                await self._update_trade_status(db, trade)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error checking trades: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _update_trade_status(self, db: Session, trade: Trade):
        """
        Update a single trade's status based on current price
        """
        try:
            # Get current price
            current_price = await self._get_current_price(trade.symbol, trade.market_type.value)
            
            if current_price is None:
                logger.warning(f"⚠️  Could not get price for {trade.symbol}")
                return
            
            # Update highest/lowest price
            if trade.direction == TradeDirection.LONG:
                if trade.highest_price is None or current_price > trade.highest_price:
                    trade.highest_price = current_price
            else:  # SHORT
                if trade.lowest_price is None or current_price < trade.lowest_price:
                    trade.lowest_price = current_price
            
            trade.last_checked = datetime.utcnow()
            
            # Check if trade hit targets or stop loss
            status_changed = False
            
            if trade.direction == TradeDirection.LONG:
                # Check stop loss
                if trade.stop_loss and current_price <= trade.stop_loss:
                    trade.status = TradeStatus.STOPPED
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🛑 LONG {trade.symbol} stopped at ${current_price}")
                
                # Check target 2
                elif trade.target_2 and current_price >= trade.target_2:
                    trade.status = TradeStatus.HIT_TARGET_2
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🎯🎯 LONG {trade.symbol} hit T2 at ${current_price}")
                
                # Check target 1
                elif trade.target_1 and current_price >= trade.target_1:
                    trade.status = TradeStatus.HIT_TARGET_1
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🎯 LONG {trade.symbol} hit T1 at ${current_price}")
            
            else:  # SHORT
                # Check stop loss
                if trade.stop_loss and current_price >= trade.stop_loss:
                    trade.status = TradeStatus.STOPPED
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🛑 SHORT {trade.symbol} stopped at ${current_price}")
                
                # Check target 2
                elif trade.target_2 and current_price <= trade.target_2:
                    trade.status = TradeStatus.HIT_TARGET_2
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🎯🎯 SHORT {trade.symbol} hit T2 at ${current_price}")
                
                # Check target 1
                elif trade.target_1 and current_price <= trade.target_1:
                    trade.status = TradeStatus.HIT_TARGET_1
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    status_changed = True
                    logger.info(f"🎯 SHORT {trade.symbol} hit T1 at ${current_price}")
            
            # Calculate P/L if trade closed
            if status_changed:
                self._calculate_trade_results(trade)
                
                # Send Telegram notification
                await self._notify_telegram(trade)
            
            # Check if trade is too old (expired)
            if trade.status == TradeStatus.PENDING:
                age_hours = (datetime.utcnow() - trade.created_at).total_seconds() / 3600
                max_age = self._get_max_age_hours(trade.timeframe)
                
                if age_hours > max_age:
                    trade.status = TradeStatus.EXPIRED
                    trade.exit_price = current_price
                    trade.exit_time = datetime.utcnow()
                    self._calculate_trade_results(trade)
                    logger.info(f"⏰ Trade {trade.symbol} expired after {age_hours:.1f}h")
        
        except Exception as e:
            logger.error(f"❌ Error updating trade {trade.id}: {e}")
    
    async def _get_current_price(self, symbol: str, market_type: str) -> Optional[float]:
        """
        Get current price for a symbol
        """
        try:
            # Get just 1 candle to get current price
            candles = await self.market_service.get_ohlcv(
                symbol=symbol,
                timeframe='1m',
                limit=1,
                market_type=market_type
            )
            
            if candles and len(candles) > 0:
                return candles[-1]['close']
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def _calculate_trade_results(self, trade: Trade):
        """
        Calculate profit/loss and other metrics for a completed trade
        """
        if not trade.exit_price:
            return
        
        # Calculate P/L percentage
        if trade.direction == TradeDirection.LONG:
            pl_percent = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
        else:  # SHORT
            pl_percent = ((trade.entry_price - trade.exit_price) / trade.entry_price) * 100
        
        trade.profit_loss_percent = pl_percent
        
        # Calculate realized R:R
        if trade.stop_loss:
            risk = abs(trade.entry_price - trade.stop_loss)
            reward = abs(trade.exit_price - trade.entry_price)
            if risk > 0:
                trade.risk_reward_realized = reward / risk
        
        # Calculate duration
        if trade.exit_time:
            duration = (trade.exit_time - trade.entry_time).total_seconds() / 60
            trade.duration_minutes = int(duration)
    
    async def _notify_telegram(self, trade: Trade):
        """
        Send Telegram notification about trade result
        """
        try:
            from ..telegram_bot.service import send_trade_result_notification
            
            if not trade.notified_telegram:
                await send_trade_result_notification(trade)
                trade.notified_telegram = True
        
        except Exception as e:
            logger.error(f"❌ Error sending Telegram notification: {e}")
    
    def _get_max_age_hours(self, timeframe: str) -> int:
        """
        Get max age in hours before a trade expires
        """
        timeframe_map = {
            '15m': 24,   # 1 day
            '1h': 72,    # 3 days
            '4h': 168,   # 1 week
            '1d': 720    # 1 month
        }
        return timeframe_map.get(timeframe, 72)
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """
        Start background monitoring of trades
        """
        logger.info("🚀 Starting trade monitoring...")
        self.is_running = True
        
        while self.is_running:
            try:
                await self.check_active_trades()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """
        Stop background monitoring
        """
        logger.info("🛑 Stopping trade monitoring...")
        self.is_running = False


# Global tracker instance
tracker = TradeTracker()

