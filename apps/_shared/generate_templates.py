"""
Generates the branded client-input Excel template for every Business
Without You milestone model. Run this once after any column-schema change
to any of the seven apps, so the templates always match what each tool's
analysis.py actually expects.

Every data tab includes a couple of greyed-out example rows so a client
sees the right format instead of having to invent their own columns, plus
a banner row marking exactly where their own data should start.

Usage:
    source apps/hidden-profit-analyzer/.venv/bin/activate
    python3 apps/_shared/generate_templates.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from template_builder import (
    add_example_label_row, add_example_rows, add_header_row,
    add_list_validation, add_range_validation, add_title_block,
    build_instructions_sheet, new_workbook, set_column_widths,
    style_data_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BLANK_ROWS = 35


def _data_sheet(wb, sheet_name, milestone_label, tool_name, headers, widths, example_rows):
    """Builds one data tab: title, header, example rows, a banner row, then
    blank styled rows. Returns (worksheet, first_blank_row, last_blank_row)
    so callers can point validation at the rows clients actually type into."""
    ws = wb.create_sheet(sheet_name)
    add_title_block(ws, milestone_label, tool_name, span=len(headers))
    add_header_row(ws, headers, row=4)

    example_start = 5
    last_example_row = add_example_rows(ws, example_rows, start_row=example_start)
    label_row = last_example_row + 1
    add_example_label_row(ws, label_row, span=len(headers))

    first_blank_row = label_row + 1
    last_blank_row = first_blank_row + BLANK_ROWS - 1
    style_data_rows(ws, start_row=first_blank_row, end_row=last_blank_row, start_col=1, end_col=len(headers))

    set_column_widths(ws, widths)
    ws.freeze_panes = f"A{first_blank_row}"
    return ws, first_blank_row, last_blank_row


def build_reclaim_protocol():
    wb = new_workbook()
    milestone, tool = "Milestone 1", "The 15-Hour Reclaim Protocol"
    headers = ["Task", "Hours Per Week", "Category", "Documented", "Trained Replacement", "Risk"]
    examples = [
        ["Approve every invoice before it's paid", 3, "delegate", "yes", "yes", "low"],
        ["Set next quarter's pricing strategy", 3, "owner_only", "no", "no", "high"],
    ]
    notes = [
        ("Task", "One row per task from your one-week time log."),
        ("Hours Per Week", "How many hours a week this task costs you, total."),
        ("Category", "owner_only (only you can do it today), delegate, automate, or eliminate."),
        ("Documented", "yes or no. Is there a written process for this task?"),
        ("Trained Replacement", "yes or no. Is there already someone trained to take this on?"),
        ("Risk", "low, medium, or high. What happens if this gets handed off and something goes wrong?"),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List every task from your Liberation Audit time log. Mark each one owner_only, "
        "delegate, automate, or eliminate, then rate how ready it is to move. The tool "
        "ranks everything that isn't owner_only and builds your reclaim plan.",
        notes)
    ws, first, last = _data_sheet(wb, "Time Log", milestone, tool, headers, [38, 16, 14, 14, 18, 10], examples)
    add_list_validation(ws, ["owner_only", "delegate", "automate", "eliminate"], f"C{first}:C{last}")
    add_list_validation(ws, ["yes", "no"], f"D{first}:D{last}")
    add_list_validation(ws, ["yes", "no"], f"E{first}:E{last}")
    add_list_validation(ws, ["low", "medium", "high"], f"F{first}:F{last}")
    out = REPO_ROOT / "apps/reclaim-protocol/Cool_Hollow_Coaching_Milestone_1_Reclaim_Protocol_Template.xlsx"
    wb.save(out)
    return out


def build_impact_map():
    wb = new_workbook()
    milestone, tool = "Milestone 2", "The 12-Month Impact Map"
    headers = ["Initiative", "Core Customer Fit", "Unfair Advantage Fit", "Impact", "Effort"]
    examples = [
        ["Launch the Instagram content engine", 5, 4, 5, 3],
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
        notes)
    ws, first, last = _data_sheet(wb, "Initiative List", milestone, tool, headers, [40, 16, 18, 10, 10], examples)
    for col in ("B", "C", "D", "E"):
        add_range_validation(ws, 1, 5, f"{col}{first}:{col}{last}")
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
    ]
    notes = [
        ("Category", "cash, sales, delivery, customer, or team. One winning metric gets picked per category."),
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
        "best one per category and builds your five-metric dashboard.",
        notes)
    ws, first, last = _data_sheet(wb, "Candidate Metrics", milestone, tool, headers, [14, 32, 14, 14, 16, 10, 10], examples)
    add_list_validation(ws, ["cash", "sales", "delivery", "customer", "team"], f"A{first}:A{last}")
    add_list_validation(ws, ["higher_better", "lower_better"], f"E{first}:E{last}")
    add_list_validation(ws, ["yes", "no"], f"F{first}:F{last}")
    add_range_validation(ws, 1, 5, f"G{first}:G{last}")
    out = REPO_ROOT / "apps/dashboard-selector/Cool_Hollow_Coaching_Milestone_3_Dashboard_Template.xlsx"
    wb.save(out)
    return out


def build_profit_discovery_audit():
    wb = new_workbook()
    milestone, tool = "Milestone 4", "The Profit Discovery Audit"
    pnl_headers = ["Line Item", "Month 1", "Month 2", "Month 3"]
    pnl_examples = [
        ["Revenue", 10000, 10000, 10000],
        ["Software Subscriptions", 400, 420, 1200],
    ]
    pnl_notes = [
        ("Line Item", "Revenue, Cost of Goods Sold, Rent, Software, Discounts, and so on."),
        ("Month 1, Month 2, Month 3", "Rename these to your actual months (e.g. Jan 2026), add more columns if you have more months."),
    ]
    breakdown_headers = ["Type", "Name", "Revenue", "Direct Cost"]
    breakdown_examples = [
        ["customer", "Acme Co", 10000, 9000],
        ["service", "Onboarding Package", 5000, 3000],
    ]
    breakdown_notes = [
        ("Type", "customer or service. One row per customer or per service line."),
        ("Name", "The customer or service name."),
        ("Revenue", "Revenue from this customer or service."),
        ("Direct Cost", "The direct cost of serving this customer or delivering this service."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "This template has two tabs. Fill in your P&L on the first tab (one row per line "
        "item, one column per month). Fill in your customer and service breakdown on the "
        "second tab. Upload both tabs into the tool to run all five profit checks.",
        pnl_notes + breakdown_notes)
    _data_sheet(wb, "P&L", milestone, tool, pnl_headers, [32, 14, 14, 14], pnl_examples)
    ws2, first2, last2 = _data_sheet(wb, "Customer Service Breakdown", milestone, tool, breakdown_headers, [16, 32, 14, 14], breakdown_examples)
    add_list_validation(ws2, ["customer", "service"], f"A{first2}:A{last2}")
    out = REPO_ROOT / "apps/profit-discovery-audit/Cool_Hollow_Coaching_Milestone_4_Profit_Discovery_Audit_Template.xlsx"
    wb.save(out)
    return out


def build_cash_confidence():
    wb = new_workbook()
    milestone, tool = "Milestone 5", "Cash Confidence"
    cash_headers = ["Week", "Type", "Category", "Description", "Amount"]
    cash_examples = [
        [1, "inflow", "client revenue", "recurring client payments", 12000],
        [1, "outflow", "payroll", "biweekly payroll", 9000],
    ]
    cash_notes = [
        ("Week", "A whole number from 1 to 13."),
        ("Type", "inflow or outflow."),
        ("Category", "A short label. If this row is a recurring expense you've also rated on the Recurring Expenses tab, use that exact expense name here."),
        ("Description", "Optional detail."),
        ("Amount", "A positive dollar amount."),
    ]
    expense_headers = [
        "Expense Name", "Weekly Amount", "Core Customer Fit", "Revenue Risk If Cut",
        "Roi Clarity", "No Cheaper Alternative", "Would Approve Today",
    ]
    expense_examples = [
        ["payroll", 9000, 5, 5, 4, 3, 5],
        ["Underused software bundle", 400, 1, 1, 1, 1, 1],
    ]
    expense_notes = [
        ("Expense Name", "Must match the Category or Description used for this expense on the Cash Items tab."),
        ("Weekly Amount", "The weekly cost of this recurring expense."),
        ("Core Customer Fit", "1 to 5. Does this expense serve your core customer?"),
        ("Revenue Risk If Cut", "1 to 5. Would cutting this put revenue at risk in the next 90 days?"),
        ("Roi Clarity", "1 to 5. Is there a clear, measurable return on this spend?"),
        ("No Cheaper Alternative", "1 to 5. Is there no cheaper way to get the same outcome?"),
        ("Would Approve Today", "1 to 5. If you were signing this contract fresh today, would you?"),
    ]
    receivables_headers = ["Customer Name", "Amount Outstanding", "Terms Days", "Days Outstanding"]
    receivables_examples = [
        ["Big Client Co", 18000, 30, 75],
        ["Steady Client", 4000, 30, 20],
    ]
    receivables_notes = [
        ("Customer Name", "Optional tab, but usually the bigger lever than cutting any expense. One row per customer who owes you money."),
        ("Amount Outstanding", "The total dollar amount this customer currently owes you."),
        ("Terms Days", "What your stated payment terms are, e.g. net-30 is 30."),
        ("Days Outstanding", "How long the invoice has actually been unpaid, in days."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "This template has three tabs. Fill in your 13-week cash items (every inflow and "
        "outflow you can see coming) on the first tab. Fill in your recurring expenses, "
        "rated against the five Decision Filter questions, on the second tab. The third "
        "tab is optional: list any customer currently paying late against your own terms, "
        "since that's usually a bigger cash lever than any expense you could cut.",
        cash_notes + expense_notes + receivables_notes)
    ws1, first1, last1 = _data_sheet(wb, "Cash Items", milestone, tool, cash_headers, [10, 12, 24, 28, 14], cash_examples)
    ws2, first2, last2 = _data_sheet(wb, "Recurring Expenses", milestone, tool, expense_headers, [28, 16, 16, 18, 14, 20, 18], expense_examples)
    ws3, first3, last3 = _data_sheet(wb, "Receivables Aging", milestone, tool, receivables_headers, [24, 18, 14, 16], receivables_examples)
    add_range_validation(ws1, 1, 13, f"A{first1}:A{last1}")
    add_list_validation(ws1, ["inflow", "outflow"], f"B{first1}:B{last1}")
    for col in ("C", "D", "E", "F", "G"):
        add_range_validation(ws2, 1, 5, f"{col}{first2}:{col}{last2}")
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
    ]
    notes = [
        ("Constraint Name", "One row per candidate constraint from your Constraint Identification worksheet."),
        ("Process", "Which of your three mapped processes this constraint sits in."),
        ("Frequency Per Week", "How many times a week this constraint actually bites."),
        ("Hours Lost Per Occurrence", "Hours lost each time it happens."),
        ("Downstream Impact", "1 to 5. How much this blocks everything else in the business."),
        ("Automatable", "yes or no."),
        ("Automation Effort", "1 to 5, only matters if Automatable is yes. 1 is trivial, 5 is hard."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "List every candidate constraint across your three mapped processes. The tool "
        "ranks them all, names the single binding constraint to break first, and builds "
        "a separate automation hit list ranked by effort-adjusted payoff.",
        notes)
    ws, first, last = _data_sheet(wb, "Constraint Worksheet", milestone, tool, headers, [38, 16, 16, 20, 16, 12, 16], examples)
    add_list_validation(ws, ["yes", "no"], f"F{first}:F{last}")
    add_range_validation(ws, 1, 5, f"E{first}:E{last}")
    add_range_validation(ws, 1, 5, f"G{first}:G{last}")
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
        ("Current Delegation Level", "1 to 5. How much of this role you still personally hold today."),
        ("Target Delegation Level", "1 to 5. How much of this role should be delegated."),
        ("Key Outcome 1, 2, 3", "What this role owns, not just what it does day to day."),
        ("Decision Rights", "What this role can decide without coming back to you."),
        ("Success Metric", "How you'll know this role is working."),
    ]
    candidate_headers = ["Candidate Name", "Role Name", "Ownership", "Communication", "Judgment", "Coachability", "Results Track Record"]
    candidate_examples = [
        ["Jordan Reyes", "Operations Manager", 4, 4, 5, 4, 4],
    ]
    candidate_notes = [
        ("Candidate Name", "One row per candidate being considered."),
        ("Role Name", "Must match a Role Name on the Roles tab exactly."),
        ("Ownership, Communication, Judgment, Coachability, Results Track Record", "Each rated 1 to 5."),
    ]
    build_instructions_sheet(wb, milestone, tool,
        "This template has two tabs. Fill in your role inventory and delegation map on "
        "the first tab. If you're actively hiring, fill in your candidate list on the "
        "second tab, using the exact same Role Name as the first tab.",
        role_notes + candidate_notes)
    ws1, first1, last1 = _data_sheet(wb, "Roles", milestone, tool, role_headers, [24, 18, 18, 30, 30, 30, 30, 28], role_examples)
    ws2, first2, last2 = _data_sheet(wb, "Candidates", milestone, tool, candidate_headers, [24, 24, 12, 14, 12, 14, 18], candidate_examples)
    for col in ("B", "C"):
        add_range_validation(ws1, 1, 5, f"{col}{first1}:{col}{last1}")
    for col in ("C", "D", "E", "F", "G"):
        add_range_validation(ws2, 1, 5, f"{col}{first2}:{col}{last2}")
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
