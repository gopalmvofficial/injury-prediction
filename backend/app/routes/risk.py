"""
routes/risk.py

GET /api/risk/{analysis_id}              - risk result for one analysis
GET /api/athletes/{athlete_id}/risk-history - all risk results for an athlete, newest first
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Athlete as AthleteModel, RiskResult as RiskResultModel, User
from app.routes.auth import get_current_user
from app.schemas.schemas import RiskResult

router = APIRouter(prefix="/api", tags=["risk"])


def _to_schema(r: RiskResultModel) -> RiskResult:
    return RiskResult(
        risk_id=r.id,
        athlete_id=r.athlete_id,
        analysis_id=r.analysis_id,
        risk_score=r.risk_score,
        risk_level=r.risk_level,
        contributing_factors=json.loads(r.contributing_factors_json) if r.contributing_factors_json else [],
        recommendations=json.loads(r.recommendations_json) if r.recommendations_json else [],
        is_placeholder_model=(r.is_placeholder_model == "true"),
        created_at=r.created_at,
    )


@router.get("/risk/{analysis_id}", response_model=RiskResult)
def get_risk_for_analysis(analysis_id: str, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    risk = (
        db.query(RiskResultModel)
        .join(AthleteModel, RiskResultModel.athlete_id == AthleteModel.id)
        .filter(RiskResultModel.analysis_id == analysis_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not risk:
        raise HTTPException(status_code=404, detail=f"No risk result found for analysis '{analysis_id}'.")
    return _to_schema(risk)


@router.get("/athletes/{athlete_id}/risk-history", response_model=list[RiskResult])
def get_risk_history(athlete_id: str, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")

    results = (
        db.query(RiskResultModel)
        .filter(RiskResultModel.athlete_id == athlete_id)
        .order_by(RiskResultModel.created_at.desc())
        .all()
    )
    return [_to_schema(r) for r in results]
