"""
Business Without You, the Monday Morning Dashboard.

The in-program tool for Milestone 3 (week 4): a client uploads their
candidate metric list across five categories (cash, sales, delivery,
customer, team), each one rated for impact and whether it's a leading or
lagging indicator.

This selects the one right metric per category, sets a red/yellow/green
threshold against the client's own target, and flags up to two leading
indicators worth checking first every Monday.
"""

import os

import pandas as pd
import streamlit as st

from analysis import build_dashboard, load_metrics

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_3_Dashboard_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, the Monday Morning Dashboard", page_icon="\U0001F4CA")

st.title("The Monday Morning Dashboard")
st.write(
    "Milestone 3. Upload your candidate metric list across cash, sales, delivery, "
    "customer, and team to get your five-metric dashboard with red/yellow/green "
    "thresholds and your leading indicators flagged."
)

st.warning(
    "This only selects from what you give it. If a category's candidates are all "
    "vanity metrics, the dashboard will dutifully pick the best of a weak set, not "
    "tell you the set itself needs rethinking."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()

st.subheader("Your candidate metric list")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per candidate metric. Required columns: "
        "**category** (cash, sales, delivery, customer, or team), **metric_name**, "
        "**current_value**, **target_value**, **direction** (higher_better or "
        "lower_better), **leading** (yes/no), **impact** (1-5, how directly this "
        "metric reflects whether the business is actually healthy)."
    )
metrics_file = st.file_uploader("Upload your metric list (CSV or Excel)", type=["csv", "xlsx", "xls"], key="metrics")

st.divider()

if metrics_file:
    try:
        raw = pd.read_csv(metrics_file) if metrics_file.name.lower().endswith(".csv") else pd.read_excel(metrics_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read that file. This usually means a metric name has a comma in "
            "it that got mistaken for a new column. Put quotes around any metric name "
            "with a comma, or swap the comma for a dash, and upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read that file. Double-check it matches the format above and try again.")
        st.stop()

    try:
        metrics = load_metrics(raw)
        result = build_dashboard(metrics)
    except Exception as exc:
        st.error(f"Could not build the dashboard: {exc}")
        st.stop()

    if result["missing_categories"]:
        st.error(
            "No candidates found for: " + ", ".join(result["missing_categories"]) + ". "
            "Add at least one metric per category to get the full five-metric dashboard."
        )

    st.header("Your five-metric dashboard")

    status_icon = {"green": "\U0001F7E2", "yellow": "\U0001F7E1", "red": "\U0001F534"}

    for m in result["dashboard"]:
        leading_tag = " (leading indicator, check first)" if m["flagged_leading"] else ""
        st.write(
            f"{status_icon[m['status']]} **{m['category'].capitalize()}: {m['metric_name']}**{leading_tag}, "
            f"currently {m['current_value']:,.1f}, target {m['target_value']:,.1f}."
        )

    st.divider()
    st.write(
        "This is the whole dashboard. The rule is 15 minutes every Monday: check the "
        "leading indicators first, then everything else, and only dig deeper into "
        "anything sitting yellow or red."
    )
else:
    st.info("Upload your candidate metric list above to build your dashboard.")
