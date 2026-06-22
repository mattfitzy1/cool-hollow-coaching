"""
Business Without You, the 15-Hour Reclaim Protocol.

The in-program tool for Milestone 1 (week 1): a client uploads their
Liberation Audit, a one-week time log where every task is sorted into
owner_only, delegate, automate, or eliminate, with a short Constraint
Diagnosis on each candidate (documented, trained replacement, risk).

This scores every non-owner-only task and outputs the 15-Hour Reclaim
Protocol: a named, deadlined list of what moves first.
"""

import os

import pandas as pd
import streamlit as st

from analysis import build_protocol, load_time_log

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_1_Reclaim_Protocol_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, the 15-Hour Reclaim Protocol", page_icon="⏱")

st.title("The 15-Hour Reclaim Protocol")
st.write(
    "Milestone 1. Upload your Liberation Audit, the one-week time log sorted into "
    "owner_only, delegate, automate, or eliminate, to get your named, deadlined "
    "reclaim list."
)

st.warning(
    "This only works if the time log is honest. If everything ends up marked "
    "owner_only, that is the result worth sitting with, not a clean bill of health."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()

st.subheader("Your Liberation Audit")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per task. Required columns: **task**, "
        "**hours_per_week**, **category** (owner_only, delegate, automate, or "
        "eliminate). Optional columns: **documented** (yes/no), "
        "**trained_replacement** (yes/no), **risk** (low, medium, high). "
        "Optional columns default to no / medium if left out."
    )
log_file = st.file_uploader("Upload your time log (CSV or Excel)", type=["csv", "xlsx", "xls"], key="time_log")

st.divider()

if log_file:
    try:
        log_raw = pd.read_csv(log_file) if log_file.name.lower().endswith(".csv") else pd.read_excel(log_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read that file. This usually means a task name has a comma in it "
            "that got mistaken for a new column. Put quotes around any task with a comma, "
            "or swap the comma for a dash, and upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read that file. Double-check it matches the format above and try again.")
        st.stop()

    try:
        log = load_time_log(log_raw)
        result = build_protocol(log)
    except Exception as exc:
        st.error(f"Could not score the time log: {exc}")
        st.stop()

    st.header(f"{result['reclaimable_hours']:.1f} hours a week up for reclaim")
    st.write(
        f"{result['owner_only_hours']:.1f} hours a week stay owner_only for now, "
        f"work only you can do today."
    )

    if not result["items"]:
        st.info("Every task in this log was marked owner_only. Nothing to hand off yet.")
    else:
        st.divider()
        for tier in ["This week", "Within 2 weeks", "Within 30 days"]:
            tier_items = [i for i in result["items"] if i["deadline"] == tier]
            if not tier_items:
                continue
            st.subheader(tier)
            for item in tier_items:
                st.write(
                    f"- **{item['action']}: {item['task']}** "
                    f"({item['hours_per_week']:.1f} hrs/week). {item['reasoning']}"
                )

    st.divider()
    st.write(
        "Bring this list to your next live call. The hours add up fastest when the "
        "top tier actually moves this week, not when the whole list looks tidy on paper."
    )
else:
    st.info("Upload your time log above to build your reclaim protocol.")
