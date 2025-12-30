"""
Database connection management
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

logger = logging.getLogger(__name__)

# Database URL (SQLite for now, easy to switch to PostgreSQL)
DATABASE_URL = "sqlite:///./trading_bot.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init error: {e}")


def get_db() -> Session:
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

