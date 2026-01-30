"""
Database configuration and session management
Provides SQLAlchemy setup for the NLP processing system
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - can be configured via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nlp_comments.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database sessions
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    from backend.models import Review, SentimentResult, TopicResult
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def reset_db():
    """
    Reset database - drop and recreate all tables
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset successfully")
