"""
prompts.py
----------
All prompt engineering for FinWise AI.

Contains:
- SYSTEM_PROMPT              : educational financial-assistant role + safety rules.
- JSON_SCHEMA_INSTRUCTIONS   : exact JSON shape the model must return.
- ANALYSIS_PROMPT_TEMPLATE   : a classic single-string PromptTemplate.
- ANALYSIS_CHAT_TEMPLATE     : ChatPromptTemplate (System + Human) for the JSON call.
- NARRATIVE_CHAT_TEMPLATE    : ChatPromptTemplate used for the streamed recommendation text.
"""

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------------------------------
# 1) SYSTEM PROMPT
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are FinWise AI, an educational personal-finance assistant.

STRICT SAFETY RULES (never break these):
1. You are NOT a licensed financial advisor and must NEVER guarantee any
   financial outcome or promise specific investment returns.
2. All numbers describing totals, ratios, and the preliminary score are
   provided to you already calculated by Python — never recompute or
   contradict them; only interpret and explain them.
3. Frame all suggestions as general education, not personalized professional
   advice, and recommend the user speak with a qualified financial advisor
   for major decisions.
4. If the numbers show negative remaining income or an expense ratio over
   100%, risk_level MUST be "HIGH" and priorities must clearly flag the
   overspending.
5. Keep the tone calm, encouraging, and non-judgmental — never shaming the
   user about their spending.
6. Reply in the currency and language context given, using the provided
   currency symbol/code consistently.
"""

# ---------------------------------------------------------------------------
# 2) JSON SCHEMA INSTRUCTIONS
# ---------------------------------------------------------------------------
JSON_SCHEMA_INSTRUCTIONS = """Return ONLY valid JSON — no markdown fences, no commentary before or after —
matching EXACTLY this structure:

{{
  "financial_summary": "one short paragraph summarizing the user's situation",
  "financial_health_score": 0,
  "spending_analysis": [
    {{"category": "category name", "observation": "what stands out", "recommendation": "what to do about it"}}
  ],
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "top_priorities": ["priority 1", "priority 2"],
  "budget_recommendations": ["recommendation 1", "recommendation 2"],
  "savings_strategy": ["strategy 1", "strategy 2"],
  "next_month_action_plan": ["action 1", "action 2"]
}}

Use the provided preliminary_score as financial_health_score unless the
numbers clearly justify a small adjustment — if you adjust it, stay within
+/- 5 points of the preliminary_score.
"""

# ---------------------------------------------------------------------------
# 3) PromptTemplate — reusable single-string template
# ---------------------------------------------------------------------------
ANALYSIS_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=[
        "monthly_income", "total_expenses", "remaining_income", "savings",
        "savings_ratio", "expense_ratio", "financial_goal",
        "expense_breakdown", "preliminary_score", "currency",
    ],
    template=(
        "Financial profile ({currency}):\n"
        "- Monthly income: {monthly_income}\n"
        "- Total expenses: {total_expenses}\n"
        "- Remaining income: {remaining_income}\n"
        "- Current savings: {savings}\n"
        "- Savings ratio: {savings_ratio}%\n"
        "- Expense ratio: {expense_ratio}%\n"
        "- Financial goal: {financial_goal}\n"
        "- Expense breakdown: {expense_breakdown}\n"
        "- Preliminary Python-calculated score (0-100): {preliminary_score}\n\n"
        + JSON_SCHEMA_INSTRUCTIONS
    ),
)

# ---------------------------------------------------------------------------
# 4) ChatPromptTemplate — used for the JSON analysis call
# ---------------------------------------------------------------------------
ANALYSIS_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Financial profile ({currency}):\n"
            "- Monthly income: {monthly_income}\n"
            "- Total expenses: {total_expenses}\n"
            "- Remaining income: {remaining_income}\n"
            "- Current savings: {savings}\n"
            "- Savings ratio: {savings_ratio}%\n"
            "- Expense ratio: {expense_ratio}%\n"
            "- Financial goal: {financial_goal}\n"
            "- Expense breakdown: {expense_breakdown}\n"
            "- Preliminary Python-calculated score (0-100): {preliminary_score}\n\n"
            + JSON_SCHEMA_INSTRUCTIONS,
        ),
    ]
)

# ---------------------------------------------------------------------------
# 5) ChatPromptTemplate — streamed, human-readable recommendation narrative
# ---------------------------------------------------------------------------
NARRATIVE_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Based on this financial profile, write a short, warm, plain-language "
            "recommendation (4-6 sentences, no JSON, no markdown headers) about "
            "what this person could focus on next month. Use {currency} when "
            "mentioning amounts.\n\n"
            "- Monthly income: {monthly_income}\n"
            "- Total expenses: {total_expenses}\n"
            "- Remaining income: {remaining_income}\n"
            "- Savings ratio: {savings_ratio}%\n"
            "- Expense ratio: {expense_ratio}%\n"
            "- Financial goal: {financial_goal}\n"
            "- Expense breakdown: {expense_breakdown}\n"
            "- Preliminary score: {preliminary_score}\n",
        ),
    ]
)
