import datetime as dt
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from app.config import settings
from app import models


def generate_matches_pdf(user: models.User, matches: list[models.Match], top_n: int = 15) -> str:
    """Builds a PDF digest of the user's top job matches. Returns the file path."""
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    filename = f"jobradar_digest_{user.id}_{dt.date.today().isoformat()}.pdf"
    path = os.path.join(settings.REPORTS_DIR, filename)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal = styles["Normal"]
    small = ParagraphStyle("small", parent=normal, fontSize=8, textColor=colors.grey)
    reason_style = ParagraphStyle("reason", parent=normal, fontSize=9, leading=12)

    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    story = [
        Paragraph("JobRadar — Daily Match Digest", title_style),
        Paragraph(f"For {user.email} &middot; {dt.date.today().strftime('%B %d, %Y')}", small),
        Spacer(1, 0.6 * cm),
    ]

    top_matches = sorted(matches, key=lambda m: m.score, reverse=True)[:top_n]

    if not top_matches:
        story.append(Paragraph("No matches found yet. Add a resume and run a scrape to get started.", normal))
    else:
        data = [["Score", "Role", "Company", "Why it fits"]]
        for m in top_matches:
            data.append([
                f"{m.score:.0f}",
                Paragraph(m.job.title, reason_style),
                m.job.company or "—",
                Paragraph(m.reasoning or "", reason_style),
            ])

        table = Table(data, colWidths=[1.6 * cm, 4.5 * cm, 3 * cm, 7.5 * cm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)

    doc.build(story)
    return path
