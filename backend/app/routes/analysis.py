"""
routes/analysis.py

POST /api/videos/analyze
GET  /api/analysis/{analysis_id}

Full pipeline: OpenCV read -> MediaPipe pose -> skeleton draw -> biomechanics
-> movement quality -> observations -> risk prediction (rule-based
placeholder) -> recommendations -> persisted to SQLite.

Runs synchronously (no task queue) - acceptable for short demo clips, per
Milestone 2 scope. The response only returns once processing has finished.
"""
from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
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
from app.schemas.schemas import AnalysisResult, AnalyzeRequest
from app.services import biomechanics, movement_quality, observations as obs_module
from app.services import recommendations as recommendations_module
from app.services import risk_prediction
from app.services.video_processing import VideoProcessingError, process_video

router = APIRouter(prefix="/api", tags=["analysis"])

from app.config import RESULTS_DIR


def _analysis_to_schema(a: MovementAnalysisModel) -> AnalysisResult:
    return AnalysisResult(
        analysis_id=a.id,
        athlete_id=a.athlete_id,
        video_id=a.video_id,
        activity=a.activity,
        status=a.status,
        created_at=a.created_at,
        frames_total=a.frames_total,
        frames_with_pose=a.frames_with_pose,
        pose_detection_rate_pct=a.pose_detection_rate_pct,
        movement_quality=json.loads(a.movement_quality_json) if a.movement_quality_json else None,
        biomechanics=json.loads(a.biomechanics_json) if a.biomechanics_json else None,
        observations=json.loads(a.observations_json) if a.observations_json else [],
        processed_video_path=a.processed_video_path,
        error=a.error,
    )


def _owned_athlete_or_404(db: Session, athlete_id: str, user_id: str) -> AthleteModel:
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == user_id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")
    return athlete


@router.post("/videos/analyze", response_model=AnalysisResult)
def analyze_video(payload: AnalyzeRequest, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    athlete = _owned_athlete_or_404(db, payload.athlete_id, current_user.id)
    video = db.query(VideoModel).filter(VideoModel.id == payload.video_id,
                                         VideoModel.athlete_id == athlete.id).first()
    if not video:
        raise HTTPException(status_code=404, detail=f"Video '{payload.video_id}' not found.")

    analysis = MovementAnalysisModel(
        athlete_id=athlete.id, video_id=video.id, activity=payload.activity, status="processing",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    video.processing_status = "processing"
    db.commit()

    try:
        result = process_video(video.stored_path, RESULTS_DIR)
    except VideoProcessingError as e:
        analysis.status = "failed"
        analysis.error = str(e)
        video.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # noqa: BLE001 - surface unexpected pipeline errors, don't crash the app
        analysis.status = "failed"
        analysis.error = f"Unexpected processing error: {e}"
        video.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Unexpected processing error: {e}\n{traceback.format_exc()[-800:]}")

    if result.frames_with_pose == 0:
        analysis.status = "failed"
        analysis.error = "No person/pose detected in any frame of this video."
        analysis.frames_total = result.frames_total
        analysis.frames_with_pose = 0
        analysis.processed_video_path = f"/api/results/video/{os.path.basename(result.processed_video_path)}"
        video.processing_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=422,
            detail="No person could be detected in this video. Try a clearer, well-lit clip with the "
                   "full body visible.",
        )

    bio = biomechanics.run_full_biomechanics(result.landmarks_df, payload.activity)
    quality = movement_quality.compute_movement_quality(bio, payload.activity)
    observation_list = obs_module.build_observations(bio, quality, result.pose_detection_rate_pct)
    processed_video_filename = os.path.basename(result.processed_video_path)

    analysis.status = "completed"
    analysis.frames_total = result.frames_total
    analysis.frames_with_pose = result.frames_with_pose
    analysis.pose_detection_rate_pct = result.pose_detection_rate_pct
    analysis.movement_quality_json = json.dumps(quality)
    analysis.biomechanics_json = json.dumps(bio)
    analysis.observations_json = json.dumps(observation_list)
    analysis.processed_video_path = f"/api/results/video/{processed_video_filename}"
    video.processing_status = "completed"
    db.commit()
    db.refresh(analysis)

    # Rule-based risk prediction + recommendations (placeholder, not a trained ML model)
    risk = risk_prediction.compute_risk(bio, quality, athlete.injury_history)
    recs = recommendations_module.generate_recommendations(bio, risk)

    risk_record = RiskResultModel(
        athlete_id=athlete.id,
        analysis_id=analysis.id,
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        contributing_factors_json=json.dumps(risk["contributing_factors"]),
        recommendations_json=json.dumps(recs),
        is_placeholder_model="true",
    )
    db.add(risk_record)
    db.commit()

    return _analysis_to_schema(analysis)


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult)
def get_analysis(analysis_id: str, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    analysis = (
        db.query(MovementAnalysisModel)
        .join(AthleteModel, MovementAnalysisModel.athlete_id == AthleteModel.id)
        .filter(MovementAnalysisModel.id == analysis_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    return _analysis_to_schema(analysis)


@router.get("/athletes/{athlete_id}/analyses", response_model=list[AnalysisResult])
def list_athlete_analyses(athlete_id: str, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    athlete = _owned_athlete_or_404(db, athlete_id, current_user.id)
    analyses = (
        db.query(MovementAnalysisModel)
        .filter(MovementAnalysisModel.athlete_id == athlete.id)
        .order_by(MovementAnalysisModel.created_at.desc())
        .all()
    )
    return [_analysis_to_schema(a) for a in analyses]
