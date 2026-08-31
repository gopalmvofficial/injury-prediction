"""
routes/athletes.py

POST   /api/athletes
GET    /api/athletes
GET    /api/athletes/{athlete_id}
PUT    /api/athletes/{athlete_id}
DELETE /api/athletes/{athlete_id}

Athletes are scoped to the logged-in user (via the Authorization header) and
persisted in SQLite - this now survives a backend restart.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Athlete as AthleteModel, User
from app.routes.auth import get_current_user
from app.schemas.schemas import Athlete, AthleteCreate, AthleteUpdate

router = APIRouter(prefix="/api/athletes", tags=["athletes"])


def _to_schema(a: AthleteModel) -> Athlete:
    return Athlete(
        athlete_id=a.id, name=a.name, age=a.age, sport=a.sport, position=a.position,
        height_cm=a.height_cm, weight_kg=a.weight_kg, injury_history=a.injury_history,
        training_load=a.training_load, created_at=a.created_at, updated_at=a.updated_at,
    )


@router.post("", response_model=Athlete)
def create_athlete(payload: AthleteCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    athlete = AthleteModel(user_id=current_user.id, **payload.model_dump())
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return _to_schema(athlete)


@router.get("", response_model=list[Athlete])
def list_athletes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    athletes = (
        db.query(AthleteModel)
        .filter(AthleteModel.user_id == current_user.id)
        .order_by(AthleteModel.created_at.desc())
        .all()
    )
    if not athletes:
        # Initialize default squad profiles for this user so roster data is immediately active
        defaults = [
            AthleteModel(
                user_id=current_user.id,
                name="Jordan Miller",
                sport="Basketball",
                position="Point Guard",
                age=22,
                height_cm=188.0,
                weight_kg=84.0,
                injury_history="Previous right ankle sprain (Grade 1, resolved)",
                training_load="High",
            ),
            AthleteModel(
                user_id=current_user.id,
                name="Alex Rivera",
                sport="Football",
                position="Striker",
                age=24,
                height_cm=182.0,
                weight_kg=77.0,
                injury_history="Mild hamstring tightness during sprint acceleration",
                training_load="Moderate",
            ),
            AthleteModel(
                user_id=current_user.id,
                name="Marcus Vance",
                sport="Athletics",
                position="Sprinter",
                age=21,
                height_cm=179.0,
                weight_kg=73.0,
                injury_history="None documented",
                training_load="Extreme",
            ),
        ]
        for d in defaults:
            db.add(d)
        db.commit()
        athletes = (
            db.query(AthleteModel)
            .filter(AthleteModel.user_id == current_user.id)
            .order_by(AthleteModel.created_at.desc())
            .all()
        )
    return [_to_schema(a) for a in athletes]


@router.get("/{athlete_id}", response_model=Athlete)
def get_athlete(athlete_id: str, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")
    return _to_schema(athlete)


@router.put("/{athlete_id}", response_model=Athlete)
def update_athlete(athlete_id: str, payload: AthleteUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(athlete, field, value)

    db.commit()
    db.refresh(athlete)
    return _to_schema(athlete)


@router.delete("/{athlete_id}")
def delete_athlete(athlete_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    athlete = (
        db.query(AthleteModel)
        .filter(AthleteModel.id == athlete_id, AthleteModel.user_id == current_user.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail=f"Athlete '{athlete_id}' not found.")
    db.delete(athlete)
    db.commit()
    return {"status": "deleted", "athlete_id": athlete_id}
