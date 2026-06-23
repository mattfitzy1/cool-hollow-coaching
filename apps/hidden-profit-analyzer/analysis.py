"""
Core analysis logic for the Cool Hollow Coaching hidden-profit analyzer.

Design rule: every figure this returns must be traceable straight back to a number
in the uploaded P&L. It reports three things, kept SEPARATE and labeled honestly:

  1. Margin: the actual gross margin, plus a clearly-conditional sensitivity
     ("each 5 points of margin is worth $X"). Never a claimed "found" amount.
  2. Cost creep: line items that genuinely grew month to month, with the real increase.
  3. Cash timing: months where money out exceeded money in, straight from the numbers.

It never blends those into a single "profit found" headline, and it never invents a
benchmark or a number the P&L does not support. Subtotal/total rows are excluded so
nothing is double counted.
"""

import re

import pandas as pd

REVENUE_KEYWORDS = ["revenue", "sales", "income", "turnover"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "cost of revenue", "direct cost"]

# Derived / subtotal / total rows. These summarize other rows, so counting them
# as well would double count. They are detected and held out of every calculation.
TOTAL_PATTERNS = [
    "total", "subtotal", "sub-total", "gross profit", "gross margin", "gross income",
    "net profit", "net income", "net loss", "net ordinary income", "operating income",
    "operating profit", "ebitda", "ebit", "profit before tax", "income before tax",
    "profit/(loss)", "grand total", "bottom line",
]

MARGIN_SENSITIVITY_POINTS = 0.05  # report the value of a 5-point gross-margin move

# Cell values that mean "empty". Anything else unparseable already returns 0 below.
_BLANK_CELLS = {"", "-"}


def _to_number(value) -> float:
    """Turn a messy cell ($1,200, (500)) into a float. Unparseable cells become 0."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    s = str(value).strip()
    negative = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[,$()%\s]", "", s)
    if s in _BLANK_CELLS:
        return 0.0
    try:
        number = float(s)
    except ValueError:
        return 0.0
    return -number if negative else number


def _is_total_row(line_item: str) -> bool:
    t = line_item.lower().strip()
    return any(p in t for p in TOTAL_PATTERNS)


def _classify(line_item: str) -> str:
    text = line_item.lower()
    # COGS first: "cost of sales" contains "sales", which would otherwise read as revenue.
    if any(k in text for k in COGS_KEYWORDS):
        return "cogs"
    if any(k in text for k in REVENUE_KEYWORDS):
        return "revenue"
    # On a P&L, any remaining non-total line is a cost. Defaulting to expense (rather
    # than silently dropping unknown labels like "Utilities" or "Insurance") keeps the
    # totals honest.
    return "expense"


def load_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a raw uploaded P&L into category, line_item, month, amount, is_total."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "line_item" not in df.columns:
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "line_item"})

    month_cols = [c for c in df.columns if c not in ("line_item", "category", "amount")]

    if month_cols:
        df = df.melt(id_vars=["line_item"], value_vars=month_cols,
                     var_name="month", value_name="amount")
        # Preserve the column order the user gave (Jan, Feb, Mar...). Sorting month
        # labels alphabetically would put "feb" before "jan" and break trend checks.
        df["month"] = pd.Categorical(df["month"], categories=month_cols, ordered=True)
    elif "amount" in df.columns:
        df["month"] = "total period"
    else:
        raise ValueError("Could not find any amount columns in the uploaded file.")

    df["amount"] = df["amount"].apply(_to_number)
    df["line_item"] = df["line_item"].astype(str).str.strip()
    df = df[df["line_item"].str.len() > 0]
    df["is_total"] = df["line_item"].apply(_is_total_row)
    df["category"] = df["line_item"].apply(_classify)
    return df[["category", "line_item", "month", "amount", "is_total"]]


def _detail(df: pd.DataFrame) -> pd.DataFrame:
    """Just the real line items, with subtotal/total rows removed."""
    return df[~df["is_total"]]


def _ordered_months(df: pd.DataFrame) -> list:
    """Months in the order the user supplied them, not alphabetical."""
    col = df["month"]
    if isinstance(col.dtype, pd.CategoricalDtype):
        present = set(col)
        return [m for m in col.cat.categories if m in present]
    return list(dict.fromkeys(col))


def classification_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """A transparency table: how each line item was read. Shown to the user so they
    can sanity-check that nothing was misread before trusting the numbers."""
    work = df.copy()
    work["read_as"] = work.apply(
        lambda r: "skipped (subtotal/total row)" if r["is_total"] else r["category"], axis=1
    )
    grouped = (work.groupby(["line_item", "read_as"])["amount"]
               .sum().reset_index().sort_values("amount", ascending=False))
    return grouped.rename(columns={"line_item": "line item", "amount": "amount"})


def check_pricing_margin(df: pd.DataFrame) -> dict:
    work = _detail(df)
    revenue = work[work["category"] == "revenue"]["amount"].sum()
    cogs = work[work["category"] == "cogs"]["amount"].sum()

    findings = []
    opportunity = 0.0
    margin = None

    if revenue <= 0:
        findings.append("No revenue line was found, so a margin read could not be run.")
        return {"name": "Pricing and margin", "opportunity": 0.0,
                "gross_margin": None, "findings": findings}

    gross_profit = revenue - cogs
    margin = gross_profit / revenue
    findings.append(
        f"On the numbers given, revenue is ${revenue:,.0f} and cost of goods is "
        f"${cogs:,.0f}, a gross margin of {margin:.0%} (${gross_profit:,.0f} gross profit)."
    )

    # Honest, clearly-conditional sensitivity. Not a claim that this money exists today.
    per_point = MARGIN_SENSITIVITY_POINTS * revenue
    opportunity = round(per_point, 2)
    findings.append(
        f"For scale: every 5 points of gross margin is worth about ${per_point:,.0f} a "
        f"period at this revenue. That is the prize if pricing or cost of delivery improves. "
        f"It is a what-if, not money sitting in the account today."
    )
    return {"name": "Pricing and margin", "opportunity": opportunity,
            "gross_margin": margin, "findings": findings}


def check_cost_creep(df: pd.DataFrame, threshold: float = 0.15) -> dict:
    work = _detail(df)
    expenses = work[work["category"].isin(["expense", "cogs"])]

    findings = []
    creep_total = 0.0
    items = []

    if expenses.empty:
        findings.append("No cost lines were found to check.")
        return {"name": "Cost creep", "creep": 0.0, "findings": findings}

    by_line = expenses.groupby("line_item")["amount"].sum().sort_values(ascending=False)
    total_expense = by_line.sum()

    months_in_order = _ordered_months(expenses)
    if len(months_in_order) > 1:
        first_m, last_m = months_in_order[0], months_in_order[-1]
        start_by = expenses[expenses["month"] == first_m].groupby("line_item")["amount"].sum()
        end_by = expenses[expenses["month"] == last_m].groupby("line_item")["amount"].sum()
        for line_item in end_by.index:
            start = float(start_by.get(line_item, 0.0))
            end = float(end_by.get(line_item, 0.0))
            if start > 0 and end > start:
                growth = (end - start) / start
                if growth > threshold:
                    increase = round(end - start, 2)
                    creep_total += increase
                    items.append((line_item, start, end, growth, increase))

    items.sort(key=lambda x: x[4], reverse=True)
    for line_item, start, end, growth, increase in items:
        findings.append(
            f"\"{line_item}\" rose {growth:.0%} from {first_m} to "
            f"{last_m} (${start:,.0f} to ${end:,.0f}), an increase of "
            f"${increase:,.0f}. Worth checking the contract or usage."
        )

    top_3 = by_line.head(3)
    findings.append(
        "Largest costs overall: "
        + ", ".join(f"\"{k}\" (${v:,.0f})" for k, v in top_3.items())
        + f", out of ${total_expense:,.0f} total."
    )
    if not items and expenses["month"].nunique() > 1:
        findings.append("No single cost line grew sharply across the months given.")
    elif expenses["month"].nunique() <= 1:
        findings.append("Only one period was provided, so month-to-month creep could "
                        "not be checked. Upload several months for this.")

    return {"name": "Cost creep", "creep": round(creep_total, 2), "findings": findings}


def check_cash_timing(df: pd.DataFrame) -> dict:
    work = _detail(df)
    findings = []
    shortfall = 0.0

    if work["month"].nunique() < 2:
        findings.append("Only one period was provided, so a cash timing trend could not "
                        "be checked. Upload at least two months side by side for this.")
        return {"name": "Cash timing", "shortfall": 0.0, "findings": findings}

    rev = work[work["category"] == "revenue"].groupby("month", observed=True)["amount"].sum()
    cost = work[work["category"].isin(["cogs", "expense"])].groupby("month", observed=True)["amount"].sum()
    months = _ordered_months(work)
    net = {m: float(rev.get(m, 0.0) - cost.get(m, 0.0)) for m in months}

    negative = {m: v for m, v in net.items() if v < 0}
    if negative:
        shortfall = round(sum(abs(v) for v in negative.values()), 2)
        findings.append(
            f"{len(negative)} of {len(months)} months show more going out than coming in: "
            + ", ".join(f"{m} (${v:,.0f})" for m, v in negative.items())
            + ". This is a timing gap a 13-week cash forecast is built to see coming."
        )
    else:
        findings.append("Every month provided shows money in ahead of money out. "
                        "No timing gap flagged.")
    return {"name": "Cash timing", "shortfall": shortfall, "findings": findings}


def run_full_analysis(df: pd.DataFrame) -> dict:
    pnl = load_pnl(df)
    margin = check_pricing_margin(pnl)
    creep = check_cost_creep(pnl)
    cash = check_cash_timing(pnl)
    return {
        "margin": margin,
        "creep": creep,
        "cash": cash,
        "breakdown": classification_breakdown(pnl),
    }
