"""
Database session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from utils.config import settings
from .base import Base

logger = logging.getLogger(__name__)

# Create engine
# For SQLite: sqlite:///./autocbot.db
# For PostgreSQL: postgresql://user:password@localhost:5432/autocbot
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./autocbot.db"

# SQLite specific settings
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,  # Log all SQL statements in debug mode
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables
    Should be called on application startup
    """
    logger.info(f"Initializing database: {DATABASE_URL}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def drop_db() -> None:
    """
    Drop all tables - USE WITH CAUTION!
    Only for development/testing
    """
    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ All tables dropped")
