"""
video_processing.py

Owns the OpenCV side of the pipeline:
- opens the uploaded video
- validates it can actually be read
- iterates frames, running MediaPipe pose estimation on each
- draws the skeleton overlay onto a new output video
- collects every frame's landmarks into a pandas DataFrame for the
  biomechanics module to consume

Real processing only. If a video can't be opened or no person is ever
detected, that is reported explicitly rather than papered over.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
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
    max_frames: Optional[int] = None,
) -> ProcessingResult:
    """
    Runs the full OpenCV + MediaPipe pipeline over a video file on disk.

    Raises VideoProcessingError if the file cannot be opened by OpenCV or
    contains zero readable frames.
    """
    if not os.path.exists(input_path):
        raise VideoProcessingError(f"Video file not found on disk: {input_path}")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise VideoProcessingError(
            "OpenCV could not open this video. The file may be corrupted or use an "
            "unsupported codec."
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width == 0 or height == 0:
        cap.release()
        raise VideoProcessingError("Video reports zero-sized frames; file appears corrupted.")

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"processed_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    # mp4v is broadly available cross-platform (Windows/Linux) without extra codec installs.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    all_rows = []
    frame_number = 0
    frames_with_pose = 0

    try:
        try:
            pose_estimator_cm = PoseEstimator()
        except RuntimeError as e:
            raise VideoProcessingError(str(e))
        with pose_estimator_cm as estimator:
            mp_drawing = mp.solutions.drawing_utils
            mp_pose_connections = mp.solutions.pose.POSE_CONNECTIONS
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if max_frames is not None and frame_number >= max_frames:
                    break

                frame_landmarks, mp_results = estimator.process_frame(frame, frame_number)

                if frame_landmarks.pose_detected:
                    frames_with_pose += 1
                    mp_drawing.draw_landmarks(
                        frame,
                        mp_results.pose_landmarks,
                        mp_pose_connections,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(
                            color=(0, 255, 0), thickness=2, circle_radius=3
                        ),
                        connection_drawing_spec=mp_drawing.DrawingSpec(
                            color=(255, 140, 0), thickness=2
                        ),
                    )
                else:
                    cv2.putText(
                        frame, "No pose detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2,
                    )

                all_rows.extend(frame_landmarks.to_rows())
                writer.write(frame)
                frame_number += 1
    finally:
        cap.release()
        writer.release()

    if frame_number == 0:
        raise VideoProcessingError("Video contains zero readable frames.")

    landmarks_df = pd.DataFrame(all_rows)

    return ProcessingResult(
        landmarks_df=landmarks_df,
        processed_video_path=output_path,
        frames_total=frame_number,
        frames_with_pose=frames_with_pose,
        fps=fps,
        width=width,
        height=height,
    )
