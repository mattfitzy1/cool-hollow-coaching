"""
Core analysis logic for the Business Without You Profit Discovery Audit.

This is Milestone 4 of the curriculum: the in-program audit a paying
client runs in week 7, covering all five areas Mark's framework defines.
Unlike the hidden-profit-analyzer lead magnet (P&L only, three checks), this
tool also takes a customer/service breakdown sheet so it can check
customer profitability and product/service mix, the two areas a P&L alone
cannot answer.

Takes:
- a parsed P&L (category, line_item, month, amount)
- a parsed breakdown sheet (type: "customer" or "service", name, revenue, direct_cost)

Returns five findings with plain-English explanations and a dollar estimate
each, summed into one headline number.

All revenue-scaled estimates (pricing gaps, customer profitability, service
mix, revenue leakage) are annualized using period_months, the number of
months the uploaded P&L actually covers. Without this, the same business
would show a 4x bigger "profit found" number from a 12-month upload than
from a 3-month upload of identical margins, since the benchmark-gap math
multiplies a percentage gap by however much revenue happens to be in the
file. The headline number is meant to be an annual figure regardless of
how many months the client uploads.

The margin benchmarks are also industry-aware (BUSINESS_TYPE_BENCHMARKS)
rather than one fixed 50%/20% for every business. A vehicle repair shop or
distributor running real cost of goods will never clear a 50% gross margin
benchmark built for a services or software business, which would otherwise
make every client in a lower-margin trade look like it has a pricing
problem it doesn't actually have.
"""

import pandas as pd

REVENUE_KEYWORDS = ["revenue", "sales", "income"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "direct cost"]
EXPENSE_KEYWORDS = ["expense", "overhead", "operating", "subscription", "software",
                    "rent", "salaries", "payroll", "marketing", "advertising", "fees"]
LEAKAGE_KEYWORDS = ["discount", "write-off", "writeoff", "credit memo", "bad debt", "refund"]

HIGH_GROWTH_FLAG = 0.15
MONTHS_PER_YEAR = 12

BUSINESS_TYPE_BENCHMARKS = {
    "Professional services, coaching, or agency (default)": {"gross_margin": 0.50, "line_margin": 0.20},
    "Software or other high-margin recurring revenue": {"gross_margin": 0.65, "line_margin": 0.30},
    "Trades, field service, or repair": {"gross_margin": 0.35, "line_margin": 0.15},
    "Retail, distribution, or resale": {"gross_margin": 0.30, "line_margin": 0.12},
}
DEFAULT_BUSINESS_TYPE = "Professional services, coaching, or agency (default)"


def _classify(line_item: str) -> str:
    text = line_item.lower()
    if any(k in text for k in LEAKAGE_KEYWORDS):
        return "leakage"
    if any(k in text for k in REVENUE_KEYWORDS):
        return "revenue"
    if any(k in text for k in COGS_KEYWORDS):
        return "cogs"
    if any(k in text for k in EXPENSE_KEYWORDS):
        return "expense"
    return "other"


def load_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a raw uploaded P&L into category, line_item, amount, and month columns."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    if "line_item" not in df.columns:
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "line_item"})

    month_cols = [c for c in df.columns if c not in ("line_item", "category", "amount")]

    if month_cols:
        df = df.melt(id_vars=["line_item"], value_vars=month_cols,
                      var_name="month", value_name="amount")
    elif "amount" in df.columns:
        df["month"] = "total"
    else:
        raise ValueError("Could not find amount columns in the uploaded P&L.")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["line_item"] = df["line_item"].astype(str)
    df["category"] = df["line_item"].apply(_classify)
    return df[["category", "line_item", "month", "amount"]]


def load_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the customer/service breakdown sheet into type, name, revenue, direct_cost."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"type", "name", "revenue", "direct_cost"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Breakdown sheet is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: type, name, revenue, direct_cost."
        )

    df["type"] = df["type"].astype(str).str.strip().str.lower()
    df["name"] = df["name"].astype(str)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    df["direct_cost"] = pd.to_numeric(df["direct_cost"], errors="coerce").fillna(0)
    return df[["type", "name", "revenue", "direct_cost"]]


def check_pricing_gaps(pnl: pd.DataFrame, healthy_gross_margin: float, annualize_factor: float) -> dict:
    revenue = pnl[pnl["category"] == "revenue"]["amount"].sum()
    cogs = pnl[pnl["category"] == "cogs"]["amount"].sum()

    findings = []
    estimate = 0.0

    if revenue > 0:
        gross_margin = (revenue - cogs) / revenue
        if gross_margin < healthy_gross_margin:
            gap = healthy_gross_margin - gross_margin
            estimate = round(gap * revenue * annualize_factor, 2)
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, below the {healthy_gross_margin:.0%} "
                f"benchmark for this kind of business. Closing that gap through pricing or delivery "
                f"cost changes is worth roughly ${estimate:,.0f} a year."
            )
        else:
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, at or above the "
                f"{healthy_gross_margin:.0%} benchmark for this kind of business. No major pricing "
                f"gap found here."
            )
    else:
        findings.append("No revenue line found in the P&L, so a pricing gap check could not be run.")

    return {"name": "Pricing gaps", "estimate": estimate, "findings": findings}


def _chronological_months(months) -> list:
    """Sort month labels chronologically, not alphabetically.

    Alphabetical sort puts "Apr" before "Jan", which silently breaks the
    growth-trend check for any P&L using month names instead of ISO dates.
    Falls back to alphabetical only if the labels can't be parsed as dates.
    """
    months = list(months)
    parsed = [pd.to_datetime(str(m), errors="coerce") for m in months]
    if all(pd.notna(p) for p in parsed):
        return [m for m, _ in sorted(zip(months, parsed), key=lambda pair: pair[1])]
    return sorted(months)


def check_cost_inefficiencies(pnl: pd.DataFrame) -> dict:
    expenses = pnl[pnl["category"] == "expense"]

    findings = []
    estimate = 0.0

    if expenses.empty:
        findings.append("No expense lines were found to check for inefficiency.")
        return {"name": "Cost structure inefficiencies", "estimate": estimate, "findings": findings}

    by_line = expenses.groupby("line_item")["amount"].sum().sort_values(ascending=False)
    total_expense = by_line.sum()

    if expenses["month"].nunique() > 1:
        pivot = expenses.pivot_table(index="line_item", columns="month", values="amount", aggfunc="sum").fillna(0)
        months_sorted = _chronological_months(pivot.columns)
        if len(months_sorted) >= 2:
            first, last = pivot[months_sorted[0]], pivot[months_sorted[-1]]
            for line_item in pivot.index:
                start, end = first.get(line_item, 0), last.get(line_item, 0)
                if start > 0:
                    growth = (end - start) / start
                    if growth > HIGH_GROWTH_FLAG and end > 0:
                        monthly_increase = round(end - start, 2)
                        annualized_risk = round(monthly_increase * MONTHS_PER_YEAR, 2)
                        estimate += annualized_risk
                        findings.append(
                            f"\"{line_item}\" grew {growth:.0%} from {months_sorted[0]} to "
                            f"{months_sorted[-1]} (${start:,.0f} to ${end:,.0f}). If that pace holds, "
                            f"it costs roughly ${annualized_risk:,.0f} a year versus where it started."
                        )

    top_3 = by_line.head(3)
    findings.append(
        "Largest recurring costs: " + ", ".join(f"\"{k}\" (${v:,.0f})" for k, v in top_3.items()) +
        f", out of ${total_expense:,.0f} total expense."
    )

    if not estimate:
        findings.append("No clear runaway cost trend found across the months provided. "
                         "Worth a manual look at vendor contracts and subscriptions even so.")

    return {"name": "Cost structure inefficiencies", "estimate": round(estimate, 2), "findings": findings}


def _profitability_check(breakdown: pd.DataFrame, row_type: str, label: str,
                          healthy_line_margin: float, annualize_factor: float) -> dict:
    rows = breakdown[breakdown["type"] == row_type]

    findings = []
    estimate = 0.0

    if rows.empty:
        findings.append(
            f"No \"{row_type}\" rows found in the breakdown sheet, so this could not be checked. "
            f"Add a row per {row_type} with revenue and direct_cost to run it."
        )
        return {"name": label, "estimate": estimate, "findings": findings}

    rows = rows.copy()
    rows["margin"] = (rows["revenue"] - rows["direct_cost"]) / rows["revenue"].replace(0, pd.NA)
    underperformers = rows[(rows["margin"].notna()) & (rows["margin"] < healthy_line_margin)]

    if underperformers.empty:
        findings.append(f"Every {row_type} is at or above the {healthy_line_margin:.0%} margin benchmark. "
                         f"No major gap found here.")
        return {"name": label, "estimate": estimate, "findings": findings}

    for _, r in underperformers.sort_values("margin").iterrows():
        gap = healthy_line_margin - r["margin"]
        line_estimate = round(gap * r["revenue"] * annualize_factor, 2)
        estimate += line_estimate
        margin_text = f"{r['margin']:.0%}" if r["margin"] >= 0 else f"-{abs(r['margin']):.0%}"
        findings.append(
            f"\"{r['name']}\" is running at a {margin_text} margin on ${r['revenue']:,.0f} of revenue "
            f"for the period uploaded. Bringing it to the {healthy_line_margin:.0%} benchmark is worth "
            f"roughly ${line_estimate:,.0f} a year."
        )

    return {"name": label, "estimate": round(estimate, 2), "findings": findings}


def check_customer_profitability(breakdown: pd.DataFrame, healthy_line_margin: float, annualize_factor: float) -> dict:
    return _profitability_check(breakdown, "customer", "Customer profitability differences",
                                 healthy_line_margin, annualize_factor)


def check_service_mix(breakdown: pd.DataFrame, healthy_line_margin: float, annualize_factor: float) -> dict:
    return _profitability_check(breakdown, "service", "Service or product mix problems",
                                 healthy_line_margin, annualize_factor)


def check_revenue_leakage(pnl: pd.DataFrame, annualize_factor: float) -> dict:
    leakage = pnl[pnl["category"] == "leakage"]

    findings = []
    estimate = 0.0

    if leakage.empty:
        findings.append(
            "No discount, write-off, credit memo, or refund lines were found in the P&L to flag "
            "automatically. Revenue leakage from unbilled work or missed upsells will not show up "
            "in a P&L. That needs a manual look at invoicing and billing records."
        )
        return {"name": "Revenue leakage points", "estimate": estimate, "findings": findings}

    by_line = leakage.groupby("line_item")["amount"].sum().sort_values(ascending=False)
    estimate = round(by_line.sum() * annualize_factor, 2)
    findings.append(
        "Flagged leakage lines for the period uploaded: " +
        ", ".join(f"\"{k}\" (${v:,.0f})" for k, v in by_line.items()) +
        f", roughly ${estimate:,.0f} a year at that pace."
    )
    findings.append(
        "This only catches what is already recorded as a discount, write-off, or refund. Unbilled "
        "work and missed upsells will not appear here, so still worth a manual look at invoicing."
    )

    return {"name": "Revenue leakage points", "estimate": estimate, "findings": findings}


def run_full_audit(pnl_raw: pd.DataFrame, breakdown_raw: pd.DataFrame,
                    business_type: str = DEFAULT_BUSINESS_TYPE, period_months: float = 12.0) -> dict:
    """Run all five checks, annualized to a consistent yearly figure.

    period_months is how many months the uploaded P&L and breakdown sheet
    actually cover (the client states this, it is not inferred from column
    headers, since labels like "Q1" or "Period 1" can't be parsed reliably).
    Every revenue-scaled estimate is annualized to 12/period_months so the
    headline number means the same thing whether a client uploads 3 months
    or a full year, and reflects the actual benchmarks for their kind of
    business rather than one fixed margin for everyone.
    """
    pnl = load_pnl(pnl_raw)
    breakdown = load_breakdown(breakdown_raw)

    benchmarks = BUSINESS_TYPE_BENCHMARKS.get(business_type, BUSINESS_TYPE_BENCHMARKS[DEFAULT_BUSINESS_TYPE])
    annualize_factor = MONTHS_PER_YEAR / period_months if period_months > 0 else 1.0

    checks = [
        check_pricing_gaps(pnl, benchmarks["gross_margin"], annualize_factor),
        check_cost_inefficiencies(pnl),
        check_customer_profitability(breakdown, benchmarks["line_margin"], annualize_factor),
        check_service_mix(breakdown, benchmarks["line_margin"], annualize_factor),
        check_revenue_leakage(pnl, annualize_factor),
    ]
    total = round(sum(c["estimate"] for c in checks), 2)
    return {"checks": checks, "total_found": total, "business_type": business_type,
            "period_months": period_months}
