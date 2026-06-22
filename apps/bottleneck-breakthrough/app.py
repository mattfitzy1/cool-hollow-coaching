"""
Business Without You, the Bottleneck Breakthrough Plan.

The in-program tool for Milestone 6 (week 8): a client uploads their
Constraint Identification worksheet, every candidate constraint across
three core processes, rated for frequency, hours lost, downstream impact,
and whether it's automatable.

This ranks every constraint by combined impact, names the single binding
constraint to break first, and builds a separate automation hit list
ranked by hours saved for the effort required.
"""

import os

import pandas as pd
import streamlit as st

from analysis import build_breakthrough_plan, load_constraints

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_6_Bottleneck_Breakthrough_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, the Bottleneck Breakthrough Plan", page_icon="\U0001F517")

st.title("The Bottleneck Breakthrough Plan")
st.write(
    "Milestone 6. Upload your Constraint Identification worksheet to get your "
    "ranked constraint list, the single binding constraint to break first, and "
    "your automation hit list."
)

st.warning(
    "Breaking a constraint that isn't actually binding just moves the bottleneck "
    "somewhere else. Rate frequency and downstream impact honestly, not by which "
    "fix feels most comfortable to do."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()

st.subheader("Your Constraint Identification worksheet")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per candidate constraint. Required "
        "columns: **constraint_name**, **process** (one of your three mapped "
        "processes), **frequency_per_week**, **hours_lost_per_occurrence**, "
        "**downstream_impact** (1-5, how much it blocks everything else), "
        "**automatable** (yes/no), **automation_effort** (1-5, 1 is trivial, "
        "5 is hard, only matters if automatable is yes)."
    )
constraints_file = st.file_uploader("Upload your constraint list (CSV or Excel)", type=["csv", "xlsx", "xls"], key="constraints")

st.divider()

if constraints_file:
    try:
        raw = pd.read_csv(constraints_file) if constraints_file.name.lower().endswith(".csv") else pd.read_excel(constraints_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read that file. This usually means a constraint name has a comma "
            "in it that got mistaken for a new column. Put quotes around any constraint "
            "with a comma, or swap the comma for a dash, and upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read that file. Double-check it matches the format above and try again.")
        st.stop()

    try:
        constraints = load_constraints(raw)
        result = build_breakthrough_plan(constraints)
    except Exception as exc:
        st.error(f"Could not build the breakthrough plan: {exc}")
        st.stop()

    if result["binding_constraint"]:
        bc = result["binding_constraint"]
        st.header(f"The binding constraint: {bc['constraint_name']}")
        st.write(
            f"In **{bc['process']}**, costing **{bc['weekly_hours_lost']:.1f} hours a week** "
            f"with a downstream impact of {bc['downstream_impact']}/5. Break this one first."
        )

    st.divider()
    st.subheader("Full ranked constraint list")
    for item in result["ranked_constraints"]:
        st.write(
            f"{item['rank']}. **{item['constraint_name']}** ({item['process']}), "
            f"{item['weekly_hours_lost']:.1f} hrs/week, downstream impact "
            f"{item['downstream_impact']}/5, score {item['constraint_score']:.1f}."
        )

    st.divider()
    st.subheader("Automation hit list")
    if result["automation_hit_list"]:
        st.write("Ranked by hours saved per week for the effort required, easiest wins first.")
        for item in result["automation_hit_list"]:
            st.write(
                f"- **{item['constraint_name']}**: {item['weekly_hours_lost']:.1f} hrs/week, "
                f"effort {item['automation_effort']}/5, ROI score {item['automation_roi']:.1f}."
            )
    else:
        st.write("Nothing in this list was marked automatable. Every fix here needs a process or people change.")

    st.divider()
    st.write(
        "Bring this plan to your next live call. The binding constraint is the one "
        "to attack, the rest of the ranked list is context, not a second priority."
    )
else:
    st.info("Upload your constraint list above to build your breakthrough plan.")
