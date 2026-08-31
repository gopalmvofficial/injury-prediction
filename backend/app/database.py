"""
database.py

Database engine and session setup via SQLAlchemy.
Supports SQLite locally and PostgreSQL in production with automatic connection recovery.
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# Normalize postgres:// to postgresql:// for SQLAlchemy 2.0+ compatibility
normalized_db_url = DATABASE_URL
if normalized_db_url.startswith("postgres://"):
    normalized_db_url = normalized_db_url.replace("postgres://", "postgresql://", 1)

# check_same_thread=False is only needed for SQLite
connect_args = {"check_same_thread": False} if normalized_db_url.startswith("sqlite") else {}

if normalized_db_url.startswith("sqlite"):
    db_path = normalized_db_url.replace("sqlite:///", "", 1)
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    normalized_db_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Automatically tests connection vitality
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Creates all tables if they don't already exist. Safe to call on every startup."""
    from app.models import db_models  # noqa: F401 - ensures models are registered on Base
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency - yields a session per-request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
