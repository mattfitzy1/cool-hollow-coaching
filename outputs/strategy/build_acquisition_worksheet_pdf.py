"""
Builds a printable PDF of the Client Acquisition Audit worksheet.
Fill-by-hand version for the Mike/Senteo homework exercise.
Run: python3 outputs/strategy/build_acquisition_worksheet_pdf.py
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT

OUTPUT = "outputs/strategy/2026-07-17-chs-client-acquisition-worksheet.pdf"

BLACK = colors.HexColor("#1A1A1A")
GREY_DK = colors.HexColor("#555555")
GREY_LT = colors.HexColor("#F0F0F0")
GREY_LINE = colors.HexColor("#BBBBBB")
WHITE = colors.white

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=19, textColor=BLACK, spaceAfter=2)
meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9.5, textColor=GREY_DK, spaceAfter=10, leading=13)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=BLACK, spaceBefore=16, spaceAfter=6)
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, textColor=BLACK, leading=14, spaceAfter=6)
note = ParagraphStyle("Note", parent=styles["Normal"], fontSize=9, textColor=GREY_DK, leading=12.5, spaceAfter=6)
cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=10, textColor=BLACK, leading=13)
cell_hdr = ParagraphStyle("CellHdr", parent=styles["Normal"], fontSize=10, textColor=WHITE, leading=13, fontName="Helvetica-Bold")


def blank_rows(n_cols, n_rows, col_labels, row_labels=None, fills=None):
    """Build a table of rows with faint ruled lines to write on.

    fills: optional dict {row_index: [col_values...]} (values after the row
    label column) to pre-populate known answers, leaving the rest blank.
    """
    header = [Paragraph(c, cell_hdr) for c in col_labels]
    data = [header]
    fills = fills or {}
    for r in range(n_rows):
        row = []
        if row_labels:
            row.append(Paragraph(row_labels[r], cell))
            start = 1
        else:
            start = 0
        known = fills.get(r)
        for i, c in enumerate(range(start, n_cols)):
            if known and i < len(known) and known[i]:
                row.append(Paragraph(known[i], cell))
            else:
                row.append("")
        data.append(row)
    return data


def styled_table(data, col_widths, header_bg=BLACK, header_height=34, row_height=32):
    t = Table(data, colWidths=col_widths, rowHeights=[header_height] + [row_height] * (len(data) - 1))
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.6, GREY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_LT]),
    ]
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=landscape(letter),
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title="Client Acquisition Audit Worksheet",
        author="Cool Hollow Solutions",
    )

    flow = []

    flow.append(Paragraph("Client Acquisition Audit: Worksheet", title_style))
    flow.append(Paragraph(
        "Mike's Exercise 1 &nbsp;&middot;&nbsp; Cool Hollow Solutions scale-up &nbsp;&middot;&nbsp; "
        "Due before the Tuesday, July 21 call with Mike",
        meta_style,
    ))
    flow.append(HRFlowable(width="100%", thickness=1, color=BLACK, spaceAfter=10))

    flow.append(Paragraph(
        "For every channel: a rough annual cost, the new clients it produced, and the cost per new client. "
        "Plus the referral percentage. Mike's guidance: be sensitive with money questions, ranges are "
        "fine, and estimates are fine everywhere. Flag an estimate with a ~ so we know which numbers are soft.",
        note,
    ))

    # --- Table 1: Channels ---
    flow.append(Paragraph("Table 1: Channels", h2))
    row_labels_1 = [
        "Networking events (incl. travel)",
        "Boardroom",
        "LAN advisory",
        "Local",
        "TSC",
        "Cool Hollow mastermind\n(fees, venue, travel)",
        "Referrals",
        "Social media\n(manager cost)",
        "Webinars (historic)",
        "Other",
        "TOTAL",
    ]
    # Known answers so far (2026-07-20). Last-12-mo counts come from the 16
    # named clients in Table 2. The "whole active book" column folds in the
    # 8 older clients from Table 3, and now matches the original totals
    # given for Mastermind (2) and Referrals (8) exactly. Cost, last-12-mo,
    # whole active book (24), cost per new client, notes.
    col_labels_1 = ["Channel", "Rough annual cost", "New clients,\nlast 12 mo", "Whole active\nbook (24)",
                     "Cost per\nnew client", "Notes"]
    fills_1 = {
        1: ["$30,000/yr", "2", "2", "$15,000", "see Table 2"],                       # Boardroom
        2: ["$57,000/yr", "3", "3", "$19,000", "see Table 2"],                       # LAN advisory
        3: ["", "3", "3", "", "see Table 2"],                                        # Local
        4: ["", "2", "2", "", "see Table 2"],                                        # TSC
        5: ["$5,000/yr", "1", "2", "$5,000", "+Chase Bricker, see Table 3"],         # Mastermind
        6: ["~$0 hard cost", "5", "8", "~$0", "+3 older clients, see Table 3"],       # Referrals
        7: ["$30,000/yr", "0", "0", "n/a, no clients", ""],                          # Social media
        9: ["", "0", "4", "", "2021 cohort, see Table 3"],                           # Other
        10: ["$122,000/yr known so far", "16 named in Table 2", "24, all named", "", "excludes networking cost"],  # TOTAL
    }
    data1 = blank_rows(6, len(row_labels_1), col_labels_1, row_labels_1, fills=fills_1)
    widths1 = [2.1 * inch, 1.6 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch, 2.3 * inch]
    flow.append(styled_table(data1, widths1, header_height=38, row_height=34))
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "All 24 active clients are now traced to a channel (Table 2 covers the last 12 months, Table 3 "
        "covers the other 8). Once the older clients are folded in, Mastermind and Referrals land exactly "
        "on the totals given at the start (2 and 8), the earlier last-12-mo-only counts (1 and 5) simply "
        "hadn't caught the older clients yet.", note
    ))

    flow.append(PageBreak())

    # --- Table 2: Last 12 new clients ---
    # Name, month, and fee pulled from the Master Client List's "Date of
    # Signed Proposal" and "Monthly Fee" columns (screenshot, 2026-07-20),
    # filtered to proposals signed in the last 12 months (2025-07-20 to
    # 2026-07-20), sorted earliest first. Source confirmed for all 16.
    client_rows = [
        ("Filippo Mainella", "Sept 2025", "Referral", "$4,750"),
        ("Rocky Anderson", "Sept 2025", "Boardroom", "$4,000"),
        ("Tom & Katie Koontz", "Oct 2025", "Local", "$1,000"),
        ("Dave DeLeon", "Oct 2025", "Referral", "$1,500"),
        ("Ken Weller", "Nov 2025", "Referral", "$0 (one-time ~$20,000)"),
        ("Braxton Bednarz", "Dec 2025", "LAN", "$2,000"),
        ("Ed Trainor", "Jan 2026", "Referral", "$2,500"),
        ("Rena & Nick Ehrhart", "Jan 2026", "Local", "$0 (one-time payment)"),
        ("Travis Frasier", "Mar 2026", "LAN", "$2,750"),
        ("Cohen Redding", "Mar 2026", "Local", "$1,000"),
        ("Mark Thibodeau", "Mar 2026", "TSC", "$1,500"),
        ("Shon Duty", "Apr 2026", "Referral", "$4,000"),
        ("John Rugg", "May 2026", "TSC", "$3,500"),
        ("John Fernando", "May 2026", "Boardroom", "$3,000"),
        ("Michael Forrest", "May 2026", "Mastermind", "$3,000"),
        ("Terry Wideman", "June 2026", "LAN", "$6,000"),
    ]
    flow.append(Paragraph(f"Table 2: The Last {len(client_rows)} New Clients, One by One", h2))
    flow.append(Paragraph(
        "Name, month signed, source, and starting fee, all confirmed. One more, Chase Bricker (Sandy "
        "Home Buyers), signed 7/3/25, just outside the 12-month window, add it if you want it counted.",
        note,
    ))
    col_labels_2 = ["#", "Client (initials fine)", "Month signed", "Where they actually came from", "Starting monthly fee"]
    data2 = [[Paragraph(c, cell_hdr) for c in col_labels_2]]
    for i, (name, month, source, fee) in enumerate(client_rows, start=1):
        row = [str(i)]
        row.append(Paragraph(name, cell) if name else "")
        row.append(Paragraph(month, cell) if month else "")
        row.append(Paragraph(source, cell) if source else "")
        row.append(Paragraph(fee, cell) if fee else "")
        data2.append(row)
    widths2 = [0.4 * inch, 2.1 * inch, 1.3 * inch, 3.8 * inch, 2.3 * inch]
    flow.append(styled_table(data2, widths2, header_height=26, row_height=26))
    flow.append(Spacer(1, 4))
    referral_count = sum(1 for _, _, source, _ in client_rows if source == "Referral")
    flow.append(Paragraph(f"Referral % of new clients: {referral_count} of {len(client_rows)}", body))

    flow.append(PageBreak())

    # --- Table 3: The other 8 active clients (16 + 8 = 24, matches active count) ---
    # Signed date and fee pulled from the Master Client List (screenshot,
    # 2026-07-20), the 8 active clients older than the last-12-mo window in
    # Table 2. Source confirmed for all 8.
    outstanding_rows = [
        ("Tim Stenger (Premier HVAC)", "3/8/21", "Webinar (Other)", "$1,750"),
        ("Dan Johnson (Buckline Collision)", "4/9/21", "Webinar (Other)", "$1,200"),
        ("Cody Shank (CS Stoneworks)", "4/9/21", "Webinar (Other)", "$700"),
        ("Alicia & Gerard Rath (Willoughby Construction)", "4/9/21", "Webinar (Other)", "$9,000"),
        ("Caleb & Nathaniel Gingrich (heating services)", "2/14/23", "Referral (long-term client)", "$0 (pay per visit)"),
        ("Cory Meyers (vet clinic)", "8/27/24", "Referral (family)", "$1,500"),
        ("Steve Latta (Gene Latta Ford)", "8/27/24", "Referral", "$1,750"),
        ("Chase Bricker (Sandy Home Buyers)", "7/3/25", "Mastermind", "$200"),
    ]
    flow.append(Paragraph(
        f"Table 3: The Other {len(outstanding_rows)} Active Clients, All Sourced", h2
    ))
    flow.append(Paragraph(
        f"{len(client_rows)} named in Table 2 plus these {len(outstanding_rows)} equals 24, the full active "
        "client count, every one now traced to a channel. These 8 signed before the last-12-month window, "
        "so they're not in Table 2.",
        note,
    ))
    col_labels_o = ["#", "Client (initials fine)", "Date signed", "Where they actually came from", "Starting monthly fee"]
    data_o = [[Paragraph(c, cell_hdr) for c in col_labels_o]]
    for i, (name, date_signed, source, fee) in enumerate(outstanding_rows, start=1):
        row = [str(i)]
        row.append(Paragraph(name, cell) if name else "")
        row.append(Paragraph(date_signed, cell) if date_signed else "")
        row.append(Paragraph(source, cell) if source else "")
        row.append(Paragraph(fee, cell) if fee else "")
        data_o.append(row)
    widths_o = [0.4 * inch, 2.1 * inch, 1.3 * inch, 3.8 * inch, 2.3 * inch]
    flow.append(styled_table(data_o, widths_o, header_height=26, row_height=26))

    flow.append(PageBreak())

    # --- Table 4: Churn autopsy ---
    # Client and last-follow-up date pulled from the "On Pause" tab
    # (screenshot, 2026-07-20), the 10 most recently followed-up-with
    # departures. That sheet has no signup date for these clients, so "how
    # long stayed" is left blank. Reason confirmed for all 10.
    churn_rows = [
        ("Bill Riddick (CSP Inc.)", "5/27/26", "Ask Cam"),
        ("Chris & Heather Bonillas (Aunt Susie's LLC)", "2/4/26", "Ask Cam"),
        ("Matt Maiwald (Maiwald Fitness)", "1/16/26", "No payment"),
        ("John & Caroline Watson (Lotus Bowls)", "1/15/26", "Can't afford"),
        ("George Snook (Snook Group)", "12/22/25", "Just wanted tax advice"),
        ("John Snider (Autobridge Systems)", "11/18/25", "Small engagement, used for hiring"),
        ("Chris Naugle (BYOB - Money Multiplier)", "9/25/25", "Financial crisis"),
        ("Ann Wilson (Joe Canal's Liquor)", "8/29/25", "Didn't see the value"),
        ("Nick Couch (Next Level Electric)", "7/31/25", "Wouldn't follow instructions"),
        ("Cain & Michael Blaeser (Blaeser Construction)", "7/30/25", "Paused"),
    ]
    flow.append(Paragraph(f"Table 4: Churn Autopsy (Last {len(churn_rows)} Departures)", h2))
    flow.append(Paragraph(
        "Client and last follow-up date pulled from the On Pause tab, most recent 10, reason confirmed. "
        "That sheet doesn't record a signup date for these clients, so fill in how long they stayed and "
        "whether they came back or referred anyone since.", note
    ))
    col_labels_3 = ["#", "Client (initials fine)", "Last\nfollow-up", "Why they left", "Came back or\nreferred since?"]
    data3 = [[Paragraph(c, cell_hdr) for c in col_labels_3]]
    for i, (name, last_followup, reason) in enumerate(churn_rows, start=1):
        data3.append([str(i), Paragraph(name, cell), Paragraph(last_followup, cell), Paragraph(reason, cell), ""])
    widths3 = [0.4 * inch, 3.0 * inch, 1.0 * inch, 3.3 * inch, 2.1 * inch]
    flow.append(styled_table(data3, widths3, header_height=26, row_height=30))

    doc.build(flow)
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()
