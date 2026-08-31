"""
app.py
------
FinWise AI — Streamlit entry point.

Run with:  streamlit run app.py

This file only handles UI + wiring. Deterministic math lives in
src/financial_calculator.py. All LangChain logic lives in src/chains.py.
"""

import time
import streamlit as st
import openai

from src import config
from src.cache_manager import apply_cache_choice, get_cache_mode
from src.chains import build_analysis_chain, stream_recommendations, demo_message_roles
from src.financial_calculator import (
    calculate_totals,
    calculate_preliminary_score,
    build_expense_breakdown_text,
)
from src.utils import safe_parse_json, risk_icon, score_band_label

st.set_page_config(page_title="FinWise AI", page_icon="💰", layout="wide")

EXPENSE_LABELS = dict(config.EXPENSE_CATEGORIES)

# ---------------------------------------------------------------------------
# SESSION STATE DEFAULTS
# ---------------------------------------------------------------------------
if "api_key_verified" not in st.session_state:
    st.session_state.api_key_verified = False
if "verified_api_key" not in st.session_state:
    st.session_state.verified_api_key = ""


def test_api_key(key: str) -> tuple[bool, str]:
    """
    Makes a minimal, cheap call to OpenAI to confirm the key actually works.
    Returns (is_valid, error_message).
    """
    if not key or not key.strip():
        return False, "Please enter an API key."

    try:
        client = openai.OpenAI(api_key=key.strip())
        # Listing models is free / doesn't consume completion tokens —
        # it just confirms the key is real and has API access.
        client.models.list()
        return True, ""
    except openai.AuthenticationError:
        return False, "Invalid API key. Please check and try again."
    except openai.APIConnectionError:
        return False, "Could not connect to OpenAI. Check your internet connection."
    except Exception as e:
        return False, f"Key test failed: {e}"


# ---------------------------------------------------------------------------
# GATE SCREEN — shown until the API key is verified
# ---------------------------------------------------------------------------
if not st.session_state.api_key_verified:
    st.title("💰 FinWise AI")
    st.caption("AI-Powered Personal Financial Analysis & Smart Budget Assistant (Educational Prototype)")
    st.warning(config.FINANCIAL_DISCLAIMER)

    st.subheader("🔑 Enter your OpenAI API key to continue")
    st.write(
        "Your key is used only for this session and is never saved to disk. "
        "We'll do a quick test to make sure it works before loading the app."
    )

    with st.form("api_key_gate_form"):
        entered_key = st.text_input(
            "OpenAI API key",
            type="password",
            placeholder="sk-...",
        )
        # Fall back to a key configured in .env, if present, as an option
        use_env_key = False
        if config.OPENAI_API_KEY:
            use_env_key = st.checkbox("Use the key configured in this app's .env file instead")

        verify_clicked = st.form_submit_button("Test key & Continue")

    if verify_clicked:
        key_to_test = config.OPENAI_API_KEY if use_env_key else entered_key
        with st.spinner("Testing your API key..."):
            is_valid, err = test_api_key(key_to_test)

        if is_valid:
            st.session_state.api_key_verified = True
            st.session_state.verified_api_key = key_to_test.strip()
            st.success("✅ API key verified! Loading the app...")
            st.rerun()
        else:
            st.error(f"❌ {err}")

    st.stop()  # Don't render anything below until the key is verified

# ---------------------------------------------------------------------------
# FROM HERE ON: key is verified — this is the original app
# ---------------------------------------------------------------------------
active_api_key = st.session_state.verified_api_key

# ---------------------------------------------------------------------------
# SIDEBAR — identity, disclaimer, model config, API key status, caching, reset
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("💰 FinWise AI")
    st.caption("AI-Powered Personal Financial Analysis & Smart Budget Assistant (Educational Prototype)")

    st.warning(config.FINANCIAL_DISCLAIMER)

    st.subheader("⚙️ Model Configuration")
    st.text(f"Model: {config.MODEL_NAME}")
    st.text(f"Temperature: {config.MODEL_TEMPERATURE}")

    st.subheader("🔑 API Key")
    st.success("Using verified API key for this session.")
    if st.button("Change API key"):
        st.session_state.api_key_verified = False
        st.session_state.verified_api_key = ""
        st.rerun()

    st.subheader("⚡ Caching")
    cache_choice = st.selectbox(
        "Cache mode", ["None", "In-Memory", "SQLite"],
        help="In-Memory: fastest, cleared on restart. SQLite: saved to disk, "
             "survives restarts. Submit the same form twice to see the speed-up.",
    )
    apply_cache_choice(cache_choice)
    st.caption(f"Active cache: `{get_cache_mode()}`")

    st.subheader("🔄 Session")
    if st.button("Reset session"):
        verified_key_backup = st.session_state.verified_api_key
        st.session_state.clear()
        # Keep the user logged in with their verified key after a reset —
        # only the form/answers get cleared, not the API-key gate.
        st.session_state.api_key_verified = True
        st.session_state.verified_api_key = verified_key_backup
        st.rerun()

    with st.expander("ℹ️ About this prototype"):
        st.write(
            "FinWise AI is a learning project built with LangChain and "
            "Streamlit. Totals, ratios, and the preliminary score are "
            "computed deterministically in Python; the AI only interprets "
            "and explains those numbers. It is **not** financial advice."
        )

# ---------------------------------------------------------------------------
# MAIN AREA — disclaimer banner + intake form
# ---------------------------------------------------------------------------
st.title("FinWise AI — Smart Budget Assistant")
st.info(config.FINANCIAL_DISCLAIMER)

with st.form("financial_form"):
    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("Currency", config.CURRENCY_OPTIONS)
        income = st.number_input("Monthly income", min_value=0.0, step=50.0, format="%.2f")
        savings = st.number_input("Current monthly savings", min_value=0.0, step=50.0, format="%.2f")
    with col2:
        financial_goal = st.selectbox("Financial goal", config.FINANCIAL_GOAL_OPTIONS)

    st.markdown("#### Monthly Expenses")
    expense_cols = st.columns(3)
    expenses = {}
    for i, (key, label) in enumerate(config.EXPENSE_CATEGORIES):
        with expense_cols[i % 3]:
            expenses[key] = st.number_input(label, min_value=0.0, step=10.0, format="%.2f", key=f"exp_{key}")

    submitted = st.form_submit_button("Analyze My Finances")

# ---------------------------------------------------------------------------
# ON SUBMIT
# ---------------------------------------------------------------------------
if submitted:
    if income <= 0:
        st.warning("Please enter a monthly income greater than 0.")
        st.stop()

    # --- Step 1: deterministic Python calculations (no AI here) ---------
    totals = calculate_totals(income, expenses, savings)
    preliminary_score = calculate_preliminary_score(income, expenses, savings)
    expense_breakdown_text = build_expense_breakdown_text(expenses, EXPENSE_LABELS)

    inputs = {
        "monthly_income": income,
        "total_expenses": totals["total_expenses"],
        "remaining_income": totals["remaining_income"],
        "savings": savings,
        "savings_ratio": totals["savings_ratio"],
        "expense_ratio": totals["expense_ratio"],
        "financial_goal": financial_goal,
        "expense_breakdown": expense_breakdown_text,
        "preliminary_score": preliminary_score,
        "currency": currency,
    }

    # --- Financial overview (pure Python numbers) ------------------------
    st.subheader("📊 Financial Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Income", f"{currency} {income:,.2f}")
    m2.metric("Total Expenses", f"{currency} {totals['total_expenses']:,.2f}")
    m3.metric("Remaining Income", f"{currency} {totals['remaining_income']:,.2f}")
    m4.metric("Current Savings", f"{currency} {savings:,.2f}")

    st.caption(
        f"Savings ratio: {totals['savings_ratio']}% | "
        f"Expense ratio: {totals['expense_ratio']}% | "
        f"Preliminary score (Python-calculated): {preliminary_score}/100"
    )

    tab_dashboard, tab_narrative, tab_debug = st.tabs(
        ["🧠 AI Analysis", "📝 Recommendation (streamed)", "🔧 Debug"]
    )

    # --- Structured JSON analysis via LLMChain ---------------------------
    start = time.time()
    chain = build_analysis_chain(api_key=active_api_key)
    raw_output = chain.run(**inputs)
    elapsed = time.time() - start

    data, error = safe_parse_json(raw_output)

    with tab_dashboard:
        st.caption(f"Response time: {elapsed:.2f}s (cache mode: {get_cache_mode()})")

        if error:
            st.error(f"Sorry, something went wrong reading the AI's response: {error}")
            with st.expander("Show raw AI output (for debugging)"):
                st.code(raw_output)
        else:
            score = int(data.get("financial_health_score", preliminary_score))
            risk = data.get("risk_level", "MEDIUM").upper()
            icon = risk_icon(risk)

            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.metric("Financial Health Score", f"{score}/100")
                st.progress(min(max(score, 0), 100) / 100)
                st.caption(score_band_label(score))
            with col_b:
                st.write(data.get("financial_summary", ""))
                st.metric("Risk Level", f"{icon} {risk}")

            if risk == "HIGH":
                st.error("🔴 High risk — spending currently outpaces income or debt burden is heavy. Prioritize the action plan below.")
            elif risk == "MEDIUM":
                st.warning("🟠 Medium risk — there's room to tighten the budget and build a safety margin.")
            else:
                st.success("🟢 Low risk — your numbers look healthy. Focus on reinforcing good habits.")

            st.subheader("📂 Spending Analysis")
            for item in data.get("spending_analysis", []):
                with st.expander(item.get("category", "Category")):
                    st.write(f"**Observation:** {item.get('observation', '')}")
                    st.write(f"**Recommendation:** {item.get('recommendation', '')}")

            col_c, col_d = st.columns(2)
            with col_c:
                st.subheader("🎯 Top Priorities")
                for p in data.get("top_priorities", []):
                    st.write(f"- {p}")

                st.subheader("💡 Budget Recommendations")
                for b in data.get("budget_recommendations", []):
                    st.write(f"- {b}")

            with col_d:
                st.subheader("🏦 Savings Strategy")
                for s in data.get("savings_strategy", []):
                    st.write(f"- {s}")

                st.subheader("📅 Next Month Action Plan")
                for a in data.get("next_month_action_plan", []):
                    st.write(f"- {a}")

            st.warning(config.FINANCIAL_DISCLAIMER)

    # --- Streamed human-readable recommendation --------------------------
    with tab_narrative:
        st.caption("Live-streamed recommendation:")
        st.write_stream(stream_recommendations(inputs, api_key=active_api_key))
        st.warning(config.FINANCIAL_DISCLAIMER)

    # --- Debug tab: raw JSON + message-roles demo -------------------------
    with tab_debug:
        st.caption("Raw JSON returned by the LLMChain:")
        st.code(raw_output, language="json")

        if st.checkbox("Run System/Human/AI message demo"):
            convo = demo_message_roles(
                "In one sentence, what's a good first step for someone overspending on food?",
                api_key=active_api_key,
            )
            for msg in convo:
                st.write(f"**{msg.__class__.__name__}:** {msg.content}")

else:
    st.caption("Fill in the form above and click **Analyze My Finances** to begin.")
