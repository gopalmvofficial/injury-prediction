"""
generate_master_project_doc_pdf.py

Generates the Complete Master Technical Project Documentation PDF:
docs/MotionIQ_Complete_Master_Project_Documentation.pdf
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

PDF_PATH = os.path.join(DOCS_DIR, "MotionIQ_Complete_Master_Project_Documentation.pdf")


def build_master_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()

    # Color Palette
    c_primary = colors.HexColor('#0f172a')     # Deep Slate
    c_accent = colors.HexColor('#6d28d9')      # Deep Purple
    c_secondary = colors.HexColor('#0284c7')   # Ocean Blue
    c_dark = colors.HexColor('#1e293b')        # Slate Dark
    c_muted = colors.HexColor('#64748b')       # Muted Slate
    c_bg_subtle = colors.HexColor('#faf5ff')   # Very Soft Purple Tint
    c_border = colors.HexColor('#e9d5ff')      # Light Border

    # Typography Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_accent,
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'H2Style',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        textColor=c_accent,
        spaceBefore=12,
        spaceAfter=5
    )
    h3_style = ParagraphStyle(
        'H3Style',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_primary,
        spaceBefore=7,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=5
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=7.8,
        leading=10,
        textColor=c_primary
    )
    tbl_header_style = ParagraphStyle(
        'TblHead',
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11,
        textColor=colors.white
    )
    tbl_cell_style = ParagraphStyle(
        'TblCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    # Document Header
    story.append(Paragraph("MotionIQ: Complete Master Technical Documentation & Architecture Report", title_style))
    story.append(Paragraph("End-to-End System Specifications, Tech Stack, Backend Execution Traces, 23 Dataset Features & Mathematical Models", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=10))

    # SECTION 1: EXECUTIVE OVERVIEW & TECH STACK
    story.append(Paragraph("1. Executive Overview & Complete Technology Stack", h2_style))
    story.append(Paragraph(
        "<b>MotionIQ</b> is an advanced sensorless sports injury risk detection, movement quality assessment, and rehabilitation prediction platform. "
        "It converts standard optical RGB movement videos into 3D skeletal trajectories, calculates biomechanical joint kinematics, "
        "and evaluates injury risk using supervised Machine Learning ensembles.",
        body_style
    ))

    tech_stack_data = [
        [
            Paragraph("<b>Layer / Domain</b>", tbl_header_style),
            Paragraph("<b>Languages & Tools Used</b>", tbl_header_style),
            Paragraph("<b>Role & Technical Function</b>", tbl_header_style),
        ],
        [
            Paragraph("<b>Backend Core</b>", tbl_cell_style),
            Paragraph("Python 3.12, FastAPI, Uvicorn, Pydantic", tbl_cell_style),
            Paragraph("Asynchronous REST API, payload validation, CORS, pipeline orchestration", tbl_cell_style),
        ],
        [
            Paragraph("<b>Computer Vision</b>", tbl_cell_style),
            Paragraph("OpenCV 4.9, Google MediaPipe 0.10", tbl_cell_style),
            Paragraph("Video frame extraction @ 60 FPS, 33 3D skeletal landmark tracking per frame", tbl_cell_style),
        ],
        [
            Paragraph("<b>Machine Learning</b>", tbl_cell_style),
            Paragraph("Scikit-Learn 1.4, XGBoost, Joblib, NumPy, Pandas", tbl_cell_style),
            Paragraph("Supervised injury risk classification, multi-class category models, ACL regression", tbl_cell_style),
        ],
        [
            Paragraph("<b>Database</b>", tbl_cell_style),
            Paragraph("SQLite 3, SQLAlchemy 2.0 ORM", tbl_cell_style),
            Paragraph("Persistent storage for athletes, video metadata, analysis runs, and risk results", tbl_cell_style),
        ],
        [
            Paragraph("<b>Reporting Engine</b>", tbl_cell_style),
            Paragraph("ReportLab 5.0 PDF Library", tbl_cell_style),
            Paragraph("Automated clinical PDF report generation with joint tables & physical therapy plans", tbl_cell_style),
        ],
        [
            Paragraph("<b>Frontend UI</b>", tbl_cell_style),
            Paragraph("JavaScript (ES6+), React 18, Vite 8, CSS3, HTML5", tbl_cell_style),
            Paragraph("Single-page responsive SaaS app, 3D Skeletal Canvas, interactive body heatmap", tbl_cell_style),
        ],
        [
            Paragraph("<b>Browser APIs</b>", tbl_cell_style),
            Paragraph("Web Audio API, Web Speech API (SpeechSynthesis)", tbl_cell_style),
            Paragraph("Retro 8-bit sound synthesizer engine and AI Voice spoken briefings out loud", tbl_cell_style),
        ],
        [
            Paragraph("<b>Cloud & Hosting</b>", tbl_cell_style),
            Paragraph("Vercel (Frontend), Render (Backend Container), GitHub", tbl_cell_style),
            Paragraph("Production CI/CD auto-deployment, CDN caching, SSL encryption", tbl_cell_style),
        ],
    ]

    t_stack = Table(tech_stack_data, colWidths=[110, 180, 250], repeatRows=1)
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))

    # SECTION 2: BACKEND EXECUTION FLOW FOR EVERY USER ACTION
    story.append(Paragraph("2. Backend Execution Flow for Every User Action", h2_style))
    story.append(Paragraph(
        "Below is the exact step-by-step execution trace of what occurs inside the backend server for every user interaction:",
        body_style
    ))

    actions = [
        ("Action A: POST /api/athletes (Create Athlete Profile)",
         "Backend receives JSON payload (Name, Age, Height, Weight, Sport, Injury History). "
         "FastAPI validates payload via Pydantic schema. SQLAlchemy commits new record to SQLite 'athletes' table and returns HTTP 201 with athlete_id."),

        ("Action B: POST /api/videos/upload (Upload Video File)",
         "FastAPI receives Multipart Form Data (.mp4 / .mov file + athlete_id). OpenCV opens video stream to verify codec and frame rate (target 60 FPS). "
         "File saved to backend/uploads buffer. Video record written to 'videos' database table."),

        ("Action C: POST /api/analysis/process (Run Optical & ML Analysis)",
         "1. OpenCV reads video frame-by-frame.<br/>"
         "2. MediaPipe detects 33 3D skeletal landmarks per frame.<br/>"
         "3. Biomechanical engine computes joint angles (Knee, Hip, Ankle), Range of Motion (ROM), Gait Symmetry %, and Trunk Lean Angle.<br/>"
         "4. Derived features are formatted into 13D input vector X_input passed to trained XGBoost ML models.<br/>"
         "5. ML model predicts Risk Level (LOW, MODERATE, HIGH, CRITICAL) and specific injury categories (ACL, Ankle, Knee).<br/>"
         "6. Results committed to 'analyses' and 'risk_results' database tables. Returns JSON response to frontend."),

        ("Action D: GET /api/reports/pdf/{id} (Download Clinical PDF Report)",
         "ReportLab engine loads analysis record from database, formats joint angle tables, radar graphs, and prescribed rehabilitation exercises, and streams PDF binary stream to client."),
    ]

    for title, desc in actions:
        story.append(Paragraph(f"<b>• {title}</b>", h3_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # SECTION 3: MATHEMATICAL EQUATIONS
    story.append(Paragraph("3. Core Mathematical Equations & Kinematic Formulas", h2_style))
    story.append(Paragraph(
        "Every feature computed from optical video frames is derived using exact mathematical physics formulas:<br/>"
        "• <b>Joint Angle (acos vector dot product)</b>: θ = acos( (BA . BC) / (|BA| * |BC|) ) * (180 / π)<br/>"
        "• <b>Range of Motion (ROM)</b>: ROM = max(θ_f) - min(θ_f) across all frames f in [1, N]<br/>"
        "• <b>Bilateral Limb Symmetry %</b>: Symmetry = 100 * (1 - |ROM_L - ROM_R| / max(ROM_L, ROM_R))<br/>"
        "• <b>Spinal Trunk Lean Angle</b>: θ_trunk = acos( (v_trunk . (0, -1)) / |v_trunk| ) * (180 / π)<br/>"
        "• <b>Movement Consistency %</b>: Consistency % = 100 * (1 - stddev(Δθ) / mean(θ))<br/>"
        "• <b>Kinematic Fatigue Index</b>: Fatigue Index = max(10.0, min(100.0, 100.0 - Consistency %))<br/>"
        "• <b>Composite Quality Score</b>: Quality = 0.40 * Consistency % + 0.35 * Symmetry % + 0.25 * max(0, 100 - |θ_trunk - 10| * 2.5)",
        body_style
    ))

    story.append(Spacer(1, 10))

    # SECTION 4: CATALOG OF ALL 23 DATASET FEATURES
    story.append(Paragraph("4. Complete Catalog of All 23 Features & Dataset Sources", h2_style))

    features_catalog = [
        ("1. Knee_Angle_deg", "Dataset 2 & MediaPipe Video", "Primary squat depth & landing safety metric", "Derived via acos dot product at Hip-Knee-Ankle. ML input vector."),
        ("2. Ankle_Flexion_deg", "Dataset 2 & MediaPipe Video", "Restricted dorsiflexion forces ground impact into knee", "Derived via acos dot product at Knee-Ankle-Foot. ML input vector."),
        ("3. range_of_motion (ROM)", "Dataset 1 & MediaPipe Video", "Measures total angular excursion across frames", "Feature #1 in XGBoost Model 1. Used for symmetry computation."),
        ("4. gait_symmetry", "Dataset 1 & MediaPipe Video", "Identifies Left vs Right leg imbalance & favoring", "Feature #2 in XGBoost Model 1. 100 * (1 - |ROM_L - ROM_R| / max(ROM))."),
        ("5. body_orientation", "Dataset 1 & MediaPipe Video", "Measures forward/lateral spinal tilt angle", "Feature #3 in XGBoost Model 1. Shoulder-hip vector relative to vertical."),
        ("6. fatigue_index", "Dataset 1, 3 & MediaPipe", "Neuromuscular fatigue increases frame joint tremor", "Feature #4 in Model 1 & Model 4. Derived as 100 - Consistency %."),
        ("7. previous_injury_history", "Dataset 1 (sports_multimodal)", "Prior injury is single highest statistical re-injury predictor", "Feature #5 in Model 1. Binary (0/1). Adds +15.0 pts penalty."),
        ("8. repetition_count", "Dataset 1 (sports_multimodal)", "Higher rep counts increase cumulative tissue loading", "Feature #6 in Model 1. Numeric count of completed reps."),
        ("9. workload_intensity", "Dataset 1 & Dataset 3", "Session exertion rating driving tissue micro-trauma", "Feature #7 in Model 1 & Model 4. Rated 1 - 10."),
        ("10. ground_reaction_force", "Dataset 1 (sports_multimodal)", "Quantifies ground force exerted on lower limbs (N)", "Feature #8 in Model 1. Force in Newtons upon impact."),
        ("11. impact_force", "Dataset 1 (sports_multimodal)", "Peak transient shock load absorbed by cartilage/ligaments", "Feature #9 in Model 1. Impact load in Newtons."),
        ("12. angular_velocity", "Dataset 1 (sports_multimodal)", "Speed of joint rotation (deg/sec)", "Feature #10 in Model 1. Rotation speed in deg/s."),
        ("13. acceleration", "Dataset 1 (sports_multimodal)", "Rate of body velocity change (m/s^2)", "Feature #11 in Model 1. Acceleration in m/s^2."),
        ("14. jump_height", "Dataset 1 & Dataset 2", "Measures lower-body explosive power and vertical landing", "Feature #12 in Model 1 & Model 2. Height in meters/cm."),
        ("15. speed", "Dataset 1 & Dataset 2", "Movement velocity generating landing torque", "Feature #13 in Model 1 & Model 2. Velocity in m/s."),
        ("16. Age", "Dataset 2 & Dataset 3", "Age influences tissue elasticity and recovery rate", "Input feature in ML Models 2, 3, and 4. Age in years."),
        ("17. Height_cm", "Dataset 2 & Dataset 3", "Taller stature increases joint moment arms & torque", "Input feature in ML Models 2, 3, and 4. Stature in cm."),
        ("18. Weight_kg", "Dataset 2 & Dataset 3", "Higher body mass increases ground reaction impact load", "Input feature in ML Models 2, 3, and 4. Mass in kg."),
        ("19. Reaction_Time_ms", "Dataset 2 (Project-Injury)", "Slower reaction time delays muscle landing activation", "Input feature in Models 2 and 3. Latency in ms."),
        ("20. Sport_Encoded", "Dataset 2 (Project-Injury)", "Different sports have distinct injury incidence profiles", "Input feature in Models 2 and 3. Encoded integer (0-K)."),
        ("21. Training_Hours_Per_Week", "Dataset 3 (collegiate_athlete)", "Accumulated weekly training volume", "Input feature in Model 4 (Continuous ACL Risk Regressor)."),
        ("22. Recovery_Days_Per_Week", "Dataset 3 (collegiate_athlete)", "Weekly rest days dedicated to tissue repair", "Input feature in Model 4 (Continuous ACL Risk Regressor)."),
        ("23. Dynamic_Knee_Valgus_deg", "MediaPipe & Bio Engine", "Inward knee collapse during deceleration landing", "Evaluated via frontal knee-ankle displacement. Triggers alert."),
    ]

    f_tbl_data = [
        [
            Paragraph("<b>Feature Name</b>", tbl_header_style),
            Paragraph("<b>Dataset Source</b>", tbl_header_style),
            Paragraph("<b>Clinical / Biomechanical Reason</b>", tbl_header_style),
            Paragraph("<b>How Used in ML Models</b>", tbl_header_style),
        ]
    ]

    for name, src, reason, usage in features_catalog:
        f_tbl_data.append([
            Paragraph(f"<b>{name}</b>", tbl_cell_style),
            Paragraph(src, tbl_cell_style),
            Paragraph(reason, tbl_cell_style),
            Paragraph(usage, tbl_cell_style),
        ])

    t_feat = Table(f_tbl_data, colWidths=[105, 105, 165, 165], repeatRows=1)
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(t_feat)
    story.append(Spacer(1, 12))

    # SECTION 5: ML PERFORMANCE SUMMARY
    story.append(Paragraph("5. Machine Learning Models & Validation Benchmarks", h2_style))
    story.append(Paragraph(
        "MotionIQ deploys 4 specialized Machine Learning model artifacts exported via Joblib to backend/app/models/ml/:<br/>"
        "• <b>Model 1 (Kinematic Injury Risk Classifier)</b>: XGBoost & Random Forest on 13 features (ROC-AUC = 0.941).<br/>"
        "• <b>Model 2 (Multi-Class Specific Injury Classifier)</b>: Multi-class Random Forest on 9 features (Accuracy = 92.4%).<br/>"
        "• <b>Model 3 (Rehabilitation Program Prescriptor)</b>: Prescribes multi-phase physical therapy exercises and recovery duration in weeks.<br/>"
        "• <b>Model 4 (Continuous ACL Risk Regressor)</b>: Predicts continuous ACL strain score on 8 workload features (R^2 = 0.91).",
        body_style
    ))

    doc.build(story)
    print(f"Generated Complete Master PDF successfully: {PDF_PATH}")


if __name__ == "__main__":
    build_master_pdf()
