"""
Database models for trade tracking
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TradeSetup(Base):
    """Individual trade setup from AI analysis"""
    __tablename__ = 'trade_setups'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade details
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False)  # 15m, 1h, 4h
    direction = Column(String, nullable=False)  # LONG, SHORT, NEUTRAL
    
    # AI Analysis
    confidence = Column(Integer, nullable=False)  # 0-100
    reasoning = Column(Text, nullable=False)
    
    # Entry points
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Outcome (filled when trade completes)
    status = Column(String, default='open')  # open, hit_tp, hit_sl, expired
    closed_at = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    profit_loss_pct = Column(Float, nullable=True)  # % gain/loss
    
    # Metadata
    scan_id = Column(Integer, index=True)  # Links to ScanResult
    valid = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'direction': self.direction,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'entry': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'current_price': self.current_price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'profit_loss_pct': self.profit_loss_pct
        }


class ScanResult(Base):
    """Scan session results - groups multiple setups"""
    __tablename__ = 'scan_results'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scan metadata
    scan_type = Column(String, default='manual')  # manual, auto_hourly, manual_commodities, auto_commodities_4h
    top_n_coins = Column(Integer, default=15)
    timeframes = Column(JSON)  # ['15m', '1h', '4h']
    ai_provider = Column(String, default='claude')  # claude, groq
    
    # Results
    setups_found = Column(Integer, default=0)
    high_confidence_count = Column(Integer, default=0)  # confidence >= 60
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default='running')  # running, completed, error
    error_message = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_type': self.scan_type,
            'top_n_coins': self.top_n_coins,
            'timeframes': self.timeframes,
            'ai_provider': self.ai_provider,
            'setups_found': self.setups_found,
            'high_confidence_count': self.high_confidence_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'status': self.status
        }

