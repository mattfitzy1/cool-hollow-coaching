"""
Builds the Miro Board Prep Pack PDF for the July 14 call with Mike.
Packages all four filled exercises into one clean offline-readable brief.
Black/white/gold house style. Run: python3 outputs/strategy/build_miro_prep_pdf.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "outputs/strategy/Miro_Board_Prep_Pack.pdf"

BLACK   = colors.HexColor("#1A1A1A")
GOLD    = colors.HexColor("#C8A227")
GOLD_LT = colors.HexColor("#F0D98A")
WHITE   = colors.white
GREY_LT = colors.HexColor("#F5F5F5")
GREY_MD = colors.HexColor("#CCCCCC")
GREY_DK = colors.HexColor("#555555")
# status colors for the sticky key
C_EXIST   = colors.HexColor("#FBE7A1")  # yellow: exists
C_PLAN    = colors.HexColor("#F3C64B")  # gold: planned
C_PEXIST  = colors.HexColor("#C9B6E8")  # purple: partner exists
C_PPLAN   = colors.HexColor("#BBDDF2")  # light blue: partner planned
C_GREEN   = colors.HexColor("#CDE7C4")
C_YELLOW  = colors.HexColor("#FBE7A1")
C_BLUE    = colors.HexColor("#BBDDF2")


def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        title="Miro Board Prep Pack - Business Without You",
        author="Cool Hollow Coaching",
    )

    def style(name, **kw):
        base = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=getSampleStyleSheet()[base], **kw)

    S_COVER_COMPANY = style("CoverCompany", fontSize=11, textColor=GOLD, spaceAfter=4, alignment=TA_CENTER)
    S_COVER_TITLE   = style("CoverTitle", fontSize=25, textColor=WHITE, leading=30, spaceAfter=8,
                            alignment=TA_CENTER, fontName="Helvetica-Bold")
    S_COVER_SUB     = style("CoverSub", fontSize=13, textColor=GOLD_LT, spaceAfter=4, alignment=TA_CENTER)
    S_COVER_DATE    = style("CoverDate", fontSize=10, textColor=GREY_MD, spaceAfter=0, alignment=TA_CENTER)
    S_H1 = style("H1", fontSize=15, textColor=WHITE, leading=20, fontName="Helvetica-Bold",
                 spaceAfter=6, backColor=BLACK, leftIndent=-0.2*inch, rightIndent=-0.2*inch,
                 borderPadding=(6, 10, 6, 10))
    S_H2 = style("H2", fontSize=12, textColor=BLACK, leading=16, fontName="Helvetica-Bold",
                 spaceAfter=4, spaceBefore=14)
    S_H3 = style("H3", fontSize=10, textColor=GREY_DK, leading=14, fontName="Helvetica-BoldOblique",
                 spaceAfter=3, spaceBefore=8)
    S_BODY = style("Body", fontSize=10, textColor=BLACK, leading=15, spaceAfter=5)
    S_BULLET = style("Bullet", fontSize=10, textColor=BLACK, leading=14, spaceAfter=2,
                     leftIndent=14, bulletIndent=0)
    S_QUOTE  = style("Quote", fontSize=11, textColor=BLACK, leading=16, fontName="Helvetica-Oblique",
                     spaceAfter=6, leftIndent=16, rightIndent=16, borderPadding=(8, 12, 8, 12),
                     backColor=GREY_LT)
    S_NOTICE = style("Notice", fontSize=9, textColor=GREY_DK, leading=13, fontName="Helvetica-Oblique",
                     spaceAfter=4, leftIndent=12, borderPadding=(4, 8, 4, 8), backColor=GREY_LT)
    S_CELL   = style("Cell", fontSize=8.5, textColor=BLACK, leading=11)
    S_CELLH  = style("CellH", fontSize=8.5, textColor=GOLD, leading=11, fontName="Helvetica-Bold")
    S_TCELL  = style("TCell", fontSize=7.5, textColor=BLACK, leading=9.5)
    S_TCELLB = style("TCellB", fontSize=7.5, textColor=BLACK, leading=9.5, fontName="Helvetica-Bold")
    S_THEAD  = style("THead", fontSize=7.5, textColor=GOLD, leading=9.5, fontName="Helvetica-Bold")

    def prow(cells, first_bold=True, header=False):
        out = []
        for i, c in enumerate(cells):
            if header:
                st = S_THEAD
            elif first_bold and i == 0:
                st = S_TCELLB
            else:
                st = S_TCELL
            out.append(Paragraph(str(c).replace("\n", "<br/>"), st))
        return out

    def hr(): return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=4)
    def gap(n=6): return Spacer(1, n)
    def h1(t): return Paragraph(t, S_H1)
    def h2(t): return Paragraph(t, S_H2)
    def h3(t): return Paragraph(t, S_H3)
    def body(t): return Paragraph(t, S_BODY)
    def bullet(t): return Paragraph(f"<bullet>&bull;</bullet> {t}", S_BULLET)
    def quote(t): return Paragraph(t, S_QUOTE)
    def notice(t): return Paragraph(t, S_NOTICE)
    def cell(t): return Paragraph(t, S_CELL)
    def cellh(t): return Paragraph(t, S_CELLH)

    story = []

    # COVER
    cover = [
        [Paragraph("COOL HOLLOW COACHING", S_COVER_COMPANY)],
        [Paragraph("Miro Board Prep Pack", S_COVER_TITLE)],
        [Paragraph("Business Without You: the community model, mapped", S_COVER_SUB)],
        [Paragraph("For the call with Mike (Senteo), July 14, 2026", S_COVER_DATE)],
        [Paragraph("Prepared July 6, 2026", S_COVER_DATE)],
    ]
    ct = Table(cover, colWidths=[6.9*inch])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLACK),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 20), ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("TOPPADDING", (0,0), (0,0), 26), ("BOTTOMPADDING", (0,4), (0,4), 26),
        ("LINEBELOW", (0,4), (0,4), 2, GOLD),
    ]))
    story += [ct, gap(16)]
    story += [notice("Internal working document. This packages the four whiteboard exercises from "
                     "Mike's Miro board, filled in for our business, so you can read them offline before "
                     "the call and place them on the board quickly."), gap(6)]

    story += [
        h2("The one idea behind all of it"),
        body("The 12-week program is the <b>front door</b>, not the business. The real business is a "
             "<b>recurring community</b>: ongoing coaching, tools, and partner services an owner pays for "
             "over years. Every exercise below maps how one owner becomes years of value instead of a "
             "single $5,000 sale. Mike's car-ownership example is the template; this is our version of it."),
        gap(4),
    ]

    # ============ EXERCISE 1: PACKAGE BREAKDOWN ============
    story += [PageBreak(), h1("Exercise 1: Package Breakdown (the nested rings)"), gap(4)]
    story += [body("Four rings, center outward. The center is the one thing they buy; each ring further "
                   "out is a looser, longer-term layer of the relationship."), gap(4)]

    rings = [
        ["RING", "WHAT GOES IN IT (our business)"],
        ["Core Product\n(center)",
         "Business Without You membership: the transformation itself. 15 hours back, up to $50,000 in "
         "profit found, a business that runs without the owner. Entered through the 12-week program, "
         "lived in the ongoing community."],
        ["Accessories\n(direct add-ons)",
         "Profit Discovery Session (Cam) | Hiring Sprint (Hannah) | Hidden-Profit Analyzer | "
         "5-metric Monday dashboard | 13-week cash-flow forecast | client action-plan templates"],
        ["Education & Planning\n(learn / decide / run it)",
         "Core video content library (Zoom-first) | weekly live Q&A with Mark | monthly CFO Office Hours "
         "(Cam) | guest masterclasses | curriculum workbooks + checklists | knowledge library"],
        ["Memorabilia / Ecosystem\n(loyalty, long-tail)",
         "Cool Hollow Mastermind (application-only) | quarterly business reviews | member discounts on "
         "partner services | peer owner network | live events / retreats | referral rewards + alumni status"],
    ]
    rings = [prow(r, header=(idx == 0)) for idx, r in enumerate(rings)]
    t1 = Table(rings, colWidths=[1.5*inch, 5.4*inch])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLACK), ("TEXTCOLOR", (0,0), (-1,0), GOLD),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#E9E9E9")),
        ("BACKGROUND", (0,2), (-1,2), C_BLUE),
        ("BACKGROUND", (0,3), (-1,3), C_GREEN),
        ("BACKGROUND", (0,4), (-1,4), C_BLUE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_MD), ("LINEBELOW", (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [t1, gap(10)]

    # ============ EXERCISE 2: JOURNEY ============
    story += [PageBreak(), h1("Exercise 2: The Journey (before / journey / after)"), gap(4)]
    story += [body("The owner's transformation journey. Stages across the top, two rows filled at each "
                   "stage: the touchpoints, and the experience to design in or out."), gap(2)]
    story += [
        h3("BEFORE"),
        body("The owner is the single point of failure. 60+ hour weeks, can't take a vacation, everything "
             "routes through them, profit leaking they can't see, a business unsellable because it is them."),
        h3("STAGES ACROSS THE TOP"),
        body("Wake-Up &rarr; Diagnostic &rarr; Onboarding (12 weeks) &rarr; Convert to Member &rarr; "
             "Ongoing Community &rarr; Ascend"),
        gap(4),
    ]
    jrows = [
        ["STAGE", "DIALOGUE & COMMUNICATION", "EXPERIENCE"],
        ["Wake-Up", "IG pain-point content, 'you're the bottleneck' hooks, free analyzer.",
         "+ Sees themselves clearly for the first time."],
        ["Diagnostic", "Profit Discovery booked, analyzer result, 'here's what we found' call.",
         "+ Fast early win: profit found in week 1-2."],
        ["Onboarding", "Weekly 12-week modules, milestone check-ins, community welcome.",
         "+ Time visibly returning.  - Homework overload risk."],
        ["Convert", "'Your program's ending, here's what continues', founding-member invite.",
         "- Risk of feeling sold-to. Design this gently."],
        ["Ongoing", "Weekly Q&A reminders, CFO Office Hours, monthly wins recap, community threads.",
         "+ A room of owners who get it.  - Empty-room risk."],
        ["Ascend", "Quarterly review invites, mastermind application, premium-service offers.",
         "+ Bigger moves with the full team."],
    ]
    jrows = [prow(r, header=(idx == 0)) for idx, r in enumerate(jrows)]
    t2 = Table(jrows, colWidths=[1.05*inch, 3.35*inch, 2.5*inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLACK), ("TEXTCOLOR", (0,0), (-1,0), GOLD),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GREY_LT]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_MD), ("LINEBELOW", (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [t2, gap(6)]
    story += [
        h3("AFTER"),
        body("Business runs without them. 15 hours a week back, $50K+ found, five metrics checked in 15 "
             "minutes every Monday, a team that owns the seats, a business worth selling. Now an advocate "
             "and a referrer, staying in the community for the peer network and ongoing edge."),
    ]

    # ============ EXERCISE 3: CYCLIC MAP ============
    story += [PageBreak(), h1("Exercise 3: Cyclic Identification & Mapping (the arcs)"), gap(4)]
    story += [body("Four arcs, inner to outer. This is the recurring-revenue engine: what naturally "
                   "repeats for an owner, and how we earn from it again and again."), gap(2)]
    arcs = [
        ("Arc 1 - Identify Cyclical Purchase Patterns",
         ["Trigger cycles: new fiscal year, tax season, hiring season, growth plateau, cash crunch, "
          "key employee leaves, planning an exit.",
          "Preset recurrence: monthly financial review, quarterly planning, annual strategy reset.",
          "Ongoing needs: cash-flow management, KPI tracking, hiring, constraint-breaking, profit optimization."]),
        ("Arc 2 - Opportunities to Shape Those Patterns",
         ["Annual membership renewal built in.",
          "Quarterly business reviews scheduled by default.",
          "'Next milestone' prompts once one is complete.",
          "Seasonal sprints timed to their calendar (Hiring Sprint before busy season).",
          "Early-bird / founding-member pricing; tier upgrade offered at growth moments."]),
        ("Arc 3 - Additional Ways to Monetize the Relationship",
         ["Fractional CFO retainer (Cam); tax-strategy service.",
          "Business valuation (quick estimate to full).",
          "Done-for-you dashboard / systems builds.",
          "Cool Hollow Mastermind tier; live events / retreats; partner referrals (revenue share)."]),
        ("Arc 4 - Elements of the Themed Ecosystem",
         ["Member discounts across all partner services.",
          "Knowledge library (playbooks, templates, benchmarks).",
          "Peer community + owner directory (social layer); gamified milestone tracking.",
          "Referral program + alumni network; future tool marketplace; live-data dashboard integration."]),
    ]
    for title, items in arcs:
        block = [h2(title)] + [bullet(i) for i in items] + [gap(3)]
        story += [KeepTogether(block)]

    # ============ EXERCISE 4: CJM BLUEPRINT GRID ============
    story += [PageBreak(), h1("Exercise 4: CJM Blueprint Components (the master grid)"), gap(4)]
    story += [body("The synthesis grid. Nine component rows across a From &rarr; Journey &rarr; To timeline. "
                   "Every item is tagged by status using Mike's four-color sticky key."), gap(4)]

    key = [
        [cell("<b>KEY</b>"),
         Paragraph("EXISTS", S_CELL), Paragraph("PLANNED", S_CELL),
         Paragraph("PARTNER-EXISTS", S_CELL), Paragraph("PARTNER-PLANNED", S_CELL)],
    ]
    kt = Table(key, colWidths=[0.7*inch, 1.4*inch, 1.4*inch, 1.65*inch, 1.75*inch])
    kt.setStyle(TableStyle([
        ("BACKGROUND", (1,0), (1,0), C_EXIST), ("BACKGROUND", (2,0), (2,0), C_PLAN),
        ("BACKGROUND", (3,0), (3,0), C_PEXIST), ("BACKGROUND", (4,0), (4,0), C_PPLAN),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_MD), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [kt, gap(2)]
    story += [body("Timeline: <b>FROM</b> = entry / onboarding. <b>JOURNEY</b> = ongoing community life. "
                   "<b>TO</b> = mature member / outcome. Tags below: [E]xists, [P]lanned, "
                   "[PE] partner-exists, [PP] partner-planned."), gap(4)]

    grid = [
        ["#  COMPONENT", "FROM", "JOURNEY", "TO"],
        ["1  Planning & Tracking Tools",
         "Hidden-Profit Analyzer [E]; 5-metric dashboard [E]; 13-week forecast [E]",
         "Live monthly dashboard [P]; quarterly KPI review [P]",
         "Dashboard on live numbers [P]; peer benchmarks [P]"],
        ["2  Education & Expert Support",
         "12-week modules [E]; workbooks + checklists [E]",
         "Weekly Q&A w/ Mark [P]; video library [P]; CFO Office Hours [PP]; masterclasses [PP]",
         "Mastermind strategy [P]; full knowledge library [P]"],
        ["3  Own Products & Accessories",
         "Business Without You 12-week [E]; action-plan templates [E]",
         "Community membership tiers [P]",
         "Cool Hollow Mastermind [P]"],
        ["4  Partner Products & Accessories",
         "Profit Discovery, Cam [PE]; Hiring Sprint, Hannah [PE]",
         "Fractional CFO retainer, Cam [PE]; tax strategy [PP]",
         "Business valuation: quick to full [PP]"],
        ["5  Marketplace Product Options",
         "-",
         "Vetted third-party tool directory [P] (phase 3)",
         "Full marketplace w/ member discounts [P]"],
        ["6  Social Components",
         "Community welcome + intro thread [P]",
         "Peer community + cohort channels [P]; live events [P]",
         "Alumni network + mastermind circle [P]; referral community [P]"],
        ["7  Dialogue & Communications",
         "IG content [P]; analyzer follow-up [P]; onboarding emails, GHL [P]",
         "Weekly Q&A reminders [P]; monthly wins recap [P]; community notifications [P]",
         "Quarterly review invites [P]; renewal + upgrade offers [P]"],
        ["8  Positive Experience (design IN)",
         "Fast win: profit found wk 1-2; time returning",
         "Weekly access to Mark; a room of owners; visible momentum",
         "Runs without them; 15 hrs back; becomes an advocate"],
        ["9  Negative Experience (design OUT)",
         "Homework overload; unclear free vs paid",
         "Empty room at launch; momentum drop after onboarding",
         "'Graduated out' w/ nowhere to go; price-vs-value doubt"],
    ]
    grid = [prow(r, header=(idx == 0)) for idx, r in enumerate(grid)]
    gt = Table(grid, colWidths=[1.55*inch, 1.85*inch, 1.9*inch, 1.6*inch])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLACK), ("TEXTCOLOR", (0,0), (-1,0), GOLD),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GREY_LT]),
        ("BACKGROUND", (0,8), (-1,8), C_GREEN),
        ("BACKGROUND", (0,9), (-1,9), colors.HexColor("#F3D2CE")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_MD), ("LINEBELOW", (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [gt, gap(10)]

    story += [
        h2("What the grid shows at a glance"),
        bullet("<b>Green (exists) clusters at FROM.</b> Almost everything we have today is onboarding: "
               "the analyzer, the 12-week program, the templates. It's real and buildable now."),
        bullet("<b>The JOURNEY column is mostly planned.</b> The recurring middle, the part that makes "
               "this a business not a course, is the part we haven't built. That's the July-to-launch work."),
        bullet("<b>Partners are real people who already deliver.</b> Cam and Hannah do this work inside "
               "Cool Hollow Solutions today. Productizing them is packaging, not invention."),
        bullet("<b>Rows 8 and 9 are the retention design.</b> The empty-room-at-launch risk is the biggest "
               "one, which is why a founding cohort should seed the community before a public freemium tier."),
    ]

    # ============ MVP + CALL PLAN ============
    story += [PageBreak(), h1("The MVP and the move to make on July 14"), gap(4)]
    story += [
        h2("The MVP, stated plainly (the green list)"),
        body("To launch, we need exactly this and nothing more:"),
    ]
    mvp = [
        "A community platform with member access and rooms.",
        "Freemium plus at least one paid tier, with payments working.",
        "GoHighLevel CRM + booking, separate from Cool Hollow Solutions.",
        "The 12-week program built and deliverable (curriculum is mostly there).",
        "One fast finance win at entry (Profit Discovery Session with Cam).",
        "A weekly live Q&A with Mark.",
        "Enough core video content to fill the first stretch (recorded Zoom-first).",
    ]
    for m in mvp:
        story += [bullet(m)]
    story += [gap(4), body("Everything else is real, but it's what we add after the doors open. The "
                           "discipline is defending that list and resisting the pull to launch the whole map.")]

    story += [
        h2("The one line to say"),
        quote("\"Same structure as your car example, built for us: the core product is the owner "
              "getting their business back. The 12-week program is how they enter, the community is how "
              "they stay, and the cyclical map is how one owner becomes years of revenue instead of a "
              "single $5,000 sale.\""),
    ]

    story += [
        h2("Questions to bring to the call"),
        bullet("What's the smallest paid tier that's still worth paying for monthly?"),
        bullet("Do we launch to a founding cohort first, before opening freemium wide?"),
        bullet("How much video is 'enough' for launch, and which milestones record first?"),
        bullet("Where's the free-vs-paid wall?"),
        bullet("What's Mike's role: partner? the journey-mapping workshop?"),
        bullet("What's the honest team capacity for weekly Q&A + monthly office hours at launch?"),
    ]

    story += [gap(8), hr(),
        Paragraph("Cool Hollow Coaching - Miro Board Prep Pack - Prepared July 6, 2026 - "
                  "For the July 14 call with Mike. Internal working document.",
                  ParagraphStyle("Footer", fontSize=8, textColor=GREY_DK, alignment=TA_CENTER, leading=12))]

    doc.build(story)
    print(f"Built: {OUTPUT}")


if __name__ == "__main__":
    build()
