"""
Database models for trade tracking and learning system
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

class TradeStatus(str, enum.Enum):
    PENDING = "pending"  # Trade aperto, in attesa
    HIT_TARGET_1 = "hit_target_1"  # Raggiunto primo target
    HIT_TARGET_2 = "hit_target_2"  # Raggiunto secondo target
    STOPPED = "stopped"  # Stop loss colpito
    CANCELLED = "cancelled"  # Trade cancellato manualmente
    EXPIRED = "expired"  # Trade scaduto (troppo tempo)

class MarketType(str, enum.Enum):
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"
    COMMODITIES = "commodities"
    INDICES = "indices"

class Trade(Base):
    """
    Represents a trade recommendation that we track
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade identification
    symbol = Column(String, index=True, nullable=False)
    market_type = Column(SQLEnum(MarketType), nullable=False)
    timeframe = Column(String, nullable=False)  # 15m, 1h, 4h, 1d
    
    # Entry details
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    entry_price = Column(Float, nullable=False)
    direction = Column(SQLEnum(TradeDirection), nullable=False)
    
    # Trade levels
    stop_loss = Column(Float, nullable=True)
    target_1 = Column(Float, nullable=True)
    target_2 = Column(Float, nullable=True)
    
    # Scoring & AI
    technical_score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-100
    ai_validation_score = Column(Float, nullable=True)  # 1-10
    ai_recommendation = Column(String, nullable=True)
    
    # Technical indicators at entry (for learning)
    indicators_snapshot = Column(JSON, nullable=True)
    confluences = Column(JSON, nullable=True)  # Array of confluence strings
    warnings = Column(JSON, nullable=True)  # Array of warning strings
    
    # Trade tracking
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.PENDING, nullable=False)
    highest_price = Column(Float, nullable=True)  # Highest price reached (for LONG)
    lowest_price = Column(Float, nullable=True)  # Lowest price reached (for SHORT)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    
    # Results
    profit_loss_percent = Column(Float, nullable=True)  # % profit or loss
    risk_reward_realized = Column(Float, nullable=True)  # R:R actually realized
    duration_minutes = Column(Integer, nullable=True)  # How long trade lasted
    
    # Metadata
    notified_telegram = Column(Boolean, default=False)
    last_checked = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, direction={self.direction}, status={self.status})>"


class TradeStatistics(Base):
    """
    Aggregate statistics for learning and improvement
    """
    __tablename__ = "trade_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Aggregation period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Overall metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # %
    
    # Performance metrics
    avg_profit_percent = Column(Float, default=0.0)
    avg_loss_percent = Column(Float, default=0.0)
    avg_risk_reward = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)  # Total profit / Total loss
    
    # By market type
    stats_by_market = Column(JSON, nullable=True)  # {crypto: {win_rate: X, ...}, stocks: {...}}
    
    # By timeframe
    stats_by_timeframe = Column(JSON, nullable=True)  # {1h: {win_rate: X, ...}, 4h: {...}}
    
    # By direction
    stats_by_direction = Column(JSON, nullable=True)  # {LONG: {win_rate: X, ...}, SHORT: {...}}
    
    # Best performing confluences
    best_confluences = Column(JSON, nullable=True)  # Array of [{confluence: "...", win_rate: X}]
    worst_confluences = Column(JSON, nullable=True)
    
    # Learning insights
    insights = Column(JSON, nullable=True)  # Array of insight strings for AI
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TradeStatistics(total={self.total_trades}, win_rate={self.win_rate}%)>"


class AILearning(Base):
    """
    Tracks what the AI learns over time to improve predictions
    """
    __tablename__ = "ai_learning"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Learning category
    category = Column(String, nullable=False)  # e.g., "rsi_overbought", "macd_divergence"
    subcategory = Column(String, nullable=True)
    
    # Performance of this specific pattern/setup
    total_occurrences = Column(Integer, default=0)
    successful_outcomes = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Average metrics when this pattern occurs
    avg_score = Column(Float, nullable=True)
    avg_rr_realized = Column(Float, nullable=True)
    
    # Context
    market_types = Column(JSON, nullable=True)  # Which markets this pattern works best in
    timeframes = Column(JSON, nullable=True)  # Which timeframes
    
    # Learning notes for AI
    ai_notes = Column(String, nullable=True)
    confidence_adjustment = Column(Float, default=0.0)  # How much to adjust confidence by
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AILearning(category={self.category}, success_rate={self.success_rate}%)>"

