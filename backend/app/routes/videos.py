"""
routes/videos.py

POST /api/videos/upload
GET  /api/results/video/{filename}   (serves processed video for playback)
GET  /api/uploads/{filename}         (serves uploaded original video for playback)
GET  /api/videos/{video_id}/stream   (streams video by ID)
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Athlete as AthleteModel, User, Video as VideoModel
from app.routes.auth import get_current_user
from app.schemas.schemas import ActivityType, VideoUploadResponse
from app.services.video_processing import (
    VideoValidationError,
    safe_stored_filename,
    validate_video_file,
)
from app.config import UPLOAD_DIR, RESULTS_DIR

router = APIRouter(prefix="/api", tags=["videos"])


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
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found. Create the athlete profile first.")

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
        # Check upload dir as fallback
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
