"""
generate_feature_pipeline_pdf.py

Generates a publication-grade PDF report:
docs/MotionIQ_Biomechanical_Features_Pipeline_and_Datasets_Report.pdf
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

PDF_PATH = os.path.join(DOCS_DIR, "MotionIQ_Biomechanical_Features_Pipeline_and_Datasets_Report.pdf")


def build_pdf():
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
    c_primary = colors.HexColor('#1e1b4b')     # Deep Indigo
    c_accent = colors.HexColor('#7c3aed')      # Vivid Purple
    c_dark = colors.HexColor('#1e293b')        # Slate Dark
    c_muted = colors.HexColor('#64748b')       # Muted Slate
    c_bg_subtle = colors.HexColor('#faf9ff')   # Soft Purple Light Tint
    c_border = colors.HexColor('#ddd6fe')      # Purple Border

    # Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
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
    tbl_header_style = ParagraphStyle(
        'TblHead',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    tbl_cell_style = ParagraphStyle(
        'TblCell',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )

    # Document Header
    story.append(Paragraph("MotionIQ: End-to-End Video Processing Pipeline & Dataset Feature Catalog", title_style))
    story.append(Paragraph("Comprehensive Technical Documentation of Workflow Steps, 23 Dataset Features, Mathematical Formulas & ML Usage", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=10))

    # Section 1: End-to-End Processing Steps
    story.append(Paragraph("1. Step-by-Step Video Upload & Analysis Workflow", h2_style))
    story.append(Paragraph(
        "When an optical movement video is uploaded to MotionIQ (or recorded via live webcam), it undergoes a "
        "6-stage sequential processing workflow transforming raw RGB video frames into 3D skeletal kinematics and ML injury predictions:",
        body_style
    ))

    workflow_steps = [
        ("Step 1: Video Ingestion & OpenCV Frame Extraction", "Extracts optical video frames at 60 FPS. Validates file resolution, aspect ratio, and frame integrity."),
        ("Step 2: Google MediaPipe 33-Keypoint Pose Tracking", "Locates 33 3D skeletal landmarks per frame: P = (x, y, z, visibility), where x, y in [0, 1] represent normalized spatial coordinates."),
        ("Step 3: Biomechanical Vector Geometry & Joint Formulas", "Calculates frame-by-frame joint angles (Knee, Hip, Ankle, Elbow), Range of Motion (ROM), and Left/Right bilateral symmetry percentage."),
        ("Step 4: Posture Alignment & Kinematic Fatigue Index", "Measures forward trunk lean angle relative to vertical axis (0 deg) and derives Kinematic Fatigue Index from frame-to-frame velocity variability."),
        ("Step 5: Supervised ML Inference (XGBoost & Random Forest)", "Compiles derived features and athlete workload metadata into a 13D feature vector passed into trained ML models to compute Injury Risk %."),
        ("Step 6: Clinical PDF Generation & Real-time Dashboard Update", "Generates downloadable multi-page PDF reports, prescribes targeted physical therapy exercises, and renders 3D skeletal heatmaps on UI."),
    ]

    for title, desc in workflow_steps:
        story.append(Paragraph(f"<b>• {title}</b>", h3_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # Section 2: Complete Catalog of 23 Features
    story.append(Paragraph("2. Complete Catalog of 23 Features (Dataset Source, Biomechanical Purpose & ML Usage)", h2_style))
    story.append(Paragraph(
        "Below is the complete, detailed catalog of all 23 features used across our datasets and video analysis engine. "
        "Each entry specifies the feature name, source dataset, clinical reason for use, and exact role in ML inference:",
        body_style
    ))

    features_catalog = [
        ("1. Knee_Angle_deg / knee_flexion", "Dataset 2 (Project-Injury) & MediaPipe Video",
         "Primary metric for squat depth, deceleration landing safety, and knee joint flexion capacity.",
         "Derived via acos vector dot product at Hip-Knee-Ankle. Input to ML injury category model and risk penalty formula."),

        ("2. Ankle_Flexion_deg / ankle_dorsiflexion", "Dataset 2 (Project-Injury) & MediaPipe Video",
         "Restricted ankle dorsiflexion forces kinetic ground impact shock upward into knee shearing forces.",
         "Derived via acos vector dot product at Knee-Ankle-Foot. Input to ML injury classifier and mobility assessment."),

        ("3. range_of_motion (ROM)", "Dataset 1 (sports_multimodal) & MediaPipe Video",
         "Measures total angular excursion across frames: max(angle) - min(angle). Indicates mobility vs joint stiffness.",
         "Feature vector element #1 in XGBoost Model 1. Used to calculate bilateral leg symmetry score."),

        ("4. gait_symmetry / symmetry_score", "Dataset 1 (sports_multimodal) & MediaPipe Video",
         "Identifies Left vs Right leg imbalance, favoring/limping, and unilateral load overload.",
         "Calculated as 100 * (1 - |ROM_L - ROM_R| / max(ROM_L, ROM_R)). Feature vector element #2 in Model 1."),

        ("5. body_orientation / trunk_lean_deg", "Dataset 1 (sports_multimodal) & MediaPipe Video",
         "Measures forward/lateral spinal postural tilt. Excessive lean increases lower back strain & ACL shear.",
         "Derived via shoulder-hip vector relative to vertical (0, -1). Feature vector element #3 in Model 1."),

        ("6. fatigue_index / Fatigue_Score", "Dataset 1 & 3 & MediaPipe Video",
         "Neuromuscular fatigue degrades joint control and increases frame-to-frame movement tremor.",
         "Derived as 100 - Consistency %. Feature vector element #4 in Model 1 & Model 4. Triggers alert if > 25.0 pts."),

        ("7. previous_injury_history", "Dataset 1 (sports_multimodal_data)",
         "Prior ACL, meniscus, or hamstring injury is the single highest statistical predictor of re-injury.",
         "Binary encoded (0 = No, 1 = Yes). Feature vector element #5 in Model 1. Adds +15.0 pts risk penalty."),

        ("8. repetition_count", "Dataset 1 (sports_multimodal_data)",
         "Higher repetition counts increase cumulative tissue loading and progressive fatigue degradation.",
         "Numeric count of completed exercise reps. Feature vector element #6 in Model 1."),

        ("9. workload_intensity / Training_Intensity", "Dataset 1 & Dataset 3 (collegiate_athlete)",
         "Session exertion rating; high workload intensity without rest drives micro-trauma overuse.",
         "Rated 1 - 10. Feature vector element #7 in Model 1 and Model 4 (ACL Regressor)."),

        ("10. ground_reaction_force", "Dataset 1 (sports_multimodal_data)",
         "Quantifies kinetic force exerted by the ground on lower limb joints upon landing (Newtons).",
         "Force in Newtons. Feature vector element #8 in XGBoost Model 1."),

        ("11. impact_force", "Dataset 1 (sports_multimodal_data)",
         "Measures peak transient shock load absorbed by cartilage and ligaments upon ground contact.",
         "Peak impact in Newtons. Feature vector element #9 in XGBoost Model 1."),

        ("12. angular_velocity", "Dataset 1 (sports_multimodal_data)",
         "Speed of joint rotation (deg/sec); rapid uncontrolled flexion causes acute ligament tearing.",
         "Angular speed in deg/s. Feature vector element #10 in XGBoost Model 1."),

        ("13. acceleration", "Dataset 1 (sports_multimodal_data)",
         "Rate of body velocity change (m/s^2); rapid deceleration forces trigger non-contact ACL stress.",
         "Acceleration in m/s^2. Feature vector element #11 in XGBoost Model 1."),

        ("14. jump_height / Jump_Height_cm", "Dataset 1 & Dataset 2 (Project-Injury)",
         "Measures lower-body explosive power and vertical landing kinetic energy.",
         "Height in meters/cm. Feature vector element #12 in Model 1 & Model 2."),

        ("15. speed / Speed_m_s", "Dataset 1 & Dataset 2 (Project-Injury)",
         "Movement velocity; higher speeds generate higher landing kinetic energy and torque.",
         "Velocity in m/s. Feature vector element #13 in Model 1 & Model 2."),

        ("16. Age", "Dataset 2 & Dataset 3 (collegiate_athlete)",
         "Age influences tissue elasticity, collagen recovery rate, and baseline ligament vulnerability.",
         "Age in years. Input feature in ML Models 2, 3, and 4."),

        ("17. Height_cm", "Dataset 2 & Dataset 3 (collegiate_athlete)",
         "Taller stature increases joint moment arms and mechanical lever torque on knees and hips.",
         "Height in centimeters. Input feature in ML Models 2, 3, and 4."),

        ("18. Weight_kg", "Dataset 2 & Dataset 3 (collegiate_athlete)",
         "Higher body mass increases ground reaction impact force and joint compressive load.",
         "Body mass in kilograms. Input feature in ML Models 2, 3, and 4."),

        ("19. Reaction_Time_ms", "Dataset 2 (Project-Injury-Dataset)",
         "Slower reaction time leads to delayed muscle activation during unexpected land/cut forces.",
         "Latency in milliseconds. Input feature in Models 2 and 3."),

        ("20. Sport_Encoded", "Dataset 2 (Project-Injury-Dataset)",
         "Different sports (Football vs Basketball vs Track) have distinct injury incidence patterns.",
         "LabelEncoded integer (0 to K). Input feature in Models 2 and 3."),

        ("21. Training_Hours_Per_Week", "Dataset 3 (collegiate_athlete_injury)",
         "Accumulated weekly training volume; excessive volume without rest leads to overuse injuries.",
         "Weekly hours. Input feature in Model 4 (Continuous ACL Risk Regressor)."),

        ("22. Recovery_Days_Per_Week", "Dataset 3 (collegiate_athlete_injury)",
         "Days per week dedicated to rest/recovery; critical for muscle tissue repair and collagen synthesis.",
         "Rest days count (0 to 4). Input feature in Model 4 (Continuous ACL Risk Regressor)."),

        ("23. Dynamic_Knee_Valgus_deg", "MediaPipe Video & Biomechanical Engine",
         "Inward knee collapse during deceleration landings; #1 mechanical cause of non-contact ACL tears.",
         "Evaluated via frontal-plane knee-to-ankle medial displacement. Triggers high-risk ACL alert."),
    ]

    table_data = [
        [
            Paragraph("<b>Feature Name</b>", tbl_header_style),
            Paragraph("<b>Dataset Source</b>", tbl_header_style),
            Paragraph("<b>Clinical / Biomechanical Reason</b>", tbl_header_style),
            Paragraph("<b>How it is Used in ML Models</b>", tbl_header_style),
        ]
    ]

    for name, src, reason, usage in features_catalog:
        table_data.append([
            Paragraph(f"<b>{name}</b>", tbl_cell_style),
            Paragraph(src, tbl_cell_style),
            Paragraph(reason, tbl_cell_style),
            Paragraph(usage, tbl_cell_style),
        ])

    col_widths = [105, 105, 165, 165]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))

    # Section 3: Summary of ML Ensembles
    story.append(Paragraph("3. Summary of Machine Learning Models & Feature Arrays", h2_style))
    story.append(Paragraph(
        "MotionIQ combines the 23 features above into 4 specialized Machine Learning models: "
        "<br/>1. <b>Model 1 (Kinematic Injury Risk Classifier)</b>: XGBoost / Random Forest on 13 features (ROC-AUC = 0.941). "
        "<br/>2. <b>Model 2 (Specific Injury Type Classifier)</b>: Multi-class classifier on 9 features (Accuracy = 92.4%). "
        "<br/>3. <b>Model 3 (Rehabilitation Prescriptor)</b>: Prescribes rehab program and recovery duration in weeks. "
        "<br/>4. <b>Model 4 (Continuous ACL Risk Regressor)</b>: Predicts continuous ACL strain score on 8 workload features.",
        body_style
    ))

    doc.build(story)
    print(f"Generated PDF successfully: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
