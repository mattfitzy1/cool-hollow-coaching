"""
Cool Hollow Coaching, the hidden-profit analyzer.

A prospect uploads a P&L (CSV, Excel, or PDF) and gets back a plain-English
report of pricing gaps, cost leakage, and cash timing risk, with a headline
dollar figure: the profit and risk found in their own numbers.
"""

import pandas as pd
import streamlit as st

from analysis import run_full_analysis
from pdf_parser import parse_pdf

st.set_page_config(page_title="Cool Hollow Coaching, the hidden-profit finder", page_icon="$")

st.title("Find the profit already in your business")
st.write(
    "Upload your P&L and we will show you where the money is leaking and where "
    "the margin is sitting unclaimed. Many owner-run businesses in this revenue "
    "range have at least $50,000 sitting unclaimed somewhere in pricing, cost, "
    "or cash timing."
)

st.divider()

with st.expander("What file should I upload?"):
    st.write(
        "A CSV, Excel, or PDF export of your profit and loss. The first column "
        "should be the line item name (Revenue, Cost of Goods Sold, Rent, "
        "Software, and so on). If you have more than one month, add a column "
        "per month. If you only have totals, one amount column is fine too. "
        "PDF exports straight from QuickBooks, Xero, or similar tools work best."
    )

uploaded = st.file_uploader("Upload your P&L (CSV, Excel, or PDF)", type=["csv", "xlsx", "xls", "pdf"])

if uploaded:
    name = uploaded.name.lower()
    try:
        if name.endswith(".csv"):
            raw = pd.read_csv(uploaded)
        elif name.endswith(".pdf"):
            raw = parse_pdf(uploaded)
            with st.expander("What we read from your PDF"):
                st.dataframe(raw)
        else:
            raw = pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read that file. Double-check it is a plain P&L export. ({exc})")
        st.stop()

    try:
        result = run_full_analysis(raw)
    except Exception as exc:
        st.error(f"Could not analyze that file: {exc}")
        st.stop()

    st.divider()
    st.header(f"We found ${result['total_found']:,.0f} in profit and cash risk")

    for check in result["checks"]:
        st.subheader(f"{check['name']}: ${check['estimate']:,.0f}")
        for line in check["findings"]:
            st.write(f"- {line}")

    st.divider()
    st.write(
        "This is a first pass, not a full audit. Business Without You goes "
        "through every one of these in detail over 12 weeks, and finds the "
        "rest of what is hiding. The program costs $5,000. You just saw why "
        "that is rarely the hard part."
    )
else:
    st.info("Upload a file above to get your first report.")
