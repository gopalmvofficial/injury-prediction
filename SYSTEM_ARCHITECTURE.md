# Sports Injury Risk Detection and Prevention System
## Complete System Architecture, Tech Stack, Flowcharts & AI Roadmap

---

## 1. End-to-End System Architecture Diagram

```mermaid
graph TD
    %% User Layer
    User([Coach / Athlete / Physio]) -->|Interacts with UI| FE[React + Vite Frontend\nNginx Port 5173/80]
    
    %% Frontend Sub-Components
    subgraph Frontend_App ["Frontend Layer (Client-Side & Nginx)"]
        FE --> AuthUI[Auth Screen\nLogin/Register]
        FE --> DashUI[Dashboard & Summary Metrics]
        FE --> AthUI[Athlete Profile Management]
        FE --> VideoUI[Video Upload & Activity Selector]
        FE --> RepUI[Interactive Risk & Biomechanics Reports]
    end

    %% Network / API Gateway Layer
    Frontend_App -->|HTTP REST + Bearer Token| BE[FastAPI Backend\nPort 8000]

    %% Backend Sub-Components
    subgraph Backend_App ["Backend Layer (FastAPI & Python 3.11)"]
        BE --> AuthAPI[Auth Router & Token Verification]
        BE --> AthAPI[Athlete CRUD Router]
        BE --> VidAPI[Video Upload & Validation Router]
        BE --> AnaAPI[Analysis & Kinematics Router]
        BE --> RepAPI[PDF Report Generator]
        
        %% Core Engines
        VidAPI --> Storage[(Local / Persistent Volume Storage\n/app/uploads)]
        AnaAPI --> CV_Engine[OpenCV Video Frame Decoder]
        CV_Engine --> MP_Engine[Google MediaPipe Pose AI\n33 3D Skeletal Keypoints]
        MP_Engine --> Bio_Engine[Kinematic & Angle Calculator\nKnee/Hip/Ankle ROM & Symmetry]
        Bio_Engine --> MQ_Engine[Movement Quality Scorer]
        MQ_Engine --> Risk_Engine[Injury Risk Prediction Engine\nRule-based / ML Classifier]
    end

    %% Database Layer
    subgraph Database_Layer ["Persistence Layer"]
        AuthAPI --> DB[(SQLite / PostgreSQL DB\nusers, athletes, analyses, risk_results)]
        AthAPI --> DB
        Risk_Engine --> DB
    end

    %% Output
    Risk_Engine --> RepAPI
    RepAPI -->|Download PDF Report & Risk Insights| User
```

---

## 2. Complete Tech Stack Breakdown

| Component Layer | Technology / Tool | Version | Role in the System | Why It Was Chosen |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React.js** | 18+ | Builds single-page user interface (SPA) | Component modularity, reactive state, fast rendering. |
| **Frontend Build Tool** | **Vite** | 5+ / 8+ | Bundler & local dev server | Instant hot module replacement (HMR), lightweight build output. |
| **Production Web Server** | **Nginx (Alpine)** | 1.25+ | Serves compiled static JS/CSS & reverse proxies API | High concurrency, low memory footprint (~15MB), SPA routing (`try_files`). |
| **Backend Framework** | **FastAPI** | 0.110+ | High-performance asynchronous REST API | Native OpenAPI Swagger documentation, async performance, Pydantic type validation. |
| **API Server (ASGI)** | **Uvicorn** | 0.29+ | ASGI web server runner | Lightning-fast Python server handling asynchronous requests. |
| **Computer Vision AI** | **MediaPipe** | 0.10.x | 33-point 3D skeletal landmark detector | Deep learning pose tracker running fast on CPU without needing dedicated GPUs. |
| **Video Processing** | **OpenCV (`cv2`)** | 4.9+ | Video decoding, frame sampling, visual stick-figure overlay | Industry standard for matrix manipulation and frame rendering. |
| **Numerical Math & Data** | **NumPy & Pandas** | 1.26+ / 2.1+ | Joint angle geometry, vectors, landmark time-series DataFrames | Vectorized trigonometric calculations and time-series aggregation. |
| **Database & ORM** | **SQLAlchemy + SQLite** | 2.0+ | Relational data persistence | DB-agnostic ORM (seamlessly switches from SQLite to PostgreSQL with zero code changes). |
| **Document Generation** | **ReportLab** | 4.1+ | PDF medical/coaching report generator | Automated generation of styled reports with scores, observations, and recommendations. |
| **Containerization** | **Docker & Docker Compose** | 24+ / v2 | Multi-container isolated environment | Replicable deployment eliminating *"works on my machine"* dependency errors. |

---

## 3. Step-by-Step Data Flow (What Happens Where & How)

### Step 1: Authentication & User Session
1. **Where:** `frontend/src/main.jsx` $\rightarrow$ `backend/app/routes/auth.py`
2. **How:** 
   - User enters email & password on React frontend.
   - Frontend calls `POST /api/auth/register` or `POST /api/auth/login`.
   - Backend hashes password with a unique salt (`hashlib.sha256`), stores it in SQLite, and returns a secure session token.
   - Frontend stores the token in `localStorage` and injects `Authorization: Bearer <token>` into all subsequent requests.

### Step 2: Athlete Profile Management
1. **Where:** `frontend/src/main.jsx` $\rightarrow$ `backend/app/routes/athletes.py` $\rightarrow$ SQLite DB
2. **How:**
   - Coach enters Athlete Name, Age, Height (cm), Weight (kg), Sport, and Prior Injury History.
   - Backend validates the schema using Pydantic (`AthleteCreate`), associates the record with `current_user.id`, and saves to the `athletes` table.

### Step 3: Video Ingestion & Validation
1. **Where:** `frontend/src/main.jsx` $\rightarrow$ `backend/app/routes/videos.py`
2. **How:**
   - User selects an athlete, chooses exercise activity (`squat`, `running`, `jumping_landing`), and uploads an MP4/MOV file.
   - Backend validates video size, extension, and headers, generates a unique UUID filename, and saves it to `/app/uploads/`.
   - Video metadata is saved to the `videos` database table.

### Step 4: Computer Vision & MediaPipe Pose Estimation
1. **Where:** `backend/app/services/video_processing.py` & `backend/app/services/pose_estimation.py`
2. **How:**
   - OpenCV opens the video stream (`cv2.VideoCapture`).
   - For every frame, MediaPipe's deep neural network detects **33 3D skeletal landmarks** (nose, shoulders, elbows, wrists, hips, knees, ankles, heels, toes).
   - Landmark coordinates $(x, y, z, \text{visibility})$ are structured into a time-series Pandas DataFrame.
   - OpenCV draws visual skeletal lines on each frame and saves an annotated video to `/app/results/`.

### Step 5: Kinematic Biomechanics Calculation
1. **Where:** `backend/app/services/biomechanics.py`
2. **How:**
   - Joint angles are computed across all frames using vector 3D trigonometry:
     $$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right)$$
   - Calculates:
     - **Left & Right Knee Range of Motion (ROM)** (Min/Max flexion angles).
     - **Left & Right Hip ROM**.
     - **Knee & Hip Bilateral Symmetry %**: Ratio comparing left vs. right joint trajectories.
     - **Trunk Lean Angle**: Angle of spine relative to vertical ground plane.
     - **Movement Consistency %**: Coefficient of variation across repetitions.

### Step 6: Injury Risk Prediction & Reporting
1. **Where:** `backend/app/services/risk_prediction.py` & `backend/app/services/report.py`
2. **How:**
   - Biomechanical outputs + Athlete baseline injury history are fed into the Risk Engine.
   - Calculates a normalized **0–100% Risk Score** and classifies into **LOW / MEDIUM / HIGH**.
   - Generates contextual clinical recommendations (e.g. glute strengthening, single-leg stability).
   - ReportLab compiles a structured PDF report ready for download.

---

## 4. Future AI/ML Roadmap: How to Predict Injury with Machine Learning (Milestone 3)

In Milestone 3, the current rule-based heuristic in `backend/app/services/risk_prediction.py` will be replaced by a **Supervised Machine Learning / Deep Learning model**.

```mermaid
graph LR
    subgraph Data_Preparation ["1. Feature Engineering"]
        K1[Knee Symmetry %] --> VEC[Feature Vector X]
        K2[Hip Symmetry %] --> VEC
        K3[Max Trunk Lean] --> VEC
        K4[Movement Quality Score] --> VEC
        K5[Athlete Age & Weight] --> VEC
        K6[Injury History Flag 0/1] --> VEC
    end

    subgraph ML_Training ["2. Machine Learning Model"]
        VEC --> MODEL{Trained ML Model\nXGBoost / Random Forest\nPyTorch / LSTM}
        DS[(Historical Sports\nInjury Dataset)] -->|Train & Validate| MODEL
    end

    subgraph Inference ["3. Live API Prediction"]
        MODEL --> PROB[Predicted Risk Probability: 78.4%]
        PROB --> CAT[Risk Class: HIGH]
        MODEL --> SHAP[SHAP / Feature Importance\nExplains 'Why' Risk is High]
    end
```

### Proposed AI/ML Stack for Milestone 3:
1. **Model Frameworks:**
   - **XGBoost / LightGBM / Scikit-Learn:** Ideal for tabular kinematic feature vectors (knee angle, symmetry %, ROM, weight, age).
   - **PyTorch (LSTM / 1D-CNN / Transformers):** Ideal for raw temporal joint coordinate sequences across video time-series.
2. **Feature Extraction Pipeline:**
   ```python
   # Feature vector prepared from Milestone 2 outputs
   feature_vector = [
       biomechanics["knee_symmetry_pct"],
       biomechanics["hip_symmetry_pct"],
       biomechanics["trunk"]["max_lean_angle"],
       movement_quality["score"],
       athlete.age,
       athlete.weight_kg,
       1 if athlete.injury_history else 0
   ]
   ```
3. **Model Integration Point:**
   - Save the trained model to `backend/app/models/injury_model.pkl` (or `.onnx` / `.pt`).
   - Load once on backend startup:
     ```python
     import joblib
     MODEL = joblib.load("app/models/injury_model.pkl")
     
     def predict_injury(features):
         probability = MODEL.predict_proba([features])[0][1] * 100
         return probability
     ```

---

## 5. Docker Multi-Container Architecture

```mermaid
graph TB
    subgraph Docker_Compose ["Docker Compose Orchestration"]
        subgraph Frontend_Container ["Container 1: sports-injury-frontend"]
            Nginx[Nginx Web Server] --> HTML[React Production Bundle]
            Nginx -->|Reverse Proxy /api/| BE_Cont
        end

        subgraph Backend_Container ["Container 2: sports-injury-backend"]
            BE_Cont[FastAPI & Uvicorn]
            CV[OpenCV & MediaPipe]
        end

        subgraph Volumes ["Named Storage Volumes"]
            V1[(sports_injury_backend_data\nSQLite DB)]
            V2[(sports_injury_backend_uploads\nRaw Videos)]
            V3[(sports_injury_backend_results\nAnnotated Videos & PDFs)]
        end

        BE_Cont --> V1
        BE_Cont --> V2
        BE_Cont --> V3
    end
```
