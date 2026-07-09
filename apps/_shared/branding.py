"""
Shared Cool Hollow Coaching branding for the milestone tools.

Every app calls apply_branding() first thing, right after st.set_page_config.
One place to change the logo, colors, or header layout for all seven tools.

Uses the compass-mark icon (approved, renders clean) paired with a text
wordmark, not the full logo lockup (brand.md flags the combined SVG has
unresolved rendering issues). Placeholder until the logo is formally locked.
"""

import base64
import os

import streamlit as st

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
_LOGO_WHITE = os.path.join(_ASSETS, "logo-gold-white.png")

INK = "#1A1A1A"
GOLD = "#C8A227"
GOLD_LT = "#E8C766"
PAPER = "#FFFFFF"


def _logo_b64():
    with open(_LOGO_WHITE, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_branding(milestone_number: int, milestone_name: str):
    """Injects the Cool Hollow Coaching header and house styling.

    Call once, right after st.set_page_config(), before any other st.* calls.
    """
    logo_b64 = _logo_b64()

    st.markdown(
        f"""
        <style>
        .chc-header {{
            background: {INK};
            padding: 20px 28px;
            border-radius: 8px;
            border-bottom: 3px solid {GOLD};
            display: flex;
            align-items: center;
            gap: 18px;
            margin-bottom: 28px;
        }}
        .chc-header img {{ height: 48px; }}
        .chc-header-text {{ display: flex; flex-direction: column; }}
        .chc-company {{
            color: {GOLD};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 0;
        }}
        .chc-milestone {{
            color: {PAPER};
            font-size: 20px;
            font-weight: 700;
            margin: 2px 0 0 0;
        }}

        /* House styling: gold accents on primary actions, ink headings */
        div.stButton > button[kind="primary"], .stDownloadButton > button {{
            background-color: {GOLD} !important;
            color: {INK} !important;
            border: none !important;
            font-weight: 700 !important;
        }}
        div.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {{
            background-color: {GOLD_LT} !important;
            color: {INK} !important;
        }}
        h1, h2, h3 {{ color: {INK}; }}
        [data-testid="stSidebar"] {{ background-color: #FAFAFA; }}
        </style>

        <div class="chc-header">
            <img src="data:image/png;base64,{logo_b64}" alt="Cool Hollow Coaching">
            <div class="chc-header-text">
                <p class="chc-company">Cool Hollow Coaching &middot; Business Without You</p>
                <p class="chc-milestone">Milestone {milestone_number}: {milestone_name}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_disclaimer():
    """Renders the standard disclaimer footer. Call once, at the bottom of every tool.

    Draft language, not yet reviewed by an attorney. See outputs/legal/disclaimer.md.
    """
    st.divider()
    st.caption(
        "This tool provides general business and financial information for "
        "educational purposes only and does not constitute financial, legal, "
        "tax, or investment advice. Outputs are generated from the data you "
        "enter and have not been independently verified. Cool Hollow Coaching "
        "is not liable for decisions made based on this tool's output. "
        "Consult a qualified professional before acting on any recommendation."
    )
