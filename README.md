🚀 **Live Demo:** [[Click Here to Access MediGuide AI Assistant](https://finwiseai-8o.streamlit.app/)]

# FinWise AI

An educational LangChain + Streamlit prototype for AI-powered personal
financial analysis and budgeting guidance. **This is not financial advice
and must not be used to make real investment or money decisions.**

## Features

- Financial intake form (income, 9 expense categories, savings, goal, currency).
- Deterministic Python calculations (`financial_calculator.py`): total
  expenses, remaining income, savings ratio, expense ratio, and a
  preliminary 0-100 health score — computed with plain math, no AI.
- Structured JSON AI analysis (summary, health score, spending analysis,
  risk level, priorities, budget recommendations, savings strategy, next
  month's action plan) via `LLMChain` + `PromptTemplate`.
- A separate `ChatPromptTemplate` conversation streamed live into the UI
  with `st.write_stream`.
- Safe JSON parsing — malformed AI output never crashes the app.
- **Bring-your-own API key**: enter your OpenAI key in the sidebar for the
  session, or fall back to the key in `.env`.
- In-memory and SQLite caching, switchable from the sidebar.
- Reset-session button.
- Educational disclaimers on every relevant screen.

## Project Structure

```
finwise_ai/
├── app.py                     # Streamlit UI - run this
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── __init__.py
    ├── config.py                 # settings + form options
    ├── prompts.py                 # PromptTemplate + ChatPromptTemplate + JSON schema
    ├── financial_calculator.py    # deterministic maths - NO AI
    ├── chains.py                  # ChatOpenAI, LLMChain, streaming, message-role demo
    ├── cache_manager.py           # in-memory + SQLite caching switches
    └── utils.py                   # safe JSON parsing + helpers
```

## Python vs AI — what does each part do?

- **Python (`financial_calculator.py`)** always gives the exact same answer
  for the exact same inputs: total expenses, remaining income, savings
  ratio, expense ratio, and a preliminary 0-100 score from a fixed weighted
  formula. This is fast, free, and 100% predictable — no API call needed.
- **The LLM** never recalculates these numbers. It receives them as already-
  computed facts in the prompt and its job is only to *interpret* them:
  write the summary, flag risks, suggest priorities, and phrase an action
  plan in plain language. The system prompt explicitly tells it to treat
  the Python numbers as ground truth (see `prompts.py`).

This separation means the "hard numbers" on the dashboard can never be
wrong or inconsistent because of an AI hallucination — only the qualitative
advice comes from the model.

## Setup

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Get an OpenAI API key**
   - Create an account at platform.openai.com and generate a key under
     *API keys*.

3. **Configure your secrets (optional)**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and paste your key, OR simply type your key into the
   sidebar's "Your OpenAI API Key" field when the app is running — either
   works. The sidebar key is used only for that session and is never saved
   to disk. Never commit `.env` to version control.

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Caching: In-Memory vs SQLite

LangChain has a single global cache slot, registered with
`set_llm_cache(...)`. Every LLM call checks this cache first — if the exact
same prompt + model + parameters were seen before, LangChain returns the
saved answer instantly instead of calling the API again.

| | InMemoryCache | SQLiteCache |
|---|---|---|
| Stored in | RAM | A `.db` file on disk |
| Speed | Fastest | Fast, slightly slower (disk I/O) |
| Survives app restart? | ❌ No | ✅ Yes |
| Best for | Quick repeated tests in one session | Reusing answers across sessions/days, saving cost long-term |

Pick a cache mode in the sidebar, submit the form once, then submit the
**exact same** inputs again — the second run should be visibly faster
("Response time" shown at the top of the AI Analysis tab).

## Testing Scenarios

| # | Input | Expected calculation | Expected AI response |
|---|---|---|---|
| 1 | Income 8000, expenses ~2000 | Large positive remaining; high savings ratio | High score; LOW risk; growth-focused tips |
| 2 | Income 2000, expenses ~2600 | Negative remaining; expense ratio >100% | Low score; HIGH risk; urgent cost-cutting |
| 3 | Income 5000, debt 2500 | High debt share of income | MEDIUM/HIGH risk; debt-reduction priorities |
| 4 | Income 4000, savings 1200 | Savings ratio ~30% | High score; LOW risk; reinforce good habits |
| 5 | Income 3000, expenses 3000 | Remaining = 0 | MEDIUM/HIGH risk; find room to save |

## Disclaimer

FinWise AI is a learning project only. It is not a licensed financial
advisor, does not execute transactions, and does not connect to real bank
accounts. Always consult a qualified financial professional before making
real financial decisions.
