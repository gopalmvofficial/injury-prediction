"""
recommendations.py

Generates preventive-training recommendations & exercise-specific corrective protocols
based on activity type, biomechanics, and risk classification.
"""
from __future__ import annotations

from typing import List


def generate_recommendations(biomechanics: dict, risk: dict, activity: str | None = None) -> List[str]:
    recs: List[str] = []

    act = (activity or "").lower().replace("_", " ")

    # 1. Activity-Specific Corrective Prescriptions
    if "swim" in act or "swimming" in act or "stroke" in act:
        recs.append("🏊 Scapular Y-T-W-L Raises & Serratus Wall Slides (3 sets x 10 reps): Stabilize shoulder girdle and prevent swimmer's shoulder impingement.")
        recs.append("🌊 Thoracic Spine Extension & Foam Roller Lat Release (2 sets x 60s): Maintain upper spinal extension and overhead stroke mobility.")
    elif "throw" in act or "pitch" in act or "tennis" in act or "badminton" in act or "overhead" in act:
        recs.append("🎾 Side-Lying Shoulder External Rotations (3 sets x 12 reps): Strengthen posterior rotator cuff (infraspinatus) for deceleration stability.")
        recs.append("🔄 Hip-Shoulder Kinetic Chain Rotations (3 sets x 8 reps): Train smooth force transfer from lower body to upper body.")
    elif "deadlift" in act or "hinge" in act or "powerlift" in act or "weightlift" in act:
        recs.append("🏋️ Banded Good Mornings & Single-Leg Romanian Deadlifts (3 sets x 10 reps): Strengthen posterior chain while maintaining neutral spine rigidity.")
        recs.append("🧘 Anti-Rotation Core Pallof Press & Iso-Holds (3 sets x 45s): Reinforce lumbar-pelvic stability under heavy axial load.")
    elif "cut" in act or "agility" in act or "sidestep" in act or "change of direction" in act:
        recs.append("⚡ Plant-and-Cut Deceleration Shuffles (3 sets x 6 reps): Train subtalar ankle stability and dynamic hip adductor control.")
        recs.append("🛡️ Copenhagen Adductor Groin Planks (3 sets x 8 reps/side): Strengthen inner thigh adductors to prevent groin strain.")
    elif "soccer" in act or "football" in act or "kick" in act:
        recs.append("⚽ Copenhagen Groin Planks & Nordic Hamstring Drops (3 sets x 8 reps): Prevent groin adductor strains and high-speed hamstring pulls.")
        recs.append("🦵 Dynamic Hip Flexor & Quad Mobilizations (2 sets x 10 reps/side): Optimize stride length and kicking mechanics.")
    elif "basketball" in act or "volleyball" in act or "dunk" in act or "rebound" in act:
        recs.append("🏀 Eccentric Calf & Achilles Tendon Heel Drops (3 sets x 10 reps): Absorb high vertical landing forces and protect Achilles/patellar tendons.")
        recs.append("🦘 Soft-Landing Box Drops with Valgus Knee Control (3 sets x 6 reps): Prevent inward knee collapse during jump landings.")
    elif "jump" in act or "landing" in act or "plyometric" in act:
        recs.append("🦘 Soft-Landing Box Drop Drills (3 sets x 6 reps): Focus on quiet ground contact, knees tracking over 2nd toe, and deep knee flexion (>80°).")
        recs.append("⚡ Deceleration & Lateral Brake Drills (3 sets x 5 reps): Train eccentric quadriceps control to absorb impact forces safely.")
    elif "single leg" in act or "unilateral" in act or "lunge" in act:
        recs.append("🦵 Single-Leg Romanian Deadlifts & Banded Clamshells (3 sets x 10 reps): Correct unilateral hip/knee stabilizer imbalance.")
        recs.append("🧘 Pelvic Iso-Hold Alignment Drills (3 sets x 30s): Prevent Trendelenburg pelvic drop during single-leg weight bearing.")
    elif "running" in act or "gait" in act or "sprint" in act or "jogging" in act:
        recs.append("🏃 Nordic Hamstring Eccentric Curls (3 sets x 6 reps): Build high-velocity eccentric force capacity for terminal swing deceleration.")
        recs.append("📏 Forward A-Skips & High Cadence Drills (3 sets x 20m): Optimize upright posture control and ground strike mechanics.")
    else:  # Squat / Overhead Squat / General
        recs.append("🏋️ Eccentric Spanish Squats (3 sets x 8 reps, 3s tempo): Build quad tendon load tolerance and reduce anterior knee shear.")
        recs.append("🦶 Ankle Dorsiflexion Wall Mobilization (2 sets x 12 reps/side): Increase ankle ROM to prevent early trunk leaning.")

    # 2. Biomechanical Asymmetry & Kinematic Adjustments
    knee_sym = biomechanics.get("knee_symmetry_pct") or biomechanics.get("symmetry_score")
    if knee_sym is not None and knee_sym < 90:
        recs.append(f"Consider unilateral single-leg loading (asymmetry measured at {knee_sym}%).")

    hip_sym = biomechanics.get("hip_symmetry_pct")
    if hip_sym is not None and hip_sym < 90:
        recs.append(f"Add targeted gluteus medius strengthening to address hip asymmetry ({hip_sym}%).")

    trunk = biomechanics.get("trunk", {}) or {}
    lean = trunk.get("mean_lean_angle")
    if lean is not None and lean > 20:
        recs.append(f"Incorporate anti-flexion core stability training to correct anterior trunk lean ({lean}°).")

    consistency = biomechanics.get("movement_consistency_pct")
    if consistency is not None and consistency < 75:
        recs.append("Focus on slow tempo movement consistency drills before progressing load or velocity.")

    # 3. Overall Risk Level Precautions
    risk_level = risk.get("risk_level")
    if risk_level in ("HIGH", "CRITICAL"):
        recs.append("Given elevated risk indicators, perform movement screening under certified sports physiotherapist supervision.")
    elif risk_level in ("MODERATE", "MEDIUM"):
        recs.append("Monitor training workload carefully and re-screen kinematics bi-weekly.")

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped
