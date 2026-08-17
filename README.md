# Sports Injury Risk Detection and Prevention System

**Infosys Springboard Internship Project — Milestone 2: Pose Estimation, Biomechanical Analysis & Persistent Data**

## 1. Project Objective

A full-stack system where a user registers/logs in, creates athlete profiles, uploads movement
videos (squatting, running, jumping/landing), and gets real computer-vision-based biomechanical
analysis: joint angles, range of motion, left/right symmetry, trunk posture, movement consistency,
a transparent movement-quality score, a rule-based injury-risk indicator, and preventive
recommendations - all persisted in a local SQLite database so nothing is lost on restart.

## 2. Milestone 2 Scope

**Implemented:**
- User registration/login (simple local auth, session tokens)
- Athlete profile management (create/list/view/update/delete), persisted in SQLite
- Video upload, validation, and OpenCV + MediaPipe pose-estimation pipeline with skeleton overlay
- Real biomechanics math: joint angles, ROM, symmetry, trunk posture, movement consistency
- Rule-based Movement Quality Score (0-100)
- **Rule-based (non-ML) injury-risk indicator** with contributing factors and preventive
  recommendations - explicitly a structured placeholder, not a trained model or medical diagnosis
- Dashboard with real, database-derived statistics (never hardcoded)
- PDF report including biomechanics, movement quality, risk indicator, and recommendations

**Explicitly NOT implemented (reserved for a future milestone):**
- A trained machine-learning risk-prediction model (current risk score is rule-based, clearly labeled)
- Movement anomaly detection
- Advanced athlete intelligence dashboard beyond the summary stats described above

## 3. Technology Stack

**Frontend:** React 18, Vite, React Router, Tailwind CSS, Axios
**Backend:** Python, FastAPI, Uvicorn
**Database:** SQLite via SQLAlchemy (file-based, zero-setup, chosen per Milestone 2 guidance to
avoid introducing PostgreSQL/MongoDB/Firebase for a local internship demo)
**Computer vision:** OpenCV, MediaPipe Pose
**Data/analysis:** NumPy, Pandas
**Reporting:** ReportLab (PDF)
**Auth:** Stdlib `hashlib.pbkdf2_hmac` password hashing (no bcrypt/passlib, to avoid a native-build
dependency) + database-persisted bearer-token sessions (survive backend restarts)
after restarting the backend, same as most local dev auth setups)

## 4. Folder Structure

```
sports-injury-risk-detection-milestone-2/
├── frontend/
│   ├── src/
│   │   ├── components/     Navbar, StatCard, ClassificationBadge, JointAngleRow
│   │   ├── pages/           Login, Register, Dashboard, Athletes, AthleteProfile,
│   │   │                    VideoAnalysis, Results
│   │   ├── services/api.js  Centralized API client (adds auth token automatically)
│   │   ├── App.jsx, main.jsx, index.css
│   ├── package.json, vite.config.js, tailwind.config.js, .env.example
├── backend/
│   ├── app/
│   │   ├── main.py                CORS, router wiring, DB init on startup
│   │   ├── database.py            SQLAlchemy engine/session (SQLite)
│   │   ├── routes/
│   │   │   ├── auth.py            register / login / me
│   │   │   ├── athletes.py        CRUD, scoped to logged-in user
│   │   │   ├── videos.py          upload, processed-video streaming, per-athlete video list
│   │   │   ├── analysis.py        runs the full CV+biomechanics pipeline, persists results
│   │   │   ├── risk.py            risk result + risk history per athlete
│   │   │   ├── dashboard.py       real summary stats
│   │   │   └── reports.py         PDF generation/download
│   │   ├── services/
│   │   │   ├── video_processing.py, pose_estimation.py   OpenCV + MediaPipe
│   │   │   ├── biomechanics.py, movement_quality.py, observations.py
│   │   │   ├── risk_prediction.py    rule-based risk placeholder (documented formulas)
│   │   │   ├── recommendations.py    rule-based preventive recommendations
│   │   │   ├── auth.py                password hashing + session tokens
│   │   │   └── report.py              PDF generation
│   │   ├── models/db_models.py    SQLAlchemy ORM: User, Athlete, Video, MovementAnalysis, RiskResult
│   │   └── schemas/schemas.py     Pydantic request/response models
│   ├── database/                  app.db created here automatically (not committed)
│   ├── uploads/, results/         Runtime data (not committed)
│   └── requirements.txt
├── README.md
├── FINAL_TEST_REPORT.md
└── .gitignore
```

## 5. Prerequisites (Windows)

- **Python 3.10-3.12** (MediaPipe/opencv-python wheels aren't published for every Python version -
  avoid the very latest release; 3.12 is a safe choice)
- **Node.js 18+** and npm
- **Git** (optional)

## 6. Backend Setup (Windows)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs at **http://localhost:8000** by default. Interactive API docs: **/docs**.
The SQLite database file is created automatically at `backend/database/app.db` on first run.

## 7. Frontend Setup (Windows)

```powershell
cd frontend
npm install
npm run dev
```
Frontend runs at **http://localhost:5173** (or 5174 if 5173 is taken).

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to match wherever your backend actually
ends up running (see Troubleshooting if you need a non-default port).

## 8. Database Setup

No manual setup needed - `init_db()` runs automatically on backend startup and creates all tables
in `backend/database/app.db` if they don't already exist. To reset all data, stop the backend and
delete `backend/database/app.db`; it will be recreated empty on next startup.

## 9. How to Run — Full Sequence

**Option A — one command (after the one-time setup in sections 6-7 below):**
```powershell
python run_app.py
```
Run this from the project root (the folder containing `backend/` and `frontend/`). It starts both
the backend and frontend together, prefixes their logs with `[backend]`/`[frontend]`, and stops
both cleanly on Ctrl+C. It does **not** run `pip install` or `npm install` for you - do the
one-time setup in sections 6 and 7 first; after that, `python run_app.py` is all you need for
every subsequent run. If your machine needs a non-default backend port (see Troubleshooting),
open `run_app.py` and change `BACKEND_PORT` at the top.

*Known rough edge on Windows:* `uvicorn --reload` and `npm run dev` each spawn a child process
(a reloader process, and Node/Vite under npm's `.cmd` wrapper). Ctrl+C normally stops everything
cleanly, but if you ever find a port still occupied after stopping the script, use the same
`netstat -ano | findstr :<port>` + `taskkill /PID <pid> /F` steps from the README Troubleshooting
section to clear it.

**Option B — two terminals (original method, still works):**
1. Terminal 1: start the backend (section 6)
2. Terminal 2: start the frontend (section 7)
3. Open the frontend URL in your browser
4. Register a new account, log in
5. Create an athlete profile
6. Upload a video and analyze it
7. Review results, risk indicator, recommendations, and download the PDF report
8. Restart the backend and refresh the frontend - your athlete/video/analysis data should still be there (this is the persistence requirement)

## 10. API Documentation

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/register` | No | Register a new user |
| POST | `/api/auth/login` | No | Log in, returns a bearer token |
| GET | `/api/auth/me` | Yes | Current user info |
| POST | `/api/athletes` | Yes | Create an athlete profile |
| GET | `/api/athletes` | Yes | List the logged-in user's athletes |
| GET | `/api/athletes/{athlete_id}` | Yes | Get one athlete |
| PUT | `/api/athletes/{athlete_id}` | Yes | Update an athlete |
| DELETE | `/api/athletes/{athlete_id}` | Yes | Delete an athlete (cascades videos/analyses) |
| POST | `/api/videos/upload` | Yes | Upload a video (multipart) |
| GET | `/api/athletes/{athlete_id}/videos` | Yes | List an athlete's videos |
| GET | `/api/results/video/{filename}` | No | Stream the processed skeleton-overlay video |
| POST | `/api/videos/analyze` | Yes | Run the full pipeline on an uploaded video |
| GET | `/api/analysis/{analysis_id}` | Yes | Fetch a stored analysis result |
| GET | `/api/athletes/{athlete_id}/analyses` | Yes | List an athlete's analyses |
| GET | `/api/risk/{analysis_id}` | Yes | Risk result for one analysis |
| GET | `/api/athletes/{athlete_id}/risk-history` | Yes | Risk history for an athlete |
| GET | `/api/dashboard/summary` | Yes | Real dashboard statistics |
| GET | `/api/reports/{analysis_id}` | Yes | Generate/download the PDF report |

All endpoints marked "Auth required" expect an `Authorization: Bearer <token>` header - the
frontend's `services/api.js` attaches this automatically once you're logged in. Full interactive
schema at `/docs`.

## 11. Video / Activity Support

Same as before: MP4/MOV/AVI/MKV/WEBM, up to 300 MB, full body visible; squat / running / jumping-landing.

## 12. Biomechanics & Movement Quality Methodology

Unchanged from the original Milestone 2 pipeline - see docstrings in `biomechanics.py` and
`movement_quality.py` for exact formulas (joint-angle vector math, ROM, symmetry %, trunk lean,
movement consistency, weighted 0-100 quality score with automatic weight re-normalization when
data is missing).

## 13. Injury Risk Indicator Methodology (rule-based placeholder)

`app/services/risk_prediction.py` combines already-computed biomechanics/movement-quality numbers
into a 0-100 risk score using five weighted factors: symmetry deficit (25%), movement-quality
deficit (25%), excessive trunk lean (20%), movement inconsistency (15%), and reported injury
history (15%). Classified LOW (0-33) / MEDIUM (34-66) / HIGH (67-100).

**This is explicitly NOT a trained machine-learning model and NOT a clinically validated
injury-risk assessment.** It exists so the pipeline has a real, working, replaceable interface -
swapping in a trained model later requires no changes to any caller (same return shape). Every
rule is documented in the module docstring.

## 14. Preventive Recommendations

`app/services/recommendations.py` generates plain-language suggestions (not medical advice) from
the same biomechanics/risk data - e.g. unilateral strength work for asymmetry, core stability work
for excessive trunk lean, movement-consistency drills, and a suggestion to consult a sports-medicine
professional when risk is HIGH.

## 15. Authentication

Simple local registration/login, intentionally not over-engineered per the Milestone 2 requirement.
Passwords are hashed with PBKDF2-HMAC-SHA256 (260,000 iterations) + a random salt - never stored in
plaintext. Session tokens are opaque random strings stored in the database, so they persist across
backend restarts and work correctly with multiple server workers on a real deployment.

## 16. Troubleshooting

- **`WinError 10013` / `PermissionError` when starting uvicorn, even as Administrator, even on
  multiple different ports** - this can be caused by third-party security software (this was traced
  to **Quick Heal Internet Security's IDS/port-scan-detection** blocking Python's socket creation).
  If you hit this: open Quick Heal → Firewall settings → look for **IDS / Intrusion Detection /
  Port Scan Detection** and turn it off, or add an exception for your Python executable. If you use
  different antivirus/security software, look for an equivalent "port scan protection" or "IDS"
  feature.
- **`AttributeError: module 'mediapipe' has no attribute 'solutions'`** — reinstall mediapipe:
  `pip uninstall mediapipe -y` then `pip install "mediapipe>=0.10.9,<0.11"`.
- **CORS errors in the browser console** — the backend allows `localhost`/`127.0.0.1` on ports 5173
  and 5174. If your frontend lands on a different port, add it to the `allow_origins` list in
  `backend/app/main.py`.
- **Frontend says "Could not reach the backend at http://localhost:XXXX"** — check `frontend/.env`
  matches the port your backend actually printed on startup, then restart `npm run dev` (Vite only
  reads `.env` at startup).
- **PowerShell "running scripts is disabled"** — run
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal before activating
  the venv or running npm.
- **401 Unauthorized on API calls** — your session token expired (backend restarted) or you're not
  logged in; log in again.
- **"No person could be detected in this video"** — try a clearer, well-lit clip with the full body in frame.

## 17. Known Limitations

- Single-camera 2D pose estimation - not true 3D biomechanics.
- Synchronous video analysis (no background task queue) - long videos take longer to return.
- The injury-risk score is a transparent, documented **rule-based heuristic**, not a trained ML
  model and not clinically validated - see section 13.
- This system does not diagnose injuries and is not a substitute for a qualified medical or
  sports-science professional.
- See `FINAL_TEST_REPORT.md` for exactly what was verified in the development environment versus
  what needs checking on your machine.

## 18. Future Work

- Replace the rule-based risk model with a trained ML model (interface is already designed to be swappable)
- Movement anomaly detection
- Background task queue for long video processing
- Migrate from SQLite to PostgreSQL if/when multi-user concurrent load requires it

## 19. Deploying This Beyond Local Development

The app is built to run locally out of the box, but is also **deployment-ready** via environment
variables - no code changes needed for a real hosted deployment, only configuration. See
`backend/app/config.py` for the full list; the key ones:

| Env var | Purpose | Local default |
|---|---|---|
| `DATABASE_URL` | Where the database lives. SQLAlchemy is DB-agnostic - set this to a PostgreSQL URL for production (`pip install psycopg2-binary` too) and no other code changes are needed. | local SQLite file |
| `UPLOAD_DIR`, `RESULTS_DIR`, `REPORTS_DIR` | Where uploaded/processed videos and reports are stored. **On most hosting platforms the filesystem is ephemeral** - point these at a persistent disk mount, or migrate to object storage (S3-compatible), or everything gets wiped on every restart/redeploy. | local folders under `backend/` |
| `ALLOWED_ORIGINS` | Comma-separated list of your real deployed frontend URL(s) for CORS, e.g. `https://myapp.vercel.app`. Local dev origins (5173/5174) are always included automatically, in addition to whatever you set here. | localhost only |
| `PORT` | Which port the backend binds to - most platforms (Render, Railway, Heroku) inject this automatically. | `8000` |

**Session tokens are stored in the database** (not in memory), so they correctly survive restarts
and work across multiple server workers/instances - this was specifically fixed to make the app
deployment-safe, not just locally functional.

**Suggested deployment path (backend):**
1. Push this repo to GitHub.
2. Deploy `backend/` to a platform like Render or Railway. Use the included `Procfile`
   (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`) as the start command, or set it
   directly in the platform's dashboard.
3. Attach a persistent disk (or migrate to PostgreSQL + object storage) so data survives restarts.
4. Set `ALLOWED_ORIGINS` to your frontend's real URL once you know it.

**Suggested deployment path (frontend):**
1. Deploy `frontend/` to Vercel or Netlify (both have first-class Vite support).
2. Set the `VITE_API_BASE_URL` environment variable in that platform's dashboard to your deployed
   backend's URL.

**Still worth knowing before deploying for real:**
- Video analysis runs **synchronously** in the request - some platforms have a request timeout
  (e.g. Heroku's is 30 seconds) that a long video could exceed. A background task queue (Celery,
  RQ, or FastAPI `BackgroundTasks` + polling) would be the next step for production-grade video
  handling; not implemented here, per Milestone 2 scope.
- `run_app.py` is a **local-development convenience only** - a real deployment uses the platform's
  own process manager (via the `Procfile`) and a separately deployed frontend, not this script.
