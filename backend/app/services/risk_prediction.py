"""
risk_prediction.py

STRUCTURED, RULE-BASED PLACEHOLDER for injury risk scoring.

This is explicitly NOT a trained machine-learning model and NOT a clinically
validated injury-risk assessment. It combines the already-computed
biomechanics and movement-quality numbers (from biomechanics.py /
movement_quality.py) into a simple, transparent risk score, so the
Milestone 2 → Milestone 3 pipeline has a real, working, replaceable
interface. Every rule here is a documented heuristic; swapping this module
for a trained model later requires no changes to callers (same return
shape).

Rules (each contributes 0-100 points to weighted risk, higher = riskier):
1. Symmetry deficit (25%): lower knee/hip symmetry% -> higher risk.
2. Poor movement quality (25%): lower movement-quality score -> higher risk.
3. Excessive trunk lean (20%): trunk lean beyond a reference range -> higher risk.
4. Movement inconsistency (15%): low frame-to-frame consistency -> higher risk.
5. Reported injury history (15%): athlete has a non-empty injury_history field.

Risk score 0-100 (higher = higher risk), classified:
    0-33   LOW
    34-66  MEDIUM
    67-100 HIGH
"""
from __future__ import annotations

from typing import Optional


WEIGHTS = {
    "symmetry_deficit": 0.25,
    "movement_quality_deficit": 0.25,
    "trunk_lean_excess": 0.20,
    "inconsistency": 0.15,
    "injury_history": 0.15,
}

TRUNK_LEAN_REFERENCE_MAX = 25.0  # degrees, matches movement_quality.py's reference


def _symmetry_deficit_score(biomechanics: dict) -> Optional[float]:
    vals = [biomechanics.get("knee_symmetry_pct"), biomechanics.get("hip_symmetry_pct")]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    avg_symmetry = sum(vals) / len(vals)
    return round(max(0.0, 100.0 - avg_symmetry), 1)


def _movement_quality_deficit_score(movement_quality: dict) -> Optional[float]:
    score = movement_quality.get("score")
    if score is None:
        return None
    return round(max(0.0, 100.0 - score), 1)


def _trunk_lean_excess_score(biomechanics: dict) -> Optional[float]:
    trunk = biomechanics.get("trunk", {}) or {}
    lean = trunk.get("mean_lean_angle")
    if lean is None:
        return None
    if lean <= TRUNK_LEAN_REFERENCE_MAX:
        return round((lean / TRUNK_LEAN_REFERENCE_MAX) * 40.0, 1)  # mild contribution within normal range
    excess = lean - TRUNK_LEAN_REFERENCE_MAX
    return round(min(100.0, 40.0 + excess * 2), 1)


def _inconsistency_score(biomechanics: dict) -> Optional[float]:
    consistency = biomechanics.get("movement_consistency_pct")
    if consistency is None:
        return None
    return round(max(0.0, 100.0 - consistency), 1)


def _injury_history_score(injury_history: Optional[str]) -> float:
    if injury_history and injury_history.strip() and injury_history.strip().lower() not in ("none", "none reported", "n/a"):
        return 70.0
    return 0.0


def classify_risk(score: float) -> str:
    if score <= 33:
        return "LOW"
    if score <= 66:
        return "MEDIUM"
    return "HIGH"


def compute_risk(biomechanics: dict, movement_quality: dict, injury_history: Optional[str]) -> dict:
    """
    Returns:
        {
            "risk_score": float | None,
            "risk_level": "LOW"|"MEDIUM"|"HIGH" | None,
            "contributing_factors": [str, ...],
            "is_placeholder_model": True,
        }
    Weights re-normalize across whatever component data is actually available,
    same pattern as movement_quality.py - never pads with a fabricated value.
    """
    raw_scores = {
        "symmetry_deficit": _symmetry_deficit_score(biomechanics),
        "movement_quality_deficit": _movement_quality_deficit_score(movement_quality),
        "trunk_lean_excess": _trunk_lean_excess_score(biomechanics),
        "inconsistency": _inconsistency_score(biomechanics),
        "injury_history": _injury_history_score(injury_history),
    }

    available = {k: v for k, v in raw_scores.items() if v is not None}
    if not available:
        return {
            "risk_score": None,
            "risk_level": None,
            "contributing_factors": ["Insufficient data to compute a risk score."],
            "is_placeholder_model": True,
        }

    total_weight = sum(WEIGHTS[k] for k in available)
    weighted_sum = sum(available[k] * WEIGHTS[k] for k in available)
    risk_score = round(weighted_sum / total_weight, 1)
    risk_level = classify_risk(risk_score)

    factors = []
    if raw_scores["symmetry_deficit"] is not None and raw_scores["symmetry_deficit"] > 15:
        factors.append(f"Left/right symmetry deficit (~{raw_scores['symmetry_deficit']:.0f} pts of contribution)")
    if raw_scores["movement_quality_deficit"] is not None and raw_scores["movement_quality_deficit"] > 25:
        factors.append("Below-average overall movement quality score")
    if raw_scores["trunk_lean_excess"] is not None and raw_scores["trunk_lean_excess"] > 40:
        factors.append("Trunk lean beyond the reference range")
    if raw_scores["inconsistency"] is not None and raw_scores["inconsistency"] > 40:
        factors.append("Inconsistent movement across the recorded repetitions")
    if raw_scores["injury_history"] > 0:
        factors.append("Athlete has a reported injury history")
    if not factors:
        factors.append("No significant risk factors identified from the available data.")

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "contributing_factors": factors,
        "is_placeholder_model": True,
    }
