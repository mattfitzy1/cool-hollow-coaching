"""
Backtest for the hidden-profit analyzer.

Each case is a hand-built P&L where the correct answers were worked out by hand.
The test runs the real analysis and checks every headline figure against those
expectations. This is the proof the tool reports honest, traceable numbers before
it ever goes in front of a prospect. Run:  python backtest.py
"""

import sys

import pandas as pd

from analysis import run_full_analysis


def approx(a, b, tol=0.01):
    if a is None or b is None:
        return a == b
    return abs(a - b) <= tol


CASES = []


# 1. Healthy business: 70% margin, no cost creep, every month cash positive.
CASES.append({
    "name": "Healthy business, multi-month",
    "df": pd.DataFrame({
        "line_item": ["Revenue", "Cost of Goods Sold", "Rent", "Payroll"],
        "jan": [100000, 30000, 5000, 20000],
        "feb": [100000, 30000, 5000, 20000],
        "mar": [100000, 30000, 5000, 20000],
    }),
    "expect": {"margin_pct": 0.70, "opportunity": 15000.0, "creep": 0.0, "shortfall": 0.0},
})

# 2. A subscription quietly doubling: cost creep must catch exactly the $1,000 rise.
CASES.append({
    "name": "Creeping software cost",
    "df": pd.DataFrame({
        "line_item": ["Sales", "Cost of Sales", "Software", "Rent"],
        "jan": [50000, 20000, 1000, 4000],
        "feb": [50000, 20000, 1500, 4000],
        "mar": [50000, 20000, 2000, 4000],
    }),
    "expect": {"margin_pct": 0.60, "opportunity": 7500.0, "creep": 1000.0, "shortfall": 0.0},
})

# 3. Underwater months: cash timing must total the two $5,000 shortfalls.
CASES.append({
    "name": "Two loss-making months",
    "df": pd.DataFrame({
        "line_item": ["Revenue", "Cost of Goods Sold", "Payroll"],
        "jan": [30000, 20000, 15000],
        "feb": [30000, 20000, 15000],
    }),
    "expect": {"margin_pct": 0.3333, "opportunity": 3000.0, "creep": 0.0, "shortfall": 10000.0},
})

# 4. Subtotals present: the killer case. Revenue must read 100k, NOT 200k, even
#    though a "Total Revenue" row repeats it. Proves no double counting.
CASES.append({
    "name": "P&L with subtotal/total rows",
    "df": pd.DataFrame({
        "line_item": ["Revenue", "Total Revenue", "Cost of Goods Sold", "Total COGS",
                      "Gross Profit", "Rent", "Payroll", "Total Expenses", "Net Income"],
        "amount": [100000, 100000, 40000, 40000, 60000, 5000, 25000, 30000, 30000],
    }),
    "expect": {"margin_pct": 0.60, "opportunity": 5000.0, "creep": 0.0, "shortfall": 0.0},
})

# 5. Messy real-world formatting: $ signs, commas, and (parentheses) for negatives.
CASES.append({
    "name": "Currency-formatted, parentheses negatives",
    "df": pd.DataFrame({
        "line_item": ["Revenue", "Cost of Goods Sold", "Refunds", "Rent"],
        "amount": ["$120,000", "$50,000", "(2,000)", "6,000"],
    }),
    "expect": {"margin_pct": 0.5833, "opportunity": 6000.0, "creep": 0.0, "shortfall": 0.0},
})


# 6. QuickBooks shape: section headers, account-code prefixes, sub-headers, and
#    "Total for ..." rows. The category must come from the SECTION, and the totals
#    must be excluded. Revenue must read 100k (not 300k from also counting totals).
CASES.append({
    "name": "QuickBooks sections + account codes + subtotals",
    "df": pd.DataFrame({
        "line_item": [
            "Income", "40000 Sales", "40200 Product Sales", "Total for 40000 Sales",
            "Total for Income",
            "Cost of Goods Sold", "51100 Materials", "51101 Vendor A", "51102 Vendor B",
            "Total for 51100 Materials", "Total for Cost of Goods Sold", "Gross Profit",
            "Expenses", "62000 Advertising", "63000 Rent", "Total Expenses", "Net Income",
        ],
        "amount": [
            None, None, 100000, 100000, 100000,
            None, None, 30000, 10000, 40000, 40000, 60000,
            None, 5000, 8000, 13000, 47000,
        ],
    }),
    "expect": {"margin_pct": 0.60, "opportunity": 5000.0, "creep": 0.0, "shortfall": 0.0},
})

# 7. The case that broke the old version: revenue named by service and COGS named by
#    category, so name-based keywords would misread both. Sections must win.
CASES.append({
    "name": "Section beats line names (services / cost categories)",
    "df": pd.DataFrame({
        "line_item": [
            "Income", "Fire/Smoke Restoration", "Water Remediation", "Total for Income",
            "Cost of Goods Sold", "Auto Gas & Tolls", "Subcontractors", "Direct Labor",
            "Total for Cost of Goods Sold", "Gross Profit",
            "Expenses", "Google Ads", "Office Rent",
        ],
        "amount": [
            None, 60000, 40000, 100000,
            None, 5000, 25000, 20000, 50000, 50000,
            None, 3000, 7000,
        ],
    }),
    "expect": {"margin_pct": 0.50, "opportunity": 5000.0, "creep": 0.0, "shortfall": 0.0},
})


def run():
    passed = 0
    failed = 0
    for case in CASES:
        result = run_full_analysis(case["df"])
        exp = case["expect"]
        checks = {
            "margin %": approx(result["snapshot"]["gross_margin"], exp["margin_pct"]),
            "opportunity $": approx(result["leverage"]["opportunity"], exp["opportunity"]),
            "cost creep $": approx(result["creep"]["creep"], exp["creep"]),
            "cash shortfall $": approx(result["cash"]["shortfall"], exp["shortfall"]),
        }
        ok = all(checks.values())
        passed += ok
        failed += (not ok)
        flag = "PASS" if ok else "FAIL"
        print(f"[{flag}] {case['name']}")
        if not ok:
            got = {
                "margin %": result["snapshot"]["gross_margin"],
                "opportunity $": result["leverage"]["opportunity"],
                "cost creep $": result["creep"]["creep"],
                "cash shortfall $": result["cash"]["shortfall"],
            }
            for k, good in checks.items():
                if not good:
                    print(f"        {k}: expected {exp}, got {got[k]}")

    print(f"\n{passed} passed, {failed} failed, out of {len(CASES)} cases.")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
