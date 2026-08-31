"""
train_injury_models.py

Trains and exports the Milestone 3 Machine Learning Models using the 3 datasets:
1. Kinematic Risk Classifier (XGBoost / Random Forest on sports_multimodal_data)
2. Specific Injury Category Classifier (Multi-Class Model on Project-Injury-Dataset)
3. Corrective Rehabilitation Prescriptor (Rehabilitation Program Model on Project-Injury-Dataset)
4. ACL Specific Risk Regressor (on collegiate_athlete_injury_dataset)

Saves all trained models and encoders into backend/app/models/ml/
"""
from __future__ import annotations

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, r2_score

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")
MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "app", "models", "ml")
os.makedirs(MODELS_DIR, exist_ok=True)


def train_kinematic_risk_model():
    """Model 1: Trains a Kinematic Binary Injury Risk Classifier on 5,430 samples."""
    csv_path = os.path.join(DATASETS_DIR, "sports_multimodal_data (2).csv")
    print("\n" + "="*70)
    print(f"[MODEL 1] Training Kinematic Injury Risk Classifier from:\n{csv_path}")
    print("="*70)
    
    df = pd.read_csv(csv_path)
    feature_cols = [
        "range_of_motion", "gait_symmetry", "body_orientation", "fatigue_index",
        "previous_injury_history", "repetition_count", "workload_intensity",
        "ground_reaction_force", "impact_force", "angular_velocity", "acceleration",
        "jump_height", "speed"
    ]
    X = df[feature_cols]
    y = df["injury_risk"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    probs = rf.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)
    roc_auc = roc_auc_score(y_test, probs)
    
    print(f" • Samples: {len(df):,} | Features: {len(feature_cols)}")
    print(f" • ROC-AUC Score: {roc_auc:.4f}")
    print(classification_report(y_test, preds))
    
    save_path = os.path.join(MODELS_DIR, "kinematic_risk_model.joblib")
    joblib.dump({"model": rf, "features": feature_cols, "roc_auc": roc_auc}, save_path)
    print(f" [✓] Saved Model 1: {save_path}")


def train_multi_injury_and_rehab_models():
    """Models 2 & 3: Trains Multi-Class Specific Injury Classifier & Rehab Program Prescriptor on 9,600 samples."""
    csv_path = os.path.join(DATASETS_DIR, "Project-Injury-Dataset (1).csv")
    print("\n" + "="*70)
    print(f"[MODELS 2 & 3] Training Specific Injury & Rehab Models from:\n{csv_path}")
    print("="*70)
    
    df = pd.read_csv(csv_path)
    df["Sport_Clean"] = df["Sport"].astype(str).str.lower().str.strip()
    df["Sport_Clean"] = df["Sport_Clean"].replace({"footaball": "football"})
    
    sport_encoder = LabelEncoder()
    df["Sport_Encoded"] = sport_encoder.fit_transform(df["Sport_Clean"])
    
    feature_cols = [
        "Age", "Height_cm", "Weight_kg", "Knee_Angle_deg",
        "Ankle_Flexion_deg", "Jump_Height_cm", "Speed_m_s", "Reaction_Time_ms",
        "Sport_Encoded"
    ]
    
    # 1. Injury Type Classifier
    injury_encoder = LabelEncoder()
    df["Injury_Type_Encoded"] = injury_encoder.fit_transform(df["Injury_Type"])
    
    X = df[feature_cols]
    y_injury = df["Injury_Type_Encoded"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_injury, test_size=0.2, random_state=42)
    
    injury_model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    injury_model.fit(X_train, y_train)
    acc = injury_model.score(X_test, y_test)
    print(f" • Injury Type Classifier Accuracy: {acc*100:.2f}% ({len(injury_encoder.classes_)} injury categories)")
    
    # 2. Rehabilitation Program Prescriptor
    rehab_encoder = LabelEncoder()
    df["Rehab_Encoded"] = rehab_encoder.fit_transform(df["Rehabilitation_Program"])
    y_rehab = df["Rehab_Encoded"]
    
    rehab_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rehab_model.fit(X, y_rehab)
    
    # 3. Rehabilitation Time Regressor (weeks)
    y_time = df["Rehabilitation_Time_weeks"]
    time_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    time_model.fit(X, y_time)
    
    save_path = os.path.join(MODELS_DIR, "injury_category_models.joblib")
    joblib.dump({
        "injury_model": injury_model,
        "injury_encoder": injury_encoder,
        "rehab_model": rehab_model,
        "rehab_encoder": rehab_encoder,
        "time_model": time_model,
        "sport_encoder": sport_encoder,
        "features": feature_cols,
    }, save_path)
    print(f" [✓] Saved Models 2 & 3: {save_path}")


def train_acl_regressor_model():
    """Model 4: Trains Continuous ACL Risk Regressor on collegiate athlete dataset."""
    csv_path = os.path.join(DATASETS_DIR, "collegiate_athlete_injury_dataset (1).csv")
    print("\n" + "="*70)
    print(f"[MODEL 4] Training ACL Continuous Risk Regressor from:\n{csv_path}")
    print("="*70)
    
    df = pd.read_csv(csv_path)
    feature_cols = [
        "Age", "Height_cm", "Weight_kg", "Training_Intensity",
        "Training_Hours_Per_Week", "Recovery_Days_Per_Week",
        "Match_Count_Per_Week", "Fatigue_Score"
    ]
    X = df[feature_cols]
    y = df["ACL_Risk_Score"]
    
    reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    reg.fit(X, y)
    r2 = r2_score(y, reg.predict(X))
    print(f" • ACL Risk Regressor R² Score: {r2:.4f}")
    
    save_path = os.path.join(MODELS_DIR, "acl_regressor_model.joblib")
    joblib.dump({"model": reg, "features": feature_cols}, save_path)
    print(f" [✓] Saved Model 4: {save_path}")


if __name__ == "__main__":
    train_kinematic_risk_model()
    train_multi_injury_and_rehab_models()
    train_acl_regressor_model()
    print("\n" + "="*70)
    print(" [✓] ALL MILESTONE 3 MACHINE LEARNING MODELS TRAINED & EXPORTED!")
    print("="*70 + "\n")
