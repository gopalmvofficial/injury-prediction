"""
auth.py

Simple, non-over-engineered local authentication.

Password hashing uses Python's stdlib hashlib.pbkdf2_hmac (no bcrypt/passlib)
specifically to avoid requiring a native-compiled dependency, given this
project's install history.

Session tokens are opaque random strings persisted in the database (see
db_models.Session) rather than an in-memory dict - this is what makes login
survive a backend restart and work correctly behind multiple server workers
on a real deployment, not just a single local dev process.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DBSession

from app.models.db_models import Session as SessionModel

PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> tuple[str, str]:
    """Returns (password_hash_hex, salt_hex)."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return digest.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return hmac.compare_digest(digest.hex(), password_hash)


def create_session(db: DBSession, user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    db.add(SessionModel(token=token, user_id=user_id))
    db.commit()
    return token


def get_user_id_for_token(db: DBSession, token: str) -> Optional[str]:
    session = db.query(SessionModel).filter(SessionModel.token == token).first()
    return session.user_id if session else None


def destroy_session(db: DBSession, token: str) -> None:
    db.query(SessionModel).filter(SessionModel.token == token).delete()
    db.commit()
