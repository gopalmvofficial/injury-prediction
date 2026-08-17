"""
recommendations.py

Generates preventive-training recommendations (not medical advice) from the
already-computed biomechanics/risk data. Purely rule-based and transparent,
matching the same pattern as risk_prediction.py.
"""
from __future__ import annotations

from typing import List


def generate_recommendations(biomechanics: dict, risk: dict) -> List[str]:
    recs: List[str] = []

    knee_sym = biomechanics.get("knee_symmetry_pct")
    if knee_sym is not None and knee_sym < 90:
        recs.append("Consider unilateral strength work (single-leg exercises) to address left/right knee asymmetry.")

    hip_sym = biomechanics.get("hip_symmetry_pct")
    if hip_sym is not None and hip_sym < 90:
        recs.append("Add hip mobility and unilateral hip-strengthening work to reduce left/right hip asymmetry.")

    trunk = biomechanics.get("trunk", {}) or {}
    lean = trunk.get("mean_lean_angle")
    if lean is not None and lean > 25:
        recs.append("Incorporate core/trunk stability training to improve posture control during movement.")

    consistency = biomechanics.get("movement_consistency_pct")
    if consistency is not None and consistency < 70:
        recs.append("Focus on movement-pattern consistency drills (slow, controlled reps) before progressing load or speed.")

    risk_level = risk.get("risk_level")
    if risk_level == "HIGH":
        recs.append("Given the elevated risk indicators, consider a full movement screening with a qualified sports-medicine professional before intense training.")
    elif risk_level == "MEDIUM":
        recs.append("Monitor training load and reassess movement quality periodically.")

    recs.append("Maintain a consistent warm-up and mobility routine appropriate to the athlete's sport.")

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped
