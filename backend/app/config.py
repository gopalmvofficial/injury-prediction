"""
config.py

Centralized configuration, reading from environment variables where set,
falling back to sensible local-development defaults otherwise. This is what
makes the app deployable: a hosting platform (Render, Railway, etc.) sets
these env vars instead of you editing code per-environment.

Nothing here requires an env var to be set - running with none set behaves
exactly like the original local-only setup.
"""
from __future__ import annotations

import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Database -----------------------------------------------------------
# Local dev: SQLite file under backend/database/app.db (unchanged default).
# Production: set DATABASE_URL to a real database, e.g.
#   postgresql://user:password@host:5432/dbname
# SQLAlchemy is already DB-agnostic, so switching this on a real deployment
# needs no other code changes - just `pip install psycopg2-binary` and set
# this env var.
_default_sqlite_path = os.path.join(BACKEND_DIR, "database", "app.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_default_sqlite_path}")

# --- File storage ---------------------------------------------------------
# Local dev: relative folders under backend/. On a real deployment, point
# these at a persistent disk mount (e.g. Render's "Persistent Disk" feature)
# so uploaded videos and processed videos survive restarts/redeploys -
# without this, an ephemeral filesystem wipes them on every deploy.
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BACKEND_DIR, "uploads"))
RESULTS_DIR = os.environ.get("RESULTS_DIR", os.path.join(BACKEND_DIR, "results"))
REPORTS_DIR = os.environ.get("REPORTS_DIR", os.path.join(RESULTS_DIR, "reports"))

# --- CORS -------------------------------------------------------------
# Local dev defaults (always included so `python run_app.py` keeps working
# unchanged). For production, set ALLOWED_ORIGINS to a comma-separated list
# of your real deployed frontend URL(s), e.g.
#   ALLOWED_ORIGINS=https://myapp.vercel.app,https://www.myapp.com
_LOCAL_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
_extra_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
_extra_origins = [o.strip() for o in _extra_origins_env.split(",") if o.strip()]
ALLOWED_ORIGINS = list(dict.fromkeys(_LOCAL_DEV_ORIGINS + _extra_origins))  # de-duplicated, order-preserved

# --- Server -----------------------------------------------------------
# Most hosting platforms (Render, Railway, Heroku) inject $PORT and expect
# the app to bind to it. Local dev defaults to 8000, matching the rest of
# this project's docs.
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")
