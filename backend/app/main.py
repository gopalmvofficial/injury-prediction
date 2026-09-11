"""
main.py

FastAPI application entrypoint.

Local dev (unchanged): uvicorn app.main:app --reload
Production: uvicorn app.main:app --host 0.0.0.0 --port $PORT
(no --reload in production - that's a dev-only file-watcher feature)

CORS origins and the port are read from environment variables via
app/config.py - see that file's comments for what to set on a real
deployment (ALLOWED_ORIGINS, PORT, DATABASE_URL, UPLOAD_DIR, etc.).
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.database import init_db
from app.routes import analysis, athletes, auth, dashboard, reports, risk, videos

app = FastAPI(
    title="Sports Injury Risk Detection and Prevention System - API",
    description="Milestone 2: Pose Estimation & Biomechanical Analysis",
    version="0.4.0",
)

@app.middleware("http")
async def dynamic_cors_middleware(request, call_next):
    origin = request.headers.get("origin", "*")
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        res = Response(status_code=200)
        res.headers["Access-Control-Allow-Origin"] = origin
        res.headers["Access-Control-Allow-Credentials"] = "true"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
        res.headers["Vary"] = "Origin"
        return res

    res = await call_next(request)
    res.headers["Access-Control-Allow-Origin"] = origin
    res.headers["Access-Control-Allow-Credentials"] = "true"
    res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
    res.headers["Vary"] = "Origin"
    return res


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(athletes.router)
app.include_router(videos.router)
app.include_router(analysis.router)
app.include_router(risk.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "sports-injury-risk-detection-api",
        "milestone": 2,
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
