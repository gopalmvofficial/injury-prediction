from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AthleteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=5, le=100)
    weight: float = Field(gt=0, le=300)
    height: Optional[float] = Field(default=None, gt=0, le=250)
    sport: str = Field(min_length=2, max_length=80)
    injury_history: str = ''

class AthleteOut(AthleteCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class HealthOut(BaseModel):
    status: str
    service: str
    milestone: int
    athletes: int
    analyses: int
