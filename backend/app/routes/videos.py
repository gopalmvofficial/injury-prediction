"""
routes/videos.py

POST /api/videos/upload
POST /api/videos/upload-and-analyze
GET  /api/results/video/{filename}
GET  /api/uploads/{filename}
GET  /api/videos/{video_id}/stream
"""
from __future__ import annotations

import json
import os
import traceback

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
from app.schemas.schemas import ActivityType, AnalysisResult, VideoUploadResponse
from app.services import biomechanics, movement_quality, observations as obs_module
from app.services import recommendations as recommendations_module
from app.services import risk_prediction
from app.services.video_processing import (
    VideoProcessingError,
    VideoValidationError,
    process_video,
    safe_stored_filename,
    validate_video_file,
)
from app.config import RESULTS_DIR, UPLOAD_DIR

router = APIRouter(prefix="/api", tags=["videos"])


@router.post("/videos/upload-and-analyze", response_model=AnalysisResult)
async def upload_and_analyze_video(
    athlete_id: str = Form(...),
    activity: ActivityType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Direct, single-step upload, optical 3D pose extraction, and ML risk analysis."""
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    raw = await file.read()
    try:
        validate_video_file(file.filename or "upload", len(raw))
    except VideoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    stored_filename = safe_stored_filename(file.filename or "upload.mp4")
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(stored_path, "wb") as f:
        f.write(raw)

    video = VideoModel(
        athlete_id=athlete_id,
        activity=activity,
        original_filename=file.filename,
        stored_filename=stored_filename,
        stored_path=stored_path,
        processing_status="processing",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    analysis = MovementAnalysisModel(
        athlete_id=athlete.id,
        video_id=video.id,
        activity=activity,
        status="processing",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        result = process_video(stored_path, RESULTS_DIR, max_frames=30)
    except Exception as e:
        analysis.status = "failed"
        analysis.error = str(e)
        video.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=422, detail=f"Processing error: {e}")

    bio = biomechanics.run_full_biomechanics(result.landmarks_df, activity)
    quality = movement_quality.compute_movement_quality(bio, activity)
    obs = obs_module.build_observations(bio, quality, result.pose_detection_rate_pct)

    analysis.status = "completed"
    analysis.frames_total = result.frames_total
    analysis.frames_with_pose = result.frames_with_pose
    analysis.pose_detection_rate_pct = result.pose_detection_rate_pct
    analysis.movement_quality_json = json.dumps(quality)
    analysis.biomechanics_json = json.dumps(bio)
    analysis.observations_json = json.dumps(obs)
    analysis.processed_video_path = f"/api/uploads/{stored_filename}"
    video.processing_status = "completed"
    db.commit()
    db.refresh(analysis)

    athlete_info = {
        "age": athlete.age,
        "height_cm": athlete.height_cm,
        "weight_kg": athlete.weight_kg,
        "sport": athlete.sport,
        "training_load": athlete.training_load,
    }
    risk = risk_prediction.compute_risk(
        bio, quality, athlete.injury_history, activity=activity, athlete_data=athlete_info
    )
    recs = recommendations_module.generate_recommendations(bio, risk)

    if risk.get("recommended_rehabilitation") and risk["recommended_rehabilitation"] not in recs:
        recs.insert(0, f"AI-Prescribed Rehabilitation: {risk['recommended_rehabilitation']} (Est. Recovery: {risk.get('estimated_recovery_weeks', 4)} weeks)")

    risk_record = RiskResultModel(
        athlete_id=athlete.id,
        analysis_id=analysis.id,
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        contributing_factors_json=json.dumps(risk["contributing_factors"]),
        recommendations_json=json.dumps(recs),
        is_placeholder_model="false",
    )
    db.add(risk_record)
    db.commit()

    return _analysis_to_schema(analysis, db)


@router.post("/videos/upload", response_model=VideoUploadResponse)
async def upload_video(
    athlete_id: str = Form(...),
    activity: ActivityType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    raw = await file.read()
    try:
        validate_video_file(file.filename or "upload", len(raw))
    except VideoValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    stored_filename = safe_stored_filename(file.filename or "upload.mp4")
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(stored_path, "wb") as f:
        f.write(raw)

    video = VideoModel(
        athlete_id=athlete_id,
        activity=activity,
        original_filename=file.filename,
        stored_filename=stored_filename,
        stored_path=stored_path,
        processing_status="uploaded",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return VideoUploadResponse(
        video_id=video.id,
        athlete_id=athlete_id,
        activity=activity,
        filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        status="uploaded",
    )


@router.get("/results/video/{filename}")
def get_processed_video(filename: str):
    safe_name = os.path.basename(filename)
    path = os.path.join(RESULTS_DIR, safe_name)
    if not os.path.exists(path):
        up_path = os.path.join(UPLOAD_DIR, safe_name)
        if os.path.exists(up_path):
            return FileResponse(up_path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})
        raise HTTPException(status_code=404, detail="Processed video not found.")
    return FileResponse(path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})


@router.get("/uploads/{filename}")
def get_uploaded_video(filename: str):
    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Uploaded video file not found.")
    return FileResponse(path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})


@router.get("/videos/{video_id}/stream")
def stream_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if not video or not video.stored_path or not os.path.exists(video.stored_path):
        raise HTTPException(status_code=404, detail="Video file not found.")
    return FileResponse(video.stored_path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})


@router.get("/athletes/{athlete_id}/videos")
def list_athlete_videos(athlete_id: str, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")

    videos = (
        db.query(VideoModel)
        .filter(VideoModel.athlete_id == athlete_id)
        .order_by(VideoModel.upload_date.desc())
        .all()
    )
    return [
        {
            "video_id": v.id, "athlete_id": v.athlete_id, "activity": v.activity,
            "original_filename": v.original_filename, "upload_date": v.upload_date,
            "processing_status": v.processing_status,
        }
        for v in videos
    ]
