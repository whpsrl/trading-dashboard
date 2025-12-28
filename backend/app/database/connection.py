"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .models import Base
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Fix for Railway PostgreSQL URLs
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False  # Set to True for SQL debugging
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("✅ Database connection configured")
else:
    engine = None
    SessionLocal = None
    logger.warning("⚠️  DATABASE_URL not configured - trade tracking disabled")


def init_db():
    """
    Initialize database tables
    """
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
    else:
        logger.warning("⚠️  Cannot initialize database - no connection")


@contextmanager
def get_db() -> Session:
    """
    Get database session context manager
    """
    if not SessionLocal:
        raise Exception("Database not configured")
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for dependency injection)
    """
    if not SessionLocal:
        return None
    
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"❌ Error creating database session: {e}")
        return None

