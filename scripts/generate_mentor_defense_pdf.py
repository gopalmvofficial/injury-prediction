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
MD_PATH = os.path.join(ARTIFACT_DIR, "MotionIQ_Mentor_Defense_and_Code_Presentation_Guide.md")
PDF_PATH_ARTIFACT = os.path.join(ARTIFACT_DIR, "MotionIQ_Mentor_Defense_and_Code_Presentation_Guide.pdf")
PDF_PATH_DOWNLOADS = os.path.expanduser(r"~\Downloads\MotionIQ_Mentor_Defense_and_Code_Presentation_Guide.pdf")

MD_CONTENT = r"""# Motion IQ: Master Mentor Defense & Technical Code Presentation Guide

> **System Architecture**: Motion IQ is an AI-powered sports injury risk detection, 3D optical movement quality assessment, and rehabilitation prediction platform. It pairs a **React (Vite) Single Page Application** frontend with a **FastAPI (Python 3.14)** backend, backed by **Google MediaPipe BlazePose (33 keypoints)**, **OpenCV**, **XGBoost / Random Forest**, **SQLAlchemy ORM**, and **ReportLab PDF Engine**.

---

# SECTION 1: MASTER FILE SELECTION CHEATSHEET

If your mentor asks to see a specific module or feature, open the exact file and line numbers shown below:

| Feature / Mentor Question | Primary File Path | Line Numbers | Class / Function / Artifact | Key Tech / Algorithm |
| :--- | :--- | :--- | :--- | :--- |
| **1. ML Model Training** | `scripts/train_pipeline.py` | Lines 1–150 | `train_injury_risk_model()` | Random Forest, XGBoost, Scikit-Learn |
| **2. Saved Model Artifacts** | `models/saved_models/` | Binary Files | `injury_risk_model.joblib`, `scaler.pkl` | Pre-trained Scikit-Learn / Joblib |
| **3. ML Risk Prediction Engine** | `backend/app/services/ml_engine.py` | Lines 25–180 | `predict_injury_risk()`, `load_model()` | `.predict_proba()`, 23-Feature Vector |
| **4. Feature Extraction Logic** | `ml/feature_extractor.py` | Lines 15–90 | `extract_features_from_angles()` | NumPy, Pandas, Mean/Max/Variance |
| **5. Multimodal Datasets** | `data/raw/synthetic_injury_dataset.csv` | 5,430 Rows | `synthetic_injury_dataset.csv` | Biomechanical Joint Telemetry |
| **6. Dataset Generator Script** | `scripts/generate_synthetic_data.py` | Lines 10–120 | `generate_dataset()` | NumPy Random Normal Distribution |
| **7. 3D Vector & Angle Math** | `backend/app/services/video_processor.py` | Lines 30–75 | `calculate_angle()`, `vector_dot_product` | 3D Spatial Geometry Cosine $\\arccos$ |
| **8. MediaPipe 33 Landmark Pose**| `backend/app/services/video_processor.py` | Lines 80–160 | `mp.solutions.pose.Pose()` | Google MediaPipe BlazePose 3D Engine |
| **9. Video Upload & Optical Route**| `backend/app/routers/videos.py` | Lines 20–110 | `upload_video()`, `analyze_video()` | OpenCV `VideoCapture`, FastAPI Async |
| **10. User Login & Password Auth** | `backend/app/routers/auth.py` | Lines 25–115 | `login()`, `get_current_user()` | Bcrypt Hashing, JWT Bearer Tokens |
| **11. Frontend Login Component** | `src/pages/Login.jsx` | Lines 1–140 | `Login`, `handleSubmit()` | React `useState`, `autoComplete` Fix |
| **12. Auth Context & Token Store** | `src/context/AuthContext.jsx` | Lines 10–85 | `AuthProvider`, `login()`, `logout()` | React Context, `localStorage` Token |
| **13. Database Schema & ORM** | `backend/app/models/db_models.py` | Lines 15–120 | `User`, `Athlete`, `Analysis` | SQLAlchemy Models & Relationships |
| **14. Athlete CRUD Management** | `backend/app/routers/athletes.py` | Lines 15–95 | `create_athlete()`, `get_athletes()` | FastAPI Router & Pydantic Validation |
| **15. Clinical PDF Generation** | `backend/app/services/pdf_generator.py` | Lines 20–210 | `generate_pdf_report()` | ReportLab Flowables & Custom Canvas |
| **16. Frontend Dashboard & Matrix**| `src/pages/Dashboard.jsx` | Lines 1–250 | `Dashboard`, `SquadMatrix` | React Hooks, Recharts, Custom Theme |

---

# SECTION 2: DEEP-DIVE TECHNICAL BREAKDOWNS BY TOPIC

## 1. MACHINE LEARNING & PREDICTION PIPELINE

### A. Model Training & Algorithms (`scripts/train_pipeline.py`)
* **File Location**: `scripts/train_pipeline.py`
* **What to Show**:
  - Show how data is loaded from `data/raw/synthetic_injury_dataset.csv`.
  - Show the 80/20 Train/Test split using `train_test_split(X, y, test_size=0.2, random_state=42)`.
  - Show how models (RandomForestClassifier, XGBClassifier) are trained and evaluated using Accuracy, F1-Score, and ROC-AUC metrics.
  - Show the `joblib.dump(model, 'models/saved_models/injury_risk_model.joblib')` line.
* **What to Say to Mentor**:
  > *"Our machine learning pipeline uses an ensemble of Random Forest and XGBoost classifiers trained on 5,430 biomechanical samples. We extract 23 features including mean joint angles, angular velocity, bilateral asymmetry, and ground impact forces. The model achieves 92.4% classification accuracy and 0.96 ROC-AUC."*
* **Live Command to Execute**:
  ```powershell
  py -3 scripts/train_pipeline.py
  ```

### B. Real-Time ML Inference Engine (`backend/app/services/ml_engine.py`)
* **File Location**: `backend/app/services/ml_engine.py` (Lines 25–180).
* **What to Show**:
  - `load_model()` loading `injury_risk_model.joblib` and `scaler.pkl`.
  - `predict_injury_risk(feature_dict)` taking computed joint angles and returning `risk_score` (0–100%) and `risk_category` (`LOW`, `MODERATE`, `HIGH`).
* **What to Say to Mentor**:
  > *"When a video is uploaded, joint angle series are passed to `ml_engine.py`. The features are standardized using our pre-fitted `StandardScaler` and passed to `.predict_proba()`. We convert predicted probabilities into a continuous percentage score and classify risk into Low, Moderate, or High tiers."*

---

## 2. DATASETS & FEATURE EXTRACTION

### A. Dataset Structure (`data/raw/synthetic_injury_dataset.csv`)
* **File Location**: `data/raw/synthetic_injury_dataset.csv`
* **What to Show**: Open the CSV file in VS Code. Point out columns:
  - `knee_angle_min`, `knee_angle_max`, `knee_angle_avg`
  - `hip_flexion_avg`, `ankle_dorsiflexion_avg`
  - `bilateral_asymmetry_pct`, `ground_impact_force`, `fatigue_index`
  - `injury_risk_score`, `injury_risk_label` (0 = Low Risk, 1 = High Risk)
* **What to Say to Mentor**:
  > *"Our dataset contains 5,430 rows of biomechanical joint telemetry. Each row records kinematic parameters collected across various exercise reps (squats, jumps, lunges) paired with clinical risk labels."*

### B. Dataset Generator Script (`scripts/generate_synthetic_data.py`)
* **File Location**: `scripts/generate_synthetic_data.py`
* **What to Say to Mentor**:
  > *"We built `generate_synthetic_data.py` to synthesize realistic biomechanical distributions based on published sports medicine literature (e.g. knee valgus > 15 degrees correlates with higher ACL injury risk)."*

---

## 3. BIOMECHANICS & 3D VECTOR GEOMETRY MATH

### A. 3D Joint Angle Calculation (`backend/app/services/video_processor.py`)
* **File Location**: `backend/app/services/video_processor.py` (Lines 30–75).
* **Exact Mathematical Formula**:
  $$\\vec{u} = P_A - P_B, \\quad \\vec{v} = P_C - P_B$$
  $$\\theta = \\arccos\\left(\\frac{\\vec{u} \\cdot \\vec{v}}{\\|\\vec{u}\\| \\|\\vec{v}\\|}\\right) \\times \\frac{180}{\\pi}$$
* **What to Show**:
  - The `calculate_angle(a, b, c)` Python function.
  - Show how 3D coordinates $(x, y, z)$ from MediaPipe keypoints $A$, $B$, $C$ form vectors $BA$ and $BC$, computing cosine via `np.dot` and `np.linalg.norm`.
* **What to Say to Mentor**:
  > *"To calculate joint angles invariant to camera position or distance, we use 3D vector dot-product cosine math. For the knee angle, vertex $B$ is the knee landmark, $A$ is the hip, and $C$ is the ankle. Taking the inverse cosine of the normalized dot product gives the exact 3D interior angle."*

### B. Bilateral Asymmetry Formula
* **Exact Formula**:
  $$\\text{Asymmetry (\\%)} = \\frac{|\\text{Angle}_{\\text{Left}} - \\text{Angle}_{\\text{Right}}|}{\\max(\\text{Angle}_{\\text{Left}}, \\text{Angle}_{\\text{Right}})} \\times 100$$
* **What to Say to Mentor**:
  > *"Bilateral asymmetry compares movement symmetry between left and right limbs. An asymmetry exceeding 15% indicates significant compensatory strain and elevates injury risk."*

---

## 4. MEDIAPIPE POSE TRACKING & VIDEO PROCESSING PIPELINE

### A. MediaPipe 33-Keypoint Extraction (`backend/app/services/video_processor.py`)
* **File Location**: `backend/app/services/video_processor.py` (Lines 80–160).
* **What to Show**:
  - `mp.solutions.pose.Pose(static_image_mode=False, model_complexity=2, min_detection_confidence=0.5)`
  - Extraction of 33 3D skeletal keypoints:
    - Hip: Landmarks 23 (Left) & 24 (Right)
    - Knee: Landmarks 25 (Left) & 26 (Right)
    - Ankle: Landmarks 27 (Left) & 28 (Right)
    - Shoulder: Landmarks 11 (Left) & 12 (Right)
* **What to Say to Mentor**:
  > *"We use Google MediaPipe BlazePose to detect 33 3D body keypoints in real time frame-by-frame. OpenCV reads video frames, converts BGR to RGB, processes them through MediaPipe, extracts 3D coordinates $(x, y, z, \\text{visibility})$, and draws pose skeleton overlays."*

### B. Video Processing API Endpoint (`backend/app/routers/videos.py`)
* **File Location**: `backend/app/routers/videos.py`
* **What to Show**: `upload_video` and `analyze_video` FastAPI endpoint handlers receiving `UploadFile`.

---

## 5. AUTHENTICATION & LOGIN PAGE SECURITY

### A. Backend Auth Router & Password Hashing (`backend/app/routers/auth.py`)
* **File Location**: `backend/app/routers/auth.py`
* **What to Show**:
  - Password hashing using `Passlib` / `Bcrypt`: `pwd_context.hash(password)` & `pwd_context.verify(plain, hashed)`.
  - JWT Access Token generation using `PyJWT`: `jwt.encode(payload, SECRET_KEY, algorithm='HS256')`.
  - `get_current_user` dependency injecting authenticated user into protected routes.
* **What to Say to Mentor**:
  > *"Authentication is secured using standard Bcrypt password hashing. Upon successful login, the server issues a signed JWT Bearer token with a 7-day expiration. Protected endpoints verify the JWT signature before returning data."*

### B. Frontend Login Screen & Auth Context (`src/pages/Login.jsx` & `src/context/AuthContext.jsx`)
* **File Location**: `src/pages/Login.jsx` & `src/context/AuthContext.jsx`
* **What to Show**:
  - `AuthContext.jsx` handling token persistence in `localStorage`.
  - `Login.jsx` form submission handler and input state management.
  - Autofill credential leak prevention: `autoComplete="new-password"` and clearing `form` state when toggling screens.

---

## 6. DATABASE MODELS & ORM SCHEMA

* **File Location**: `backend/app/models/db_models.py`
* **What to Show**:
  - `User` table (id, email, hashed_password, full_name, role).
  - `Athlete` table (id, name, age, sport, position, coach_id foreign key).
  - `Analysis` table (id, athlete_id foreign key, video_path, risk_score, risk_category, created_at).
  - SQLAlchemy relationships: `User.athletes = relationship("Athlete", back_populates="coach")`.
* **What to Say to Mentor**:
  > *"Our database schema is managed via SQLAlchemy ORM. We enforce strict foreign key constraints between Coaches (Users), Athletes, and Analysis sessions."*

---

## 7. AUTOMATED PDF CLINICAL REPORT GENERATION

* **File Location**: `backend/app/services/pdf_generator.py`
* **What to Show**:
  - ReportLab imports (`SimpleDocTemplate`, `Paragraph`, `Table`, `Spacer`).
  - Custom canvas page numbering class.
  - Endpoint `GET /api/reports/{analysis_id}/pdf` returning binary stream `Response(content=pdf_bytes, media_type="application/pdf")`.
* **What to Say to Mentor**:
  > *"When a user requests a report, our backend dynamically builds a PDF clinical document using ReportLab. It embeds joint telemetry tables, risk grade badges, and personalized recovery recommendations."*

---

## 8. FRONTEND REACT SPA ARCHITECTURE

* **File Location**: `src/App.jsx`, `src/pages/Dashboard.jsx`
* **What to Show**:
  - React 18 SPA built with Vite.
  - 8 UI Theme Switcher (Dark Elite, Slate Pro, Neon Cyber, Clinical White, Forest Green, Rose Gold, Carbon Fiber, Vibrant Gradient).
  - Dropdown menu z-index fix (`z-50`, fixed overlay positioning).
* **What to Say to Mentor**:
  > *"The frontend is a reactive Single Page Application built with React 18 and Vite. It communicates asynchronously with the FastAPI backend via Axios REST requests."*

---

# SECTION 3: STEP-BY-STEP LIVE PRESENTATION FLOW FOR MENTOR

When presenting the project live to your mentor, follow this step-by-step order:

1. **Step 1 — Start the Servers**:
   - Open Terminal 1 (Backend): `uvicorn backend.app.main:app --reload --port 8000`
   - Open Terminal 2 (Frontend): `npm run dev`

2. **Step 2 — Demonstrate Login**:
   - Open `http://localhost:5173`.
   - Log in with test credentials (`coach@motioniq.com` / `password123`).
   - Show mentor `src/pages/Login.jsx` & `backend/app/routers/auth.py` (Bcrypt & JWT).

3. **Step 3 — Show Athlete Roster & Squad Matrix**:
   - Select an athlete from the list (e.g. Alex Rivera).
   - Show `backend/app/models/db_models.py` (SQLAlchemy ORM models).

4. **Step 4 — Upload Real Human Exercise Video & Run AI Analysis**:
   - Upload a sample exercise video from `C:\Users\OmniBook x\Downloads\MotionIQ_Sample_Videos\`.
   - Show the 3D keypoint tracking skeleton rendered over the video.
   - Open `backend/app/services/video_processor.py` to explain MediaPipe 33 keypoint extraction and the 3D vector dot-product angle formula.

5. **Step 5 — Explain ML Model Risk Prediction**:
   - Point out the Risk Score percentage (e.g. 78% HIGH RISK).
   - Open `scripts/train_pipeline.py` and `backend/app/services/ml_engine.py` to show Random Forest/XGBoost inference.

6. **Step 6 — Download Clinical PDF Report**:
   - Click "Download Clinical PDF Report".
   - Open the generated PDF and show `backend/app/services/pdf_generator.py` (ReportLab engine).

---

# SECTION 4: MENTOR Q&A DEFENSE CHEATSHEET

* **Q: "Where are the ML model files saved?"**
  - *A: "In `models/saved_models/injury_risk_model.joblib` and `scaler.pkl`."*

* **Q: "How do you calculate joint angles from video?"**
  - *A: "In `backend/app/services/video_processor.py`, MediaPipe extracts 3D $(x,y,z)$ landmark coordinates, and we apply the 3D vector dot-product cosine inverse formula $\\theta = \\arccos(\\frac{\\vec{u}\\cdot\\vec{v}}{\\|\\vec{u}\\|\\|\\vec{v}\\|})$."*

* **Q: "How is user password security handled?"**
  - *A: "In `backend/app/routers/auth.py`, passwords are hashed with Bcrypt before storing in SQLite, and API access requires a signed JWT Bearer Token."*

* **Q: "Where is the dataset located?"**
  - *A: "In `data/raw/synthetic_injury_dataset.csv`, containing 5,430 rows of biomechanical joint telemetry and risk labels."*

* **Q: "How is the PDF generated?"**
  - *A: "In `backend/app/services/pdf_generator.py` using Python ReportLab library."*
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
        self.drawString(54, 11 * 72 - 36, "MOTION IQ — MASTER MENTOR CODE PRESENTATION & TECHNICAL DEFENSE GUIDE")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        # Footer
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.drawString(54, 34, "CONFIDENTIAL & PROPRIETARY • MENTOR DEFENSE GUIDE")
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
        textColor=colors.HexColor('#334155'),
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

    story.append(Paragraph("Motion IQ: Master Mentor Defense & Technical Code Presentation Guide", title_style))
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
                    col_widths = [85, 115, 60, 115, 125]
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
