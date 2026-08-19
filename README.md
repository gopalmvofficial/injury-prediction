# Sports Injury Risk Detection — GitHub / Vercel / Render

Milestone 2 — Pose Estimation & Biomechanics.

## Architecture

- **Frontend:** React + Vite, deployed on Vercel.
- **Backend:** Python + FastAPI, deployed on Render.
- **Database:** SQLite for the supplied/local project; PostgreSQL can be configured for a persistent production database.
- **Video/biomechanics:** OpenCV + MediaPipe in the Python backend.
- **Cloud video option:** Cloudinary browser upload variables are supported by the frontend.
- **Docker:** `backend/Dockerfile` and `docker-compose.yml` are included for mentor/local container testing.

The frontend uses `VITE_API_BASE_URL`. In production it defaults to:
`https://injury-prediction-backend.onrender.com`

## Deploy

1. Push the entire repository to GitHub.
2. Vercel: import the repository. Keep the repository root as the project root. `vercel.json` builds `frontend/`.
3. Render: keep the existing Python web service pointed at `backend/` if you are already using the working Render service.
4. In Render, set:
   `ALLOWED_ORIGINS=https://injury-prediction-three.vercel.app`
5. If the Vercel URL changes, update `ALLOWED_ORIGINS` in Render.
6. Vercel does not need a backend service definition; it only hosts the React frontend.
7. Optional Cloudinary variables:
   `VITE_CLOUDINARY_CLOUD_NAME`
   `VITE_CLOUDINARY_UPLOAD_PRESET`

## Local frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses localhost:8000 automatically when opened on localhost.

## Local backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## Docker

```powershell
docker compose up --build
```

The backend will be available at `http://localhost:8000`.

## Authentication UI

The supplied frontend includes a professional login/register screen and Google/Microsoft/Apple-style provider buttons. Email registration/login in this package is a local browser demo using `localStorage`; the social buttons are UI placeholders until OAuth credentials and a real identity provider/backend auth flow are configured. Do not describe these buttons as live OAuth authentication until that provider integration is configured.

## Important

Do not commit `.env` files or secrets. Only commit `.env.example`.
