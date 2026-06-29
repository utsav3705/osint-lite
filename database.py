"""
OSINT-Pro — Database Configuration
SQLAlchemy engine, session factory, and initialisation for SQLite.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE = DATABASE_DIR / "osint_pro.db"
DB_URI = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(DB_URI, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    """Create all tables if they do not already exist."""
    # Import models so Base.metadata knows about them
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new database session. Caller is responsible for closing it."""
    return SessionLocal()
