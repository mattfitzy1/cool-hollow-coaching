"""
Core analysis logic for the Business Without You Profit Discovery Audit.

This is Milestone 5, Skill 2 of the curriculum: the in-program audit a paying
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
"""

import pandas as pd

REVENUE_KEYWORDS = ["revenue", "sales", "income"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "direct cost"]
EXPENSE_KEYWORDS = ["expense", "overhead", "operating", "subscription", "software",
                    "rent", "salaries", "payroll", "marketing", "advertising", "fees"]
LEAKAGE_KEYWORDS = ["discount", "write-off", "writeoff", "credit memo", "bad debt", "refund"]

HEALTHY_GROSS_MARGIN = 0.50
HIGH_GROWTH_FLAG = 0.15
HEALTHY_LINE_MARGIN = 0.20


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
        raise ValueError("Could not find amount columns in the uploaded P&L.")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["line_item"] = df["line_item"].astype(str)
    df["category"] = df["line_item"].apply(_classify)
    return df[["category", "line_item", "month", "amount"]]


def load_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the customer/service breakdown sheet into type, name, revenue, direct_cost."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

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


def check_pricing_gaps(pnl: pd.DataFrame) -> dict:
    revenue = pnl[pnl["category"] == "revenue"]["amount"].sum()
    cogs = pnl[pnl["category"] == "cogs"]["amount"].sum()

    findings = []
    estimate = 0.0

    if revenue > 0:
        gross_margin = (revenue - cogs) / revenue
        if gross_margin < HEALTHY_GROSS_MARGIN:
            gap = HEALTHY_GROSS_MARGIN - gross_margin
            estimate = round(gap * revenue, 2)
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, below the {HEALTHY_GROSS_MARGIN:.0%} "
                f"benchmark. Closing that gap through pricing or delivery cost changes is worth "
                f"roughly ${estimate:,.0f}."
            )
        else:
            findings.append(
                f"Gross margin is running at {gross_margin:.0%}, at or above the "
                f"{HEALTHY_GROSS_MARGIN:.0%} benchmark. No major pricing gap found here."
            )
    else:
        findings.append("No revenue line found in the P&L, so a pricing gap check could not be run.")

    return {"name": "Pricing gaps", "estimate": estimate, "findings": findings}


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
                            f"\"{line_item}\" grew {growth:.0%} from {months_sorted[0]} to "
                            f"{months_sorted[-1]} (${start:,.0f} to ${end:,.0f}), ${risk:,.0f} of "
                            f"creeping cost worth a hard look."
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


def _profitability_check(breakdown: pd.DataFrame, row_type: str, label: str) -> dict:
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
    underperformers = rows[(rows["margin"].notna()) & (rows["margin"] < HEALTHY_LINE_MARGIN)]

    if underperformers.empty:
        findings.append(f"Every {row_type} is at or above the {HEALTHY_LINE_MARGIN:.0%} margin benchmark. "
                         f"No major gap found here.")
        return {"name": label, "estimate": estimate, "findings": findings}

    for _, r in underperformers.sort_values("margin").iterrows():
        gap = HEALTHY_LINE_MARGIN - r["margin"]
        line_estimate = round(gap * r["revenue"], 2)
        estimate += line_estimate
        margin_text = f"{r['margin']:.0%}" if r["margin"] >= 0 else f"-{abs(r['margin']):.0%}"
        findings.append(
            f"\"{r['name']}\" is running at a {margin_text} margin on ${r['revenue']:,.0f} of revenue. "
            f"Bringing it to the {HEALTHY_LINE_MARGIN:.0%} benchmark is worth roughly ${line_estimate:,.0f}."
        )

    return {"name": label, "estimate": round(estimate, 2), "findings": findings}


def check_customer_profitability(breakdown: pd.DataFrame) -> dict:
    return _profitability_check(breakdown, "customer", "Customer profitability differences")


def check_service_mix(breakdown: pd.DataFrame) -> dict:
    return _profitability_check(breakdown, "service", "Service or product mix problems")


def check_revenue_leakage(pnl: pd.DataFrame) -> dict:
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
    estimate = round(by_line.sum(), 2)
    findings.append(
        "Flagged leakage lines: " + ", ".join(f"\"{k}\" (${v:,.0f})" for k, v in by_line.items()) + "."
    )
    findings.append(
        "This only catches what is already recorded as a discount, write-off, or refund. Unbilled "
        "work and missed upsells will not appear here, so still worth a manual look at invoicing."
    )

    return {"name": "Revenue leakage points", "estimate": estimate, "findings": findings}


def run_full_audit(pnl_raw: pd.DataFrame, breakdown_raw: pd.DataFrame) -> dict:
    pnl = load_pnl(pnl_raw)
    breakdown = load_breakdown(breakdown_raw)

    checks = [
        check_pricing_gaps(pnl),
        check_cost_inefficiencies(pnl),
        check_customer_profitability(breakdown),
        check_service_mix(breakdown),
        check_revenue_leakage(pnl),
    ]
    total = round(sum(c["estimate"] for c in checks), 2)
    return {"checks": checks, "total_found": total}
