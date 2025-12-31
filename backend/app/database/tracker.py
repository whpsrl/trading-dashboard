"""
Trade Tracking Service
Saves setups, tracks outcomes, calculates win rate
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .models import TradeSetup, ScanResult
from .connection import SessionLocal

logger = logging.getLogger(__name__)


class TradeTracker:
    """Handles all trade tracking operations"""
    
    def __init__(self):
        logger.info("✅ Trade Tracker initialized")
    
    def create_scan_session(
        self,
        scan_type: str = 'manual',
        top_n: int = 15,
        timeframes: List[str] = None,
        ai_provider: str = 'claude'
    ) -> int:
        """
        Create a new scan session
        Returns: scan_id
        """
        db = SessionLocal()
        try:
            scan = ScanResult(
                scan_type=scan_type,
                top_n_coins=top_n,
                timeframes=timeframes or ['15m', '1h', '4h'],
                ai_provider=ai_provider,
                started_at=datetime.utcnow(),
                status='running'
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)
            
            logger.info(f"📊 Created scan session #{scan.id} with {ai_provider.upper()} AI")
            return scan.id
            
        except Exception as e:
            logger.error(f"❌ Error creating scan session: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def save_setup(self, setup: Dict, scan_id: int = None) -> bool:
        """Save a trade setup to database"""
        db = SessionLocal()
        try:
            trade = TradeSetup(
                symbol=setup.get('symbol'),
                timeframe=setup.get('timeframe'),
                direction=setup.get('direction'),
                confidence=setup.get('confidence'),
                reasoning=setup.get('reasoning'),
                entry_price=setup.get('entry'),
                stop_loss=setup.get('stop_loss'),
                take_profit=setup.get('take_profit'),
                current_price=setup.get('current_price'),
                scan_id=scan_id,
                valid=setup.get('valid', True)
            )
            
            db.add(trade)
            db.commit()
            
            logger.info(f"💾 Saved setup: {setup['symbol']} {setup['timeframe']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving setup: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def complete_scan_session(
        self,
        scan_id: int,
        setups_count: int,
        high_confidence_count: int,
        status: str = 'completed'
    ):
        """Mark scan as completed"""
        db = SessionLocal()
        try:
            scan = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
            if scan:
                scan.completed_at = datetime.utcnow()
                scan.duration_seconds = (scan.completed_at - scan.started_at).total_seconds()
                scan.setups_found = setups_count
                scan.high_confidence_count = high_confidence_count
                scan.status = status
                db.commit()
                
                logger.info(f"✅ Scan #{scan_id} completed in {scan.duration_seconds:.1f}s")
                
        except Exception as e:
            logger.error(f"❌ Error completing scan: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_recent_scans(self, limit: int = 20) -> List[Dict]:
        """Get recent scan sessions"""
        db = SessionLocal()
        try:
            scans = db.query(ScanResult).order_by(
                ScanResult.started_at.desc()
            ).limit(limit).all()
            
            return [scan.to_dict() for scan in scans]
            
        except Exception as e:
            logger.error(f"❌ Error fetching scans: {e}")
            return []
        finally:
            db.close()
    
    def get_setups_by_scan(self, scan_id: int) -> List[Dict]:
        """Get all setups from a specific scan"""
        db = SessionLocal()
        try:
            setups = db.query(TradeSetup).filter(
                TradeSetup.scan_id == scan_id
            ).order_by(
                TradeSetup.confidence.desc()
            ).all()
            
            return [setup.to_dict() for setup in setups]
            
        except Exception as e:
            logger.error(f"❌ Error fetching setups: {e}")
            return []
        finally:
            db.close()
    
    def get_all_setups(
        self, 
        limit: int = 100,
        status: str = None,
        market_type: str = None,
        timeframe: str = None
    ) -> List[Dict]:
        """Get all recent setups with optional filters"""
        db = SessionLocal()
        try:
            query = db.query(TradeSetup)
            
            # Apply filters if provided
            if status:
                query = query.filter(TradeSetup.status == status)
            if timeframe:
                query = query.filter(TradeSetup.timeframe == timeframe)
            
            # Order by most recent first
            setups = query.order_by(
                TradeSetup.created_at.desc()
            ).limit(limit).all()
            
            return [setup.to_dict() for setup in setups]
            
        except Exception as e:
            logger.error(f"❌ Error fetching all setups: {e}")
            return []
        finally:
            db.close()
    
    def get_stats(self) -> Dict:
        """Get overall statistics for auto-learning"""
        db = SessionLocal()
        try:
            total_setups = db.query(TradeSetup).count()
            
            closed_trades = db.query(TradeSetup).filter(
                TradeSetup.status.in_(['hit_tp', 'hit_sl'])
            ).all()
            
            if not closed_trades:
                return {
                    'total_setups': total_setups,
                    'tracked_trades': 0,
                    'win_count': 0,
                    'loss_count': 0,
                    'win_rate': 0,
                    'avg_profit': 0,
                    'avg_loss': 0,
                    'total_pl': 0,
                    'expected_value': 0,
                    'risk_reward': 0,
                    'learning_score': 0,
                    'total_scans': db.query(ScanResult).count()
                }
            
            winners = [t for t in closed_trades if t.status == 'hit_tp']
            losers = [t for t in closed_trades if t.status == 'hit_sl']
            
            win_count = len(winners)
            loss_count = len(losers)
            
            win_rate = (win_count / len(closed_trades)) * 100 if closed_trades else 0
            loss_rate = 100 - win_rate
            
            avg_profit = sum([t.profit_loss_pct for t in winners]) / win_count if winners else 0
            avg_loss = sum([abs(t.profit_loss_pct) for t in losers]) / loss_count if losers else 0
            
            # Total P/L (net profit/loss)
            total_pl = sum([t.profit_loss_pct for t in closed_trades])
            
            # Expected Value per trade
            expected_value = (win_rate / 100 * avg_profit) - (loss_rate / 100 * avg_loss)
            
            # Risk/Reward ratio
            risk_reward = avg_profit / avg_loss if avg_loss > 0 else 0
            
            # Learning score: combination of win rate and risk/reward
            learning_score = min(100, win_rate * (1 + avg_profit / 10))
            
            return {
                'total_setups': total_setups,
                'tracked_trades': len(closed_trades),
                'win_count': win_count,
                'loss_count': loss_count,
                'win_rate': round(win_rate, 2),
                'avg_profit': round(avg_profit, 2),
                'avg_loss': round(avg_loss, 2),
                'total_pl': round(total_pl, 2),
                'expected_value': round(expected_value, 2),
                'risk_reward': round(risk_reward, 2),
                'learning_score': round(learning_score, 2),
                'total_scans': db.query(ScanResult).count()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating stats: {e}")
            return {'error': str(e)}
        finally:
            db.close()


# Global instance
trade_tracker = TradeTracker()

