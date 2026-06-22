"""
Business Without You, Build the Team.

The in-program tool for Milestone 7 (weeks 10-11), the last of the seven:
a client uploads their role inventory and delegation map, and optionally a
candidate list for any role actively hiring.

This ranks roles by delegation gap, builds an outcome-based hiring
template per role, and scores candidates against a five-trait leadership
scorecard.
"""

import pandas as pd
import os

import streamlit as st

from analysis import run_team_builder

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_7_Team_Builder_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, Build the Team", page_icon="\U0001F465")

st.title("Build the Team That Builds the Business")
st.write(
    "Milestone 7. Upload your role inventory and delegation map to get your "
    "delegation-gap ranking and outcome-based hiring templates. Add a candidate "
    "list to also score candidates on the leadership scorecard."
)

st.warning(
    "A high delegation target means nothing without a decision right handed over "
    "with it. If a role's decision rights still say \"owner signs off,\" the "
    "delegation level on paper is not the real one."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()

st.subheader("1. Role inventory and delegation map")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per role. Required columns: "
        "**role_name**, **current_delegation_level** (1-5), "
        "**target_delegation_level** (1-5), **key_outcome_1/2/3**, "
        "**decision_rights**, **success_metric**."
    )
roles_file = st.file_uploader("Upload your role inventory (CSV or Excel)", type=["csv", "xlsx", "xls"], key="roles")

st.subheader("2. Candidates (optional)")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per candidate. Required columns: "
        "**candidate_name**, **role_name** (must match a role above), and five "
        "1-5 ratings: **ownership**, **communication**, **judgment**, "
        "**coachability**, **results_track_record**."
    )
candidates_file = st.file_uploader("Upload your candidate list (CSV or Excel, optional)", type=["csv", "xlsx", "xls"], key="candidates")

st.divider()

if roles_file:
    try:
        roles_raw = pd.read_csv(roles_file) if roles_file.name.lower().endswith(".csv") else pd.read_excel(roles_file)
        candidates_raw = None
        if candidates_file:
            candidates_raw = pd.read_csv(candidates_file) if candidates_file.name.lower().endswith(".csv") else pd.read_excel(candidates_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read one of those files. This usually means a role or outcome "
            "description has a comma in it that got mistaken for a new column. Put "
            "quotes around any text with a comma, or swap the comma for a dash, and "
            "upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read one of those files. Double-check they match the format above and try again.")
        st.stop()

    try:
        result = run_team_builder(roles_raw, candidates_raw)
    except Exception as exc:
        st.error(f"Could not build the team plan: {exc}")
        st.stop()

    st.header("Delegation-gap ranking")
    st.write("Biggest gap first. This is the order to work on roles, not a ranking of importance.")
    for item in result["delegation_scores"]:
        st.write(
            f"{item['rank']}. **{item['role_name']}**: currently level "
            f"{item['current_delegation_level']}/5, target {item['target_delegation_level']}/5, "
            f"gap of {item['delegation_gap']:.1f}."
        )

    st.divider()
    st.header("Outcome-based hiring templates")
    for item in result["hiring_templates"]:
        with st.expander(item["role_name"]):
            st.text(item["template"])

    if result["unmatched_roles"]:
        st.warning(
            "These candidate role names don't match any role in your inventory, "
            "check for a typo: " + ", ".join(result["unmatched_roles"]) + "."
        )

    if result["leadership_scorecard"]:
        st.divider()
        st.header("Leadership scorecard")
        for role_name, candidates in result["leadership_scorecard"].items():
            st.subheader(role_name)
            for c in candidates:
                top_tag = " (top candidate)" if c["is_top_candidate"] else ""
                trait_text = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in c["traits"].items())
                st.write(f"{c['rank']}. **{c['candidate_name']}**{top_tag}, composite {c['composite']}/5. {trait_text}.")
    else:
        st.divider()
        st.info("Upload a candidate list above if you're actively hiring for any of these roles.")

    st.divider()
    st.write(
        "Bring this to your next live call. The test for this milestone is whether "
        "the business passes a two-week owner-absence test, not whether the org "
        "chart looks complete."
    )
else:
    st.info("Upload your role inventory above to build your team plan.")
