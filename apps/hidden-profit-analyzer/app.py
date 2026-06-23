"""
Cool Hollow Coaching, the hidden-profit analyzer.

An owner uploads a P&L (CSV, Excel, or PDF) and gets a plain-English first look at
their numbers: the profit picture, where the money goes, the levers worth pulling,
and (if they upload monthly columns) costs that crept up and months that ran short.

Honesty rules baked in: every figure points back to a line in the uploaded file, the
findings are kept separate (never one inflated "profit found" number), and the page
does not sell or promise anything that is not built.
"""

import pandas as pd
import streamlit as st

from analysis import run_full_analysis
from pdf_parser import parse_pdf
from excel_parser import parse_excel

st.set_page_config(page_title="Cool Hollow Coaching, the hidden-profit finder", page_icon="$")

st.title("See what your own numbers are telling you")
st.write(
    "Upload your profit and loss and get a plain-English read of your margins, where "
    "your money actually goes, and the levers worth pulling. It is a first look, not a "
    "full audit, and every number points back to a line in your file."
)
st.info(
    "Best results: upload a P&L with a **column for each month** (not just a single "
    "annual total). With monthly columns it can also spot costs that crept up and "
    "months where cash ran short."
)
st.caption("Your file is read only to produce this report, in this session. It is not "
           "saved or stored anywhere.")

st.divider()

with st.expander("What file should I upload?"):
    st.write(
        "A CSV, Excel, or PDF export of your profit and loss. The first column should be "
        "the line item name, with your usual section headers (Income, Cost of Goods Sold, "
        "Expenses). Add a column per month for the richest read; a single total column "
        "works too. PDF and Excel exports straight from QuickBooks or Xero work well."
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
        raw = parse_excel(uploaded)
except Exception as exc:
    st.error(f"Could not read that file. Double-check it is a plain P&L export. ({exc})")
    st.stop()

try:
    result = run_full_analysis(raw)
except Exception as exc:
    st.error(f"Could not analyze that file: {exc}")
    st.stop()

st.divider()

with st.expander("How we read your file (check this first)"):
    st.write("Here is how each line was classified. If anything looks misread, your "
             "export may use unusual labels. Everything below is built only from these.")
    st.dataframe(result["breakdown"], use_container_width=True)

snapshot = result["snapshot"]
where = result["where"]
lev = result["leverage"]
creep = result["creep"]
cash = result["cash"]

st.header("Your profit snapshot")
cols = st.columns(2)
if snapshot["gross_margin"] is not None:
    cols[0].metric("Gross margin", f"{snapshot['gross_margin']:.0%}")
if snapshot["operating_margin"] is not None:
    cols[1].metric("Operating margin", f"{snapshot['operating_margin']:.0%}")
for line in snapshot["findings"]:
    st.write("- " + line.replace("$", "\\$"))

st.header("Where the money goes")
if where.get("rows"):
    table = pd.DataFrame([
        {
            "Cost line": r["line_item"],
            "Amount": f"${r['amount']:,.0f}",
            "Share of revenue": (f"{r['share_of_revenue']:.0%}"
                                 if r["share_of_revenue"] is not None else "n/a"),
        }
        for r in where["rows"]
    ])
    st.table(table)
for line in where["findings"]:
    st.write("- " + line.replace("$", "\\$"))

st.header("Your levers")
for line in lev["findings"]:
    st.write("- " + line.replace("$", "\\$"))

st.header("Cost creep")
if creep["creep"] > 0:
    st.metric("Costs that crept up over the period", f"${creep['creep']:,.0f}")
for line in creep["findings"]:
    st.write("- " + line.replace("$", "\\$"))

st.header("Cash timing")
if cash["shortfall"] > 0:
    st.metric("Total of the months that ran short", f"${cash['shortfall']:,.0f}")
for line in cash["findings"]:
    st.write("- " + line.replace("$", "\\$"))

st.divider()
st.write(
    "This is a first look at your own numbers, not a full audit. The real work is going "
    "through each of these line by line: where the margin is leaking, which costs are "
    "worth a hard look, and how to see a cash gap coming before it lands. That is exactly "
    "the kind of thing Cool Hollow works on with owners."
)
