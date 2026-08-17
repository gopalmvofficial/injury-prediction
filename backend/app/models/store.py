"""
store.py

Lightweight in-memory data store for Milestone 2, per spec section 8:
"do NOT overcomplicate the database... temporary in-memory or lightweight
local storage approach is acceptable... design the code so PostgreSQL can
be added in a later milestone."

Design note for Milestone 3: every method here is intentionally isolated
behind a small interface (get/save/list) so swapping this module for a
real SQLAlchemy + PostgreSQL-backed repository later does not require
touching the route handlers - they only ever call these functions.

This in-memory store resets whenever the backend process restarts, and is
NOT process-safe for multiple workers (uvicorn --workers 1 during
development is assumed, as is standard while iterating locally).
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

_lock = threading.Lock()

_athletes: Dict[str, dict] = {}
_videos: Dict[str, dict] = {}
_analyses: Dict[str, dict] = {}


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# --- Athletes ---------------------------------------------------------

def save_athlete(data: dict) -> dict:
    with _lock:
        athlete_id = data.get("athlete_id") or new_id("ATH")
        record = {**data, "athlete_id": athlete_id, "created_at": datetime.now(timezone.utc)}
        _athletes[athlete_id] = record
        return record


def get_athlete(athlete_id: str) -> Optional[dict]:
    return _athletes.get(athlete_id)


def list_athletes() -> List[dict]:
    return list(_athletes.values())


# --- Videos -------------------------------------------------------------

def save_video(data: dict) -> dict:
    with _lock:
        video_id = data.get("video_id") or new_id("VID")
        record = {**data, "video_id": video_id}
        _videos[video_id] = record
        return record


def get_video(video_id: str) -> Optional[dict]:
    return _videos.get(video_id)


# --- Analyses -------------------------------------------------------------

def save_analysis(data: dict) -> dict:
    with _lock:
        analysis_id = data.get("analysis_id") or new_id("ANALYSIS")
        record = {**data, "analysis_id": analysis_id}
        _analyses[analysis_id] = record
        return record


def get_analysis(analysis_id: str) -> Optional[dict]:
    return _analyses.get(analysis_id)


def list_analyses() -> List[dict]:
    return list(_analyses.values())
