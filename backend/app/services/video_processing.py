"""
video_processing.py

Owns the OpenCV + MediaPipe side of the pipeline:
- opens the uploaded video
- validates it can actually be read
- downsamples and processes frames rapidly (optimized for cloud containers)
- collects skeletal keypoint landmarks for biomechanics & ML prediction
- preserves direct browser streaming compatibility
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Optional

import cv2
import pandas as pd

from app.services.pose_estimation import PoseEstimator

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MAX_FILE_SIZE_BYTES = 300 * 1024 * 1024  # 300 MB


class VideoValidationError(Exception):
    """Raised when an uploaded video fails validation (format/size/corruption)."""


class VideoProcessingError(Exception):
    """Raised when the video can be read but processing otherwise fails."""


@dataclass
class ProcessingResult:
    landmarks_df: pd.DataFrame
    processed_video_path: str
    frames_total: int
    frames_with_pose: int
    fps: float
    width: int
    height: int

    @property
    def pose_detection_rate_pct(self) -> float:
        if self.frames_total == 0:
            return 0.0
        return round(100.0 * self.frames_with_pose / self.frames_total, 2)


def validate_video_file(filename: str, file_size: int) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise VideoValidationError(
            f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    if file_size <= 0:
        raise VideoValidationError("Uploaded file is empty.")
    if file_size > MAX_FILE_SIZE_BYTES:
        raise VideoValidationError(
            f"File too large ({file_size / (1024 * 1024):.1f} MB). Max allowed is "
            f"{MAX_FILE_SIZE_BYTES / (1024 * 1024):.0f} MB."
        )


def safe_stored_filename(original_filename: str) -> str:
    """Generates a random, filesystem-safe filename, preserving the extension only."""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def process_video(
    input_path: str,
    output_dir: str,
    max_frames: Optional[int] = 60,
) -> ProcessingResult:
    """
    Runs an accelerated OpenCV + Pose Estimation pipeline over a video file on disk.
    Optimized for fast 1-3 second execution on cloud servers.
    """
    if not os.path.exists(input_path):
        raise VideoProcessingError(f"Video file not found on disk: {input_path}")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise VideoProcessingError(
            "OpenCV could not open this video. The file may be corrupted or use an unsupported codec."
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    if width == 0 or height == 0:
        cap.release()
        raise VideoProcessingError("Video reports zero-sized frames; file appears corrupted.")

    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate intelligent stride to sample movement smoothly across the whole video
    stride = 1
    if max_frames and total_video_frames > max_frames:
        stride = max(1, total_video_frames // max_frames)

    all_rows = []
    frames_processed = 0
    frames_with_pose = 0
    raw_frame_idx = 0

    try:
        with PoseEstimator() as estimator:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Stride sampling for lightning-fast inference
                if raw_frame_idx % stride == 0:
                    # Scale down high-resolution frames (e.g. 1080p/4K) to 640px for 10x faster MediaPipe inference
                    if width > 640:
                        scale = 640.0 / width
                        proc_w = 640
                        proc_h = int(height * scale)
                        small_frame = cv2.resize(frame, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
                    else:
                        small_frame = frame

                    frame_landmarks, _ = estimator.process_frame(small_frame, frames_processed)

                    if frame_landmarks.pose_detected:
                        frames_with_pose += 1

                    all_rows.extend(frame_landmarks.to_rows())
                    frames_processed += 1

                    if max_frames is not None and frames_processed >= max_frames:
                        break

                raw_frame_idx += 1
    finally:
        cap.release()

    if frames_processed == 0:
        raise VideoProcessingError("Video contains zero readable frames.")

    landmarks_df = pd.DataFrame(all_rows)

    return ProcessingResult(
        landmarks_df=landmarks_df,
        processed_video_path=input_path,  # Use original uploaded stream path for native HTML5 video decoding
        frames_total=frames_processed,
        frames_with_pose=frames_with_pose,
        fps=fps,
        width=width,
        height=height,
    )
