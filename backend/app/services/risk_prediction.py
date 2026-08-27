"""
risk_prediction.py

Weighted Risk Scoring Engine for Sports Injury Detection.
Implements the official Module 8 Weighted Scoring Model:

    Injury Risk Score =
        Biomechanical Deviations 35%
        Historical Injury Factors 20%
        Movement Asymmetry 20%
        Training Load Indicators 15%
        Fatigue Indicators 10%

Risk Categories:
    0 - 25%   LOW RISK
    26 - 50%  MODERATE RISK
    51 - 75%  HIGH RISK
    76 - 100% CRITICAL RISK
"""
from __future__ import annotations

from typing import Optional


WEIGHTS = {
    "biomechanical_deviations": 0.35,  # 35% - Joint alignment, ROM, trunk lean
    "movement_asymmetry": 0.20,        # 20% - Bilateral knee & hip asymmetry
    "historical_injury": 0.20,         # 20% - Athlete prior injury record
    "training_load": 0.15,             # 15% - Activity intensity & movement volume
    "fatigue_indicators": 0.10,        # 10% - Motion inconsistency across reps
}

TRUNK_LEAN_REFERENCE_MAX = 25.0  # degrees


def _biomechanical_deviations_score(biomechanics: dict, movement_quality: dict) -> Optional[float]:
    """Combines movement quality deficit (joint alignment/depth) and trunk lean excess (35% weight)."""
    scores = []
    mq_score = movement_quality.get("score")
    if mq_score is not None:
        scores.append(max(0.0, 100.0 - mq_score))

    trunk = biomechanics.get("trunk", {}) or {}
    lean = trunk.get("mean_lean_angle")
    if lean is not None:
        if lean <= TRUNK_LEAN_REFERENCE_MAX:
            scores.append((lean / TRUNK_LEAN_REFERENCE_MAX) * 35.0)
        else:
            excess = lean - TRUNK_LEAN_REFERENCE_MAX
            scores.append(min(100.0, 35.0 + excess * 2.5))

    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def _movement_asymmetry_score(biomechanics: dict) -> Optional[float]:
    """Calculates bilateral symmetry deficit across knees and hips (20% weight)."""
    vals = [biomechanics.get("knee_symmetry_pct"), biomechanics.get("hip_symmetry_pct")]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    avg_symmetry = sum(vals) / len(vals)
    return round(max(0.0, 100.0 - avg_symmetry), 1)


def _historical_injury_score(injury_history: Optional[str]) -> float:
    """Evaluates past injury record vulnerabilities (20% weight)."""
    if injury_history and injury_history.strip() and injury_history.strip().lower() not in ("none", "none reported", "n/a"):
        return 75.0
    return 0.0


def _training_load_score(biomechanics: dict, activity: str = "squat") -> float:
    """Estimates training load intensity based on exercise dynamic impact (15% weight)."""
    act = (activity or "squat").lower()
    if "jump" in act or "landing" in act or "cutting" in act:
        return 50.0  # High impact / deceleration load
    elif "running" in act or "sprint" in act:
        return 35.0  # Moderate repetitive impact
    return 20.0      # Controlled resistance load (squat)


def _fatigue_indicators_score(biomechanics: dict) -> Optional[float]:
    """Calculates movement inconsistency across repetition cycles as fatigue proxy (10% weight)."""
    consistency = biomechanics.get("movement_consistency_pct")
    if consistency is None:
        return None
    return round(max(0.0, 100.0 - consistency), 1)


def classify_risk(score: float) -> str:
    """Classifies final score into official 4 risk tiers."""
    if score <= 25.0:
        return "LOW"
    if score <= 50.0:
        return "MODERATE"
    if score <= 75.0:
        return "HIGH"
    return "CRITICAL"


def compute_risk(
    biomechanics: dict,
    movement_quality: dict,
    injury_history: Optional[str],
    activity: str = "squat",
) -> dict:
    """
    Computes overall risk score (0-100%) and category based on the official weighted scoring model.
    """
    factors = {
        "biomechanical_deviations": _biomechanical_deviations_score(biomechanics, movement_quality),
        "movement_asymmetry": _movement_asymmetry_score(biomechanics),
        "historical_injury": _historical_injury_score(injury_history),
        "training_load": _training_load_score(biomechanics, activity),
        "fatigue_indicators": _fatigue_indicators_score(biomechanics),
    }

    available_factors = {k: v for k, v in factors.items() if v is not None}
    if not available_factors:
        return {
            "risk_score": None,
            "risk_level": None,
            "contributing_factors": [],
            "breakdown": {},
        }

    total_weight = sum(WEIGHTS[k] for k in available_factors)
    weighted_score = sum(available_factors[k] * (WEIGHTS[k] / total_weight) for k in available_factors)
    final_score = round(max(0.0, min(100.0, weighted_score)), 1)

    contributing = []
    if factors["biomechanical_deviations"] is not None and factors["biomechanical_deviations"] > 30.0:
        contributing.append(f"Biomechanical alignment & posture deviation ({factors['biomechanical_deviations']} pts)")
    if factors["movement_asymmetry"] is not None and factors["movement_asymmetry"] > 15.0:
        contributing.append(f"Bilateral limb asymmetry deficit ({factors['movement_asymmetry']} pts)")
    if factors["historical_injury"] > 0:
        contributing.append("Documented prior injury history vulnerability")
    if factors["fatigue_indicators"] is not None and factors["fatigue_indicators"] > 20.0:
        contributing.append(f"Kinematic fatigue & repetition inconsistency ({factors['fatigue_indicators']} pts)")

    return {
        "risk_score": final_score,
        "risk_level": classify_risk(final_score),
        "contributing_factors": contributing,
        "breakdown": factors,
    }
