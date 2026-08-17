"""
db_models.py

SQLAlchemy ORM models backing persistent SQLite storage. Replaces the
Milestone 2 in-memory store.py for athlete/video/analysis data per the
updated mentor requirement that data survive a backend restart.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid(prefix: str):
    def _gen():
        return f"{prefix}_{uuid.uuid4().hex[:10]}"
    return _gen


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid("USER"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    athletes = relationship("Athlete", back_populates="owner", cascade="all, delete-orphan")


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(String, primary_key=True, default=_uuid("ATH"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    sport = Column(String, nullable=False)
    position = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    injury_history = Column(Text, nullable=True)
    training_load = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="athletes")
    videos = relationship("Video", back_populates="athlete", cascade="all, delete-orphan")
    analyses = relationship("MovementAnalysis", back_populates="athlete", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=_uuid("VID"))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    activity = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    stored_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processing_status = Column(String, default="uploaded")  # uploaded | processing | completed | failed

    athlete = relationship("Athlete", back_populates="videos")
    analyses = relationship("MovementAnalysis", back_populates="video", cascade="all, delete-orphan")


class MovementAnalysis(Base):
    __tablename__ = "movement_analyses"

    id = Column(String, primary_key=True, default=_uuid("ANALYSIS"))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    activity = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing | completed | failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    frames_total = Column(Integer, nullable=True)
    frames_with_pose = Column(Integer, nullable=True)
    pose_detection_rate_pct = Column(Float, nullable=True)

    # Stored as JSON-encoded text - kept simple (no JSON column type dependency)
    movement_quality_json = Column(Text, nullable=True)
    biomechanics_json = Column(Text, nullable=True)
    observations_json = Column(Text, nullable=True)

    processed_video_path = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    athlete = relationship("Athlete", back_populates="analyses")
    video = relationship("Video", back_populates="analyses")
    risk_result = relationship("RiskResult", back_populates="analysis", uselist=False,
                                cascade="all, delete-orphan")


class RiskResult(Base):
    __tablename__ = "risk_results"

    id = Column(String, primary_key=True, default=_uuid("RISK"))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    analysis_id = Column(String, ForeignKey("movement_analyses.id"), nullable=False, unique=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # LOW | MEDIUM | HIGH
    contributing_factors_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    is_placeholder_model = Column(String, default="true")  # "true" - rule-based, not a trained ML model
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    analysis = relationship("MovementAnalysis", back_populates="risk_result")


class Session(Base):
    """
    Login session tokens, persisted in the database rather than kept in an
    in-memory dict. This matters for a real deployment: an in-memory store
    would lose all sessions on every restart, and would be inconsistent
    across multiple server workers/instances (a request could land on a
    worker that never saw the token get created). Storing it in the
    database - the same one every worker already reads from - fixes both.
    """
    __tablename__ = "sessions"

    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
