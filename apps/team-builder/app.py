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
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from branding import apply_branding, show_disclaimer
from client_upload import read_upload
from results_pdf import build_results_pdf

from analysis import run_team_builder

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_7_Team_Builder_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, Build the Team", page_icon="\U0001F465")
apply_branding(7, "Build the Team That Builds the Business")

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
    st.caption("Fill in the data tabs, save, and upload that same file into every upload box below. Each box automatically finds the tab it needs.")

st.divider()

st.info(
    "**One workbook, uploaded twice.** Your filled-in template has both tabs in it. "
    "Upload that same file into the role inventory box below, then upload it again "
    "into the candidates box if you're actively hiring, each one automatically "
    "reads the tab it needs."
)

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
        roles_raw = read_upload(roles_file, {
            "role_name", "current_delegation_level", "target_delegation_level",
            "key_outcome_1", "key_outcome_2", "key_outcome_3",
            "decision_rights", "success_metric",
        })
        candidates_raw = None
        if candidates_file:
            candidates_raw = read_upload(candidates_file, {
                "candidate_name", "role_name", "ownership", "communication",
                "judgment", "coachability", "results_track_record",
            })
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

    pdf_sections = [("Delegation-gap ranking", [
        f"{item['rank']}. {item['role_name']}: currently level "
        f"{item['current_delegation_level']}/5, target {item['target_delegation_level']}/5, "
        f"gap of {item['delegation_gap']:.1f}."
        for item in result["delegation_scores"]
    ])]
    pdf_sections.append(("Outcome-based hiring templates", [
        f"{item['role_name']}: {item['template']}" for item in result["hiring_templates"]
    ]))
    if result["leadership_scorecard"]:
        lines = []
        for role_name, candidates in result["leadership_scorecard"].items():
            for c in candidates:
                top_tag = " (top candidate)" if c["is_top_candidate"] else ""
                trait_text = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in c["traits"].items())
                lines.append(f"{role_name}, {c['rank']}. {c['candidate_name']}{top_tag}, composite {c['composite']}/5. {trait_text}.")
        pdf_sections.append(("Leadership scorecard", lines))
    pdf_bytes = build_results_pdf(
        7, "Build the Team That Builds the Business",
        "Delegation-gap ranking, hiring templates, and leadership scorecard.",
        pdf_sections,
    )
    st.download_button(
        "Download your results (PDF)", pdf_bytes,
        file_name="Cool_Hollow_Coaching_Team_Builder_Results.pdf",
        mime="application/pdf", type="primary",
    )
    st.caption("Nothing you upload or generate here is stored on our servers. This download is your only copy.")
else:
    st.info("Upload your role inventory above to build your team plan.")

show_disclaimer()
