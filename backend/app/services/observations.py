"""
observations.py

Builds plain-English observation strings strictly from already-computed
biomechanics/movement-quality numbers. No new inference happens here -
this only narrates numbers that were calculated elsewhere.
"""
from __future__ import annotations

from typing import List


def build_observations(biomechanics: dict, quality: dict, pose_detection_rate_pct: float) -> List[str]:
    obs: List[str] = []

    if pose_detection_rate_pct < 50:
        obs.append(
            f"Pose was detected in only {pose_detection_rate_pct:.0f}% of frames - "
            "results below are based on limited data and may be unreliable."
        )

    knee_sym = biomechanics.get("knee_symmetry_pct")
    if knee_sym is not None:
        if knee_sym >= 95:
            obs.append("Left/right knee movement is highly symmetric.")
        elif knee_sym >= 85:
            obs.append("Slight left/right knee asymmetry detected.")
        else:
            obs.append(f"Notable left/right knee asymmetry detected ({knee_sym}% symmetry).")

    hip_sym = biomechanics.get("hip_symmetry_pct")
    if hip_sym is not None:
        if hip_sym < 85:
            obs.append(f"Notable left/right hip asymmetry detected ({hip_sym}% symmetry).")

    trunk = biomechanics.get("trunk", {})
    lean = trunk.get("mean_lean_angle")
    if lean is not None:
        if lean > 25:
            obs.append(f"Average trunk lean of {lean}° is higher than the reference range.")
        else:
            obs.append(f"Trunk posture stayed within a typical range (avg lean {lean}°).")

    consistency = biomechanics.get("movement_consistency_pct")
    if consistency is not None:
        if consistency < 60:
            obs.append("Movement showed noticeable frame-to-frame inconsistency.")
        else:
            obs.append("Movement was reasonably consistent across the recorded repetitions.")

    score = quality.get("score")
    classification = quality.get("classification")
    if score is not None:
        obs.append(f"Overall movement quality score: {score}/100 ({classification}).")
    else:
        obs.append("Movement quality score could not be computed - insufficient landmark data.")

    if not obs:
        obs.append("No observations could be generated - insufficient pose data in this video.")

    return obs
