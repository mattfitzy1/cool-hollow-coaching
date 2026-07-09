"""
Shared branded PDF builder for a client's own results.

Every milestone tool runs entirely in memory: nothing uploaded or
generated is written to disk or a database (see outputs/legal/privacy-notice.md).
Because nothing is stored server-side, this is the client's only way to
keep a copy of their own results. Each app calls build_results_pdf() with
its own output and offers it as a download button, right in the browser,
never touching a server file.
"""

import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER

INK = colors.HexColor("#1A1A1A")
GOLD = colors.HexColor("#C8A227")
GOLD_LT = colors.HexColor("#E8C766")
WHITE = colors.white
GREY_DK = colors.HexColor("#555555")


def build_results_pdf(milestone_number: int, milestone_name: str, headline: str, sections: list) -> bytes:
    """Builds a branded PDF of a client's own results.

    sections: list of (heading: str, lines: list[str]) tuples. Each line
    becomes one bullet under that heading.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        title=f"Business Without You, {milestone_name}",
        author="Cool Hollow Coaching",
    )

    def style(name, **kw):
        base = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=getSampleStyleSheet()[base], **kw)

    s_company = style("Company", fontSize=10, textColor=GOLD, fontName="Helvetica-Bold",
                       spaceAfter=2, alignment=TA_CENTER)
    s_title = style("Title", fontSize=18, textColor=WHITE, fontName="Helvetica-Bold",
                     leading=22, alignment=TA_CENTER)
    s_headline = style("Headline", fontSize=12, textColor=INK, fontName="Helvetica-Bold",
                        spaceAfter=10, spaceBefore=4)
    s_heading = style("Heading", fontSize=11, textColor=INK, fontName="Helvetica-Bold",
                       spaceBefore=12, spaceAfter=4)
    s_bullet = style("Bullet", fontSize=9.5, textColor=INK, leading=14, spaceAfter=3,
                      leftIndent=12)
    s_footer = style("Footer", fontSize=7.5, textColor=GREY_DK, alignment=TA_CENTER, leading=11)

    story = []

    cover = Table(
        [[Paragraph("COOL HOLLOW COACHING &middot; BUSINESS WITHOUT YOU", s_company)],
         [Paragraph(f"Milestone {milestone_number}: {milestone_name}", s_title)]],
        colWidths=[6.9*inch],
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INK),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 1), (0, 1), 14),
        ("LINEBELOW", (0, 1), (0, 1), 2, GOLD),
    ]))
    story += [cover, Spacer(1, 14)]

    if headline:
        story += [Paragraph(headline, s_headline)]

    for heading, lines in sections:
        story += [Paragraph(heading, s_heading)]
        for line in lines:
            story += [Paragraph(f"&bull; {line}", s_bullet)]

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=6),
        Paragraph(
            "This is your own copy of your results. Cool Hollow Coaching does not "
            "store this data on our servers, this download is the only copy. "
            "General business and financial information for educational purposes "
            "only, not financial, legal, tax, or investment advice.",
            s_footer,
        ),
    ]

    doc.build(story)
    return buf.getvalue()
