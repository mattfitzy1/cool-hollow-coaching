"""
Generates the branded client-input Excel template for every Business
Without You milestone tool. Run this after any column-schema change to any
of the seven apps, so the templates always match what each tool's
analysis.py actually expects.

Template layout (per workbook): an Instructions tab (columns explained,
grouped by tab), an Examples tab (filled-in reference, never read by the
tools), then one or more clean data tabs, title block, header row, blank
validated rows only. The shared reader in client_upload.py locates the
header row below the title block, so a client can upload this same file
straight into the tool, including into every slot of a multi-file tool.

Usage:
    apps/hidden-profit-analyzer/.venv/bin/python3 apps/_shared/generate_templates.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from template_builder import (
    add_header_row, add_list_validation, add_range_validation,
    add_title_block, apply_number_formats, build_examples_sheet,
    build_instructions_sheet, build_starter_sheet, new_workbook,
    set_column_widths, set_tab_color, style_data_rows,
)

STARTER_NOTE = (
    "The most common answers we see across owner-run businesses. Copy any that are "
    "true for yours onto the data tab, reworded to match how your business actually "
    "runs, then fill in the numbers and ratings yourself, honestly. Don't copy "
    "anything that isn't real for you."
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BLANK_ROWS = 40

MONEY = "$#,##0"
HOURS = "0.0"
WHOLE = "0"


def _data_sheet(wb, sheet_name, milestone_label, tool_name, headers, widths, formats=None):
    """Builds one clean data tab: title block, header row, blank styled rows.
    Returns (worksheet, first_row, last_row) for validation ranges."""
    ws = wb.create_sheet(sheet_name)
    add_title_block(ws, milestone_label, tool_name, span=len(headers))
    add_header_row(ws, headers, row=4)
    set_tab_color(ws)

    first_row = 5
    last_row = first_row + BLANK_ROWS - 1
    style_data_rows(ws, start_row=first_row, end_row=last_row, start_col=1, end_col=len(headers))
    if formats:
        apply_number_formats(ws, formats, first_row, last_row)

    set_column_widths(ws, widths)
    ws.freeze_panes = f"A{first_row}"
    return ws, first_row, last_row


def build_reclaim_protocol():
    wb = new_workbook()
    milestone, tool = "Milestone 1", "The 15-Hour Reclaim Protocol"
    headers = ["Task", "Hours Per Week", "Category", "Documented", "Trained Replacement", "Risk"]
    examples = [
        ["Approve every invoice before it's paid", 3, "delegate", "yes", "yes", "low"],
        ["Respond to every support email personally", 6, "delegate", "no", "no", "medium"],
        ["Set next quarter's pricing strategy", 3, "owner_only", "no", "no", "high"],
    ]
    notes = [
        ("Task", "One row per task from your one-week time log."),
        ("Hours Per Week", "How many hours a week this task costs you, total."),
        ("Category", "owner_only (only you can do it today), delegate, automate, or eliminate. Pick from the dropdown."),
        ("Documented", "yes or no. Is there a written process for this task?"),
        ("Trained Replacement", "yes or no. Is there already someone trained to take this on?"),
        ("Risk", "low, medium, or high. What happens if this gets handed off and something goes wrong?"),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List every task from your Liberation Audit time log. Mark each one owner_only, "
        "delegate, automate, or eliminate, then rate how ready it is to move. The tool "
        "ranks everything that isn't owner_only and builds your reclaim plan. Stuck on "
        "where to start? The Starter Ideas tab lists the tasks that eat most owners' weeks.",
        [("Time Log", notes)])
    build_examples_sheet(wb, milestone, tool, [("Time Log", headers, examples)])
    build_starter_sheet(wb, milestone, tool, STARTER_NOTE, [
        ("Money tasks owners hold onto", [
            "Approving every quote or estimate before it goes out",
            "Approving and paying supplier invoices",
            "Running payroll",
            "Chasing overdue customer invoices",
            "Reconciling bank statements / bookkeeping",
            "Setting or approving every price",
        ]),
        ("Day-to-day operations", [
            "Scheduling jobs, staff, or deliveries",
            "Ordering materials and supplies",
            "Final review of every job or deliverable before it ships",
            "Fixing problems the team escalates instead of solving",
            "Opening and closing the shop or office",
        ]),
        ("Customers and people", [
            "Answering customer calls and complaints personally",
            "Writing customer emails, follow-ups, and proposals",
            "Sitting in on every new-hire interview",
            "Training every new employee personally",
            "Posting on social media",
        ]),
    ])
    ws, first, last = _data_sheet(wb, "Time Log", milestone, tool, headers,
                                  [38, 16, 14, 14, 18, 10],
                                  [None, HOURS, None, None, None, None])
    add_list_validation(ws, ["owner_only", "delegate", "automate", "eliminate"], f"C{first}:C{last}",
                        hint="owner_only, delegate, automate, or eliminate")
    add_list_validation(ws, ["yes", "no"], f"D{first}:D{last}", hint="Is there a written process?")
    add_list_validation(ws, ["yes", "no"], f"E{first}:E{last}", hint="Is someone already trained for this?")
    add_list_validation(ws, ["low", "medium", "high"], f"F{first}:F{last}",
                        hint="Risk if this gets handed off and something goes wrong")
    out = REPO_ROOT / "apps/reclaim-protocol/Cool_Hollow_Coaching_Milestone_1_Reclaim_Protocol_Template.xlsx"
    wb.save(out)
    return out


def build_impact_map():
    wb = new_workbook()
    milestone, tool = "Milestone 2", "The 12-Month Impact Map"
    headers = ["Initiative", "Core Customer Fit", "Unfair Advantage Fit", "Impact", "Effort"]
    examples = [
        ["Launch the Instagram content engine", 5, 4, 5, 3],
        ["Redesign the client onboarding packet", 4, 3, 3, 2],
        ["Sponsor a local sports team", 1, 1, 1, 2],
    ]
    notes = [
        ("Initiative", "One row per item on your raw list of everything planned for the next 12 months."),
        ("Core Customer Fit", "1 to 5. Does this directly serve your core customer, as defined in your Core Customer Decree?"),
        ("Unfair Advantage Fit", "1 to 5. Does this lean on something from your Unfair Advantage list?"),
        ("Impact", "1 to 5. How much would this actually move the business if it worked?"),
        ("Effort", "1 to 5. How much time, money, or team capacity will this take?"),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List everything you're considering for the next 12 months, then rate each one "
        "against your Strategy Razor. The tool keeps the 3 to 5 initiatives worth the "
        "focus and shows you exactly what got cut and why.",
        [("Initiative List", notes)])
    build_examples_sheet(wb, milestone, tool, [("Initiative List", headers, examples)])
    ws, first, last = _data_sheet(wb, "Initiative List", milestone, tool, headers,
                                  [40, 16, 18, 10, 10],
                                  [None, WHOLE, WHOLE, WHOLE, WHOLE])
    add_range_validation(ws, 1, 5, f"B{first}:B{last}", hint="Does this serve your core customer?")
    add_range_validation(ws, 1, 5, f"C{first}:C{last}", hint="Does this lean on your unfair advantage?")
    add_range_validation(ws, 1, 5, f"D{first}:D{last}", hint="How much would this move the business?")
    add_range_validation(ws, 1, 5, f"E{first}:E{last}", hint="Time, money, and team capacity required")
    out = REPO_ROOT / "apps/impact-map/Cool_Hollow_Coaching_Milestone_2_Impact_Map_Template.xlsx"
    wb.save(out)
    return out


def build_dashboard_selector():
    wb = new_workbook()
    milestone, tool = "Milestone 3", "The Monday Morning Dashboard"
    headers = ["Category", "Metric Name", "Current Value", "Target Value", "Direction", "Leading", "Impact"]
    examples = [
        ["cash", "13-week cash runway (weeks)", 9, 13, "higher_better", "yes", 5],
        ["sales", "Monthly revenue", 42000, 50000, "higher_better", "no", 5],
        ["customer", "Net promoter score", 41, 60, "higher_better", "yes", 4],
    ]
    notes = [
        ("Category", "cash, sales, delivery, customer, or team. One winning metric gets picked per category, so add candidates to all five."),
        ("Metric Name", "What this metric is called, in plain English."),
        ("Current Value", "Where this metric stands today, as a number."),
        ("Target Value", "Where you want this metric to be."),
        ("Direction", "higher_better if more is good, lower_better if less is good."),
        ("Leading", "yes or no. Does this metric move before a problem shows up elsewhere?"),
        ("Impact", "1 to 5. How directly this metric reflects whether the business is actually healthy."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List every metric you could track across cash, sales, delivery, customer, and "
        "team. Add as many candidates per category as you like. The tool picks the single "
        "best one per category and builds your five-metric dashboard. The Starter Ideas "
        "tab lists proven candidates for each category if you're not sure what to consider.",
        [("Candidate Metrics", notes)])
    build_examples_sheet(wb, milestone, tool, [("Candidate Metrics", headers, examples)])
    build_starter_sheet(wb, milestone, tool, STARTER_NOTE, [
        ("cash", [
            "Weeks of cash runway",
            "Days customers take to pay (AR days)",
            "Cash balance vs next payroll due",
        ]),
        ("sales", [
            "Monthly revenue",
            "Quotes or proposals sent per week",
            "Close rate on quotes",
            "Average job or order value",
        ]),
        ("delivery", [
            "On-time completion rate",
            "Jobs or orders completed per week",
            "Rework or callback rate",
        ]),
        ("customer", [
            "Complaints per week",
            "Repeat purchase rate",
            "New reviews per month (and average rating)",
        ]),
        ("team", [
            "Open roles unfilled",
            "Overtime hours per week",
            "Staff turnover in the last 90 days",
        ]),
    ])
    ws, first, last = _data_sheet(wb, "Candidate Metrics", milestone, tool, headers,
                                  [14, 32, 14, 14, 16, 10, 10],
                                  [None, None, "#,##0.0", "#,##0.0", None, None, WHOLE])
    add_list_validation(ws, ["cash", "sales", "delivery", "customer", "team"], f"A{first}:A{last}",
                        hint="One winning metric gets picked per category")
    add_list_validation(ws, ["higher_better", "lower_better"], f"E{first}:E{last}",
                        hint="Is more of this good, or less?")
    add_list_validation(ws, ["yes", "no"], f"F{first}:F{last}",
                        hint="Does this move before problems show elsewhere?")
    add_range_validation(ws, 1, 5, f"G{first}:G{last}", hint="How directly this reflects business health")
    out = REPO_ROOT / "apps/dashboard-selector/Cool_Hollow_Coaching_Milestone_3_Dashboard_Template.xlsx"
    wb.save(out)
    return out


def build_profit_discovery_audit():
    wb = new_workbook()
    milestone, tool = "Milestone 4", "The Profit Discovery Audit"
    pnl_headers = ["Line Item", "Month 1", "Month 2", "Month 3"]
    pnl_examples = [
        ["Revenue", 85000, 88000, 91000],
        ["Cost of Goods Sold", 51000, 53000, 55000],
        ["Software Subscriptions", 400, 420, 1200],
        ["Discounts Given", 2500, 3100, 2800],
    ]
    pnl_notes = [
        ("Line Item", "One row per P&L line: Revenue, Cost of Goods Sold, Rent, Software, Discounts, and so on. Straight from your accounting export is fine."),
        ("Month 1, Month 2, Month 3", "Rename these to your actual months (e.g. Jan 2026). Add more columns if you have more months, the more months, the better the audit."),
    ]
    breakdown_headers = ["Type", "Name", "Revenue", "Direct Cost"]
    breakdown_examples = [
        ["customer", "Acme Co", 10000, 9000],
        ["customer", "Bolt Industries", 24000, 12000],
        ["service", "Onboarding Package", 5000, 3000],
    ]
    breakdown_notes = [
        ("Type", "customer or service. One row per customer or per service line."),
        ("Name", "The customer or service name."),
        ("Revenue", "Revenue from this customer or service."),
        ("Direct Cost", "The direct cost of serving this customer or delivering this service."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "Two data tabs. Fill in your P&L on the first (one row per line item, one column "
        "per month) and your customer and service breakdown on the second. Then upload "
        "this same file into both upload boxes in the tool, each box automatically reads "
        "the tab it needs.",
        [("P&L", pnl_notes), ("Customer Service Breakdown", breakdown_notes)])
    build_examples_sheet(wb, milestone, tool, [
        ("P&L", pnl_headers, pnl_examples),
        ("Customer Service Breakdown", breakdown_headers, breakdown_examples),
    ])
    _data_sheet(wb, "P&L", milestone, tool, pnl_headers, [32, 14, 14, 14],
                [None, MONEY, MONEY, MONEY])
    ws2, first2, last2 = _data_sheet(wb, "Customer Service Breakdown", milestone, tool,
                                     breakdown_headers, [16, 32, 14, 14],
                                     [None, None, MONEY, MONEY])
    add_list_validation(ws2, ["customer", "service"], f"A{first2}:A{last2}",
                        hint="One row per customer or per service line")
    out = REPO_ROOT / "apps/profit-discovery-audit/Cool_Hollow_Coaching_Milestone_4_Profit_Discovery_Audit_Template.xlsx"
    wb.save(out)
    return out


def build_cash_confidence():
    wb = new_workbook()
    milestone, tool = "Milestone 5", "Cash Confidence"
    cash_headers = ["Week", "Type", "Category", "Description", "Amount"]
    cash_examples = [
        [1, "inflow", "client revenue", "Recurring client payments", 12000],
        [1, "outflow", "Payroll", "Biweekly payroll", 9000],
        [2, "outflow", "rent", "Office lease", 3200],
    ]
    cash_notes = [
        ("Week", "A whole number from 1 to 13."),
        ("Type", "inflow or outflow."),
        ("Category", "A short label. If this row is a recurring expense you've also rated on the Recurring Expenses tab, use that exact expense name here so the two match up."),
        ("Description", "Optional detail."),
        ("Amount", "A positive dollar amount."),
    ]
    expense_headers = [
        "Expense Name", "Weekly Amount", "Core Customer Fit", "Revenue Risk If Cut",
        "ROI Clarity", "No Cheaper Alternative", "Would Approve Today",
    ]
    expense_examples = [
        ["Payroll", 9000, 5, 5, 4, 3, 5],
        ["Underused software bundle", 400, 1, 1, 1, 1, 1],
    ]
    expense_notes = [
        ("Expense Name", "Must match the Category or Description used for this expense on the Cash Items tab."),
        ("Weekly Amount", "The weekly cost of this recurring expense."),
        ("Core Customer Fit", "1 to 5. Does this expense serve your core customer?"),
        ("Revenue Risk If Cut", "1 to 5. Would cutting this put revenue at risk in the next 90 days?"),
        ("ROI Clarity", "1 to 5. Is there a clear, measurable return on this spend?"),
        ("No Cheaper Alternative", "1 to 5. Is there no cheaper way to get the same outcome?"),
        ("Would Approve Today", "1 to 5. If you were signing this contract fresh today, would you?"),
    ]
    receivables_headers = ["Customer Name", "Amount Outstanding", "Terms Days", "Days Outstanding"]
    receivables_examples = [
        ["Big Client Co", 18000, 30, 75],
        ["Steady Client", 4000, 30, 20],
    ]
    receivables_notes = [
        ("Customer Name", "Optional tab, but usually a bigger cash lever than cutting any expense. One row per customer who owes you money."),
        ("Amount Outstanding", "The total dollar amount this customer currently owes you."),
        ("Terms Days", "What your stated payment terms are, e.g. net-30 is 30."),
        ("Days Outstanding", "How long the invoice has actually been unpaid, in days."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "Three data tabs. Cash Items: every inflow and outflow you can see coming over "
        "the next 13 weeks. Recurring Expenses: each recurring expense rated against the "
        "five Decision Filter questions. Receivables Aging (optional): any customer "
        "paying late against your own terms. Then upload this same file into each upload "
        "box in the tool, each box automatically reads the tab it needs. The Starter "
        "Ideas tab lists the cash items owners most often forget, worth a scan before "
        "you call the list complete.",
        [("Cash Items", cash_notes), ("Recurring Expenses", expense_notes),
         ("Receivables Aging", receivables_notes)])
    build_examples_sheet(wb, milestone, tool, [
        ("Cash Items", cash_headers, cash_examples),
        ("Recurring Expenses", expense_headers, expense_examples),
        ("Receivables Aging", receivables_headers, receivables_examples),
    ])
    build_starter_sheet(wb, milestone, tool,
        "The cash items owners most often forget, which is exactly how a 13-week "
        "forecast ends up looking calmer than the 13 weeks ahead of you. Scan this "
        "before you call your list complete, add anything that applies with your own "
        "real amounts.",
        [
            ("Outflows that get forgotten", [
                "Quarterly tax payments",
                "Insurance premiums (annual or semi-annual renewals)",
                "Loan and equipment finance payments",
                "Credit card payments",
                "Software subscriptions (annual renewals especially)",
                "Vehicle costs: fuel, maintenance, registration",
                "Merchant and payment processing fees",
                "Owner draw or distributions",
                "Seasonal inventory or materials stock-up",
                "Marketing and advertising spend",
            ]),
            ("Inflows worth listing", [
                "Recurring client payments, by actual expected week",
                "Deposits on newly signed work",
                "Tax refunds due",
                "Rebates or vendor credits owed to you",
            ]),
        ])
    ws1, first1, last1 = _data_sheet(wb, "Cash Items", milestone, tool, cash_headers,
                                     [10, 12, 24, 28, 14],
                                     [WHOLE, None, None, None, MONEY])
    ws2, first2, last2 = _data_sheet(wb, "Recurring Expenses", milestone, tool, expense_headers,
                                     [28, 16, 16, 18, 14, 20, 18],
                                     [None, MONEY, WHOLE, WHOLE, WHOLE, WHOLE, WHOLE])
    ws3, first3, last3 = _data_sheet(wb, "Receivables Aging", milestone, tool, receivables_headers,
                                     [24, 18, 14, 16],
                                     [None, MONEY, WHOLE, WHOLE])
    add_range_validation(ws1, 1, 13, f"A{first1}:A{last1}", hint="Which of the 13 weeks this lands in")
    add_list_validation(ws1, ["inflow", "outflow"], f"B{first1}:B{last1}",
                        hint="Money coming in, or going out?")
    hints = [
        "Does this expense serve your core customer?",
        "Would cutting this risk revenue in the next 90 days?",
        "Is there a clear, measurable return on this spend?",
        "Is there no cheaper way to get the same outcome?",
        "Signing fresh today, would you approve this?",
    ]
    for col, hint in zip(("C", "D", "E", "F", "G"), hints):
        add_range_validation(ws2, 1, 5, f"{col}{first2}:{col}{last2}", hint=hint)
    out = REPO_ROOT / "apps/cash-confidence/Cool_Hollow_Coaching_Milestone_5_Cash_Confidence_Template.xlsx"
    wb.save(out)
    return out


def build_bottleneck_breakthrough():
    wb = new_workbook()
    milestone, tool = "Milestone 6", "The Bottleneck Breakthrough Plan"
    headers = [
        "Constraint Name", "Process", "Frequency Per Week", "Hours Lost Per Occurrence",
        "Downstream Impact", "Automatable", "Automation Effort",
    ]
    examples = [
        ["Owner approves every quote before it goes out", "Sales", 15, 0.5, 5, "yes", 2],
        ["Only one person knows how to run delivery scheduling", "Delivery", 5, 2, 5, "no", 5],
        ["Invoices assembled by hand from job notes", "Billing", 10, 0.75, 3, "yes", 1],
    ]
    notes = [
        ("Constraint Name", "One row per candidate constraint from your Constraint Identification worksheet."),
        ("Process", "Which of your three mapped processes this constraint sits in."),
        ("Frequency Per Week", "How many times a week this constraint actually bites."),
        ("Hours Lost Per Occurrence", "Hours lost each time it happens. Decimals are fine, 30 minutes is 0.5."),
        ("Downstream Impact", "1 to 5. How much this blocks everything else in the business."),
        ("Automatable", "yes or no."),
        ("Automation Effort", "1 to 5, only matters if Automatable is yes. 1 is trivial, 5 is hard."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List every candidate constraint across your three mapped processes. The tool "
        "ranks them all, names the single binding constraint to break first, and builds "
        "a separate automation hit list ranked by effort-adjusted payoff. The Starter "
        "Ideas tab lists the constraints we see most often, use it to jog your memory.",
        [("Constraint Worksheet", notes)])
    build_examples_sheet(wb, milestone, tool, [("Constraint Worksheet", headers, examples)])
    build_starter_sheet(wb, milestone, tool, STARTER_NOTE, [
        ("The owner is the constraint", [
            "Owner approves every quote before it goes out",
            "Waiting on the owner for pricing decisions",
            "Every problem escalates to the owner instead of getting solved",
            "Owner is the only one who talks to key customers",
        ]),
        ("Knowledge lives in one head", [
            "Only one person knows how to run scheduling",
            "No documented onboarding for new hires",
            "Job details live in one person's head or notebook",
            "Only one person can quote complex work",
        ]),
        ("Manual work that slows everything", [
            "Invoices assembled by hand from job notes",
            "Payments collected manually after the job",
            "Materials ordered only when someone notices they're low",
            "Jobs scheduled on a whiteboard or by phone calls",
            "Same customer questions answered one at a time, from scratch",
        ]),
    ])
    ws, first, last = _data_sheet(wb, "Constraint Worksheet", milestone, tool, headers,
                                  [38, 16, 16, 20, 16, 12, 16],
                                  [None, None, WHOLE, HOURS, WHOLE, None, WHOLE])
    add_range_validation(ws, 1, 5, f"E{first}:E{last}", hint="How much this blocks everything else")
    add_list_validation(ws, ["yes", "no"], f"F{first}:F{last}", hint="Could software or a system do this?")
    add_range_validation(ws, 1, 5, f"G{first}:G{last}", hint="1 is trivial, 5 is hard")
    out = REPO_ROOT / "apps/bottleneck-breakthrough/Cool_Hollow_Coaching_Milestone_6_Bottleneck_Breakthrough_Template.xlsx"
    wb.save(out)
    return out


def build_team_builder():
    wb = new_workbook()
    milestone, tool = "Milestone 7", "Build the Team That Builds the Business"
    role_headers = [
        "Role Name", "Current Delegation Level", "Target Delegation Level",
        "Key Outcome 1", "Key Outcome 2", "Key Outcome 3", "Decision Rights", "Success Metric",
    ]
    role_examples = [
        ["Operations Manager", 2, 5, "Keeps delivery on schedule across all active clients",
         "Owns vendor relationships and renewals", "Runs the weekly team check-in",
         "Can approve spend up to $2000 without sign-off", "On-time delivery rate at or above 95%"],
    ]
    role_notes = [
        ("Role Name", "One row per role in your inventory."),
        ("Current Delegation Level", "1 to 5. How much of this role you still personally hold today. 1 means it's all you, 5 means fully handed off."),
        ("Target Delegation Level", "1 to 5. How much of this role should be delegated."),
        ("Key Outcome 1, 2, 3", "What this role owns, not just what it does day to day."),
        ("Decision Rights", "What this role can decide without coming back to you."),
        ("Success Metric", "How you'll know this role is working."),
    ]
    candidate_headers = ["Candidate Name", "Role Name", "Ownership", "Communication", "Judgment", "Coachability", "Results Track Record"]
    candidate_examples = [
        ["Jordan Reyes", "Operations Manager", 4, 4, 5, 4, 4],
        ["Sam Whitfield", "Operations Manager", 3, 5, 4, 5, 3],
    ]
    candidate_notes = [
        ("Candidate Name", "One row per candidate being considered. This tab is optional, only fill it if you're actively hiring."),
        ("Role Name", "Must match a Role Name on the Roles tab exactly."),
        ("Ownership, Communication, Judgment, Coachability, Results Track Record", "Each rated 1 to 5."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "Two data tabs. Fill in your role inventory and delegation map on the Roles tab. "
        "If you're actively hiring, fill in the Candidates tab too, using the exact same "
        "Role Name as the Roles tab. Then upload this same file into each upload box in "
        "the tool, each box automatically reads the tab it needs. The Starter Ideas tab "
        "lists the roles most owner-run businesses need, check yours against it.",
        [("Roles", role_notes), ("Candidates", candidate_notes)])
    build_examples_sheet(wb, milestone, tool, [
        ("Roles", role_headers, role_examples),
        ("Candidates", candidate_headers, candidate_examples),
    ])
    build_starter_sheet(wb, milestone, tool, STARTER_NOTE, [
        ("Roles most owner-run businesses need", [
            "Operations Manager (keeps delivery running without you)",
            "Office Manager / Admin (paperwork, scheduling, phones)",
            "Bookkeeper / Finance Lead (invoices, bills, payroll, reports)",
            "Sales Lead (quotes, follow-ups, closing)",
            "Service or Delivery Lead (quality and dispatch on the ground)",
            "Field Supervisor / Crew Lead (runs the team day to day)",
            "Customer Service Lead (owns the inbox and the phone)",
            "Marketing Coordinator (content, ads, and the pipeline top)",
            "HR / Hiring Coordinator (job posts, screening, onboarding)",
        ]),
    ])
    ws1, first1, last1 = _data_sheet(wb, "Roles", milestone, tool, role_headers,
                                     [24, 18, 18, 30, 30, 30, 30, 28],
                                     [None, WHOLE, WHOLE, None, None, None, None, None])
    ws2, first2, last2 = _data_sheet(wb, "Candidates", milestone, tool, candidate_headers,
                                     [24, 24, 12, 14, 12, 14, 18],
                                     [None, None, WHOLE, WHOLE, WHOLE, WHOLE, WHOLE])
    add_range_validation(ws1, 1, 5, f"B{first1}:B{last1}", hint="1 means it's all you, 5 means fully handed off")
    add_range_validation(ws1, 1, 5, f"C{first1}:C{last1}", hint="Where this role's delegation should get to")
    for col in ("C", "D", "E", "F", "G"):
        add_range_validation(ws2, 1, 5, f"{col}{first2}:{col}{last2}", hint="Rate 1 to 5")
    out = REPO_ROOT / "apps/team-builder/Cool_Hollow_Coaching_Milestone_7_Team_Builder_Template.xlsx"
    wb.save(out)
    return out


if __name__ == "__main__":
    builders = [
        build_reclaim_protocol, build_impact_map, build_dashboard_selector,
        build_profit_discovery_audit, build_cash_confidence,
        build_bottleneck_breakthrough, build_team_builder,
    ]
    for builder in builders:
        path = builder()
        print(f"Built: {path.relative_to(REPO_ROOT)}")
