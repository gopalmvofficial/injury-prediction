"""
generate_athlete_workflow_pdf.py

Generates a dedicated, publication-quality PDF report:
docs/MotionIQ_Athlete_Video_Upload_and_Screening_Workflow.pdf
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

PDF_PATH = os.path.join(DOCS_DIR, "MotionIQ_Athlete_Video_Upload_and_Screening_Workflow.pdf")


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
    c_primary = colors.HexColor('#1e1b4b')     # Deep Purple Indigo
    c_accent = colors.HexColor('#7c3aed')      # Vivid Purple
    c_dark = colors.HexColor('#1e293b')        # Slate Dark
    c_muted = colors.HexColor('#64748b')       # Muted Slate
    c_bg_subtle = colors.HexColor('#faf9ff')   # Soft Tint
    c_border = colors.HexColor('#ddd6fe')      # Purple Border
    c_green = colors.HexColor('#059669')

    # Styles
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
        fontSize=13,
        leading=16,
        textColor=c_accent,
        spaceBefore=14,
        spaceAfter=6
    )
    h3_style = ParagraphStyle(
        'H3Style',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
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
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    # Document Header
    story.append(Paragraph("MotionIQ: Athlete Video Upload & Screening Workflow Specification", title_style))
    story.append(Paragraph("Complete Technical Guide from Video File Upload to Computer Vision, Feature Mathematics, ML Scoring & PDF Reports", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=12))

    # Executive Overview
    story.append(Paragraph("1. Executive Workflow Summary", h2_style))
    story.append(Paragraph(
        "MotionIQ provides a sensorless, non-invasive biomechanical movement screening platform. "
        "Athletes or coaches upload optical video recordings of movement exercises (such as squats, vertical jumps, or cutting drills), "
        "which are automatically converted into 3D skeletal trajectories, evaluated mathematically for kinematic risk deviations, "
        "and scored by Machine Learning classifiers to prevent injuries before they occur.",
        body_style
    ))

    # Phase Breakdown
    story.append(Paragraph("2. Detailed 5-Phase End-to-End Processing Architecture", h2_style))

    phases = [
        ("Phase 1: Athlete Ingestion & Video Upload",
         "The athlete selects their profile (Name, Sport, Position, Height, Weight, Injury History) and uploads a movement video file (.mp4, .mov) or starts live webcam capture. "
         "The system pre-validates video frame rate (target 60 FPS), aspect ratio, and lighting integrity."),

        ("Phase 2: Computer Vision & Skeletal Pose Tracking",
         "OpenCV ingests the video and extracts RGB frames. Google MediaPipe Pose tracks 33 3D skeletal landmarks per frame: P = (x, y, z, visibility). "
         "Normalized spatial coordinates are converted into sequential landmark time-series data."),

        ("Phase 3: Mathematical Feature Derivation Engine", "The engine computes mathematical joint angles using vector dot-products: acos((BA . BC) / (|BA|*|BC|)). "
         "It derives Range of Motion (ROM), Left/Right Bilateral Limb Symmetry %, Spinal Trunk Lean Angle, and Kinematic Fatigue Index."),

        ("Phase 4: Machine Learning Inference & Multi-Class Scoring",
         "Features are compiled into a 13-dimensional input vector X_input passed to trained XGBoost & Random Forest Ensembles. "
         "The model evaluates Injury Risk % (0-100), classifies Risk Level (LOW, MODERATE, HIGH, CRITICAL), and identifies specific injury categories (ACL, Ankle, Knee)."),

        ("Phase 5: Output Generation, Rehabilitation & Dashboard UI",
         "Generates a downloadable clinical PDF report, prescribes multi-phase corrective physical therapy exercises, "
         "updates the interactive 3D Skeletal Canvas, populates the Biomechanical Body Heatmap, and triggers AI Voice Briefings."),
    ]

    for title, desc in phases:
        story.append(Paragraph(f"<b>{title}</b>", h3_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # Phase Table
    story.append(Paragraph("3. Summary Table: Inputs, Actions & Outputs per Processing Phase", h2_style))

    phase_table_data = [
        [
            Paragraph("<b>Workflow Phase</b>", tbl_header_style),
            Paragraph("<b>Input Data</b>", tbl_header_style),
            Paragraph("<b>System Action & Algorithms</b>", tbl_header_style),
            Paragraph("<b>Generated Output</b>", tbl_header_style),
        ],
        [
            Paragraph("<b>1. Athlete Upload</b>", tbl_cell_style),
            Paragraph("Raw Video File (.mp4) + Profile Metadata", tbl_cell_style),
            Paragraph("Client-side validation & REST API POST /api/videos/upload", tbl_cell_style),
            Paragraph("Uploaded video stored in temp server buffer", tbl_cell_style),
        ],
        [
            Paragraph("<b>2. Pose Tracking</b>", tbl_cell_style),
            Paragraph("Raw RGB Video Frames", tbl_cell_style),
            Paragraph("OpenCV frame extraction + MediaPipe 33 landmark tracking", tbl_cell_style),
            Paragraph("Time-series keypoint coordinates: P(x, y, z, vis)", tbl_cell_style),
        ],
        [
            Paragraph("<b>3. Feature Derivation</b>", tbl_cell_style),
            Paragraph("Landmark time-series data", tbl_cell_style),
            Paragraph("Vector dot-product angles, ROM, Symmetry %, Trunk Lean, Fatigue Index", tbl_cell_style),
            Paragraph("Kinematic metric dictionary (Angles, ROM, Symmetry)", tbl_cell_style),
        ],
        [
            Paragraph("<b>4. ML Scoring</b>", tbl_cell_style),
            Paragraph("13D Feature Vector X_input", tbl_cell_style),
            Paragraph("Supervised XGBoost & Random Forest Inference", tbl_cell_style),
            Paragraph("Injury Risk Score % + Specific Category Predictions", tbl_cell_style),
        ],
        [
            Paragraph("<b>5. Output & Report</b>", tbl_cell_style),
            Paragraph("ML Predictions + Biomechanics", tbl_cell_style),
            Paragraph("PDF generator + Exercise prescriptor + UI socket update", tbl_cell_style),
            Paragraph("Downloadable Clinical PDF + 3D Skeletal Canvas + AI Voice", tbl_cell_style),
        ],
    ]

    col_widths = [110, 120, 160, 150]
    table = Table(phase_table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 14))

    # Concrete Squat Example
    story.append(Paragraph("4. Concrete Numerical Example: Bilateral Squat Screening", h2_style))
    story.append(Paragraph(
        "<b>Example Input</b>: Athlete performs a 3-second bilateral squat (180 frames @ 60 FPS).<br/>"
        "• <b>Frame 90 (Peak Flexion)</b>: Left Knee Angle = 78.5 deg | Right Knee Angle = 94.2 deg.<br/>"
        "• <b>Range of Motion</b>: Left ROM = 93.5 deg | Right ROM = 75.8 deg.<br/>"
        "• <b>Calculated Symmetry Score</b>: 100 * (1 - |93.5 - 75.8| / 93.5) = <b>81.1% (18.9% Asymmetry Deficit)</b>.<br/>"
        "• <b>Trunk Lean Angle</b>: 28.4 deg (Exceeds 25.0 deg postural limit).<br/>"
        "• <b>Fatigue Index</b>: 31.5 pts (Exceeds 25.0 pts consistency threshold).<br/>"
        "• <b>ML XGBoost Score</b>: <b>78.4% (HIGH RISK)</b>.<br/>"
        "• <b>Prescription Output</b>: Single-Leg Eccentric Squats (3x10), Gluteus Medius Band Walks (4x15), Nordic Hamstring Curls (3x8).",
        body_style
    ))

    doc.build(story)
    print(f"Generated Workflow PDF successfully: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
