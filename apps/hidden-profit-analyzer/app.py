"""
Cool Hollow Coaching, the hidden-profit analyzer.

A business owner uploads a P&L (CSV, Excel, or PDF) and gets back a plain-English
first look at three things, read straight from their own numbers: gross margin,
costs that crept up, and any months where money went out faster than it came in.

Honesty rules baked in: every figure points back to a line in the uploaded file,
the three findings are kept separate (never summed into one inflated "profit found"
number), and the page does not sell or promise anything that is not built.
"""

import pandas as pd
import streamlit as st

from analysis import run_full_analysis
from pdf_parser import parse_pdf

st.set_page_config(page_title="Cool Hollow Coaching, the hidden-profit finder", page_icon="$")

st.title("See what your own numbers are telling you")
st.write(
    "Upload your profit and loss and this reads three things straight from it: your "
    "gross margin, any costs that have crept up, and any months where more went out "
    "than came in. It is a first look, not a full audit, and every number it shows "
    "points back to a line in your file."
)
st.caption(
    "Your file is read only to produce this report, in this session. It is not saved "
    "or stored anywhere."
)

st.divider()

with st.expander("What file should I upload?"):
    st.write(
        "A CSV, Excel, or PDF export of your profit and loss. The first column should "
        "be the line item name (Revenue, Cost of Goods Sold, Rent, Software, and so "
        "on). If you have more than one month, add a column per month, in date order. "
        "If you only have totals, a single amount column is fine. PDF exports straight "
        "from QuickBooks, Xero, or similar tools work best."
    )

uploaded = st.file_uploader("Upload your P&L (CSV, Excel, or PDF)", type=["csv", "xlsx", "xls", "pdf"])

if not uploaded:
    st.info("Upload a file above to get your first look.")
    st.stop()

name = uploaded.name.lower()
try:
    if name.endswith(".csv"):
        raw = pd.read_csv(uploaded)
    elif name.endswith(".pdf"):
        raw = parse_pdf(uploaded)
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

# Transparency first: show how every line was read, so the numbers can be trusted.
with st.expander("How we read your file (check this first)"):
    st.write(
        "Here is how each line was classified. If anything looks misread, your export "
        "may use unusual labels. The numbers below are built only from these."
    )
    st.dataframe(result["breakdown"], use_container_width=True)

margin = result["margin"]
creep = result["creep"]
cash = result["cash"]

st.header("Pricing and margin")
if margin["gross_margin"] is not None:
    st.metric("Your gross margin", f"{margin['gross_margin']:.0%}")
for line in margin["findings"]:
    st.write(f"- {line}")

st.header("Cost creep")
if creep["creep"] > 0:
    st.metric("Costs that crept up over the period", f"${creep['creep']:,.0f}")
for line in creep["findings"]:
    st.write(f"- {line}")

st.header("Cash timing")
if cash["shortfall"] > 0:
    st.metric("Total of the months that ran short", f"${cash['shortfall']:,.0f}")
for line in cash["findings"]:
    st.write(f"- {line}")

st.divider()
st.write(
    "This is a first look at your own numbers, not a full audit. The real work is "
    "going through each of these line by line: where the margin is leaking, which "
    "costs are worth a hard look, and how to see a cash gap coming before it lands. "
    "That is exactly the kind of thing Cool Hollow works on with owners."
)
