"""
config.py
----------
Central place for:
1. Loading secrets (API key) from the .env file.
2. Holding constant options used by the Streamlit form.

Beginner note: The OPENAI_API_KEY here is only a FALLBACK. The app also lets
each user type their own key into the sidebar at runtime (see app.py) so the
app can be shared without baking a personal key into .env at all.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Secrets / model settings
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.3"))

# ---------------------------------------------------------------------------
# Form options
# ---------------------------------------------------------------------------
FINANCIAL_GOAL_OPTIONS = [
    "Save money", "Build an emergency fund", "Pay off debt",
    "Plan a vacation", "Start a business", "Improve budgeting",
]

CURRENCY_OPTIONS = ["USD", "PKR", "EUR", "GBP", "AED", "INR"]

EXPENSE_CATEGORIES = [
    ("housing", "Housing / Rent"),
    ("food", "Food"),
    ("transportation", "Transportation"),
    ("utilities", "Utilities"),
    ("education", "Education"),
    ("healthcare", "Healthcare"),
    ("entertainment", "Entertainment"),
    ("debt", "Loan / Debt payments"),
    ("other", "Other"),
]

RISK_COLORS = {
    "LOW": "green",
    "MEDIUM": "orange",
    "HIGH": "red",
}

REQUIRED_JSON_KEYS = [
    "financial_summary",
    "financial_health_score",
    "spending_analysis",
    "risk_level",
    "top_priorities",
    "budget_recommendations",
    "savings_strategy",
    "next_month_action_plan",
]

FINANCIAL_DISCLAIMER = (
    "⚠️ **FinWise AI is an educational prototype, not a licensed financial advisor.** "
    "It does not provide guaranteed investment advice and does not connect to real "
    "bank accounts. Always consult a qualified financial professional before making "
    "real financial decisions."
)
