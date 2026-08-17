"""
database.py

Database engine and session setup via SQLAlchemy. Uses SQLite locally by
default (backend/database/app.db) or whatever DATABASE_URL is set to in
production - see config.py. SQLAlchemy is DB-agnostic, so pointing this at
PostgreSQL for a real deployment needs no changes here, only the env var
and `pip install psycopg2-binary`.
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# check_same_thread=False is only needed/valid for SQLite; harmless to omit
# for other engines, so only pass it when actually using SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

if DATABASE_URL.startswith("sqlite"):
    # Ensure the directory for the SQLite file exists (e.g. backend/database/).
    db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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
