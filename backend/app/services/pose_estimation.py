"""
pose_estimation.py

Wraps MediaPipe Pose to run pose detection across every frame of a video,
returning a structured, frame-by-frame landmark table suitable for
mathematical / biomechanical analysis (not just visualization).

No random or fabricated values: every landmark below either comes directly
from MediaPipe's detector output for that frame, or is explicitly marked
missing (None / visibility 0) when detection fails on that frame.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import mediapipe as mp

MIN_VISIBILITY = 0.5  # below this, MediaPipe's own estimate is unreliable

_MEDIAPIPE_SOLUTIONS_HELP = (
    "This installed 'mediapipe' package does not expose the classic "
    "'mediapipe.solutions.pose' API that this app uses (some builds only ship the "
    "newer Tasks API). Fix: in backend/, run "
    "'pip uninstall mediapipe -y' then 'pip install \"mediapipe>=0.10.9,<0.11\"' "
    "(the standard PyPI wheel for Windows/macOS/Linux includes mediapipe.solutions). "
    "See README Troubleshooting section."
)


def _get_mp_pose_module():
    """Lazily resolves mediapipe.solutions.pose, raising a clear, actionable
    error instead of a bare AttributeError if this mediapipe build lacks it."""
    solutions = getattr(mp, "solutions", None)
    pose_module = getattr(solutions, "pose", None) if solutions else None
    if pose_module is None:
        raise RuntimeError(_MEDIAPIPE_SOLUTIONS_HELP)
    return pose_module


def _get_tracked_landmarks() -> Dict[str, int]:
    mp_pose = _get_mp_pose_module()
    return {
        "nose": mp_pose.PoseLandmark.NOSE.value,
        "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW.value,
        "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST.value,
        "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST.value,
        "left_hip": mp_pose.PoseLandmark.LEFT_HIP.value,
        "right_hip": mp_pose.PoseLandmark.RIGHT_HIP.value,
        "left_knee": mp_pose.PoseLandmark.LEFT_KNEE.value,
        "right_knee": mp_pose.PoseLandmark.RIGHT_KNEE.value,
        "left_ankle": mp_pose.PoseLandmark.LEFT_ANKLE.value,
        "right_ankle": mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    }


@dataclass
class LandmarkPoint:
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class FrameLandmarks:
    frame_number: int
    pose_detected: bool
    landmarks: Dict[str, Optional[LandmarkPoint]] = field(default_factory=dict)

    def to_rows(self) -> List[dict]:
        """Flatten into (frame_number, landmark_name, x, y, z, visibility) rows."""
        rows = []
        for name, pt in self.landmarks.items():
            rows.append({
                "frame_number": self.frame_number,
                "landmark": name,
                "x": pt.x if pt else None,
                "y": pt.y if pt else None,
                "z": pt.z if pt else None,
                "visibility": pt.visibility if pt else 0.0,
            })
        return rows


class PoseEstimator:
    """Thin, reusable wrapper around mediapipe.solutions.pose.Pose."""

    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        mp_pose = _get_mp_pose_module()
        self._tracked_landmarks = _get_tracked_landmarks()
        self._pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process_frame(self, frame_bgr, frame_number: int) -> tuple[FrameLandmarks, object]:
        """
        Runs MediaPipe on a single BGR frame (as read by OpenCV).
        Returns (FrameLandmarks, mediapipe_results) - the raw results object
        is returned too so the caller can draw the skeleton without re-running
        detection.
        """
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._pose.process(rgb)

        if not results.pose_landmarks:
            return FrameLandmarks(frame_number=frame_number, pose_detected=False), results

        fl = FrameLandmarks(frame_number=frame_number, pose_detected=True)
        lm_list = results.pose_landmarks.landmark
        for name, idx in self._tracked_landmarks.items():
            lm = lm_list[idx]
            if lm.visibility is not None and lm.visibility < MIN_VISIBILITY:
                fl.landmarks[name] = None
            else:
                fl.landmarks[name] = LandmarkPoint(x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility)
        return fl, results

    def close(self):
        self._pose.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
