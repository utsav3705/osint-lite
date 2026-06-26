"""
OSINT-Pro — Database Configuration
SQLAlchemy engine, session factory, and initialisation for SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database file lives in database/ subdirectory
DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "osint_pro.db")
DB_URI = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URI, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    """Create all tables if they do not already exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    # Import models so Base.metadata knows about them
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new database session. Caller is responsible for closing it."""
    return SessionLocal()
