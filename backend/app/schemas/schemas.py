"""
Pydantic schemas (request/response models) for the Sports Injury Risk
Detection and Prevention System - Milestone 2.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, EmailStr


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: str
    name: str
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: UserOut


# ---------------------------------------------------------------------------
# Athletes
# ---------------------------------------------------------------------------

class AthleteCreate(BaseModel):
    name: str
    age: int = Field(ge=5, le=80)
    sport: str
    position: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, gt=0)
    weight_kg: Optional[float] = Field(default=None, gt=0)
    injury_history: Optional[str] = None
    training_load: Optional[str] = None


class AthleteUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=5, le=80)
    sport: Optional[str] = None
    position: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, gt=0)
    weight_kg: Optional[float] = Field(default=None, gt=0)
    injury_history: Optional[str] = None
    training_load: Optional[str] = None


class Athlete(AthleteCreate):
    athlete_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Videos / Analysis
# ---------------------------------------------------------------------------

ActivityType = Literal["squat", "running", "jumping_landing"]
AnalysisStatus = Literal["pending", "processing", "completed", "failed"]


class VideoUploadResponse(BaseModel):
    video_id: str
    athlete_id: str
    activity: ActivityType
    filename: str
    stored_filename: str
    status: str = "uploaded"


class AnalyzeRequest(BaseModel):
    video_id: str
    athlete_id: str
    activity: ActivityType


class JointROM(BaseModel):
    min_angle: Optional[float] = None
    max_angle: Optional[float] = None
    range_of_motion: Optional[float] = None
    available: bool = True


class TrunkMetrics(BaseModel):
    mean_lean_angle: Optional[float] = None
    max_lean_angle: Optional[float] = None
    available: bool = True


class MovementQuality(BaseModel):
    score: Optional[float] = None
    classification: Optional[str] = None
    components: dict = Field(default_factory=dict)


class Biomechanics(BaseModel):
    left_knee: JointROM = Field(default_factory=JointROM)
    right_knee: JointROM = Field(default_factory=JointROM)
    left_hip: JointROM = Field(default_factory=JointROM)
    right_hip: JointROM = Field(default_factory=JointROM)
    left_elbow: JointROM = Field(default_factory=JointROM)
    right_elbow: JointROM = Field(default_factory=JointROM)
    knee_symmetry_pct: Optional[float] = None
    hip_symmetry_pct: Optional[float] = None
    trunk: TrunkMetrics = Field(default_factory=TrunkMetrics)
    movement_consistency_pct: Optional[float] = None


class AnalysisResult(BaseModel):
    analysis_id: str
    athlete_id: str
    video_id: str
    activity: ActivityType
    status: AnalysisStatus
    created_at: datetime
    frames_total: Optional[int] = None
    frames_with_pose: Optional[int] = None
    pose_detection_rate_pct: Optional[float] = None
    movement_quality: Optional[MovementQuality] = None
    biomechanics: Optional[Biomechanics] = None
    observations: List[str] = Field(default_factory=list)
    processed_video_path: Optional[str] = None
    landmarks_file_path: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Risk / Recommendations
# ---------------------------------------------------------------------------

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class RiskResult(BaseModel):
    risk_id: str
    athlete_id: str
    analysis_id: str
    risk_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    contributing_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    is_placeholder_model: bool = True
    created_at: datetime


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_athletes: int
    total_videos: int
    total_analyses: int
    high_risk_athletes: int
    risk_distribution: dict = Field(default_factory=dict)
    recent_athletes: List[Athlete] = Field(default_factory=list)
    recent_analyses: List[AnalysisResult] = Field(default_factory=list)
