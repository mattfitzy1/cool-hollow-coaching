"""
Core analysis logic for the Cool Hollow Coaching hidden-profit analyzer.

Takes a parsed P&L (a list of {category, line_item, amount, month (optional)} rows)
and runs three checks: pricing/margin gaps, cost leakage, and cash flow timing risk.
Each check returns findings with a plain-English explanation and a dollar estimate
of profit or cash at risk, so the total can be summed into one headline number.
"""

import pandas as pd

REVENUE_KEYWORDS = ["revenue", "sales", "income"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "direct cost"]
EXPENSE_KEYWORDS = ["expense", "overhead", "operating", "subscription", "software",
                    "rent", "salaries", "payroll", "marketing", "advertising", "fees"]

HEALTHY_GROSS_MARGIN = 0.50
HIGH_GROWTH_FLAG = 0.15


def _classify(line_item: str) -> str:
    text = line_item.lower()
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
    df.columns = [str(c).strip().lower() for c in df.columns]

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
        raise ValueError("Could not find amount columns in the uploaded file.")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["line_item"] = df["line_item"].astype(str)
    df["category"] = df["line_item"].apply(_classify)
    return df[["category", "line_item", "month", "amount"]]


def check_pricing_margin(df: pd.DataFrame) -> dict:
    revenue = df[df["category"] == "revenue"]["amount"].sum()
    cogs = df[df["category"] == "cogs"]["amount"].sum()

    findings = []
    estimate = 0.0

    if revenue > 0:
        gross_margin = (revenue - cogs) / revenue
        if gross_margin < HEALTHY_GROSS_MARGIN:
            gap = HEALTHY_GROSS_MARGIN - gross_margin
            estimate = round(gap * revenue, 2)
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, below the {HEALTHY_GROSS_MARGIN:.0%} "
                f"benchmark for a healthy service or product business. Closing that gap through pricing "
                f"or cost of delivery changes is worth roughly ${estimate:,.0f}."
            )
        else:
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, at or above the {HEALTHY_GROSS_MARGIN:.0%} "
                f"benchmark. No major pricing gap found here."
            )
    else:
        findings.append("No revenue line found, so a margin check could not be run.")

    return {"name": "Pricing and margin gaps", "estimate": estimate, "findings": findings}


def check_cost_leakage(df: pd.DataFrame) -> dict:
    expenses = df[df["category"] == "expense"]

    findings = []
    estimate = 0.0

    if expenses.empty:
        findings.append("No expense lines were found to check for leakage.")
        return {"name": "Cost leakage", "estimate": estimate, "findings": findings}

    by_line = expenses.groupby("line_item")["amount"].sum().sort_values(ascending=False)
    total_expense = by_line.sum()

    if "month" in expenses.columns and expenses["month"].nunique() > 1:
        pivot = expenses.pivot_table(index="line_item", columns="month", values="amount", aggfunc="sum").fillna(0)
        months_sorted = sorted(pivot.columns)
        if len(months_sorted) >= 2:
            first, last = pivot[months_sorted[0]], pivot[months_sorted[-1]]
            for line_item in pivot.index:
                start, end = first.get(line_item, 0), last.get(line_item, 0)
                if start > 0:
                    growth = (end - start) / start
                    if growth > HIGH_GROWTH_FLAG and end > 0:
                        risk = round(end - start, 2)
                        estimate += risk
                        findings.append(
                            f"\"{line_item}\" grew {growth:.0%} from {months_sorted[0]} to {months_sorted[-1]} "
                            f"(${start:,.0f} to ${end:,.0f}). Worth a look, that is ${risk:,.0f} of creeping cost."
                        )

    top_3 = by_line.head(3)
    findings.append(
        "Largest recurring costs: " + ", ".join(f"\"{k}\" (${v:,.0f})" for k, v in top_3.items()) +
        f", out of ${total_expense:,.0f} total expense."
    )

    if not estimate:
        findings.append("No clear runaway cost trend found across the months provided. "
                         "Worth a manual look at vendor contracts and subscriptions even so.")

    return {"name": "Cost leakage", "estimate": round(estimate, 2), "findings": findings}


def check_cash_timing(df: pd.DataFrame) -> dict:
    findings = []
    estimate = 0.0

    if "month" not in df.columns or df["month"].nunique() < 2:
        findings.append("Only one period was provided, so a cash timing trend could not be checked. "
                         "Upload at least two months side by side for this check to run.")
        return {"name": "Cash flow timing", "estimate": estimate, "findings": findings}

    monthly = df.groupby("month")["amount"].apply(
        lambda s: df.loc[s.index][df.loc[s.index, "category"] == "revenue"]["amount"].sum()
        - df.loc[s.index][df.loc[s.index, "category"].isin(["cogs", "expense"])]["amount"].sum()
    )

    negative_months = monthly[monthly < 0]
    if not negative_months.empty:
        estimate = round(abs(negative_months.sum()), 2)
        findings.append(
            f"{len(negative_months)} month(s) show more going out than coming in: "
            + ", ".join(f"{m} (${v:,.0f})" for m, v in negative_months.items()) +
            ". That is the gap a 13-week cash forecast is built to catch before it becomes a real problem."
        )
    else:
        findings.append("Every month provided shows cash in ahead of cash out. No timing risk flagged.")

    return {"name": "Cash flow timing", "estimate": estimate, "findings": findings}


def run_full_analysis(df: pd.DataFrame) -> dict:
    pnl = load_pnl(df)
    checks = [check_pricing_margin(pnl), check_cost_leakage(pnl), check_cash_timing(pnl)]
    total = round(sum(c["estimate"] for c in checks), 2)
    return {"checks": checks, "total_found": total}
