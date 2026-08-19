"""
generate_docs_pdf.py

Generates two comprehensive, professional PDF documents:
1. docs/Sports_Injury_Risk_Detection_Flowchart.pdf
2. docs/Sports_Injury_System_Architecture_and_AI_Roadmap.pdf
"""
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
FLOWCHART_IMG = os.path.join(DOCS_DIR, "system_flowchart.jpg")
os.makedirs(DOCS_DIR, exist_ok=True)

def generate_flowchart_pdf():
    pdf_path = os.path.join(DOCS_DIR, "Sports_Injury_Risk_Detection_Flowchart.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f2942'),
        alignment=1,
        spaceAfter=10
    )
    
    story.append(Paragraph("SPORTS INJURY RISK DETECTION AND PREVENTION SYSTEM", title_style))
    story.append(Paragraph("<font color='#0f766e' size=11><b>End-to-End System Workflow Diagram (Milestone 2 & AI Roadmap)</b></font>", ParagraphStyle('Sub', alignment=1, spaceAfter=12)))
    
    if os.path.exists(FLOWCHART_IMG):
        img = Image(FLOWCHART_IMG, width=740, height=415)
        story.append(img)
    
    doc.build(story)
    print(f"Generated: {pdf_path}")


def generate_architecture_pdf():
    pdf_path = os.path.join(DOCS_DIR, "Sports_Injury_System_Architecture_and_AI_Roadmap.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor('#0f2942')
    c_accent = colors.HexColor('#0f766e')
    c_dark = colors.HexColor('#1e293b')
    c_muted = colors.HexColor('#64748b')
    c_bg_light = colors.HexColor('#f8fafc')
    c_border = colors.HexColor('#cbd5e1')

    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=c_primary, spaceAfter=4)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=c_accent, spaceBefore=12, spaceAfter=6)
    h3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_primary, spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, spaceAfter=5)
    bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=8.5, leading=12, textColor=c_dark, leftIndent=10, spaceAfter=2)
    
    # Header
    story.append(Paragraph("Sports Injury Risk Detection and Prevention System", h1))
    story.append(Paragraph("<b>Comprehensive Technical Architecture, Cloud Hosting, Detailed Workflow & AI Roadmap</b>", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=10.5, textColor=c_accent, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=10))
    
    # 1. Executive Summary
    story.append(Paragraph("1. Executive Overview & Problem Statement", h2))
    story.append(Paragraph(
        "Non-contact sports injuries (such as ACL ruptures, meniscus tears, and lower back strains) are predominantly caused by "
        "biomechanical movement flaws (e.g., knee valgus collapse, severe bilateral asymmetry, and excessive trunk lean). "
        "The <b>Sports Injury Risk Detection System</b> is a sensorless screening platform that transforms standard video "
        "into quantifiable 3D kinematic joint coordinates, predicts injury risk probability, and prescribes targeted corrective exercises.",
        body
    ))
    
    # 2. Visual Flowchart Infographic
    story.append(Paragraph("2. System Workflow Infographic", h2))
    if os.path.exists(FLOWCHART_IMG):
        story.append(Image(FLOWCHART_IMG, width=540, height=303))
        story.append(Spacer(1, 8))
    
    story.append(PageBreak())
    
    # 3. Complete Tech Stack Table
    story.append(Paragraph("3. Technical Stack Matrix", h2))
    
    stack_data = [
        [Paragraph("<b>Component</b>", body), Paragraph("<b>Technology</b>", body), Paragraph("<b>Role & Technical Function</b>", body)],
        [Paragraph("<b>Frontend UI</b>", body), Paragraph("React.js 18 + Vite", body), Paragraph("Modular Single Page Application (SPA) dashboard, athlete records & video upload interface.", body)],
        [Paragraph("<b>Web Server</b>", body), Paragraph("Nginx (Alpine)", body), Paragraph("High-concurrency static asset server (~15MB RAM), SPA fallback routing (`try_files`), gzip compression.", body)],
        [Paragraph("<b>Backend API</b>", body), Paragraph("FastAPI + Uvicorn", body), Paragraph("Asynchronous REST API, native OpenAPI Swagger UI (`/docs`), automated Pydantic schema validation.", body)],
        [Paragraph("<b>Pose Tracking AI</b>", body), Paragraph("Google MediaPipe", body), Paragraph("Deep learning neural network tracking 33 3D skeletal landmarks per frame with sub-pixel precision.", body)],
        [Paragraph("<b>Video Processing</b>", body), Paragraph("OpenCV (`cv2`)", body), Paragraph("Frame decoding, frame sampling rate standardization, visual stick-figure skeletal overlays.", body)],
        [Paragraph("<b>Kinematics Math</b>", body), Paragraph("NumPy & Pandas", body), Paragraph("Vector trigonometry, joint angle computation, time-series landmark DataFrames.", body)],
        [Paragraph("<b>Persistence Layer</b>", body), Paragraph("SQLAlchemy + SQLite", body), Paragraph("Relational storage for user auth, athlete profiles, video metadata, and risk records.", body)],
        [Paragraph("<b>Report Generator</b>", body), Paragraph("ReportLab", body), Paragraph("Automated compilation of styled clinical PDF reports with observations and recommendations.", body)],
        [Paragraph("<b>Containerization</b>", body), Paragraph("Docker & Compose", body), Paragraph("Multi-container isolation with persistent storage volumes (`uploads`, `results`, `data`).", body)],
    ]
    
    t_stack = Table(stack_data, colWidths=[105, 110, 325])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))
    
    # 4. Cloud Hosting Guide
    story.append(Paragraph("4. Cloud Hosting & Production Deployment Architecture", h2))
    
    cloud_data = [
        [Paragraph("<b>Platform</b>", body), Paragraph("<b>Component</b>", body), Paragraph("<b>Scalability & Benefits</b>", body)],
        [Paragraph("<b>Vercel</b>", body), Paragraph("Frontend (React UI)", body), Paragraph("Global Edge CDN, automated GitHub CI/CD, zero-maintenance static serving.", body)],
        [Paragraph("<b>Render</b>", body), Paragraph("Backend (FastAPI)", body), Paragraph("Docker container web service, persistent disk storage for videos, automated SSL.", body)],
        [Paragraph("<b>Railway</b>", body), Paragraph("Full Stack Stack", body), Paragraph("One-click multi-container deployment with internal Docker networking.", body)],
        [Paragraph("<b>AWS / GCP / VPS</b>", body), Paragraph("Docker Compose", body), Paragraph("Single-command production deployment (`docker compose up -d`) with full data privacy.", body)],
    ]
    t_cloud = Table(cloud_data, colWidths=[90, 120, 330])
    t_cloud.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(t_cloud)
    
    story.append(PageBreak())
    
    # 5. Detailed Step by Step Workflow
    story.append(Paragraph("5. Detailed Step-by-Step User & Data Processing Workflow", h2))
    
    phases = [
        ("Phase 1: User Registration & Session Security", "Coaches/physios create an account or sign in. Passwords are encrypted with SHA-256 and unique salts. A secure UUID session token is generated in SQLite and attached as <code>Authorization: Bearer &lt;token&gt;</code> to all subsequent API requests."),
        ("Phase 2: Athlete Profile & Baseline Recording", "User registers athlete demographic data: Full Name, Sport, Age, Height (cm), Weight (kg), and Prior Injury History. This provides historical context for kinetic load calculations."),
        ("Phase 3: Video Ingestion & Validation", "User selects the athlete, chooses activity (Squat, Running, Jumping/Landing), and uploads video (MP4/MOV). Backend validates MIME types, headers, generates a collision-free UUID, and writes to <code>/app/uploads/</code>."),
        ("Phase 4: AI Computer Vision & Pose Tracking", "OpenCV decodes frames; Google MediaPipe deep neural network extracts <b>33 3D coordinates</b> $(x,y,z)$ per frame. An annotated video with drawn skeletal landmarks is saved to <code>/app/results/</code>."),
        ("Phase 5: Biomechanical Kinematic Calculations", "Vector trigonometry computes Knee & Hip Range of Motion (ROM), Bilateral Symmetry Deficit % (comparing left vs right leg loading), Trunk Lean Angle, and Movement Consistency across repetitions."),
        ("Phase 6: Injury Risk Prediction & Clinical Scoring", "A composite weighted model computes a 0-100% Risk Score classified into <b>LOW RISK (0-33%)</b>, <b>MEDIUM RISK (34-66%)</b>, or <b>HIGH RISK (67-100%)</b>, identifying specific flaws like knee valgus or trunk shear."),
        ("Phase 7: Dashboard Analytics & PDF Report Export", "Results populate the live dashboard in real-time. A formal medical PDF report with charts, observations, and targeted corrective exercises is compiled via ReportLab for download.")
    ]
    
    for p_title, p_desc in phases:
        story.append(Paragraph(f"<b>{p_title}</b>", h3))
        story.append(Paragraph(p_desc, body))
        story.append(Spacer(1, 2))
    
    story.append(PageBreak())
    
    # 6. System Statistics
    story.append(Paragraph("6. Key System Benchmarks & Technical Metrics", h2))
    
    stats_data = [
        [Paragraph("<b>Metric / Benchmark</b>", body), Paragraph("<b>Performance Value</b>", body), Paragraph("<b>Description</b>", body)],
        [Paragraph("<b>Pose Keypoints</b>", body), Paragraph("33 3D Landmarks", body), Paragraph("Full-body tracking: shoulders, elbows, wrists, hips, knees, ankles, heels, toes.", body)],
        [Paragraph("<b>Processing Speed</b>", body), Paragraph("25 – 45 FPS (CPU)", body), Paragraph("Real-time / near-real-time CPU execution without requiring dedicated GPUs.", body)],
        [Paragraph("<b>Resolution Support</b>", body), Paragraph("720p / 1080p / 4K", body), Paragraph("Standardized scaling during OpenCV decoding pipeline.", body)],
        [Paragraph("<b>API Latency</b>", body), Paragraph("< 45 ms (CRUD)", body), Paragraph("Asynchronous non-blocking endpoints via FastAPI.", body)],
        [Paragraph("<b>Supported Formats</b>", body), Paragraph("MP4, MOV, AVI, WebM", body), Paragraph("Cross-platform desktop and mobile video compatibility.", body)],
    ]
    t_stats = Table(stats_data, colWidths=[120, 110, 310])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 10))
    
    # 7. Future AI Roadmap
    story.append(Paragraph("7. Future AI/ML Roadmap: Supervised Injury Prediction (Milestone 3)", h2))
    story.append(Paragraph(
        "In Milestone 3, the rule-based risk evaluation will be upgraded to a <b>Supervised Machine Learning & Deep Learning model</b>. "
        "The Milestone 2 feature extraction pipeline directly supplies the exact numerical vectors needed for ML training:",
        body
    ))
    
    story.append(Paragraph("<b>A. Machine Learning Feature Vector:</b>", h3))
    story.append(Paragraph("• <code>Knee Symmetry Deficit (%)</code>: Left vs right knee angle deviation during impact", bullet))
    story.append(Paragraph("• <code>Hip Symmetry Deficit (%)</code>: Pelvic tilt and bilateral hip displacement", bullet))
    story.append(Paragraph("• <code>Max Trunk Lean Angle (°)</code>: Correlates with spinal shear stress and core fatigue", bullet))
    story.append(Paragraph("• <code>Movement Quality Score (0-100)</code>: Composite score of joint coordination", bullet))
    story.append(Paragraph("• <code>Athlete Baseline (Age, Weight, Sport)</code>: Physical demographics and body levers", bullet))
    story.append(Paragraph("• <code>Reported Injury History (0 or 1)</code>: Historical risk factor weighting", bullet))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>B. Recommended AI Frameworks:</b>", h3))
    story.append(Paragraph("1. <b>Tabular Machine Learning (XGBoost / LightGBM / Random Forest):</b> High accuracy, low latency, and robust interpretability for vector-based injury prediction.", body))
    story.append(Paragraph("2. <b>Temporal Deep Learning (PyTorch LSTM / 1D-CNN):</b> Directly models raw time-series joint angle sequences over the full duration of athletic jumps and sprints.", body))
    story.append(Paragraph("3. <b>Explainable AI (SHAP / LIME):</b> Quantifies exactly why an athlete was flagged (e.g. <i>'+35% risk attributed to 24° left knee valgus collapse'</i>).", body))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>C. Model Integration:</b>", h3))
    story.append(Paragraph(
        "The trained model (<code>injury_model.pkl</code>) will be stored in <code>backend/app/models/</code> and loaded once on startup. "
        "The existing <code>compute_risk()</code> function will call <code>model.predict_proba()</code> seamlessly with zero breaking changes to frontend consumers.",
        body
    ))
    
    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    generate_flowchart_pdf()
    generate_architecture_pdf()
