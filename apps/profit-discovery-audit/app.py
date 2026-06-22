"""
Business Without You, the Profit Discovery Audit.

The in-program tool for Milestone 4 (week 5): a paying client uploads their
P&L plus a customer/service breakdown sheet and gets a plain-English report
covering all five areas of Mark's Profit Discovery Audit framework: pricing
gaps, cost inefficiencies, customer profitability, service mix, and revenue
leakage.

This is for clients already in the program, not a prospect-facing lead
magnet. For that, see apps/hidden-profit-analyzer.
"""

import os

import pandas as pd
import streamlit as st

from analysis import run_full_audit, BUSINESS_TYPE_BENCHMARKS, DEFAULT_BUSINESS_TYPE

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_4_Profit_Discovery_Audit_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, the Profit Discovery Audit", page_icon="$")

st.title("The Profit Discovery Audit")
st.write(
    "Milestone 4. Upload your P&L and your customer/service breakdown to run all five "
    "checks: pricing gaps, cost inefficiencies, customer profitability, service mix, "
    "and revenue leakage."
)

st.warning(
    "This audit is only as good as the honesty you bring to it. The numbers will not "
    "explain away a client you keep for reasons other than profit, or a price you are "
    "afraid to raise. Run it straight, and bring anything that surprises you to your "
    "next live call."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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

col3, col4 = st.columns(2)

with col3:
    business_type = st.selectbox(
        "What kind of business is this?",
        options=list(BUSINESS_TYPE_BENCHMARKS.keys()),
        index=list(BUSINESS_TYPE_BENCHMARKS.keys()).index(DEFAULT_BUSINESS_TYPE),
        help="The margin benchmarks this audit checks against are different for a "
             "services business than a repair shop or a distributor. Pick the closest fit.",
    )

with col4:
    period_months = st.number_input(
        "How many months does the P&L cover?",
        min_value=1, max_value=24, value=12, step=1,
        help="So the profit-found number reflects a real year, not however many months "
             "happened to be in the file. If you uploaded 3 months, put 3.",
    )

st.divider()

if pnl_file and breakdown_file:
    try:
        pnl_raw = pd.read_csv(pnl_file) if pnl_file.name.lower().endswith(".csv") else pd.read_excel(pnl_file)
        breakdown_raw = pd.read_csv(breakdown_file) if breakdown_file.name.lower().endswith(".csv") else pd.read_excel(breakdown_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read one of those files. This usually means a line item or "
            "customer/service name has a comma in it that got mistaken for a new "
            "column (e.g. \"Smith, Jones & Co\"). Put quotes around any name with a "
            "comma, or swap the comma for a dash, and upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read one of those files. Double-check they match the format above and try again.")
        st.stop()

    try:
        result = run_full_audit(pnl_raw, breakdown_raw, business_type=business_type, period_months=period_months)
    except Exception as exc:
        st.error(f"Could not run the audit: {exc}")
        st.stop()

    st.header(f"Audit found ${result['total_found']:,.0f} a year in profit opportunity")
    st.caption(
        f"Annualized from {result['period_months']:.0f} month(s) of data, benchmarked against "
        f"a {result['business_type'].lower()} business."
    )

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
