"""
routes/auth.py

POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

Token is passed back to the client and sent as `Authorization: Bearer <token>`
on subsequent requests. Sessions are persisted in the database (see
app/services/auth.py) so login survives a backend restart and works
correctly across multiple server workers on a real deployment.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.schemas.schemas import AuthResponse, UserLogin, UserOut, UserRegister
from app.services.auth import create_session, get_user_id_for_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    """Dependency other routes can use to require a logged-in user.
    Expects header: Authorization: Bearer <token>"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1].strip()
    user_id = get_user_id_for_token(db, token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in again.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    return user


@router.post("/register", response_model=AuthResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    password_hash, salt = hash_password(payload.password)
    user = User(
        name=payload.name,
        email=payload.email,
        role=payload.role or "coach",
        password_hash=password_hash,
        password_salt=salt,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_session(db, user.id)
    return AuthResponse(
        token=token,
        user=UserOut(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=getattr(user, "role", "coach") or "coach",
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash, user.password_salt):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_session(db, user.id)
    return AuthResponse(
        token=token,
        user=UserOut(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=getattr(user, "role", "coach") or "coach",
            created_at=user.created_at,
        ),
    )


@router.post("/oauth-login", response_model=AuthResponse)
def oauth_login(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Auto-create user from Google / Social OAuth profile
        display_name = payload.name.strip() if payload.name and payload.name.strip() else payload.email.split("@")[0].title()
        password_hash, salt = hash_password(f"oauth_{payload.provider}_{payload.email}_key")
        user = User(
            name=display_name,
            email=payload.email,
            role=payload.role or "coach",
            password_hash=password_hash,
            password_salt=salt,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_session(db, user.id)
    return AuthResponse(
        token=token,
        user=UserOut(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=getattr(user, "role", "coach") or "coach",
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=getattr(current_user, "role", "coach") or "coach",
        created_at=current_user.created_at,
    )
