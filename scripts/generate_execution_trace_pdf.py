import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

MD_PATH = r"C:\Users\OmniBook x\.gemini\antigravity\brain\07a7d22c-fcd9-450e-9448-d65d07f5afcb\MotionIQ_Complete_System_Execution_Trace.md"
PDF_PATH_ARTIFACT = r"C:\Users\OmniBook x\.gemini\antigravity\brain\07a7d22c-fcd9-450e-9448-d65d07f5afcb\MotionIQ_Complete_System_Execution_Trace.pdf"
PDF_PATH_DOWNLOADS = os.path.expanduser(r"~\Downloads\MotionIQ_Complete_System_Execution_Trace.pdf")

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
        self.drawString(54, 11 * 72 - 36, "MOTION IQ — SYSTEM EXECUTION TRACE & MASTER SPECIFICATION")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        # Footer
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.drawString(54, 34, "CONFIDENTIAL & PROPRIETARY • SPORTS MOTION INTELLIGENCE PLATFORM")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 34, page_str)
        self.restoreState()

def clean_html(text):
    text = html.escape(text)
    # Convert bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italic *text*
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Convert inline code `text`
    text = re.sub(r'`(.*?)`', r'<font face="Courier" size="8.5" color="#4c1d95">\1</font>', text)
    return text

import html

def build_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

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
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#4c1d95'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
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

    # Title
    story.append(Paragraph("Motion IQ: Complete End-to-End System Execution Trace & Master Specification", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#7c3aed'), spaceAfter=12))

    # Parse sections
    lines = md_text.split('\n')
    in_table = False
    table_lines = []

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
            # Render Table
            if len(table_lines) > 2:
                table_data = []
                # Header
                headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
                table_data.append([Paragraph(clean_html(h), table_header_style) for h in headers])
                # Rows
                for row_line in table_lines[2:]:
                    cols = [c.strip() for c in row_line.split('|')[1:-1]]
                    if len(cols) == len(headers):
                        table_data.append([Paragraph(clean_html(c), table_cell_style) for c in cols])
                
                if table_data:
                    col_widths = [48, 48, 54, 54, 54, 48, 48, 48, 54, 48]
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
                    story.append(Spacer(1, 10))
            table_lines = []

        if line_str.startswith('# '):
            story.append(Paragraph(clean_html(line_str[2:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd6fe'), spaceAfter=8))
        elif line_str.startswith('## '):
            story.append(Paragraph(clean_html(line_str[3:]), h2_style))
        elif line_str.startswith('### '):
            story.append(Paragraph(clean_html(line_str[4:]), h2_style))
        elif line_str.startswith('> '):
            story.append(Paragraph(f"<i>{clean_html(line_str[2:])}</i>", body_style))
        else:
            story.append(Paragraph(clean_html(line_str), body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Artifact PDF built successfully at: {PDF_PATH_ARTIFACT}")

    # Copy to Downloads
    import shutil
    shutil.copy(PDF_PATH_ARTIFACT, PDF_PATH_DOWNLOADS)
    print(f"Downloads copy created at: {PDF_PATH_DOWNLOADS}")

if __name__ == "__main__":
    build_pdf()
