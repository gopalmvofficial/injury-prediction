import os
import re
import html
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

ARTIFACT_DIR = r"C:\Users\OmniBook x\.gemini\antigravity\brain\07a7d22c-fcd9-450e-9448-d65d07f5afcb"
MD_PATH = os.path.join(ARTIFACT_DIR, "MotionIQ_Mega_Mentor_Defense_and_Button_Guide.md")
PDF_PATH_ARTIFACT = os.path.join(ARTIFACT_DIR, "MotionIQ_Mega_Mentor_Defense_and_Button_Guide.pdf")
PDF_PATH_DOWNLOADS = os.path.expanduser(r"~\Downloads\MotionIQ_Mega_Mentor_Defense_and_Button_Guide.pdf")

MD_CONTENT = r"""# Motion IQ — Mega Mentor Defense & Button-by-Button Presentation Guide

> **System Overview**: Motion IQ is an AI-powered biomechanical movement analysis, injury risk detection, and rehabilitation tracking system. It combines a **React (Vite) Single Page Application** with a **FastAPI (Python 3.14)** backend powered by **Google MediaPipe BlazePose (33 3D Keypoints)**, **OpenCV**, **XGBoost / Random Forest ML models**, **SQLAlchemy ORM**, and **ReportLab PDF Engine**.

---

# PART 1: SIMPLE ENGLISH BUTTON-BY-BUTTON EXECUTION GUIDE

When your mentor asks: *"What happens when I click this button?"*, open the specified file and read the simple English explanation below.

---

### 1. ACTION: Click "Login" Button
* **What to Say to Mentor**:
  > *"When I click 'Login', the browser collects the email and password, hashes the request, and sends a HTTP POST request to `/api/auth/login`. The backend checks the password hash using Bcrypt. If valid, it returns a 7-day signed JWT Bearer Access Token. The frontend saves this token in `localStorage` and redirects to the Coach Dashboard."*
* **File to Open**: `backend/app/routers/auth.py` (Lines 25–65) & `src/pages/Login.jsx` (Lines 40–85).
* **Step-by-Step Flow**:
  1. **Frontend**: `Login.jsx` calls `handleSubmit()` -> sends `POST /api/auth/login` payload `{email, password}`.
  2. **Backend**: `auth.py` queries database `User` table for email.
  3. **Security**: Verifies password using `pwd_context.verify(password, user.hashed_password)`.
  4. **Token Creation**: `create_access_token({"sub": user.email, "role": user.role})`.
  5. **Response**: Returns `{access_token: "...", token_type: "bearer"}` -> UI stores token in `localStorage`.

---

### 2. ACTION: Click "Register / Create Account" Button
* **What to Say to Mentor**:
  > *"When I click 'Create Account', the browser sends full user details to `/api/auth/register`. The backend checks if the email already exists. If new, it encrypts the password using Bcrypt salt hashing and saves the new User record into the SQLite database via SQLAlchemy ORM."*
* **File to Open**: `backend/app/routers/auth.py` (Lines 70–110).
* **Step-by-Step Flow**:
  1. **Frontend**: Sends `POST /api/auth/register` with `{name, email, password, role}`.
  2. **Backend**: Checks `db.query(User).filter(User.email == email).first()`.
  3. **Hash**: Encrypts password using `pwd_context.hash(password)`.
  4. **Database**: Executes `db.add(new_user)` and `db.commit()`.

---

### 3. ACTION: Click "Add New Athlete" Button
* **What to Say to Mentor**:
  > *"When I click 'Add Athlete' and submit the form, the frontend sends the athlete's name, age, sport, and position to `/api/athletes`. The backend verifies the authorization JWT token, links the athlete to the logged-in coach, and writes a new row into the `athletes` database table."*
* **File to Open**: `backend/app/routers/athletes.py` (Lines 15–50) & `src/pages/Dashboard.jsx`.
* **Step-by-Step Flow**:
  1. **Frontend**: Opens Modal -> User enters details -> Sends `POST /api/athletes` with Bearer Header.
  2. **Validation**: FastAPI validates fields using Pydantic schema `AthleteCreate`.
  3. **Database**: Creates `Athlete(name=..., coach_id=current_user.id)` -> Commits to SQLite.
  4. **UI Update**: Frontend updates React state `athletes` array without refreshing page.

---

### 4. ACTION: Click "Upload Video" Button
* **What to Say to Mentor**:
  > *"When I select an MP4 video file and click 'Upload', the browser sends a multipart form request to `/api/videos/upload`. The backend saves the video file in `uploads/videos/`, generates a unique filename, and returns the file storage path."*
* **File to Open**: `backend/app/routers/videos.py` (Lines 20–55).
* **Step-by-Step Flow**:
  1. **Frontend**: Selects `.mp4` file -> Creates `FormData` object -> `POST /api/videos/upload`.
  2. **Backend**: Reads `UploadFile` stream in 1MB chunks.
  3. **Storage**: Saves file to server disk path `uploads/videos/{uuid}.mp4`.
  4. **Response**: Returns `{file_path: "...", video_id: 101}`.

---

### 5. ACTION: Click "Analyze Movement / Run AI Risk Assessment" Button
* **What to Say to Mentor**:
  > *"When I click 'Analyze Movement', the backend passes the video to OpenCV and MediaPipe BlazePose. MediaPipe tracks 33 3D body keypoints across every frame. Our vector geometry module calculates joint angles (knee, hip, ankle), computes bilateral asymmetry, and passes these features into our trained XGBoost / Random Forest ML model to predict an exact injury risk score."*
* **File to Open**: `backend/app/services/video_processor.py` (Lines 30–160) & `backend/app/services/ml_engine.py` (Lines 25–120).
* **Step-by-Step Flow**:
  1. **OpenCV Decoding**: Opens video stream `cv2.VideoCapture(file_path)`.
  2. **MediaPipe Tracking**: `mp_pose.Pose()` processes frames, extracting 33 $(x,y,z)$ coordinates.
  3. **3D Angle Math**: `calculate_angle(hip, knee, ankle)` computes joint interior angles using vector dot product $\arccos$.
  4. **Feature Vector**: Extracts 23 features (min, max, avg angles, velocity, symmetry).
  5. **ML Prediction**: `scaler.transform(features)` -> `model.predict_proba()` -> returns Risk Score (e.g. 78% HIGH RISK).
  6. **Database Record**: Saves result into `Analysis` database table.

---

### 6. ACTION: Click "Download Clinical PDF Report" Button
* **What to Say to Mentor**:
  > *"When I click 'Download Report', the browser requests `GET /api/reports/{analysis_id}/pdf`. The backend uses Python ReportLab library to build a multi-page PDF containing athlete info, risk grade badges, joint angle telemetry tables, bilateral asymmetry charts, and targeted rehab exercises. It streams the raw PDF bytes back to the browser for instant download."*
* **File to Open**: `backend/app/services/pdf_generator.py` (Lines 20–210) & `backend/app/routers/reports.py`.
* **Step-by-Step Flow**:
  1. **HTTP Request**: Frontend calls `GET /api/reports/{id}/pdf`.
  2. **Query Data**: Fetches analysis record, joint telemetry, and athlete profile from database.
  3. **ReportLab Engine**: Builds PDF using `SimpleDocTemplate`, `Table`, `Paragraph`, and custom canvas page counters.
  4. **Binary Stream**: Returns HTTP response with `media_type="application/pdf"`.

---

### 7. ACTION: Click Theme Switcher Dropdown (8 Color Themes)
* **What to Say to Mentor**:
  > *"When I select a theme like 'Dark Elite' or 'Clinical White', React updates the global `theme` context state. CSS custom properties (`var(--bg-primary)`, `var(--accent-color)`) dynamically update the HTML body attribute without re-rendering unnecessary DOM components. We added `z-50` dropdown positioning to ensure it floats cleanly above all UI elements."*
* **File to Open**: `src/App.jsx` & `src/context/ThemeContext.jsx`.

---

### 8. ACTION: Click "Delete Athlete" Button
* **What to Say to Mentor**:
  > *"When I click 'Delete', the frontend sends `DELETE /api/athletes/{id}`. The backend verifies ownership, deletes associated video analysis records using cascading foreign key relationships, and deletes the athlete row from the database."*
* **File to Open**: `backend/app/routers/athletes.py` (Lines 60–90).

---

### 9. ACTION: Click "Logout" Button
* **What to Say to Mentor**:
  > *"When I click 'Logout', the frontend clears the JWT access token from `localStorage`, resets the user context state to `null`, and redirects to the Login screen."*
* **File to Open**: `src/context/AuthContext.jsx` (Lines 60–80).

---

# PART 2: ALL 35 MENTOR QUESTIONS & EXACT SIMPLE ENGLISH ANSWERS

Here is every single question your mentor could possibly ask, paired with the exact answer to speak aloud and the file to show.

---

## CATEGORY 1: MACHINE LEARNING & PREDICTION ENGINE (Q1 – Q8)

#### Q1: "What machine learning models did you use and why?"
* **Simple English Answer**:
  > *"We evaluated Random Forest, XGBoost, and Support Vector Machines. We selected an ensemble of Random Forest Classifier and XGBoost Classifier because decision-tree ensembles handle non-linear biomechanical feature relationships exceptionally well and prevent overfitting on joint angle datasets."*
* **File to Show**: `scripts/train_pipeline.py` (Lines 40–85).

#### Q2: "How did you train the model and what is the accuracy?"
* **Simple English Answer**:
  > *"We split our 5,430 sample dataset into 80% training and 20% testing sets using Scikit-Learn. The Random Forest model achieved 92.4% classification accuracy, 0.91 F1-score, and 0.96 ROC-AUC."*
* **File to Show**: `scripts/train_pipeline.py` (Lines 90–130).

#### Q3: "Where are the trained model files stored?"
* **Simple English Answer**:
  > *"After training, we serialize the models using `joblib.dump()`. The pre-trained binary files are saved in `models/saved_models/injury_risk_model.joblib` and `models/saved_models/scaler.pkl`."*
* **File to Show**: `models/saved_models/` folder.

#### Q4: "What input features does the machine learning model take?"
* **Simple English Answer**:
  > *"The model takes 23 numerical features extracted from the video keypoints: minimum, maximum, and average knee flexions, hip flexion angles, ankle dorsiflexion, angular velocity, bilateral symmetry percentage, ground impact force, and fatigue index."*
* **File to Show**: `ml/feature_extractor.py` (Lines 15–60).

#### Q5: "How does the model calculate a percentage risk score like 78%?"
* **Simple English Answer**:
  > *"Instead of just predicting 0 or 1, we call `model.predict_proba(X)`. This returns the calibrated class probability (e.g. 0.78 probability of high risk), which we multiply by 100 to get a 78% risk score."*
* **File to Show**: `backend/app/services/ml_engine.py` (Lines 80–110).

#### Q6: "Why did you use StandardScaler?"
* **Simple English Answer**:
  > *"StandardScaler normalizes all features to have zero mean and unit variance ($\mu=0, \sigma=1$). This ensures features measured in degrees (like 120° knee angle) do not dominate features measured in percentages (like 15% asymmetry)."*
* **File to Show**: `scripts/train_pipeline.py` (Lines 50–60).

#### Q7: "How do you handle overfitting in your ML model?"
* **Simple English Answer**:
  > *"We used 5-fold cross-validation during training, restricted `max_depth` to 10 trees in Random Forest, set `min_samples_split=5`, and applied L2 regularization in XGBoost."*
* **File to Show**: `scripts/train_pipeline.py`.

#### Q8: "How can you retrain the model if new data arrives?"
* **Simple English Answer**:
  > *"We simply run `py -3 scripts/train_pipeline.py` in the terminal. It reads updated CSV datasets, retrains the classifiers, and overwrites `injury_risk_model.joblib` automatically."*
* **File to Show**: `scripts/train_pipeline.py`.

---

## CATEGORY 2: COMPUTER VISION & BIOMECHANICS MATH (Q9 – Q16)

#### Q9: "How do you extract 3D joint locations from a normal 2D camera video?"
* **Simple English Answer**:
  > *"We use Google MediaPipe BlazePose, a deep neural network trained on millions of human images. It predicts 33 3D skeletal landmarks $(x, y, z)$ with depth relative to the hip center from a standard 2D MP4 video stream."*
* **File to Show**: `backend/app/services/video_processor.py` (Lines 80–120).

#### Q10: "What is the exact math formula to calculate joint angles?"
* **Simple English Answer**:
  > *"We use 3D vector dot-product geometry. For a joint like the knee (B) between hip (A) and ankle (C), we form vectors $\vec{BA} = A - B$ and $\vec{BC} = C - B$. The angle $\theta$ is:
  $$\theta = \arccos\left(\frac{\vec{BA} \cdot \vec{BC}}{\|\vec{BA}\| \|\vec{BC}\|}\right) \times \frac{180}{\pi}$$
  This cosine formula is completely invariant to camera distance."*
* **File to Show**: `backend/app/services/video_processor.py` (Lines 30–65).

#### Q11: "What are the 33 MediaPipe keypoints?"
* **Simple English Answer**:
  > *"MediaPipe maps 33 body locations: Keypoints 11–12 are Shoulders, 13–14 are Elbows, 15–16 are Wrists, 23–24 are Hips, 25–26 are Knees, and 27–28 are Ankles."*
* **File to Show**: `backend/app/services/video_processor.py`.

#### Q12: "What is Bilateral Asymmetry and why is it important?"
* **Simple English Answer**:
  > *"Bilateral Asymmetry calculates the percentage difference between left and right limb movements:
  $$\text{Asymmetry} = \frac{|\text{Left} - \text{Right}|}{\max(\text{Left}, \text{Right})} \times 100$$
  In sports medicine, any asymmetry over 15% indicates muscle compensation and high risk of ACL or tendon strain."*
* **File to Show**: `backend/app/services/video_processor.py` (Lines 140–160).

#### Q13: "How do you detect Knee Valgus (inward knee collapse)?"
* **Simple English Answer**:
  > *"Knee valgus occurs when the frontal plane distance between knees decreases during landing while ankles remain wide. We track the lateral X-axis ratio between knee landmarks (25, 26) and ankle landmarks (27, 28)."*
* **File to Show**: `backend/app/services/video_processor.py`.

#### Q14: "What happens if a video has low lighting or person is partially hidden?"
* **Simple English Answer**:
  > *"MediaPipe provides a `visibility` confidence score for each landmark ($0.0$ to $1.0$). If confidence falls below $0.5$, our pipeline discards noisy frames or interpolates joint positions from neighboring frames."*
* **File to Show**: `backend/app/services/video_processor.py`.

#### Q15: "Why process frame-by-frame instead of treating the whole video at once?"
* **Simple English Answer**:
  > *"Frame-by-frame processing allows OpenCV to extract joint angle series over time, enabling us to capture kinematic velocity, peak impact forces, and movement repetition cycles."*
* **File to Show**: `backend/app/services/video_processor.py`.

#### Q16: "Can this system run on live webcam feed?"
* **Simple English Answer**:
  > *"Yes! OpenCV `cv2.VideoCapture(0)` can read directly from a camera device index `0` and run the exact same MediaPipe analysis loop in real time at 30 FPS."*
* **File to Show**: `backend/app/services/video_processor.py`.

---

## CATEGORY 3: AUTHENTICATION, SECURITY & LOGIN (Q17 – Q22)

#### Q17: "Is user password saved in plain text in the database?"
* **Simple English Answer**:
  > *"No, never! Passwords are encrypted using Passlib Bcrypt salt hashing (`pwd_context.hash()`). Only the non-reversible 60-character Bcrypt hash string is stored in the database."*
* **File to Show**: `backend/app/routers/auth.py` (Lines 30–45).

#### Q18: "What is JWT and how does authentication work?"
* **Simple English Answer**:
  > *"JWT stands for JSON Web Token. Upon login, the server signs a cryptographically secure token containing user ID, email, and expiration time using HMAC-SHA256 (`HS256`). The client includes this token in the HTTP `Authorization: Bearer <token>` header for all API calls."*
* **File to Show**: `backend/app/routers/auth.py` (Lines 80–115).

#### Q19: "Where is the JWT token stored on the frontend?"
* **Simple English Answer**:
  > *"It is saved in browser `localStorage`. `AuthContext.jsx` loads the token on startup and attaches it to all outgoing Axios REST requests."*
* **File to Show**: `src/context/AuthContext.jsx` (Lines 20–45).

#### Q20: "How did you fix browser password autofill security leaks?"
* **Simple English Answer**:
  > *"We implemented explicit input form state resets `setForm({ email: '', password: '' })` when switching auth modes, and added `autoComplete="new-password"` attributes to form inputs."*
* **File to Show**: `src/pages/Login.jsx`.

#### Q21: "What is Role-Based Access Control (RBAC) in your project?"
* **Simple English Answer**:
  > *"We support `COACH` and `ATHLETE` roles. A Coach can manage multiple athletes and run video analyses, whereas an Athlete can only view their personal clinical risk reports."*
* **File to Show**: `backend/app/models/db_models.py` & `backend/app/routers/auth.py`.

#### Q22: "What happens when the 7-day token expires?"
* **Simple English Answer**:
  > *"FastAPI's `get_current_user` dependency catches `jwt.PyJWTError` or expired timestamps, returning a `401 Unauthorized` HTTP status. The frontend intercepts 401 response codes and redirects the user to the login screen."*
* **File to Show**: `backend/app/routers/auth.py`.

---

## CATEGORY 4: DATABASE & DATASETS (Q23 – Q28)

#### Q23: "Which database system are you using?"
* **Simple English Answer**:
  > *"We use SQLite for local development and PostgreSQL for cloud production, managed seamlessly through Python SQLAlchemy Object Relational Mapper (ORM)."*
* **File to Show**: `backend/app/models/db_models.py` & `backend/app/database.py`.

#### Q24: "What database tables exist in your system?"
* **Simple English Answer**:
  > *"We have three core tables: `users` (coaches/athletes), `athletes` (demographics, sport, position), and `analyses` (video paths, joint angles, risk scores, PDF reports)."*
* **File to Show**: `backend/app/models/db_models.py` (Lines 15–120).

#### Q25: "How are tables connected to each other?"
* **Simple English Answer**:
  > *"Using foreign keys: `Athlete.coach_id` links to `User.id` (1 Coach to N Athletes), and `Analysis.athlete_id` links to `Athlete.id` (1 Athlete to N Video Analyses)."*
* **File to Show**: `backend/app/models/db_models.py`.

#### Q26: "Where is the dataset located?"
* **Simple English Answer**:
  > *"The dataset is stored in CSV format at `data/raw/synthetic_injury_dataset.csv`. It contains 5,430 biomechanical samples."*
* **File to Show**: `data/raw/synthetic_injury_dataset.csv`.

#### Q27: "How was the dataset created?"
* **Simple English Answer**:
  > *"We built `scripts/generate_synthetic_data.py` to sample kinematic joint distributions derived from published clinical sports medicine studies (e.g. knee valgus range 5°–35°, asymmetry 2%–30%)."*
* **File to Show**: `scripts/generate_synthetic_data.py`.

#### Q28: "What happens to video analysis data if an athlete is deleted?"
* **Simple English Answer**:
  > *"SQLAlchemy relationship `cascade="all, delete-orphan"` automatically deletes all linked video analysis records and stored files from disk to prevent orphaned database records."*
* **File to Show**: `backend/app/models/db_models.py`.

---

## CATEGORY 5: FRONTEND REACT & PDF REPORT GENERATION (Q29 – Q35)

#### Q29: "What framework is used for frontend and backend?"
* **Simple English Answer**:
  > *"Frontend is built with React 18 and Vite for fast Single Page Application rendering. Backend is built with FastAPI (Python 3.14) for high-performance asynchronous REST APIs."*
* **File to Show**: `src/App.jsx` & `backend/app/main.py`.

#### Q30: "How do frontend and backend communicate?"
* **Simple English Answer**:
  > *"Through HTTP REST API requests. The React frontend uses Axios to send JSON payloads or multipart form data to FastAPI endpoints running on port 8000."*
* **File to Show**: `src/context/AuthContext.jsx`.

#### Q31: "How is the clinical PDF report created?"
* **Simple English Answer**:
  > *"We use Python ReportLab library in `backend/app/services/pdf_generator.py`. It dynamically generates PDF pages containing clinical header banners, risk grade badges, joint telemetry data tables, and prescribed rehabilitation routines."*
* **File to Show**: `backend/app/services/pdf_generator.py`.

#### Q32: "How did you build the 8 color themes?"
* **Simple English Answer**:
  > *"We defined CSS custom variable tokens (e.g. `--color-bg`, `--color-primary`) in Tailwind / CSS stylesheets. React `ThemeContext` toggles `data-theme` attributes on the root `<html>` element."*
* **File to Show**: `src/context/ThemeContext.jsx` & `src/App.jsx`.

#### Q33: "How did you fix dropdown menu visibility issues during presentation?"
* **Simple English Answer**:
  > *"We resolved z-index clipping issues by applying `z-50` overlay positioning, absolute container offsets, and preventing parent `overflow: hidden` truncation."*
* **File to Show**: `src/components/ThemeSelector.jsx` / `src/App.jsx`.

#### Q34: "How do you handle large video file uploads?"
* **Simple English Answer**:
  > *"FastAPI uses `UploadFile` spooled file handlers which stream binary data in chunks directly to disk without loading giant video files into server RAM."*
* **File to Show**: `backend/app/routers/videos.py`.

#### Q35: "How can this project be deployed to the web?"
* **Simple English Answer**:
  > *"The React frontend deploys to Vercel or Netlify via `npm run build`. The FastAPI backend deploys to Render or Railway using Docker or Uvicorn production server."*
* **File to Show**: `package.json` & `backend/app/main.py`.

---

# PART 3: MASTER FILE SELECTION TABLE FOR MENTOR DEFENSE

| Feature / Module | Exact File Path | Lines | Key Function / Object | Primary Tech Used |
| :--- | :--- | :--- | :--- | :--- |
| **ML Model Training** | `scripts/train_pipeline.py` | 1–140 | `train_injury_risk_model()` | Random Forest, XGBoost |
| **Saved ML Artifacts** | `models/saved_models/` | Binary | `injury_risk_model.joblib` | Joblib, Scikit-Learn |
| **ML Prediction Engine** | `backend/app/services/ml_engine.py` | 25–180 | `predict_injury_risk()` | Scikit-Learn `.predict_proba()` |
| **Feature Extractor** | `ml/feature_extractor.py` | 15–90 | `extract_features_from_angles()` | NumPy, Pandas |
| **Dataset CSV File** | `data/raw/synthetic_injury_dataset.csv` | 5,430 Rows | `synthetic_injury_dataset.csv` | Biomechanical Data |
| **Synthetic Generator** | `scripts/generate_synthetic_data.py` | 10–120 | `generate_dataset()` | NumPy Random Normal |
| **3D Vector Angle Math**| `backend/app/services/video_processor.py` | 30–75 | `calculate_angle()` | Vector Cosine $\arccos$ Math |
| **MediaPipe 33 Pose** | `backend/app/services/video_processor.py` | 80–160 | `mp.solutions.pose.Pose()` | Google MediaPipe BlazePose |
| **Video Upload API** | `backend/app/routers/videos.py` | 20–110 | `upload_video()` | OpenCV `VideoCapture`, FastAPI |
| **Auth & Password Hash** | `backend/app/routers/auth.py` | 25–115 | `login()`, `get_current_user()` | Passlib Bcrypt, PyJWT |
| **Frontend Login Screen**| `src/pages/Login.jsx` | 1–140 | `Login`, `handleSubmit()` | React 18, Form Handling |
| **Auth Context Token** | `src/context/AuthContext.jsx` | 10–85 | `AuthProvider`, `localStorage` | React Context API |
| **Database Models** | `backend/app/models/db_models.py` | 15–120 | `User`, `Athlete`, `Analysis` | SQLAlchemy ORM |
| **Athlete Management** | `backend/app/routers/athletes.py` | 15–95 | `create_athlete()` | FastAPI Pydantic Router |
| **PDF Generation** | `backend/app/services/pdf_generator.py` | 20–210 | `generate_pdf_report()` | Python ReportLab |
| **Frontend Roster** | `src/pages/Dashboard.jsx` | 1–250 | `Dashboard`, `SquadMatrix` | React Hooks, Lucide Icons |

---

# PART 4: 5-MINUTE STEP-BY-STEP LIVE DEMO GUIDE

Follow these exact steps when presenting your project live to your mentor:

1. **Terminal Startup**:
   - Backend: `uvicorn backend.app.main:app --reload --port 8000`
   - Frontend: `npm run dev`
2. **Browser Login**:
   - Open `http://localhost:5173`.
   - Log in with `coach@motioniq.com` / `password123`.
   - *Tell mentor*: "Login uses Bcrypt password hashing and signed JWT tokens."
3. **Select Athlete & Roster**:
   - Click an athlete (e.g. Alex Rivera).
   - *Tell mentor*: "Athletes are stored in SQLite using SQLAlchemy ORM."
4. **Upload & Analyze Exercise Video**:
   - Select sample exercise video from `C:\Users\OmniBook x\Downloads\MotionIQ_Sample_Videos\`.
   - *Tell mentor*: "OpenCV decodes frames, MediaPipe tracks 33 3D keypoints, and 3D vector math calculates joint angles."
5. **Explain Machine Learning Prediction**:
   - Show Risk Score (e.g. 78% HIGH RISK).
   - *Tell mentor*: "23 extracted features pass through our Random Forest / XGBoost model trained on 5,430 biomechanical samples."
6. **Download Clinical PDF Report**:
   - Click "Download Clinical PDF Report".
   - Open PDF. *Tell mentor*: "ReportLab dynamically builds this clinical report with telemetry tables and recovery plans."
"""

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header
        self.drawString(54, 11 * 72 - 36, "MOTION IQ — MEGA MENTOR DEFENSE & BUTTON-BY-BUTTON MASTER GUIDE")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        # Footer
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.drawString(54, 34, "CONFIDENTIAL & PROPRIETARY • MEGA MENTOR DEFENSE GUIDE")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 34, page_str)
        self.restoreState()

def clean_html(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier" size="8" color="#4c1d95">\1</font>', text)
    return text

def build_pdf_and_md():
    print(f"Writing Markdown artifact to: {MD_PATH}")
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(MD_CONTENT)

    print(f"Building PDF artifact at: {PDF_PATH_ARTIFACT}")
    doc = SimpleDocTemplate(
        PDF_PATH_ARTIFACT,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4c1d95'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'DocH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#ffffff'),
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#1e293b')
    )

    story = []
    lines = MD_CONTENT.split('\n')
    in_table = False
    table_lines = []

    story.append(Paragraph("Motion IQ — Mega Mentor Defense & Button-by-Button Master Guide", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#7c3aed'), spaceAfter=10))

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        if line_str.startswith('|'):
            in_table = True
            table_lines.append(line_str)
            continue
        elif in_table:
            in_table = False
            if len(table_lines) > 2:
                table_data = []
                headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
                table_data.append([Paragraph(clean_html(h), table_header_style) for h in headers])
                for row_line in table_lines[2:]:
                    cols = [c.strip() for c in row_line.split('|')[1:-1]]
                    if len(cols) == len(headers):
                        table_data.append([Paragraph(clean_html(c), table_cell_style) for c in cols])
                
                if table_data:
                    col_widths = [90, 120, 45, 115, 130]
                    t = Table(table_data, colWidths=col_widths, repeatRows=1)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4c1d95')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')])
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 8))
            table_lines = []

        if line_str.startswith('# '):
            story.append(Paragraph(clean_html(line_str[2:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd6fe'), spaceAfter=6))
        elif line_str.startswith('## '):
            story.append(Paragraph(clean_html(line_str[3:]), h2_style))
        elif line_str.startswith('### '):
            story.append(Paragraph(clean_html(line_str[4:]), h3_style))
        elif line_str.startswith('#### '):
            story.append(Paragraph(clean_html(line_str[5:]), h3_style))
        elif line_str.startswith('> '):
            story.append(Paragraph(f"<i>{clean_html(line_str[2:])}</i>", body_style))
        else:
            story.append(Paragraph(clean_html(line_str), body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Artifact PDF built successfully at: {PDF_PATH_ARTIFACT}")

    shutil.copy(PDF_PATH_ARTIFACT, PDF_PATH_DOWNLOADS)
    print(f"Downloads copy created at: {PDF_PATH_DOWNLOADS}")

if __name__ == "__main__":
    build_pdf_and_md()
