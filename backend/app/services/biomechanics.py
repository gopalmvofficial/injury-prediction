"""
biomechanics.py

Actual mathematical biomechanical analysis computed from MediaPipe landmark
coordinates. No hardcoded or random values - every number here is derived
from the landmarks_df produced by video_processing.process_video().

Formulas used (documented per section 12 of the spec):

1. JOINT ANGLE (e.g. knee angle at Hip-Knee-Ankle):
   Given three 2D points A (proximal), B (vertex/joint), C (distal),
   the angle at B is:
       BA = A - B
       BC = C - B
       angle = degrees(acos( (BA . BC) / (|BA| * |BC|) ))
   This is standard vector-based joint angle computation, using image-plane
   (x, y) coordinates normalized by MediaPipe to [0, 1].

2. RANGE OF MOTION (ROM):
   ROM = max(angle over all frames) - min(angle over all frames)
   Computed per joint, across all frames where that joint's three landmarks
   were all detected with sufficient visibility.

3. LEFT/RIGHT SYMMETRY:
   For a paired joint (e.g. left knee ROM vs right knee ROM):
       symmetry_pct = 100 * (1 - |ROM_left - ROM_right| / max(ROM_left, ROM_right))
   100% = perfectly symmetric ROM between sides. Lower = greater asymmetry.
   If either side's ROM is unavailable, symmetry is reported as unavailable.

4. TRUNK / POSTURE (lean angle):
   Using the midpoint of the shoulders and the midpoint of the hips, the
   trunk lean angle is the angle between the shoulder-hip vector and true
   vertical (0,-1 in image coords), in degrees. 0 deg = perfectly upright.

5. MOVEMENT CONSISTENCY:
   Frame-to-frame variability of the primary joint angle (knee angle for
   squat/jump, hip angle for running) measured as:
       consistency_pct = 100 * (1 - stddev(angle_frame_deltas) / mean(angle))
   clipped to [0, 100]. Higher = smoother, more consistent movement between
   consecutive frames. This is a simple, transparent proxy - not a
   validated clinical metric.

None of these values constitute a medical diagnosis.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

Point2D = Tuple[float, float]

# (proximal_landmark, vertex_landmark, distal_landmark) triples that define each joint angle
JOINT_DEFINITIONS: Dict[str, Tuple[str, str, str]] = {
    "left_knee": ("left_hip", "left_knee", "left_ankle"),
    "right_knee": ("right_hip", "right_knee", "right_ankle"),
    "left_hip": ("left_shoulder", "left_hip", "left_knee"),
    "right_hip": ("right_shoulder", "right_hip", "right_knee"),
    "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
    "right_elbow": ("right_shoulder", "right_elbow", "right_wrist"),
}

PAIRED_JOINTS = [
    ("left_knee", "right_knee", "knee_symmetry_pct"),
    ("left_hip", "right_hip", "hip_symmetry_pct"),
]


def _angle_at_vertex(a: Point2D, b: Point2D, c: Point2D) -> Optional[float]:
    """Angle (degrees) at vertex b, formed by points a-b-c. None if degenerate."""
    ba = np.array([a[0] - b[0], a[1] - b[1]], dtype=float)
    bc = np.array([c[0] - b[0], c[1] - b[1]], dtype=float)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba < 1e-9 or norm_bc < 1e-9:
        return None
    cos_angle = float(np.dot(ba, bc) / (norm_ba * norm_bc))
    cos_angle = max(-1.0, min(1.0, cos_angle))  # clamp for floating-point safety
    return math.degrees(math.acos(cos_angle))


@dataclass
class JointAngleSeries:
    joint: str
    angles_by_frame: Dict[int, float] = field(default_factory=dict)

    @property
    def min_angle(self) -> Optional[float]:
        return round(min(self.angles_by_frame.values()), 1) if self.angles_by_frame else None

    @property
    def max_angle(self) -> Optional[float]:
        return round(max(self.angles_by_frame.values()), 1) if self.angles_by_frame else None

    @property
    def range_of_motion(self) -> Optional[float]:
        if not self.angles_by_frame:
            return None
        return round(self.max_angle - self.min_angle, 1)

    @property
    def mean_angle(self) -> Optional[float]:
        return round(float(np.mean(list(self.angles_by_frame.values()))), 1) if self.angles_by_frame else None


def _wide_landmarks(landmarks_df: pd.DataFrame) -> pd.DataFrame:
    """Pivots the long-format landmark rows into a wide table indexed by frame_number,
    with (landmark, x/y) columns, keeping only landmarks with a real x/y (not None)."""
    if landmarks_df.empty:
        return pd.DataFrame()
    df = landmarks_df.dropna(subset=["x", "y"]).copy()
    wide = df.pivot_table(index="frame_number", columns="landmark", values=["x", "y"])
    return wide


def compute_joint_angles(landmarks_df: pd.DataFrame) -> Dict[str, JointAngleSeries]:
    """Computes per-frame joint angles for every joint in JOINT_DEFINITIONS,
    then rolls each up into a JointAngleSeries (min/max/ROM/mean)."""
    wide = _wide_landmarks(landmarks_df)
    results: Dict[str, JointAngleSeries] = {j: JointAngleSeries(joint=j) for j in JOINT_DEFINITIONS}

    if wide.empty:
        return results

    for joint, (prox, vertex, distal) in JOINT_DEFINITIONS.items():
        try:
            xs = wide["x"]
            ys = wide["y"]
        except KeyError:
            continue
        needed = {prox, vertex, distal}
        if not needed.issubset(set(xs.columns)):
            continue

        for frame_number in wide.index:
            try:
                a = (xs.at[frame_number, prox], ys.at[frame_number, prox])
                b = (xs.at[frame_number, vertex], ys.at[frame_number, vertex])
                c = (xs.at[frame_number, distal], ys.at[frame_number, distal])
            except KeyError:
                continue
            if any(pd.isna(v) for v in (*a, *b, *c)):
                continue
            angle = _angle_at_vertex(a, b, c)
            if angle is not None:
                results[joint].angles_by_frame[int(frame_number)] = angle

    return results


def compute_symmetry(angle_series: Dict[str, JointAngleSeries]) -> Dict[str, Optional[float]]:
    """Left/right ROM symmetry percentage for each paired joint. See module docstring for formula."""
    out: Dict[str, Optional[float]] = {}
    for left, right, key in PAIRED_JOINTS:
        rom_l = angle_series[left].range_of_motion
        rom_r = angle_series[right].range_of_motion
        if rom_l is None or rom_r is None:
            out[key] = None
            continue
        max_rom = max(rom_l, rom_r)
        if max_rom < 1e-6:
            out[key] = 100.0  # both sides essentially static -> trivially symmetric
            continue
        symmetry = 100.0 * (1 - abs(rom_l - rom_r) / max_rom)
        out[key] = round(max(0.0, min(100.0, symmetry)), 1)
    return out


def compute_trunk_metrics(landmarks_df: pd.DataFrame) -> Dict[str, Optional[float]]:
    """Trunk lean angle per frame relative to vertical, using shoulder & hip midpoints."""
    wide = _wide_landmarks(landmarks_df)
    if wide.empty:
        return {"mean_lean_angle": None, "max_lean_angle": None}

    try:
        xs, ys = wide["x"], wide["y"]
    except KeyError:
        return {"mean_lean_angle": None, "max_lean_angle": None}

    required = {"left_shoulder", "right_shoulder", "left_hip", "right_hip"}
    if not required.issubset(set(xs.columns)):
        return {"mean_lean_angle": None, "max_lean_angle": None}

    lean_angles: List[float] = []
    for frame_number in wide.index:
        try:
            ls = (xs.at[frame_number, "left_shoulder"], ys.at[frame_number, "left_shoulder"])
            rs = (xs.at[frame_number, "right_shoulder"], ys.at[frame_number, "right_shoulder"])
            lh = (xs.at[frame_number, "left_hip"], ys.at[frame_number, "left_hip"])
            rh = (xs.at[frame_number, "right_hip"], ys.at[frame_number, "right_hip"])
        except KeyError:
            continue
        if any(pd.isna(v) for v in (*ls, *rs, *lh, *rh)):
            continue

        shoulder_mid = ((ls[0] + rs[0]) / 2, (ls[1] + rs[1]) / 2)
        hip_mid = ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2)

        # Vector from hip midpoint to shoulder midpoint (the "spine" vector).
        # In image coordinates, y increases downward, so "up" is (0, -1).
        spine = np.array([shoulder_mid[0] - hip_mid[0], shoulder_mid[1] - hip_mid[1]])
        vertical = np.array([0.0, -1.0])
        norm_spine = np.linalg.norm(spine)
        if norm_spine < 1e-9:
            continue
        cos_angle = float(np.dot(spine, vertical) / norm_spine)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        lean_angles.append(math.degrees(math.acos(cos_angle)))

    if not lean_angles:
        return {"mean_lean_angle": None, "max_lean_angle": None}

    return {
        "mean_lean_angle": round(float(np.mean(lean_angles)), 1),
        "max_lean_angle": round(float(np.max(lean_angles)), 1),
    }


def compute_movement_consistency(angle_series: Dict[str, JointAngleSeries], primary_joint: str) -> Optional[float]:
    """
    Frame-to-frame consistency of the primary joint's angle trajectory.
    See module docstring formula #5. Returns None if fewer than 3 frames
    of data are available for that joint.
    """
    series = angle_series.get(primary_joint)
    if not series or len(series.angles_by_frame) < 3:
        return None

    frames_sorted = sorted(series.angles_by_frame.items())
    angles = [a for _, a in frames_sorted]
    deltas = np.diff(angles)
    mean_angle = float(np.mean(angles))
    if mean_angle < 1e-6:
        return None

    stddev_delta = float(np.std(deltas))
    consistency = 100.0 * (1 - stddev_delta / mean_angle)
    return round(max(0.0, min(100.0, consistency)), 1)


PRIMARY_JOINT_BY_ACTIVITY = {
    "squat": "left_knee",
    "squatting": "left_knee",
    "running": "left_hip",
    "sprinting": "left_hip",
    "jumping": "left_knee",
    "landing": "left_knee",
    "jumping_landing": "left_knee",
    "throwing": "right_elbow",
    "cutting": "left_knee",
    "cutting_movements": "left_knee",
    "sport_specific_drills": "left_knee",
    "drills": "left_knee",
}


def run_full_biomechanics(landmarks_df: pd.DataFrame, activity: str) -> dict:
    """Top-level entry point: runs every biomechanics calculation and returns
    a single dict shaped to match the AnalysisResult.biomechanics schema."""
    angle_series = compute_joint_angles(landmarks_df)
    symmetry = compute_symmetry(angle_series)
    trunk = compute_trunk_metrics(landmarks_df)
    primary_joint = PRIMARY_JOINT_BY_ACTIVITY.get(activity, "left_knee")
    consistency = compute_movement_consistency(angle_series, primary_joint)

    def joint_dict(name: str) -> dict:
        s = angle_series[name]
        available = s.range_of_motion is not None
        return {
            "min_angle": s.min_angle,
            "max_angle": s.max_angle,
            "range_of_motion": s.range_of_motion,
            "available": available,
        }

    return {
        "left_knee": joint_dict("left_knee"),
        "right_knee": joint_dict("right_knee"),
        "left_hip": joint_dict("left_hip"),
        "right_hip": joint_dict("right_hip"),
        "left_elbow": joint_dict("left_elbow"),
        "right_elbow": joint_dict("right_elbow"),
        "knee_symmetry_pct": symmetry.get("knee_symmetry_pct"),
        "hip_symmetry_pct": symmetry.get("hip_symmetry_pct"),
        "trunk": {
            "mean_lean_angle": trunk.get("mean_lean_angle"),
            "max_lean_angle": trunk.get("max_lean_angle"),
            "available": trunk.get("mean_lean_angle") is not None,
        },
        "movement_consistency_pct": consistency,
    }
