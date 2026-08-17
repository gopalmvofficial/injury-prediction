"""
routes/dashboard.py

GET /api/dashboard/summary

Returns real, database-derived counts and recent activity for the logged-in
user - never hardcoded numbers. If there are 0 athletes, this returns 0.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import (
    Athlete as AthleteModel,
    MovementAnalysis as MovementAnalysisModel,
    RiskResult as RiskResultModel,
    User,
    Video as VideoModel,
)
from app.routes.auth import get_current_user
from app.routes.analysis import _analysis_to_schema
from app.routes.athletes import _to_schema as _athlete_to_schema
from app.schemas.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    athlete_ids_subq = db.query(AthleteModel.id).filter(AthleteModel.user_id == current_user.id)
    athlete_id_list = [row[0] for row in athlete_ids_subq.all()]

    total_athletes = len(athlete_id_list)

    total_videos = (
        db.query(VideoModel).filter(VideoModel.athlete_id.in_(athlete_id_list)).count()
        if athlete_id_list else 0
    )
    total_analyses = (
        db.query(MovementAnalysisModel).filter(MovementAnalysisModel.athlete_id.in_(athlete_id_list)).count()
        if athlete_id_list else 0
    )

    risk_results = (
        db.query(RiskResultModel).filter(RiskResultModel.athlete_id.in_(athlete_id_list)).all()
        if athlete_id_list else []
    )
    high_risk_athletes = len({r.athlete_id for r in risk_results if r.risk_level == "HIGH"})

    risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r in risk_results:
        if r.risk_level in risk_distribution:
            risk_distribution[r.risk_level] += 1

    recent_athletes = (
        db.query(AthleteModel)
        .filter(AthleteModel.user_id == current_user.id)
        .order_by(AthleteModel.created_at.desc())
        .limit(5)
        .all()
    )
    recent_analyses = (
        db.query(MovementAnalysisModel)
        .filter(MovementAnalysisModel.athlete_id.in_(athlete_id_list))
        .order_by(MovementAnalysisModel.created_at.desc())
        .limit(5)
        .all()
        if athlete_id_list else []
    )

    return DashboardSummary(
        total_athletes=total_athletes,
        total_videos=total_videos,
        total_analyses=total_analyses,
        high_risk_athletes=high_risk_athletes,
        risk_distribution=risk_distribution,
        recent_athletes=[_athlete_to_schema(a) for a in recent_athletes],
        recent_analyses=[_analysis_to_schema(a) for a in recent_analyses],
    )
