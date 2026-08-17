"""
routes/reports.py

GET /api/reports/{analysis_id}   -> generates (if needed) and returns the PDF

Rewritten to read from SQLite (athlete + analysis + risk result) instead of
the old in-memory store.
"""
from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import (
    Athlete as AthleteModel,
    MovementAnalysis as MovementAnalysisModel,
    RiskResult as RiskResultModel,
    User,
)
from app.routes.auth import get_current_user
from app.services.report import generate_pdf_report

router = APIRouter(prefix="/api/reports", tags=["reports"])

from app.config import REPORTS_DIR


@router.get("/{analysis_id}")
def get_report(analysis_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    analysis = (
        db.query(MovementAnalysisModel)
        .join(AthleteModel, MovementAnalysisModel.athlete_id == AthleteModel.id)
        .filter(MovementAnalysisModel.id == analysis_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    if analysis.status != "completed":
        raise HTTPException(status_code=422, detail="Analysis is not completed yet; report unavailable.")

    athlete = db.query(AthleteModel).filter(AthleteModel.id == analysis.athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete for this analysis was not found.")

    risk = db.query(RiskResultModel).filter(RiskResultModel.analysis_id == analysis_id).first()

    athlete_dict = {
        "athlete_id": athlete.id, "name": athlete.name, "sport": athlete.sport, "age": athlete.age,
        "height_cm": athlete.height_cm, "weight_kg": athlete.weight_kg,
        "injury_history": athlete.injury_history,
    }
    analysis_dict = {
        "activity": analysis.activity,
        "created_at": analysis.created_at,
        "frames_total": analysis.frames_total,
        "pose_detection_rate_pct": analysis.pose_detection_rate_pct,
        "biomechanics": json.loads(analysis.biomechanics_json) if analysis.biomechanics_json else {},
        "movement_quality": json.loads(analysis.movement_quality_json) if analysis.movement_quality_json else {},
        "observations": json.loads(analysis.observations_json) if analysis.observations_json else [],
    }
    risk_dict = None
    if risk:
        risk_dict = {
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level,
            "contributing_factors": json.loads(risk.contributing_factors_json) if risk.contributing_factors_json else [],
            "recommendations": json.loads(risk.recommendations_json) if risk.recommendations_json else [],
        }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, f"{analysis_id}_report.pdf")
    generate_pdf_report(athlete_dict, analysis_dict, output_path, risk=risk_dict)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"{analysis_id}_biomechanics_report.pdf",
    )
