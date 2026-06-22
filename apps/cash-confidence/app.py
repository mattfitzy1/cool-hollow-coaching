"""
Business Without You, Cash Confidence.

The in-program tool for Milestone 5 (week 6): a client uploads their
13-week cash item list (AR/AP and payment timing turned into weekly
inflows and outflows) plus their recurring expense list rated against the
five-question Financial Decision Filter.

This produces the 13-week rolling cash forecast, scores every recurring
expense, and shows what the forecast looks like if every cut candidate
actually gets cut.
"""

import os

import pandas as pd
import streamlit as st

from analysis import run_cash_confidence

TEMPLATE_NAME = "Cool_Hollow_Coaching_Milestone_5_Cash_Confidence_Template.xlsx"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), TEMPLATE_NAME)

st.set_page_config(page_title="Business Without You, Cash Confidence", page_icon="\U0001F4B0")

st.title("Cash Confidence")
st.write(
    "Milestone 5. Upload your 13-week cash item list and your recurring expense "
    "list to get your cash forecast, your Financial Decision Filter results, and "
    "the dollar difference between the two."
)

st.warning(
    "The forecast is only as good as the cash items you give it. Leave out a "
    "known expense because it's uncomfortable, and the forecast will look "
    "calmer than the actual 13 weeks ahead of you."
)

if os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button("Download the blank template", f.read(), file_name=TEMPLATE_NAME,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()

starting_balance = st.number_input("Your current cash balance ($)", min_value=0.0, value=0.0, step=1000.0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 13-week cash items")
    with st.expander("What file should I upload?"):
        st.write(
            "A CSV or Excel sheet with one row per cash item. Required columns: "
            "**week** (1-13), **type** (inflow or outflow), **amount**. Optional: "
            "**category** and **description**. If a row is a recurring expense "
            "you've also rated in the filter, put that exact expense name in "
            "**category** or **description** so the model can match it."
        )
    cash_file = st.file_uploader("Upload your cash items (CSV or Excel)", type=["csv", "xlsx", "xls"], key="cash")

with col2:
    st.subheader("2. Recurring expenses")
    with st.expander("What file should I upload?"):
        st.write(
            "A CSV or Excel sheet with one row per recurring expense. Required: "
            "**expense_name**, **weekly_amount**, and five ratings (1-5): "
            "**core_customer_fit**, **revenue_risk_if_cut**, **roi_clarity**, "
            "**no_cheaper_alternative**, **would_approve_today**."
        )
    expenses_file = st.file_uploader("Upload your recurring expenses (CSV or Excel)", type=["csv", "xlsx", "xls"], key="expenses")

st.subheader("3. Receivables aging (optional, but the most common real cash problem)")
with st.expander("What file should I upload?"):
    st.write(
        "A CSV or Excel sheet with one row per customer who owes you money. Required: "
        "**customer_name**, **amount_outstanding**, **terms_days** (what your stated "
        "terms are, net-30 is 30), **days_outstanding** (how long it's actually been "
        "unpaid). The Decision Filter above only ever catches spend worth cutting, it "
        "does nothing for cash that's stuck because a customer is paying late. This is "
        "usually the bigger lever."
    )
receivables_file = st.file_uploader("Upload your receivables aging (CSV or Excel)", type=["csv", "xlsx", "xls"], key="receivables")

st.divider()

if cash_file and expenses_file:
    try:
        cash_raw = pd.read_csv(cash_file) if cash_file.name.lower().endswith(".csv") else pd.read_excel(cash_file)
        expenses_raw = pd.read_csv(expenses_file) if expenses_file.name.lower().endswith(".csv") else pd.read_excel(expenses_file)
        receivables_raw = None
        if receivables_file:
            receivables_raw = pd.read_csv(receivables_file) if receivables_file.name.lower().endswith(".csv") else pd.read_excel(receivables_file)
    except pd.errors.ParserError:
        st.error(
            "Could not read one of those files. This usually means a description or "
            "expense name has a comma in it that got mistaken for a new column. Put "
            "quotes around any name with a comma, or swap the comma for a dash, and "
            "upload again."
        )
        st.stop()
    except Exception:
        st.error("Could not read one of those files. Double-check they match the format above and try again.")
        st.stop()

    try:
        result = run_cash_confidence(cash_raw, expenses_raw, starting_balance, receivables_raw)
    except Exception as exc:
        st.error(f"Could not run the forecast: {exc}")
        st.stop()

    if result["baseline_negative_weeks"]:
        st.error(
            "Baseline forecast goes negative in week(s): "
            + ", ".join(str(w) for w in result["baseline_negative_weeks"]) + "."
        )
    else:
        st.success("Baseline forecast stays positive across all 13 weeks.")

    st.header("13-week cash forecast")
    forecast_df = pd.DataFrame(result["baseline_forecast"]).rename(
        columns={"week": "Week", "net": "Net this week", "balance": "Running balance"}
    )
    st.line_chart(forecast_df.set_index("Week")["Running balance"])
    st.dataframe(forecast_df, hide_index=True)

    receivables = result["receivables"]
    if receivables["overdue_accounts"]:
        st.divider()
        st.header(f"Receivables timing: ${receivables['overdue_amount']:,.0f} stuck beyond your own terms")
        st.write(
            f"Of ${receivables['total_outstanding']:,.0f} total outstanding, "
            f"${receivables['overdue_amount']:,.0f} is sitting past the terms you actually quoted. "
            f"This is cash you've already earned, it's just not in the bank yet. For most owners "
            f"in this program, accelerating this is a bigger lever than cutting any expense below."
        )
        for acct in receivables["overdue_accounts"]:
            st.write(
                f"- **{acct['customer_name']}**: ${acct['amount_outstanding']:,.0f} outstanding, "
                f"{acct['days_outstanding']} days (terms are {acct['terms_days']}), "
                f"{acct['days_overdue']} days past terms."
            )
        st.write(
            "Levers worth a real conversation: a deposit or milestone billing on the next job, "
            "tighter terms on renewal, or factoring the invoice if the cash is needed sooner than "
            "a conversation with the customer will get it."
        )

    st.divider()
    st.header("The Financial Decision Filter")
    filt = result["decision_filter"]

    if filt["cut_candidates"]:
        st.subheader(f"Cut candidates: ${filt['weekly_savings_if_cut']:,.0f}/week")
        for item in filt["cut_candidates"]:
            st.write(f"- **{item['expense_name']}** (${item['weekly_amount']:,.0f}/week, score {item['composite']}/5). {item['reasoning']}")
    else:
        st.write("No recurring expense failed the filter. Everything earns its place today.")

    if filt["keep"]:
        with st.expander(f"See the {len(filt['keep'])} expense(s) that passed"):
            for item in filt["keep"]:
                st.write(f"- **{item['expense_name']}** (${item['weekly_amount']:,.0f}/week, score {item['composite']}/5). {item['reasoning']}")

    if filt["cut_candidates"]:
        st.divider()
        st.header("If you cut them starting next week")
        adjusted_df = pd.DataFrame(result["adjusted_forecast"]).rename(
            columns={"week": "Week", "net": "Net this week", "balance": "Running balance"}
        )
        st.line_chart(adjusted_df.set_index("Week")["Running balance"])
        if result["adjusted_negative_weeks"]:
            st.warning(
                "Even after cutting, the forecast still goes negative in week(s): "
                + ", ".join(str(w) for w in result["adjusted_negative_weeks"]) + "."
            )
        else:
            st.success("Cutting these clears every negative week in the 13-week window.")

    st.divider()
    st.write(
        "Bring both forecasts to your next live call. The Decision Filter only "
        "matters if a cut candidate actually gets cancelled, not just flagged."
    )
else:
    st.info("Upload both files above to run Cash Confidence.")
