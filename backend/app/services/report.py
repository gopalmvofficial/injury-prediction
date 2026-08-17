"""
report.py

Generates a professional PDF biomechanics report from an analysis record
+ athlete record, using ReportLab. All content is pulled directly from the
already-computed analysis dict - nothing here invents new figures.
"""
from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)


def _fmt(value, suffix=""):
    if value is None:
        return "Not available"
    return f"{value}{suffix}"


def generate_pdf_report(athlete: dict, analysis: dict, output_path: str, risk: dict | None = None) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=18)
    heading_style = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("SPORTS INJURY MOVEMENT ANALYSIS REPORT", title_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Movement-quality assessment prototype - Infosys Springboard Milestone 2", styles["Normal"]
    ))
    story.append(Spacer(1, 0.6 * cm))

    # Athlete Information
    story.append(Paragraph("Athlete Information", heading_style))
    athlete_rows = [
        ["Athlete ID", athlete.get("athlete_id", "N/A")],
        ["Name", athlete.get("name", "N/A")],
        ["Sport", athlete.get("sport", "N/A")],
        ["Age", str(athlete.get("age", "N/A"))],
        ["Height (cm)", str(athlete.get("height_cm") or "Not provided")],
        ["Weight (kg)", str(athlete.get("weight_kg") or "Not provided")],
        ["Injury history", athlete.get("injury_history") or "None reported"],
    ]
    t = Table(athlete_rows, colWidths=[5 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)

    # Video Information
    story.append(Paragraph("Video Information", heading_style))
    video_rows = [
        ["Activity", analysis.get("activity", "N/A")],
        ["Analysis date", str(analysis.get("created_at", datetime.utcnow()))],
        ["Frames processed", str(analysis.get("frames_total", "N/A"))],
        ["Pose detection rate", _fmt(analysis.get("pose_detection_rate_pct"), "%")],
    ]
    t2 = Table(video_rows, colWidths=[5 * cm, 10 * cm])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t2)

    # Biomechanical Analysis
    story.append(Paragraph("Biomechanical Analysis", heading_style))
    bio = analysis.get("biomechanics") or {}

    def joint_row(label, key):
        j = bio.get(key, {}) or {}
        return [
            label,
            _fmt(j.get("min_angle"), "°"),
            _fmt(j.get("max_angle"), "°"),
            _fmt(j.get("range_of_motion"), "°"),
        ]

    bio_rows = [["Joint", "Min angle", "Max angle", "ROM"]]
    for label, key in [
        ("Left knee", "left_knee"), ("Right knee", "right_knee"),
        ("Left hip", "left_hip"), ("Right hip", "right_hip"),
        ("Left elbow", "left_elbow"), ("Right elbow", "right_elbow"),
    ]:
        bio_rows.append(joint_row(label, key))
    t3 = Table(bio_rows, colWidths=[4 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
    t3.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3 * cm))

    trunk = bio.get("trunk", {}) or {}
    story.append(Paragraph(
        f"Knee symmetry: {_fmt(bio.get('knee_symmetry_pct'), '%')} &nbsp;&nbsp; "
        f"Hip symmetry: {_fmt(bio.get('hip_symmetry_pct'), '%')} &nbsp;&nbsp; "
        f"Trunk lean (avg): {_fmt(trunk.get('mean_lean_angle'), '°')} &nbsp;&nbsp; "
        f"Movement consistency: {_fmt(bio.get('movement_consistency_pct'), '%')}",
        body,
    ))

    # Movement Quality
    story.append(Paragraph("Movement Quality", heading_style))
    quality = analysis.get("movement_quality") or {}
    story.append(Paragraph(
        f"<b>Score:</b> {_fmt(quality.get('score'))} / 100 &nbsp;&nbsp; "
        f"<b>Classification:</b> {quality.get('classification') or 'Not available'}",
        body,
    ))
    components = quality.get("components") or {}
    if components:
        comp_rows = [["Component", "Score"]] + [
            [k.replace("_", " ").title(), _fmt(v)] for k, v in components.items()
        ]
        t4 = Table(comp_rows, colWidths=[7 * cm, 7 * cm])
        t4.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(t4)

    # Observations
    story.append(Paragraph("Observations", heading_style))
    observations = analysis.get("observations") or []
    if observations:
        story.append(ListFlowable(
            [ListItem(Paragraph(o, body)) for o in observations], bulletType="bullet"
        ))
    else:
        story.append(Paragraph("No observations recorded.", body))

    # Risk & Recommendations (rule-based placeholder - see Limitations)
    if risk:
        story.append(Paragraph("Injury Risk Indicator (Rule-Based Placeholder)", heading_style))
        story.append(Paragraph(
            f"<b>Risk score:</b> {_fmt(risk.get('risk_score'))} / 100 &nbsp;&nbsp; "
            f"<b>Risk level:</b> {risk.get('risk_level') or 'Not available'}",
            body,
        ))
        factors = risk.get("contributing_factors") or []
        if factors:
            story.append(Paragraph("Contributing factors:", body))
            story.append(ListFlowable(
                [ListItem(Paragraph(f, body)) for f in factors], bulletType="bullet"
            ))
        recs = risk.get("recommendations") or []
        if recs:
            story.append(Paragraph("Preventive recommendations:", body))
            story.append(ListFlowable(
                [ListItem(Paragraph(r, body)) for r in recs], bulletType="bullet"
            ))

    # Limitations
    story.append(Paragraph("Limitations", heading_style))
    story.append(Paragraph(
        "This report is generated by a movement-analysis prototype built for an academic "
        "internship milestone. It reflects a rule-based movement-quality assessment derived "
        "from 2D pose estimation and does NOT constitute a medical diagnosis, a clinical "
        "injury-risk assessment, or a substitute for evaluation by a qualified medical or "
        "sports-science professional. The risk score above (if shown) is a structured, "
        "rule-based placeholder - NOT a trained machine-learning model and NOT a clinically "
        "validated prediction. Accuracy depends on video quality, camera angle, lighting, and "
        "pose-detection confidence.",
        body,
    ))

    doc.build(story)
    return output_path
