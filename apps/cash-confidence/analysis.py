"""
Core forecasting and scoring logic for Business Without You Cash Confidence.

This is Milestone 5's model. The owner runs the exercise first: pull AR/AP
data and payment timing into a week-by-week cash item list (13 weeks out),
and list every recurring expense rated against the five-question Financial
Decision Filter.

This module takes those two sheets and produces:
1. A 13-week rolling cash forecast (starting balance, weekly net, running
   balance, and which weeks go negative).
2. The Financial Decision Filter scored against every recurring expense,
   flagging weak-case spend as a cut candidate.
3. An adjusted forecast showing what the 13 weeks look like if every cut
   candidate actually gets cut starting next week, so the dollar impact of
   acting on the filter is visible against the cash position itself.

A third, optional sheet (the AR aging list) drives a fourth check:
receivables timing. The Decision Filter only ever catches discretionary
spend worth cutting, which does nothing for the most common real cash
problem in this program's buyer profile: a $1M-$10M owner-operator with
one or two large customers paying late against their own stated terms.
This check names exactly how much cash is sitting overdue beyond the
client's own terms, separate from and usually much larger than whatever
the Decision Filter finds.
"""

import pandas as pd

TOTAL_WEEKS = 13
FILTER_QUESTIONS = [
    "core_customer_fit",
    "revenue_risk_if_cut",
    "roi_clarity",
    "no_cheaper_alternative",
    "would_approve_today",
]
DECISION_PASS_THRESHOLD = 3.0


def load_cash_items(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded week-by-week cash item list."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"week", "type", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Cash item list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: week (1-13), type (inflow or outflow), amount, and "
            f"optionally category, description."
        )

    df["week"] = pd.to_numeric(df["week"], errors="coerce").fillna(0).astype(int).clip(1, TOTAL_WEEKS)
    df["type"] = df["type"].astype(str).str.strip().str.lower()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0).abs()

    bad_types = set(df["type"]) - {"inflow", "outflow"}
    if bad_types:
        raise ValueError(
            f"Found type value(s) not recognized: {', '.join(sorted(bad_types))}. "
            f"Each row's type must be inflow or outflow."
        )

    if "category" not in df.columns:
        df["category"] = "uncategorized"
    if "description" not in df.columns:
        df["description"] = ""

    return df[["week", "type", "category", "description", "amount"]]


def load_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded recurring expense list with Decision Filter ratings."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"expense_name", "weekly_amount"} | set(FILTER_QUESTIONS)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Expense list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: expense_name, weekly_amount, and the five Decision Filter "
            f"ratings (1-5): {', '.join(FILTER_QUESTIONS)}."
        )

    df["expense_name"] = df["expense_name"].astype(str)
    df["weekly_amount"] = pd.to_numeric(df["weekly_amount"], errors="coerce").fillna(0).abs()
    for q in FILTER_QUESTIONS:
        df[q] = pd.to_numeric(df[q], errors="coerce").fillna(0).clip(0, 5)

    return df[["expense_name", "weekly_amount"] + FILTER_QUESTIONS]


def load_receivables(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded AR aging list."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"customer_name", "amount_outstanding", "terms_days", "days_outstanding"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Receivables list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: customer_name, amount_outstanding, terms_days (what your terms "
            f"say, e.g. net-30 is 30), days_outstanding (how long it's actually been "
            f"unpaid)."
        )

    df["customer_name"] = df["customer_name"].astype(str)
    df["amount_outstanding"] = pd.to_numeric(df["amount_outstanding"], errors="coerce").fillna(0).abs()
    df["terms_days"] = pd.to_numeric(df["terms_days"], errors="coerce").fillna(30).abs()
    df["days_outstanding"] = pd.to_numeric(df["days_outstanding"], errors="coerce").fillna(0).abs()

    return df[["customer_name", "amount_outstanding", "terms_days", "days_outstanding"]]


def run_receivables_check(receivables: pd.DataFrame) -> dict:
    """Name exactly how much cash is sitting overdue beyond the client's own terms."""
    if receivables.empty:
        return {"overdue_amount": 0.0, "total_outstanding": 0.0, "overdue_accounts": []}

    df = receivables.copy()
    df["days_overdue"] = (df["days_outstanding"] - df["terms_days"]).clip(lower=0)
    overdue = df[df["days_overdue"] > 0].sort_values("amount_outstanding", ascending=False)

    overdue_accounts = []
    for _, row in overdue.iterrows():
        overdue_accounts.append({
            "customer_name": row["customer_name"],
            "amount_outstanding": round(row["amount_outstanding"], 2),
            "terms_days": int(row["terms_days"]),
            "days_outstanding": int(row["days_outstanding"]),
            "days_overdue": int(row["days_overdue"]),
        })

    return {
        "overdue_amount": round(overdue["amount_outstanding"].sum(), 2),
        "total_outstanding": round(df["amount_outstanding"].sum(), 2),
        "overdue_accounts": overdue_accounts,
    }


def _weekly_balances(cash_items: pd.DataFrame, starting_balance: float) -> list:
    weekly_net = {w: 0.0 for w in range(1, TOTAL_WEEKS + 1)}
    for _, row in cash_items.iterrows():
        sign = 1 if row["type"] == "inflow" else -1
        weekly_net[row["week"]] += sign * row["amount"]

    balances = []
    running = starting_balance
    for week in range(1, TOTAL_WEEKS + 1):
        running += weekly_net[week]
        balances.append({"week": week, "net": round(weekly_net[week], 2), "balance": round(running, 2)})
    return balances


def run_decision_filter(expenses: pd.DataFrame) -> dict:
    """Score every recurring expense against the five-question filter."""
    if expenses.empty:
        return {"keep": [], "cut_candidates": [], "weekly_savings_if_cut": 0.0}

    df = expenses.copy()
    df["composite"] = df[FILTER_QUESTIONS].mean(axis=1)
    df["passes"] = df["composite"] >= DECISION_PASS_THRESHOLD

    keep, cut_candidates = [], []
    for _, row in df.sort_values("composite").iterrows():
        weak_questions = [q for q in FILTER_QUESTIONS if row[q] < DECISION_PASS_THRESHOLD]
        entry = {
            "expense_name": row["expense_name"],
            "weekly_amount": round(row["weekly_amount"], 2),
            "composite": round(row["composite"], 1),
        }
        if row["passes"]:
            entry["reasoning"] = "Clears the filter, the case to keep it holds up."
            keep.append(entry)
        else:
            entry["reasoning"] = "Weak case on: " + ", ".join(q.replace("_", " ") for q in weak_questions) + "."
            cut_candidates.append(entry)

    weekly_savings = round(sum(c["weekly_amount"] for c in cut_candidates), 2)
    return {"keep": keep, "cut_candidates": cut_candidates, "weekly_savings_if_cut": weekly_savings}


def run_cash_confidence(cash_items_raw: pd.DataFrame, expenses_raw: pd.DataFrame, starting_balance: float,
                         receivables_raw: pd.DataFrame = None) -> dict:
    cash_items = load_cash_items(cash_items_raw)
    expenses = load_expenses(expenses_raw)

    receivables_result = {"overdue_amount": 0.0, "total_outstanding": 0.0, "overdue_accounts": []}
    if receivables_raw is not None and not receivables_raw.empty:
        receivables = load_receivables(receivables_raw)
        receivables_result = run_receivables_check(receivables)

    baseline = _weekly_balances(cash_items, starting_balance)

    filter_result = run_decision_filter(expenses)
    cut_names = {c["expense_name"] for c in filter_result["cut_candidates"]}

    # Cut candidates reduce outflow from next week (week 2) onward, matched by
    # category or description against the expense name since cash items and
    # expenses are tracked separately by the owner. Week 1 is left alone
    # since that spend is already committed.
    adjusted_items = cash_items.copy()
    if cut_names:
        is_cut_expense = adjusted_items["description"].isin(cut_names) | adjusted_items["category"].isin(cut_names)
        drop_mask = is_cut_expense & (adjusted_items["week"] > 1)
        adjusted_items = adjusted_items[~drop_mask]

    adjusted = _weekly_balances(adjusted_items, starting_balance)

    baseline_negative_weeks = [w["week"] for w in baseline if w["balance"] < 0]
    adjusted_negative_weeks = [w["week"] for w in adjusted if w["balance"] < 0]

    return {
        "starting_balance": starting_balance,
        "baseline_forecast": baseline,
        "adjusted_forecast": adjusted,
        "baseline_negative_weeks": baseline_negative_weeks,
        "adjusted_negative_weeks": adjusted_negative_weeks,
        "decision_filter": filter_result,
        "receivables": receivables_result,
    }
