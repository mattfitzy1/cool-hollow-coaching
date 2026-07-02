"""
Builds the Business Without You — Signature Framework & Funnel Blueprint PDF.
For Cam and Mark. Clean, professional, black/white/gold.
Run: python3 outputs/strategy/build_framework_pdf.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

OUTPUT = "outputs/strategy/BWY_Signature_Framework_and_Funnel_Blueprint.pdf"

# Brand palette
BLACK   = colors.HexColor("#1A1A1A")
GOLD    = colors.HexColor("#C8A227")
GOLD_LT = colors.HexColor("#F0D98A")
WHITE   = colors.white
GREY_LT = colors.HexColor("#F5F5F5")
GREY_MD = colors.HexColor("#CCCCCC")
GREY_DK = colors.HexColor("#555555")

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.85*inch,
        rightMargin=0.85*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Business Without You — Signature Framework & Funnel Blueprint",
        author="Cool Hollow Coaching",
    )

    # --- Styles ---
    def style(name, **kw):
        base = kw.pop("parent", "Normal")
        s = ParagraphStyle(name, parent=getSampleStyleSheet()[base], **kw)
        return s

    S_COVER_COMPANY = style("CoverCompany", fontSize=11, textColor=GOLD,
                            spaceAfter=4, alignment=TA_CENTER)
    S_COVER_TITLE   = style("CoverTitle", fontSize=26, textColor=WHITE,
                            leading=32, spaceAfter=8, alignment=TA_CENTER,
                            fontName="Helvetica-Bold")
    S_COVER_SUB     = style("CoverSub", fontSize=13, textColor=GOLD_LT,
                            spaceAfter=4, alignment=TA_CENTER)
    S_COVER_DATE    = style("CoverDate", fontSize=10, textColor=GREY_MD,
                            spaceAfter=0, alignment=TA_CENTER)

    S_H1 = style("H1", fontSize=15, textColor=WHITE, leading=20,
                 fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=0,
                 backColor=BLACK, leftIndent=-0.2*inch, rightIndent=-0.2*inch,
                 borderPadding=(6, 10, 6, 10))
    S_H2 = style("H2", fontSize=12, textColor=BLACK, leading=16,
                 fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=14,
                 borderPadding=(0, 0, 2, 0))
    S_H3 = style("H3", fontSize=10, textColor=GREY_DK, leading=14,
                 fontName="Helvetica-BoldOblique", spaceAfter=3, spaceBefore=8)
    S_BODY = style("Body", fontSize=10, textColor=BLACK, leading=15,
                   spaceAfter=5)
    S_BULLET = style("Bullet", fontSize=10, textColor=BLACK, leading=15,
                     spaceAfter=3, leftIndent=14, bulletIndent=0)
    S_QUOTE  = style("Quote", fontSize=11, textColor=BLACK, leading=16,
                     fontName="Helvetica-Oblique", spaceAfter=6,
                     leftIndent=20, rightIndent=20,
                     borderPadding=(8, 12, 8, 12), backColor=GREY_LT)
    S_LABEL  = style("Label", fontSize=8, textColor=GREY_DK, leading=11,
                     fontName="Helvetica-Bold")
    S_CAPTION= style("Caption", fontSize=8, textColor=GREY_DK, leading=11,
                     alignment=TA_CENTER, spaceAfter=2)
    S_NOTICE = style("Notice", fontSize=9, textColor=GREY_DK, leading=13,
                     fontName="Helvetica-Oblique", spaceAfter=4,
                     leftIndent=12, borderPadding=(4, 8, 4, 8),
                     backColor=GREY_LT)

    def hr(): return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=4)
    def gap(n=6): return Spacer(1, n)
    def h1(t): return Paragraph(t, S_H1)
    def h2(t): return Paragraph(t, S_H2)
    def h3(t): return Paragraph(t, S_H3)
    def body(t): return Paragraph(t, S_BODY)
    def bullet(t): return Paragraph(f"<bullet>&bull;</bullet> {t}", S_BULLET)
    def quote(t): return Paragraph(t, S_QUOTE)
    def notice(t): return Paragraph(t, S_NOTICE)
    def label(t): return Paragraph(t, S_LABEL)

    story = []

    # ======================================================
    # COVER BLOCK (simulated with a dark table)
    # ======================================================
    cover_inner = [
        [Paragraph("COOL HOLLOW COACHING", S_COVER_COMPANY)],
        [Paragraph("Business Without You", S_COVER_TITLE)],
        [Paragraph("Signature Framework and Funnel Blueprint", S_COVER_SUB)],
        [Paragraph("Internal Briefing — July 1, 2026", S_COVER_DATE)],
        [Paragraph("For Cam and Mark", S_COVER_DATE)],
    ]
    cover_tbl = Table(cover_inner, colWidths=[6.8*inch])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLACK),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("TOPPADDING",    (0,0), (0,0), 28),
        ("BOTTOMPADDING", (0,4), (0,4), 28),
        ("LINEBELOW", (0,4), (0,4), 2, GOLD),
    ]))
    story += [cover_tbl, gap(18)]

    story += [
        notice("This document is confidential and for internal use only. "
               "No figures or claims here are public-facing until verified and approved by Matt."),
        gap(4),
    ]

    # ======================================================
    # PART 1: SIGNATURE FRAMEWORK
    # ======================================================
    story += [h1("Part 1: The Signature Framework"), gap(4)]

    story += [
        h2("Why we need a named framework"),
        body("Business Without You is a strong curriculum: seven milestones, twelve weeks, "
             "seven working tools. What it is not yet is a <b>named, ownable method</b> a prospect "
             "can picture in one glance and a graduate can describe to a colleague in one sentence. "
             "Every premium program that commands a premium price has a piece of visual IP that "
             "makes the method feel engineered, not improvised. That is what justifies the $5,000 "
             "price without apology: you are not buying coaching hours, you are buying a proven "
             "operating system."),
        gap(6),
    ]

    story += [
        h2("The framework name (decided July 1, 2026)"),
        quote("<b>The Business Without You Method</b>"),
        body("The program name is the method name. Zero new branding to build, "
             "and \"method\" signals engineered, not improvised. All copy, the VSL, "
             "and the landing page will use this name."),
        gap(6),
    ]

    story += [h2("The three-phase structure"), gap(2)]

    phases = [
        ["PHASE", "WEEKS", "MILESTONES", "PROMISE"],
        ["Phase 1\nGet Your Time Back", "1–3",
         "1. Reclaim the Owner's Time and Identity\n2. Define the Destination with Precision",
         "15 hours back on your calendar before we ask for anything else."],
        ["Phase 2\nFind the Money", "4–7",
         "3. Install the Dashboard That Tells the Truth\n4. Discover the Hidden Profit\n5. Build Cash Confidence",
         "A specific dollar figure found in your own books by a real CFO."],
        ["Phase 3\nMake It Run Without You", "8–12",
         "6. Break the Binding Constraint\n7. Build the Team That Builds the Business",
         "The two-week vacation test. The business passes or it doesn't."],
    ]
    phase_tbl = Table(phases, colWidths=[1.3*inch, 0.6*inch, 3.0*inch, 2.0*inch])
    phase_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLACK),
        ("TEXTCOLOR",     (0,0), (-1,0), GOLD),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8),
        ("BACKGROUND",    (0,1), (-1,1), GREY_LT),
        ("BACKGROUND",    (0,2), (-1,2), WHITE),
        ("BACKGROUND",    (0,3), (-1,3), GREY_LT),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("TEXTCOLOR",     (0,1), (-1,-1), BLACK),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, GREY_MD),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [phase_tbl, gap(10)]

    story += [
        h2("The one-glance version"),
        quote("<b>Get your time back. Find the money. Make it run without you.</b><br/>"
              "Seven milestones. Twelve weeks. Seven working tools you keep."),
        gap(4),
    ]

    story += [
        h2("The premium logic: Seven milestones, seven tools"),
        body("The tools are the physical proof that this is a system, not a seminar. Every milestone "
             "ends with the owner's own data running through a purpose-built model that outputs a "
             "named, specific recommendation. Nobody leaves with notes; everyone leaves with a working "
             "dashboard, a 13-week cash forecast, a reclaim protocol, and a hiring system — built on "
             "their numbers, theirs to keep."),
        quote("<b>\"You don't graduate with a binder. You graduate with a working operating system: "
              "your dashboard, your cash forecast, your delegation map, your hiring templates. "
              "Built on your numbers, yours to keep.\"</b>"),
        gap(6),
    ]

    story += [
        h2("The seven tools (all live)"),
        gap(2),
    ]
    tools = [
        ["MILESTONE", "TOOL", "WHAT IT OUTPUTS"],
        ["1 — Reclaim Time", "15-Hour Reclaim Protocol", "Ranked delegate / automate / eliminate list with deadlines"],
        ["2 — Define Destination", "12-Month Impact Map", "3-5 filtered priorities + a focus score"],
        ["3 — Install Dashboard", "Five-Metric Dashboard", "Right metrics, red/yellow/green thresholds set against owner's targets"],
        ["4 — Discover Hidden Profit", "Profit Discovery Audit", "Specific dollar figure found: pricing gaps, cost leaks, revenue leakage"],
        ["5 — Build Cash Confidence", "13-Week Cash Forecast", "Rolling forecast + Decision Filter + receivables-timing check"],
        ["6 — Break Constraint", "Bottleneck Breakthrough Plan", "Single binding constraint named + effort-adjusted automation hit list"],
        ["7 — Build the Team", "Hiring & Delegation System", "Outcome-based templates, delegation gap score, leadership scorecard"],
    ]
    tools_tbl = Table(tools, colWidths=[1.7*inch, 2.0*inch, 3.2*inch])
    tools_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLACK),
        ("TEXTCOLOR",     (0,0), (-1,0), GOLD),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND",    (0,2), (-1,2), GREY_LT),
        ("BACKGROUND",    (0,4), (-1,4), GREY_LT),
        ("BACKGROUND",    (0,6), (-1,6), GREY_LT),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
        ("GRID",          (0,0), (-1,-1), 0.5, GREY_MD),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [tools_tbl, gap(14)]

    # ======================================================
    # PART 2: RELATIONSHIP MODEL
    # ======================================================
    story += [h1("Part 2: The Relationship-Centric Business Model"), gap(4)]

    story += [
        body("The goal is a client who pays $5,000 once but is worth far more than $5,000 — "
             "not through upsell pressure, but because the relationship genuinely keeps paying "
             "them. Five layers, in the order a client experiences them."),
        gap(6),
    ]

    layers = [
        ("Layer 1 — The habit that outlives the program",
         "The Monday Morning Dashboard is the retention engine hiding in plain sight. By week 4 "
         "every client has a five-metric dashboard and a 15-minute Monday review rhythm. That "
         "rhythm is a weekly touchpoint with our system, forever. The dashboard and the 13-week "
         "cash forecast (which needs refreshing every week to stay alive) are the reason clients "
         "stay connected after week 12."),
        ("Layer 2 — The graduate re-audit (the comeback moment)",
         "90 days after the Liberation Finale, every graduate gets a personal invitation to "
         "re-run their numbers: fresh Profit Discovery Audit, fresh dashboard thresholds, fresh "
         "reclaim scan. This shows them their progress in their own numbers (the strongest "
         "testimonial generator we will ever have), surfaces new leakage, and puts a real date "
         "in the calendar so graduation never means goodbye. Costs us almost nothing because "
         "the tools already exist."),
        ("Layer 3 — The alumni circle",
         "Graduates keep access to the tool suite, a monthly open Q&A call with Mark, and each "
         "other. Not a paid tier, not a heavy build. Owners of $1M to $10M businesses are "
         "isolated; the peer room is worth more to them than most content. This is also where "
         "Tier 2 invitations come from, so ascension happens inside a warm room."),
        ("Layer 4 — The ascension path",
         "Tier 2 at $22K/yr stays invitation-only for graduates who got a result. "
         "\"The audit found $X. Tier 2 is where the full team helps you take the bigger swings: "
         "tax strategy, investment, 10x moves.\" The $50K found in Tier 1 funds Tier 2. "
         "The 4.4x price jump is bridged by the re-audit (Layer 2) and the alumni circle "
         "(Layer 3), so the invitation happens after renewed proof, not straight off the finale."),
        ("Layer 5 — The referral loop",
         "The natural moment to ask is the re-audit, when a graduate is looking at their own "
         "before-and-after numbers. The ask: \"Who do you know who's where you were six months "
         "ago?\" Referrals from owners whose numbers moved are the highest-trust lead source "
         "available. Referral mechanics (thank-you format, incentive) are parked until launch."),
    ]

    for title, text in layers:
        story += [h2(title), body(text), gap(4)]

    story += [hr(), gap(6)]

    # ======================================================
    # PART 3: THE FUNNEL
    # ======================================================
    story += [h1("Part 3: The Client Acquisition Funnel"), gap(4)]

    story += [
        body("The mechanism is Hormozi's diagnostic-first structure, adapted for Business Without You. "
             "The hidden-profit analyzer is the front door. Free diagnostic first, email gate before "
             "the result, immediate next-step pitch on the results page, fit application, booked call."),
        gap(6),
    ]

    story += [h2("The funnel map"), gap(2)]

    funnel = [
        ["STAGE", "ASSET", "PSYCHOLOGY"],
        ["1. Awareness",
         "Daily Instagram content. Mark fronts it. Value only, no sale. One link in bio: the analyzer.",
         "Give until they ask. Trust compounds, authority builds."],
        ["2. Lead capture",
         "The hidden-profit analyzer. Upload a P&L, get a sized result: \"$X leaking out of your business.\" Email captured to deliver it.",
         "A diagnostic exposes a deficiency the owner cannot unsee. Reveals a problem AND its size."],
        ["3. Results page\n+ VSL",
         "On the results page, immediately: 2–4 minute video. Mark on camera, plain operator backdrop. Beat sheet in this document.",
         "Pattern-interrupt at peak intent. The number they just saw from their own books is the proof."],
        ["4. Fit application",
         "Short application: revenue, hours in the business, biggest constraint, are you the single point of failure.",
         "Positions the paid step as qualification. Filtering tire-kickers raises perceived value at zero cost."],
        ["5. Booked call",
         "GoHighLevel booking via thank-you.html. Call is NOT required to get the report.",
         "Inverts buyer-seller dynamic. We are qualifying them, not pitching them."],
        ["6. Tier 1 enrol",
         "$5,000, 12 weeks, Business Without You Method.",
         "Math sells itself: up to $50K found, program costs $5K. Lead with the math, not the price."],
        ["7. Ascension",
         "Tier 2 at $22K/yr, invitation-only for graduates with results.",
         "\"10x is easier than 2x.\" Proven trust, warm room, not a cold sale."],
    ]
    funnel_tbl = Table(funnel, colWidths=[1.3*inch, 2.9*inch, 2.7*inch])
    funnel_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLACK),
        ("TEXTCOLOR",     (0,0), (-1,0), GOLD),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND",    (0,2), (-1,2), GREY_LT),
        ("BACKGROUND",    (0,4), (-1,4), GREY_LT),
        ("BACKGROUND",    (0,6), (-1,6), GREY_LT),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
        ("GRID",          (0,0), (-1,-1), 0.5, GREY_MD),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [funnel_tbl, gap(12)]

    # ======================================================
    # PART 4: THE VSL
    # ======================================================
    story += [h1("Part 4: The VSL Beat Sheet"), gap(4)]

    story += [
        body("The VSL's one job: convert the results-page visitor into a fit-application submission. "
             "It plays at the exact moment the prospect is staring at a dollar figure from their own "
             "P&L — the highest-intent moment we will ever get. 2–4 minutes. Mark on camera, plain "
             "operator backdrop (no guru polish). Nothing films until this beat sheet is approved."),
        gap(2),
        notice("Two facts are needed from Mark before final copy is written: "
               "(1) the real weekly time commitment outside live sessions, "
               "(2) whether there is a guarantee and what it says. "
               "Placeholder-safe language is used below until those are confirmed."),
        gap(8),
    ]

    beats = [
        ["#", "BEAT", "TIME", "DIRECTION"],
        ["1", "The number hook",     "0:00–0:15",
         "\"That number you're looking at is real. And it's probably conservative. "
         "I'm Mark, and finding money like that in businesses like yours is what my firm does for a living.\""],
        ["2", "The twist",           "0:15–0:40",
         "\"Here's what that report can't tell you: WHY the money is leaking. In almost every "
         "business we work with, it has the same root cause. The owner is doing too much for "
         "anyone to watch the numbers.\""],
        ["3", "Credibility, fast",   "0:40–1:00",
         "Real advisory firm, real clients, a real CFO on staff. Plain facts, no flexing. "
         "\"We're not consultants in suits. We run this stuff for real companies.\""],
        ["4", "The method",          "1:00–1:45",
         "\"Get your time back. Find the money. Make it run without you. Seven milestones, twelve "
         "weeks, seven working tools you keep.\" Show the three phases visually."],
        ["5", "Time objection, preempted", "1:45–2:15",
         "\"If you're thinking 'I don't have time for a 12-week program,' that's exactly why "
         "milestone one exists. The first thing we do is get hours back on your calendar. "
         "Before anything else.\""],
        ["6", "The math",            "2:15–2:35",
         "PLACEHOLDER (needs verified client result): "
         "\"The program costs $5,000. The audit alone routinely pays for it.\" "
         "Once a real $50K+ result is confirmed, update to: \"We typically find up to $50,000. "
         "The program is $5,000. You do the math.\""],
        ["7", "The fit gate",        "2:35–2:50",
         "\"This isn't for everyone. It's for owners doing $1M to $10M who are still the "
         "single point of failure. If that's you, there's a short application below. "
         "It's not a sales form — it's how we decide together whether this fits.\""],
        ["8", "The soft close",      "2:50–3:00",
         "\"Your full report is in your inbox either way. If you want help finding the rest, "
         "you know where the button is.\""],
    ]
    beats_tbl = Table(beats, colWidths=[0.25*inch, 1.5*inch, 0.75*inch, 4.4*inch])
    beats_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLACK),
        ("TEXTCOLOR",     (0,0), (-1,0), GOLD),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (1,-1), "Helvetica-Bold"),
        ("BACKGROUND",    (0,2), (-1,2), GREY_LT),
        ("BACKGROUND",    (0,4), (-1,4), GREY_LT),
        ("BACKGROUND",    (0,6), (-1,6), GREY_LT),
        ("BACKGROUND",    (0,8), (-1,8), GREY_LT),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("GRID",          (0,0), (-1,-1), 0.5, GREY_MD),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, GOLD),
        ("TEXTCOLOR",     (0,7), (-1,7), colors.HexColor("#8B6000")),
    ]))
    story += [beats_tbl, gap(12)]

    # ======================================================
    # PART 5: LANDING PAGE LAYOUT
    # ======================================================
    story += [h1("Part 5: Landing Page Layout"), gap(4)]

    story += [
        body("The landing page restructured around The Business Without You Method. "
             "The analyzer stays the primary CTA throughout — it is the front door, "
             "never buried. Nine sections, top to bottom."),
        gap(6),
    ]

    lp = [
        ["#", "SECTION", "CONTENT", "CTA"],
        ["1", "Hero",
         "Headline leads with a number, not a dream: \"If you're doing $1M to $10M and the business "
         "still can't run a day without you, there's profit hiding in your books.\" "
         "Subhead: the one-glance framework line.",
         "\"Find out what's hiding in your numbers\" → analyzer"],
        ["2", "The mirror",
         "Three short pain statements in the owner's own words. No solution yet. Let them see themselves.",
         "None"],
        ["3", "The diagnostic",
         "The analyzer as the front door: what it does, what they get, ~3 minutes, free. "
         "This is the page's center of gravity.",
         "\"Run the free analyzer\""],
        ["4", "The method",
         "The three phases as a visual: Get your time back → Find the money → Make it run without you. "
         "Seven milestones listed beneath, one line each.",
         "None (belief-building section)"],
        ["5", "Seven tools you keep",
         "The tool suite as tangible IP. \"You don't graduate with a binder.\"",
         "None"],
        ["6", "Who's behind it",
         "Mark, Cam (CFO), Hannah (hiring), Cool Hollow Solutions' track record. "
         "Operators, not suits.",
         "None"],
        ["7", "The math",
         "Price transparency: $5,000, 12 weeks. The profit-found-vs-price frame, "
         "using only verified numbers.",
         "\"See if it's a fit\" → discovery.html"],
        ["8", "The fit gate",
         "Who it IS for and who it is NOT for, stated plainly. The not-for list does "
         "real work at this price point.",
         "\"Apply\" → discovery.html"],
        ["9", "Footer",
         "Quiet. Contact, disclosure line, no link soup.",
         "Analyzer link repeats"],
    ]
    lp_tbl = Table(lp, colWidths=[0.3*inch, 1.0*inch, 3.8*inch, 1.8*inch])
    lp_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLACK),
        ("TEXTCOLOR",     (0,0), (-1,0), GOLD),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("FONTNAME",      (0,1), (1,-1), "Helvetica-Bold"),
        ("BACKGROUND",    (0,2), (-1,2), GREY_LT),
        ("BACKGROUND",    (0,4), (-1,4), GREY_LT),
        ("BACKGROUND",    (0,6), (-1,6), GREY_LT),
        ("BACKGROUND",    (0,8), (-1,8), GREY_LT),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("GRID",          (0,0), (-1,-1), 0.5, GREY_MD),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, GOLD),
    ]))
    story += [lp_tbl, gap(12)]

    # ======================================================
    # PART 6: OPEN ITEMS
    # ======================================================
    story += [h1("Open Items — Needed Before Final Copy or Filming"), gap(4)]

    open_items = [
        ("For Mark",
         [
             "Weekly time commitment outside live sessions (needed for the VSL and landing page copy).",
             "Guarantee decision: yes, no, or conditioned on what? Do not invent terms.",
             "Confirm which real client result(s) can be named publicly as verified proof (the $50K found claim).",
         ]),
        ("For Cam",
         [
             "Confirm the receivables-timing module in the Cash Confidence tool matches your methodology.",
             "Review the Profit Discovery Audit's industry benchmark logic (trades/repair, retail, "
             "professional services, high-margin recurring) and flag anything that doesn't hold under scrutiny.",
             "Confirm you're comfortable being named and quoted in the VSL and landing page.",
         ]),
        ("For Matt",
         [
             "Approve the VSL beat sheet above before any filming is scheduled.",
             "Confirm the landing page section order before the rebuild starts.",
             "Run milestones 1-3 live with 3-4 beta owners (already the plan) to generate the first real proof numbers.",
         ]),
    ]

    for who, items in open_items:
        story += [h2(who)]
        for item in items:
            story += [bullet(item)]
        story += [gap(4)]

    # ======================================================
    # FOOTER NOTE
    # ======================================================
    story += [
        hr(),
        Paragraph(
            "Cool Hollow Coaching — Business Without You — Internal Briefing — July 1, 2026<br/>"
            "Confidential. Not for distribution. All claims marked as unverified must be confirmed "
            "before appearing in any client-facing material.",
            ParagraphStyle("Footer", fontSize=8, textColor=GREY_DK,
                           alignment=TA_CENTER, leading=12)
        ),
    ]

    doc.build(story)
    print(f"Built: {OUTPUT}")

if __name__ == "__main__":
    build()
