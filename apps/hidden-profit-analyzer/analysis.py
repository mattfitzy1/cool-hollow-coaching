"""
Core analysis logic for the Cool Hollow Coaching hidden-profit analyzer.

Design rule: every figure is traceable straight back to a number in the uploaded P&L.
Nothing is invented, no benchmark is made up, and what-ifs are always labeled as what-ifs.

What an owner gets back:
  - Profit snapshot: gross margin, overhead, operating margin ("you keep X cents per dollar").
  - Where the money goes: the biggest cost lines, each as a share of revenue.
  - Your levers: what a price move or a margin point is worth, and the revenue needed
    to cover overhead. All clearly conditional.
  - Cost creep and cash timing: only when monthly columns are supplied (they need them).
  - A "how we read your file" table so nothing is taken on trust.

How lines are classified: a real P&L is read by its SECTION HEADERS (Income, Cost of
Goods Sold, Expenses), the way an accountant reads it, not by guessing from line names.
Files with no section headers (a bare CSV) fall back to keyword classification.
Subtotal/total rows are always excluded so nothing is double counted.
"""

import re

import pandas as pd

# Fallback keyword classification (only used when a file has no section headers).
REVENUE_KEYWORDS = ["revenue", "sales", "income", "turnover"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "cost of revenue", "direct cost"]

REVENUE_HEADERS = {"income", "revenue", "sales", "ordinary income", "service income",
                   "income / revenue", "revenues"}
COGS_HEADERS = {"cost of goods sold", "cost of sales", "cogs", "cost of revenue",
                "costs of goods sold"}
EXPENSE_HEADERS = {"expenses", "expense", "operating expenses", "operating expense",
                   "overhead", "general & administrative", "payroll expenses",
                   "selling general & administrative"}
OTHER_HEADERS = {"other income", "other expenses", "other expense",
                 "other income / expense", "other income/expense"}

TOTAL_PATTERNS = [
    "total", "subtotal", "sub-total", "gross profit", "gross margin", "gross income",
    "net profit", "net income", "net loss", "net ordinary income", "operating income",
    "operating profit", "ebitda", "ebit", "profit before tax", "income before tax",
    "profit/(loss)", "grand total", "bottom line",
]

MARGIN_SENSITIVITY_POINTS = 0.05
PRICE_SENSITIVITY = 0.01

_BLANK_CELLS = {"", "-"}


def _to_number(value) -> float:
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


def _strip_code(label: str) -> str:
    return re.sub(r"^(?:\d+\s+)+", "", str(label)).strip()


def _norm(label: str) -> str:
    s = _strip_code(label).lower().strip()
    s = re.sub(r"[^a-z0-9& ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_total_row(label: str) -> bool:
    t = label.lower().strip()
    return any(p in t for p in TOTAL_PATTERNS)


def _classify(label: str) -> str:
    text = label.lower()
    if any(k in text for k in COGS_KEYWORDS):
        return "cogs"
    if any(k in text for k in REVENUE_KEYWORDS):
        return "revenue"
    return "expense"


def _section_for(norm_label: str):
    if norm_label in REVENUE_HEADERS:
        return "revenue"
    if norm_label in COGS_HEADERS:
        return "cogs"
    if norm_label in EXPENSE_HEADERS:
        return "expense"
    if norm_label in OTHER_HEADERS:
        return "other"
    return None


def _amount_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c not in ("line_item", "category", "amount", "is_total")]


def _classify_rows(df: pd.DataFrame, amount_cols: list):
    def has_amount(row) -> bool:
        for c in amount_cols:
            v = row[c]
            if v is None:
                continue
            if isinstance(v, float) and pd.isna(v):
                continue
            if str(v).strip() == "":
                continue
            return True
        return False

    categories, totals = [], []
    current = None
    for _, row in df.iterrows():
        label = str(row["line_item"]).strip()
        if _is_total_row(label):
            categories.append(current or "other")
            totals.append(True)
            continue
        section = _section_for(_norm(label)) if not has_amount(row) else None
        if section is not None:
            current = section
            categories.append(section)
            totals.append(False)
            continue
        categories.append(current if current is not None else _classify(label))
        totals.append(False)
    return categories, totals


def load_pnl(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "line_item" not in df.columns:
        df = df.rename(columns={df.columns[0]: "line_item"})
    df["line_item"] = df["line_item"].astype(str).str.strip()
    df = df[df["line_item"].str.len() > 0]

    amount_cols = _amount_columns(df)
    if not amount_cols:
        if "amount" not in df.columns:
            raise ValueError("Could not find any amount columns in the uploaded file.")
        amount_cols = ["amount"]

    categories, totals = _classify_rows(df, amount_cols)
    df["category"] = categories
    df["is_total"] = totals

    month_cols = [c for c in amount_cols if c != "amount"]
    if month_cols:
        df = df.melt(id_vars=["line_item", "category", "is_total"], value_vars=month_cols,
                     var_name="month", value_name="amount")
        df["month"] = pd.Categorical(df["month"], categories=month_cols, ordered=True)
    else:
        df["month"] = "total period"

    df["amount"] = df["amount"].apply(_to_number)
    return df[["category", "line_item", "month", "amount", "is_total"]]


def _detail(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["is_total"]]


def _sums(df: pd.DataFrame):
    work = _detail(df)
    revenue = work[work["category"] == "revenue"]["amount"].sum()
    cogs = work[work["category"] == "cogs"]["amount"].sum()
    opex = work[work["category"] == "expense"]["amount"].sum()
    return float(revenue), float(cogs), float(opex)


def _ordered_months(df: pd.DataFrame) -> list:
    col = df["month"]
    if isinstance(col.dtype, pd.CategoricalDtype):
        present = set(col)
        return [m for m in col.cat.categories if m in present]
    return list(dict.fromkeys(col))


def classification_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["read_as"] = work.apply(
        lambda r: "skipped (subtotal/total row)" if r["is_total"] else r["category"], axis=1
    )
    grouped = (work.groupby(["line_item", "read_as"])["amount"]
               .sum().reset_index().sort_values("amount", ascending=False))
    return grouped.rename(columns={"line_item": "line item", "amount": "amount"})


def profit_snapshot(df: pd.DataFrame) -> dict:
    """The headline picture: gross margin, overhead, and operating margin in plain English."""
    revenue, cogs, opex = _sums(df)
    findings = []
    if revenue <= 0:
        findings.append("No revenue was found, so the profit picture could not be built.")
        return {"name": "Profit snapshot", "revenue": revenue, "cogs": cogs, "opex": opex,
                "gross_margin": None, "operating_margin": None, "findings": findings}

    gross_profit = revenue - cogs
    gross_margin = gross_profit / revenue
    operating_income = gross_profit - opex
    operating_margin = operating_income / revenue

    findings.append(
        f"Revenue ${revenue:,.0f}. After ${cogs:,.0f} cost of goods, gross profit is "
        f"${gross_profit:,.0f}, a gross margin of {gross_margin:.0%}."
    )
    findings.append(
        f"After ${opex:,.0f} of overhead, operating profit is ${operating_income:,.0f}, "
        f"an operating margin of {operating_margin:.0%}."
    )
    cents = operating_margin * 100
    if operating_income >= 0:
        findings.append(f"In plain terms: you keep about {cents:.0f} cents of every dollar "
                        f"of revenue after cost of goods and overhead.")
    else:
        findings.append(f"In plain terms: right now overhead and cost of goods take more "
                        f"than every dollar of revenue. You are about {abs(cents):.0f} cents "
                        f"underwater per dollar before any other income.")
    return {"name": "Profit snapshot", "revenue": revenue, "cogs": cogs, "opex": opex,
            "gross_margin": gross_margin, "operating_margin": operating_margin,
            "findings": findings}


def where_money_goes(df: pd.DataFrame, top_n: int = 5) -> dict:
    """The biggest cost lines, each as a share of revenue. Factual and eye-opening."""
    work = _detail(df)
    revenue, cogs, opex = _sums(df)
    costs = work[work["category"].isin(["cogs", "expense"])]
    findings = []
    rows = []
    if costs.empty:
        findings.append("No cost lines were found.")
        return {"name": "Where the money goes", "rows": rows, "findings": findings}

    by_line = costs.groupby("line_item")["amount"].sum().sort_values(ascending=False)
    total_cost = float(by_line.sum())
    for line_item, amount in by_line.head(top_n).items():
        share = (amount / revenue) if revenue > 0 else None
        rows.append({"line_item": line_item, "amount": float(amount), "share_of_revenue": share})

    if revenue > 0:
        findings.append(f"Your costs total ${total_cost:,.0f}, about {total_cost/revenue:.0%} "
                        f"of revenue.")
        biggest = by_line.index[0]
        findings.append(f"The single biggest is \"{biggest}\" at ${by_line.iloc[0]:,.0f} "
                        f"({by_line.iloc[0]/revenue:.0%} of revenue). That is your largest lever.")
    return {"name": "Where the money goes", "rows": rows, "total_cost": total_cost,
            "findings": findings}


def leverage(df: pd.DataFrame) -> dict:
    """Clearly-conditional what-ifs: what a price move or margin point is worth, and the
    revenue needed to cover overhead. Never claimed as money already found."""
    revenue, cogs, opex = _sums(df)
    findings = []
    if revenue <= 0:
        return {"name": "Your levers", "opportunity": 0.0, "findings":
                ["No revenue found, so the levers could not be sized."]}

    gross_margin = (revenue - cogs) / revenue
    margin_point = round(MARGIN_SENSITIVITY_POINTS * revenue, 2)
    price_move = round(PRICE_SENSITIVITY * revenue, 2)

    findings.append(
        f"A 1% price increase, if every customer stayed, is about ${price_move:,.0f} a "
        f"period, and most of it drops to the bottom line. A what-if, not a promise."
    )
    findings.append(
        f"Every 5 points of gross margin is worth about ${margin_point:,.0f} a period at "
        f"this revenue. That is the prize if pricing or cost of delivery improves."
    )
    if gross_margin > 0:
        breakeven = opex / gross_margin
        findings.append(
            f"At this gross margin, you need about ${breakeven:,.0f} of revenue just to "
            f"cover overhead. Everything above that is where profit is made. (An estimate "
            f"that assumes margin holds.)"
        )
    return {"name": "Your levers", "opportunity": margin_point, "price_move": price_move,
            "findings": findings}


def check_cost_creep(df: pd.DataFrame, threshold: float = 0.15) -> dict:
    work = _detail(df)
    expenses = work[work["category"].isin(["expense", "cogs"])]
    findings = []
    creep_total = 0.0
    items = []

    if expenses.empty:
        findings.append("No cost lines were found to check.")
        return {"name": "Cost creep", "creep": 0.0, "findings": findings}

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
                f"\"{line_item}\" rose {growth:.0%} from {first_m} to {last_m} "
                f"(${start:,.0f} to ${end:,.0f}), an increase of ${increase:,.0f}. "
                f"Worth checking the contract or usage."
            )
        if not items:
            findings.append("No single cost line grew sharply across the months given.")
    else:
        findings.append("Only one period was provided, so month-to-month creep could not be "
                        "checked. Upload a P&L with a column per month to switch this on.")

    return {"name": "Cost creep", "creep": round(creep_total, 2), "findings": findings}


def check_cash_timing(df: pd.DataFrame) -> dict:
    work = _detail(df)
    findings = []
    shortfall = 0.0

    if work["month"].nunique() < 2:
        findings.append("Only one period was provided, so a cash timing trend could not be "
                        "checked. Upload a P&L with a column per month to switch this on.")
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
    return {
        "snapshot": profit_snapshot(pnl),
        "where": where_money_goes(pnl),
        "leverage": leverage(pnl),
        "creep": check_cost_creep(pnl),
        "cash": check_cash_timing(pnl),
        "breakdown": classification_breakdown(pnl),
    }
