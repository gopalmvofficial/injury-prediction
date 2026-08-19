"""
generate_docs_pdf.py

Generates two professional PDF documents:
1. docs/Sports_Injury_Risk_Detection_Flowchart.pdf
2. docs/Sports_Injury_System_Architecture_and_AI_Roadmap.pdf
"""
import os
from reportlab.lib.pagesizes import letter, landscape, A4
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
        # Landscape letter is 792 x 612 pts. Usable width ~ 750 pts.
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
    
    # Custom Palette
    c_primary = colors.HexColor('#0f2942')
    c_accent = colors.HexColor('#0f766e')
    c_dark = colors.HexColor('#1e293b')
    c_muted = colors.HexColor('#64748b')
    c_bg_light = colors.HexColor('#f8fafc')
    c_border = colors.HexColor('#e2e8f0')

    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=c_primary, spaceAfter=6)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=c_accent, spaceBefore=14, spaceAfter=8)
    h3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=c_primary, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=c_dark, spaceAfter=6)
    bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, leftIndent=12, spaceAfter=3)
    code = ParagraphStyle('Code', fontName='Courier', fontSize=8, leading=11, textColor=colors.HexColor('#0f766e'))
    
    # Title & Header
    story.append(Paragraph("Sports Injury Risk Detection and Prevention System", h1))
    story.append(Paragraph("<b>Comprehensive Technical Architecture, Workflow & Future AI/ML Roadmap</b>", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11, textColor=c_accent, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=14))
    
    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h2))
    story.append(Paragraph(
        "The <b>Sports Injury Risk Detection and Prevention System</b> is a non-invasive athletic screening platform that utilizes "
        "computer vision (MediaPipe & OpenCV) and biomechanical kinematics to analyze human movement patterns from video. "
        "It calculates joint angles, Range of Motion (ROM), and bilateral asymmetries to identify high-risk movement flaws "
        "(such as knee valgus collapse or excessive spinal lean) and deliver preventive exercise recommendations before non-contact injuries occur.",
        body
    ))
    
    # Visual Flowchart
    story.append(Paragraph("2. System Workflow Infographic", h2))
    if os.path.exists(FLOWCHART_IMG):
        story.append(Image(FLOWCHART_IMG, width=540, height=303))
        story.append(Spacer(1, 10))
    
    story.append(PageBreak())
    
    # Tech Stack Table
    story.append(Paragraph("3. Technical Stack Breakdown", h2))
    
    table_data = [
        [Paragraph("<b>Component Layer</b>", body), Paragraph("<b>Technology</b>", body), Paragraph("<b>Role & Responsibility</b>", body)],
        [Paragraph("<b>Frontend UI</b>", body), Paragraph("React.js 18 + Vite", body), Paragraph("Single Page Application (SPA) dashboard, athlete records & video upload interface.", body)],
        [Paragraph("<b>Web Server</b>", body), Paragraph("Nginx (Alpine)", body), Paragraph("High-performance static asset server with SPA routing (`try_files`) & API reverse proxy.", body)],
        [Paragraph("<b>Backend API</b>", body), Paragraph("FastAPI + Uvicorn", body), Paragraph("Asynchronous REST API, Pydantic data validation, and Swagger OpenAPI docs.", body)],
        [Paragraph("<b>Pose Tracking AI</b>", body), Paragraph("Google MediaPipe", body), Paragraph("Deep learning neural network extracting 33 3D skeletal landmarks per frame.", body)],
        [Paragraph("<b>Video Processing</b>", body), Paragraph("OpenCV (`cv2`)", body), Paragraph("Video decoding, frame sampling, visual skeleton overlay rendering.", body)],
        [Paragraph("<b>Kinematics Math</b>", body), Paragraph("NumPy & Pandas", body), Paragraph("3D vector trigonometry, joint angle computation, time-series landmark DataFrames.", body)],
        [Paragraph("<b>Persistence Layer</b>", body), Paragraph("SQLAlchemy + SQLite", body), Paragraph("Relational storage for user auth, athletes, movement data, and risk records.", body)],
        [Paragraph("<b>Report Generator</b>", body), Paragraph("ReportLab", body), Paragraph("Automated compilation of clinical PDF reports with observations and recommendations.", body)],
        [Paragraph("<b>Containerization</b>", body), Paragraph("Docker & Compose", body), Paragraph("Multi-container isolation with persistent storage volumes and health checks.", body)],
    ]
    
    t = Table(table_data, colWidths=[110, 110, 320])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    
    # End to End Workflow
    story.append(Paragraph("4. End-to-End Data Processing Pipeline", h2))
    
    steps = [
        ("Step 1: User Authentication", "Coaches/physios authenticate via <code>POST /api/auth/register</code> and <code>/login</code>. A secure session token is generated and attached as <code>Authorization: Bearer &lt;token&gt;</code> to all subsequent requests."),
        ("Step 2: Athlete Profile Management", "Athletic baseline metrics (Age, Weight, Height, Sport, and Prior Injury History) are collected and saved in SQLite to provide context for kinematic evaluation."),
        ("Step 3: Video Ingestion & Validation", "Action videos (MP4/MOV) are uploaded to <code>/app/uploads</code> with automated format, size, and header verification."),
        ("Step 4: MediaPipe 33-Landmark Pose Estimation", "OpenCV decodes video frames; MediaPipe tracks 33 3D coordinates $(x,y,z)$ per frame. An annotated video with skeletal overlays is rendered and saved to <code>/app/results/</code>."),
        ("Step 5: Kinematic Joint Calculations", "Vector math computes Knee/Hip Range of Motion (ROM), Bilateral Asymmetry % (comparing left vs right leg loading), Trunk Lean Angle, and Movement Consistency across repetitions."),
        ("Step 6: Injury Risk Prediction & Reporting", "Calculates a 0-100% Risk Score classified as <b>LOW</b>, <b>MEDIUM</b>, or <b>HIGH</b>, generates targeted corrective exercises, and compiles an exportable PDF report.")
    ]
    
    for s_title, s_desc in steps:
        story.append(Paragraph(f"<b>{s_title}</b>", h3))
        story.append(Paragraph(s_desc, body))
    
    story.append(PageBreak())
    
    # Milestone 3 AI Roadmap
    story.append(Paragraph("5. Future AI/ML Roadmap (Milestone 3)", h2))
    story.append(Paragraph(
        "In Milestone 3, the rule-based risk evaluation will be upgraded to a <b>Supervised Machine Learning & Deep Learning model</b>. "
        "The Milestone 2 feature extraction pipeline directly supplies the exact numerical features needed for ML training:",
        body
    ))
    
    story.append(Paragraph("<b>A. Machine Learning Feature Vector:</b>", h3))
    story.append(Paragraph("• <code>Knee Symmetry Deficit (%)</code>: Left vs right knee angle deviation", bullet))
    story.append(Paragraph("• <code>Hip Symmetry Deficit (%)</code>: Pelvic tilt and bilateral hip displacement", bullet))
    story.append(Paragraph("• <code>Max Trunk Lean Angle (°)</code>: Correlates with spinal shear stress and core fatigue", bullet))
    story.append(Paragraph("• <code>Movement Quality Score (0-100)</code>: Composite score of joint coordination", bullet))
    story.append(Paragraph("• <code>Athlete Baseline (Age, Weight, Sport)</code>: Physical demographics", bullet))
    story.append(Paragraph("• <code>Reported Injury History (0 or 1)</code>: Historical risk weighting", bullet))
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>B. Recommended AI Frameworks & Architecture:</b>", h3))
    story.append(Paragraph("1. <b>Tabular Classification (XGBoost / Random Forest / LightGBM):</b> High accuracy and interpretability for vector-based injury classification.", body))
    story.append(Paragraph("2. <b>Temporal Deep Learning (PyTorch LSTM / 1D-CNN):</b> Directly models full sequence kinematics over the entire duration of a jump or sprint.", body))
    story.append(Paragraph("3. <b>Model Explainability (SHAP / LIME):</b> Quantifies exactly why a risk score was assigned (e.g. <i>'+35% risk attributed to 22° left knee valgus collapse'</i>).", body))
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>C. Model Integration Architecture:</b>", h3))
    story.append(Paragraph(
        "The model file (e.g., <code>injury_model.pkl</code> or <code>.onnx</code>) is placed in <code>backend/app/models/</code> and loaded on server startup. "
        "The existing <code>compute_risk()</code> function calls <code>model.predict_proba()</code> seamlessly with zero breaking changes to frontend consumers.",
        body
    ))
    
    story.append(Spacer(1, 14))
    story.append(Paragraph("6. Docker Deployment Architecture", h2))
    story.append(Paragraph(
        "The entire system is orchestratable via <code>docker compose up --build</code>. "
        "The frontend (Nginx on Port 5173/80) and backend (FastAPI on Port 8000) run in isolated containers connected via an internal Docker bridge network. "
        "Named volumes (<code>sports_injury_backend_data</code>, <code>uploads</code>, and <code>results</code>) guarantee persistent SQLite databases and video files across container lifecycles.",
        body
    ))
    
    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    generate_flowchart_pdf()
    generate_architecture_pdf()
