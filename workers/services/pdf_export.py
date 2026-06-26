import io
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_BULLET_RE = re.compile(r"^[-*]\s+(.*)$")


def _register_font() -> str:
    font_name = "STSong-Light"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    return font_name


def _markdown_to_flowables(markdown: str, font_name: str) -> list:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#111827"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=8,
        spaceAfter=6,
    )
    h3_style = ParagraphStyle(
        "ReportH3",
        parent=styles["Heading3"],
        fontName=font_name,
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#374151"),
        spaceBefore=6,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=2,
    )

    flowables: list = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            flowables.append(Spacer(1, 4))
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            text = escape(heading_match.group(2))
            if level == 1:
                flowables.append(Paragraph(text, title_style))
            elif level == 2:
                flowables.append(Paragraph(text, h2_style))
            else:
                flowables.append(Paragraph(text, h3_style))
            continue

        bullet_match = _BULLET_RE.match(line)
        if bullet_match:
            text = escape(bullet_match.group(1))
            flowables.append(Paragraph(f"• {text}", bullet_style))
            continue

        flowables.append(Paragraph(escape(line), body_style))

    if not flowables:
        flowables.append(Paragraph("（空报告）", body_style))

    return flowables


def markdown_to_pdf_bytes(markdown: str) -> bytes:
    font_name = _register_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="CreatorDNA Report",
    )
    doc.build(_markdown_to_flowables(markdown, font_name))
    return buffer.getvalue()
