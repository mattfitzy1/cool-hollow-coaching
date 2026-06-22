"""
Business Without You, the Profit Discovery Audit.

The in-program tool for Milestone 5 (week 7): a paying client uploads their
P&L plus a customer/service breakdown sheet and gets a plain-English report
covering all five areas of Mark's Profit Discovery Audit framework: pricing
gaps, cost inefficiencies, customer profitability, service mix, and revenue
leakage.

This is for clients already in the program, not a prospect-facing lead
magnet. For that, see apps/hidden-profit-analyzer.
"""

import pandas as pd
import streamlit as st

from analysis import run_full_audit

st.set_page_config(page_title="Business Without You, the Profit Discovery Audit", page_icon="$")

st.title("The Profit Discovery Audit")
st.write(
    "Milestone 5. Upload your P&L and your customer/service breakdown to run all five "
    "checks: pricing gaps, cost inefficiencies, customer profitability, service mix, "
    "and revenue leakage."
)

st.warning(
    "This audit is only as good as the honesty you bring to it. The numbers will not "
    "explain away a client you keep for reasons other than profit, or a price you are "
    "afraid to raise. Run it straight, and bring anything that surprises you to your "
    "next live call."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Your P&L")
    with st.expander("What file should I upload?"):
        st.write(
            "A CSV or Excel export of your profit and loss. The first column should be "
            "the line item name (Revenue, Cost of Goods Sold, Rent, Software, Discounts, "
            "and so on). If you have more than one month, add a column per month."
        )
    pnl_file = st.file_uploader("Upload your P&L (CSV or Excel)", type=["csv", "xlsx", "xls"], key="pnl")

with col2:
    st.subheader("2. Customer / service breakdown")
    with st.expander("What file should I upload?"):
        st.write(
            "A simple sheet with one row per customer or per service line: "
            "**type** (\"customer\" or \"service\"), **name**, **revenue**, **direct_cost**. "
            "This is what makes the customer-profitability and service-mix checks possible, "
            "a P&L alone cannot answer those two."
        )
    breakdown_file = st.file_uploader("Upload your breakdown sheet (CSV or Excel)", type=["csv", "xlsx", "xls"], key="breakdown")

st.divider()

if pnl_file and breakdown_file:
    try:
        pnl_raw = pd.read_csv(pnl_file) if pnl_file.name.lower().endswith(".csv") else pd.read_excel(pnl_file)
        breakdown_raw = pd.read_csv(breakdown_file) if breakdown_file.name.lower().endswith(".csv") else pd.read_excel(breakdown_file)
    except Exception as exc:
        st.error(f"Could not read one of those files. Double-check the format. ({exc})")
        st.stop()

    try:
        result = run_full_audit(pnl_raw, breakdown_raw)
    except Exception as exc:
        st.error(f"Could not run the audit: {exc}")
        st.stop()

    st.header(f"Audit found ${result['total_found']:,.0f} in profit opportunity")

    for check in result["checks"]:
        st.subheader(f"{check['name']}: ${check['estimate']:,.0f}")
        for line in check["findings"]:
            st.write(f"- {line}")

    st.divider()
    st.write(
        "Bring this report to your next live call. The areas with the biggest dollar "
        "figure are where Mark or the specialist team should look closest, the model "
        "behind this number is a guide, not the final word."
    )
else:
    st.info("Upload both files above to run the audit.")
