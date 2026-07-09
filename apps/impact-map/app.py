"""
Business Without You, the 12-Month Impact Map.

The in-program tool for Milestone 2 (week 2): a client uploads their raw
list of everything planned for the next 12 months, each initiative rated
against the Strategy Razor (core customer fit, unfair advantage fit,
impact, effort).

This applies the razor and outputs the filtered 12-Month Impact Map: the
3-5 initiatives worth the focus, a focus score showing how much got cut,
and the reasoning behind every cut.
"""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from branding import apply_branding, show_disclaimer
from client_upload import read_upload
from results_pdf import build_results_pdf

from analysis import build_impact_map, load_initiatives

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_2_Impact_Map_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, the 12-Month Impact Map", page_icon="\U0001F3AF")
apply_branding(2, "The 12-Month Impact Map")

st.title("The 12-Month Impact Map")
st.write(
    "Milestone 2. Upload your raw initiative list, each one rated against the "
    "Strategy Razor, to get your filtered 12-Month Impact Map."
)

st.warning(
    "Rate honestly. If you rate everything a 5 across the board to protect a pet "
    "project, the razor cannot do its job and the list stays exactly as crowded "
    "as it is today."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.caption("Fill in the data tab, save, and upload that same file below. The Instructions and Examples tabs stay in the file, the tool skips them automatically.")

st.divider()

st.subheader("Your initiative list")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per initiative. Required columns: "
        "**initiative**, **core_customer_fit** (1-5), **unfair_advantage_fit** (1-5), "
        "**impact** (1-5), **effort** (1-5). Rate each from your Strategy Razor draft, "
        "Core Customer Decree, and Unfair Advantage list."
    )
initiatives_file = st.file_uploader("Upload your initiative list (CSV or Excel)", type=["csv", "xlsx", "xls"], key="initiatives")

st.divider()

if initiatives_file:
    try:
        raw = read_upload(initiatives_file, {"initiative", "core_customer_fit", "unfair_advantage_fit", "impact", "effort"})
    except pd.errors.ParserError:
        st.error(
            "Could not read that file. This usually means an initiative name has a comma "
            "in it that got mistaken for a new column. Put quotes around any initiative "
            "with a comma, or swap the comma for a dash, and upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read that file. Double-check it matches the format above and try again.")
        st.stop()

    try:
        initiatives = load_initiatives(raw)
        result = build_impact_map(initiatives)
    except Exception as exc:
        st.error(f"Could not build the impact map: {exc}")
        st.stop()

    st.header(f"{result['focus_score']:.0%} of the list cut")
    st.write(
        f"{len(result['kept'])} of {result['total_initiatives']} initiatives kept for the next 12 months."
    )

    st.subheader("The 12-Month Impact Map")
    for item in result["kept"]:
        st.write(f"- **{item['initiative']}** (impact {item['impact']}/5, effort {item['effort']}/5). {item['reasoning']}")

    if result["cut"]:
        st.divider()
        with st.expander(f"See the {len(result['cut'])} initiative(s) cut, and why"):
            for item in result["cut"]:
                st.write(f"- **{item['initiative']}**. {item['reasoning']}")

    st.divider()
    st.write(
        "Bring this map to your next live call. The test is not whether the kept list "
        "looks impressive, it's whether you actually stop chasing what got cut."
    )

    pdf_sections = [("Kept for the next 12 months", [
        f"{item['initiative']} (impact {item['impact']}/5, effort {item['effort']}/5). {item['reasoning']}"
        for item in result["kept"]
    ])]
    if result["cut"]:
        pdf_sections.append(("Cut, and why", [
            f"{item['initiative']}. {item['reasoning']}" for item in result["cut"]
        ]))
    pdf_bytes = build_results_pdf(
        2, "The 12-Month Impact Map",
        f"{result['focus_score']:.0%} of the list cut. "
        f"{len(result['kept'])} of {result['total_initiatives']} initiatives kept for the next 12 months.",
        pdf_sections,
    )
    st.download_button(
        "Download your results (PDF)", pdf_bytes,
        file_name="Cool_Hollow_Coaching_Impact_Map_Results.pdf",
        mime="application/pdf", type="primary",
    )
    st.caption("Nothing you upload or generate here is stored on our servers. This download is your only copy.")
else:
    st.info("Upload your initiative list above to build your 12-Month Impact Map.")

show_disclaimer()
