"""
financial_calculator.py
------------------------
Pure, deterministic Python math — NO AI calls in this file.

The assignment requires these calculations to be clearly separated from the
LLM's job: given the same numbers, this file always returns the same result.
The LLM only interprets and explains what these numbers already established.
"""


def calculate_totals(income: float, expenses: dict, savings: float) -> dict:
    """Compute total expenses, remaining income, savings ratio, expense ratio.

    `expenses` is a dict like {"housing": 500, "food": 300, ...}.
    Guards against divide-by-zero when income is 0.
    """
    total_expenses = sum(expenses.values())
    remaining_income = income - total_expenses

    if income > 0:
        savings_ratio = (savings / income) * 100
        expense_ratio = (total_expenses / income) * 100
    else:
        savings_ratio = 0.0
        expense_ratio = 0.0

    return {
        "total_expenses": round(total_expenses, 2),
        "remaining_income": round(remaining_income, 2),
        "savings_ratio": round(savings_ratio, 2),
        "expense_ratio": round(expense_ratio, 2),
    }


def calculate_preliminary_score(income: float, expenses: dict, savings: float) -> int:
    """A simple weighted 0-100 heuristic used BEFORE calling the AI.

    This gives the dashboard something to show immediately and gives the LLM
    a consistent, Python-verified number to reference rather than inventing
    its own score from scratch. Weights (informal, education-only):
      - 40 pts: savings ratio (savings / income)
      - 30 pts: leftover income ratio (remaining / income)
      - 20 pts: expense ratio penalty (total expenses / income)
      - 10 pts: debt burden penalty (debt / income)
    """
    if income <= 0:
        return 0

    totals = calculate_totals(income, expenses, savings)
    savings_ratio = totals["savings_ratio"]
    remaining_income = totals["remaining_income"]
    expense_ratio = totals["expense_ratio"]
    debt = expenses.get("debt", 0)
    debt_ratio = (debt / income) * 100 if income > 0 else 0

    # 1) Savings score: 20%+ savings ratio = full marks
    savings_score = min(savings_ratio / 20, 1.0) * 40

    # 2) Leftover income score: 20%+ leftover = full marks
    leftover_ratio = max(remaining_income / income, 0) * 100
    leftover_score = min(leftover_ratio / 20, 1.0) * 30

    # 3) Expense ratio penalty: under 60% expense ratio = full marks
    if expense_ratio <= 60:
        expense_score = 20
    elif expense_ratio >= 100:
        expense_score = 0
    else:
        expense_score = 20 * (1 - (expense_ratio - 60) / 40)

    # 4) Debt burden penalty: under 15% debt ratio = full marks
    if debt_ratio <= 15:
        debt_score = 10
    elif debt_ratio >= 50:
        debt_score = 0
    else:
        debt_score = 10 * (1 - (debt_ratio - 15) / 35)

    score = savings_score + leftover_score + expense_score + debt_score
    return int(round(max(0, min(score, 100))))


def build_expense_breakdown_text(expenses: dict, labels: dict) -> str:
    """Turn the expenses dict into a readable "Category: amount" string
    for insertion into the LLM prompt."""
    lines = [f"{labels.get(key, key)}: {amount}" for key, amount in expenses.items()]
    return "; ".join(lines)
