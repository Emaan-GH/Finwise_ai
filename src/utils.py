"""
utils.py
--------
Small stateless helpers:

- strip_json_fences()  : removes accidental ```json ... ``` wrappers.
- safe_parse_json()    : never lets a bad LLM response crash the app.
- risk_icon()           : emoji for a risk level.
- score_band_label()    : human label for a financial-health-score band.
"""

import json
import re

from src.config import REQUIRED_JSON_KEYS


def strip_json_fences(text: str) -> str:
    """Remove ```json / ``` fences and any stray text around the JSON object."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    return text


def safe_parse_json(raw_text: str):
    """Try to parse the model's raw output into a dict.

    Returns (parsed_dict_or_None, error_message_or_None). Never raises.
    """
    cleaned = strip_json_fences(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return None, f"Could not parse the AI's response as JSON ({exc})."

    missing = [key for key in REQUIRED_JSON_KEYS if key not in data]
    if missing:
        return None, f"AI response is missing expected fields: {', '.join(missing)}."

    return data, None


def risk_icon(level: str) -> str:
    icons = {"LOW": "🟢", "MEDIUM": "🟠", "HIGH": "🔴"}
    return icons.get(level.upper(), "⚪")


def score_band_label(score: int) -> str:
    """Educational-only score band, per the assignment spec (section 12)."""
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Generally healthy"
    if score >= 40:
        return "Needs improvement"
    return "High attention"
