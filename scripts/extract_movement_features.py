"""
extract_movement_features.py

Demonstration and validation tool for:
1. Video Ingestion & OpenCV frame decoding
2. MediaPipe 33-landmark 3D pose extraction
3. Biomechanical Feature Extraction (Joint angles, ROM, Symmetry %, Trunk lean, Consistency)
4. Annotated video export with skeletal pose overlays

Usage:
    backend/.venv/Scripts/python scripts/extract_movement_features.py [path_to_video.mp4]
"""
from __future__ import annotations

import os
import sys
import math
import numpy as np
import cv2
import pandas as pd

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.services.pose_estimation import PoseEstimator
from app.services.biomechanics import run_full_biomechanics
from app.services.movement_quality import compute_movement_quality
from app.services.video_processing import process_video


def run_feature_extraction(video_path: str, activity: str = "squat"):
    print("=" * 75)
    print("      SPORTS INJURY RISK DETECTION — MOVEMENT FEATURE EXTRACTION")
    print("=" * 75)
    print(f"\n[1. VIDEO INGESTION & VALIDATION]")
    print(f" • Input Video File: {video_path}")
    print(f" • Target Activity:  {activity.upper()}")
    
    if not os.path.exists(video_path):
        print(f"\n [!] Notice: Video file '{video_path}' not found.")
        print(f"     Pass a real athlete video clip, e.g.:")
        print(f"     python scripts/extract_movement_features.py path/to/squat_video.mp4")
        return

    results_dir = os.path.join(PROJECT_ROOT, "backend", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\n[2. OPENCV FRAME DECODING & MEDIAPIPE POSE TRACKING]")
    print(f" • Decoding video frames with OpenCV...")
    print(f" • Tracking 33 3D skeletal landmarks per frame with MediaPipe Pose...")
    
    processing_result = process_video(video_path, results_dir)
    
    print(f" • Total Frames Read:        {processing_result.frames_total}")
    print(f" • Frames With Pose Tracked: {processing_result.frames_with_pose}")
    print(f" • Pose Detection Rate:      {processing_result.pose_detection_rate_pct}%")
    print(f" • Annotated Output Video:   {processing_result.processed_video_path}")
    
    print(f"\n[3. KINEMATIC BIOMECHANICAL FEATURE EXTRACTION]")
    print(f" • Computing joint angles using vector 3D trigonometry...")
    biomechanics_data = run_full_biomechanics(processing_result.landmarks_df, activity)
    
    # Display Extracted Joint Features
    print(f"\n --- EXTRACTED MOVEMENT FEATURES ---")
    
    lk = biomechanics_data.get("left_knee", {})
    rk = biomechanics_data.get("right_knee", {})
    print(f" • Left Knee ROM:   Min: {lk.get('min_angle')}°, Max: {lk.get('max_angle')}°, ROM: {lk.get('range_of_motion')}°")
    print(f" • Right Knee ROM:  Min: {rk.get('min_angle')}°, Max: {rk.get('max_angle')}°, ROM: {rk.get('range_of_motion')}°")
    print(f" • Knee Symmetry:   {biomechanics_data.get('knee_symmetry_pct')}% (Bilateral balance)")
    
    lh = biomechanics_data.get("left_hip", {})
    rh = biomechanics_data.get("right_hip", {})
    print(f" • Left Hip ROM:    Min: {lh.get('min_angle')}°, Max: {lh.get('max_angle')}°, ROM: {lh.get('range_of_motion')}°")
    print(f" • Right Hip ROM:   Min: {rh.get('min_angle')}°, Max: {rh.get('max_angle')}°, ROM: {rh.get('range_of_motion')}°")
    print(f" • Hip Symmetry:    {biomechanics_data.get('hip_symmetry_pct')}%")
    
    trunk = biomechanics_data.get("trunk", {})
    print(f" • Mean Trunk Lean: {trunk.get('mean_lean_angle')}° (Spine relative to vertical axis)")
    print(f" • Max Trunk Lean:  {trunk.get('max_lean_angle')}°")
    print(f" • Consistency:     {biomechanics_data.get('movement_consistency_pct')}% across repetition cycles")
    
    print(f"\n[4. MOVEMENT QUALITY SCORE & CLASSIFICATION]")
    quality = compute_movement_quality(biomechanics_data, activity)
    print(f" • Movement Score:  {quality.get('score')}%")
    print(f" • Quality Class:   {quality.get('classification')}")
    print(f" • Sub-components:  {quality.get('components')}")
    
    print("\n" + "=" * 75)
    print(" [OK] MOVEMENT FEATURE EXTRACTION PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    video_arg = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    run_feature_extraction(video_arg)
