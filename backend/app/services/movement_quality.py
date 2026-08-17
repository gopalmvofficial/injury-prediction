"""
movement_quality.py

Transparent, rule-based Movement Quality Score (0-100), built entirely from
the biomechanics dict produced by biomechanics.run_full_biomechanics().
No randomness, no hardcoded per-athlete overrides.

Component weights (per spec section 13, adjustable but documented here):
    Joint alignment   : 30%
    Symmetry          : 25%
    Range of motion   : 20%
    Posture/trunk     : 15%
    Movement consist. : 10%

Each component is scored 0-100 independently, then combined by weighted
average. If a component's underlying data is unavailable for this video
(e.g. elbow never visible, or too few frames for consistency), that
component is EXCLUDED and the remaining weights are re-normalized so they
still sum to 100% - the score is never padded with a fabricated value.

Per-activity "ideal" ROM/angle targets below are reasonable, commonly-cited
biomechanical reference ranges used only to score movement quality -
they are not medical thresholds and do not diagnose injury risk.
"""
from __future__ import annotations

from typing import Optional

COMPONENT_WEIGHTS = {
    "joint_alignment": 0.30,
    "symmetry": 0.25,
    "range_of_motion": 0.20,
    "posture": 0.15,
    "consistency": 0.10,
}

# Reference target ROM (degrees) per activity/joint, used only for scoring the
# range_of_motion component. Source: generally cited biomechanics literature
# ranges for recreational movement screening (not a diagnostic threshold).
TARGET_ROM = {
    "squat": {"left_knee": 90, "right_knee": 90, "left_hip": 80, "right_hip": 80},
    "jumping_landing": {"left_knee": 70, "right_knee": 70, "left_hip": 60, "right_hip": 60},
    "running": {"left_hip": 40, "right_hip": 40, "left_knee": 60, "right_knee": 60},
}

# Reference "good" max knee flexion angle range (min_angle, i.e. deepest bend)
# used to score joint_alignment for squat/jump activities.
TARGET_MIN_KNEE_ANGLE = {
    "squat": (80, 130),
    "jumping_landing": (90, 150),
    "running": (110, 170),
}

MAX_ACCEPTABLE_TRUNK_LEAN = 25.0  # degrees, beyond which posture score drops sharply


def _score_from_target(value: float, target: float, tolerance: float = 0.5) -> float:
    """Scores how close `value` is to `target` as a percentage, decaying
    linearly and reaching 0 once the deviation exceeds `tolerance` * target."""
    if target <= 0:
        return 50.0
    deviation = abs(value - target) / target
    score = 100.0 * (1 - deviation / tolerance)
    return max(0.0, min(100.0, score))


def _score_joint_alignment(biomechanics: dict, activity: str) -> Optional[float]:
    target_range = TARGET_MIN_KNEE_ANGLE.get(activity)
    if not target_range:
        return None
    lo, hi = target_range
    scores = []
    for joint in ("left_knee", "right_knee"):
        joint_data = biomechanics.get(joint, {})
        min_angle = joint_data.get("min_angle")
        if min_angle is None:
            continue
        if lo <= min_angle <= hi:
            scores.append(100.0)
        else:
            midpoint = (lo + hi) / 2
            scores.append(_score_from_target(min_angle, midpoint, tolerance=0.6))
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def _score_symmetry(biomechanics: dict) -> Optional[float]:
    vals = [
        biomechanics.get("knee_symmetry_pct"),
        biomechanics.get("hip_symmetry_pct"),
    ]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 1)


def _score_rom(biomechanics: dict, activity: str) -> Optional[float]:
    targets = TARGET_ROM.get(activity)
    if not targets:
        return None
    scores = []
    for joint, target in targets.items():
        joint_data = biomechanics.get(joint, {})
        rom = joint_data.get("range_of_motion")
        if rom is None:
            continue
        scores.append(_score_from_target(rom, target, tolerance=0.7))
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def _score_posture(biomechanics: dict) -> Optional[float]:
    trunk = biomechanics.get("trunk", {})
    lean = trunk.get("mean_lean_angle")
    if lean is None:
        return None
    if lean <= MAX_ACCEPTABLE_TRUNK_LEAN:
        # Linear: 0 deg lean = 100, MAX_ACCEPTABLE_TRUNK_LEAN = 70
        return round(100.0 - (lean / MAX_ACCEPTABLE_TRUNK_LEAN) * 30.0, 1)
    # Beyond the acceptable range, score decays further toward 0
    excess = lean - MAX_ACCEPTABLE_TRUNK_LEAN
    return round(max(0.0, 70.0 - excess * 2), 1)


def _score_consistency(biomechanics: dict) -> Optional[float]:
    return biomechanics.get("movement_consistency_pct")


def classify(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Moderate"
    return "Needs Attention"


def compute_movement_quality(biomechanics: dict, activity: str) -> dict:
    """
    Returns {"score": float|None, "classification": str|None, "components": {...}}
    Weights are re-normalized across whatever components had usable data.
    """
    raw_scores = {
        "joint_alignment": _score_joint_alignment(biomechanics, activity),
        "symmetry": _score_symmetry(biomechanics),
        "range_of_motion": _score_rom(biomechanics, activity),
        "posture": _score_posture(biomechanics),
        "consistency": _score_consistency(biomechanics),
    }

    available = {k: v for k, v in raw_scores.items() if v is not None}
    if not available:
        return {"score": None, "classification": None, "components": raw_scores}

    total_weight = sum(COMPONENT_WEIGHTS[k] for k in available)
    weighted_sum = sum(available[k] * COMPONENT_WEIGHTS[k] for k in available)
    final_score = round(weighted_sum / total_weight, 1)

    return {
        "score": final_score,
        "classification": classify(final_score),
        "components": raw_scores,
    }
