"""
LLM analysis layer.

Calls the Claude API (claude-sonnet-4-6) to produce a structured risk
assessment on top of the ML baseline score.  Degrades gracefully to None
when ``ANTHROPIC_API_KEY`` is absent or any API error occurs.

Public surface
--------------
- ``build_prompt()``   — construct the user-turn text sent to Claude
- ``parse_llm_response()`` — extract LLMResult from raw model output
- ``analyze()``        — orchestrate the API call; returns None on failure
"""
from __future__ import annotations

import json
import logging
import os
import re

import anthropic
from pydantic import ValidationError

from app.schemas import LLMResult

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 512

_SYSTEM_PROMPT = """\
You are a defensive cybersecurity analyst specialising in phishing detection.
Your task is to assess whether the email below is a phishing attempt and explain your reasoning.

RULES:
- Respond ONLY with a single valid JSON object — no prose, no markdown fences.
- JSON must have exactly these keys:
    "risk_level"  : one of "high", "medium", or "low"
    "reasoning"   : 2-3 sentences explaining the risk assessment
    "iocs"        : array of strings listing observed indicators of compromise (empty array if none)
- Do NOT generate phishing content, attack code, or offensive material.
- Treat this as a purely defensive, educational analysis.
"""


def _get_client() -> anthropic.Anthropic | None:
    """Return an Anthropic client if the API key is configured, else None."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def build_prompt(*, subject: str, body: str, ml_score: float) -> str:
    """Build the user-turn message sent to Claude."""
    return (
        f"ML baseline phishing probability: {ml_score:.2f}\n\n"
        f"Subject: {subject}\n\n"
        f"Body:\n{body}"
    )


def parse_llm_response(raw: str) -> LLMResult | None:
    """
    Extract an LLMResult from the model's raw text output.

    Handles optional markdown code fences (```json ... ```) that Claude
    sometimes adds even when instructed not to.  Returns None if the text
    cannot be parsed into a valid LLMResult.
    """
    # Strip markdown code fence if present
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)
    try:
        data = json.loads(cleaned)
        return LLMResult.model_validate(data)
    except (json.JSONDecodeError, ValidationError, ValueError):
        return None


def analyze(*, subject: str, body: str, ml_score: float) -> LLMResult | None:
    """
    Run the LLM analysis layer on one email.

    Returns an LLMResult on success, or None if the API key is absent,
    the API call fails, or the response cannot be parsed.
    """
    client = _get_client()
    if client is None:
        logger.debug("ANTHROPIC_API_KEY not set — skipping LLM analysis")
        return None

    prompt = build_prompt(subject=subject, body=body, ml_score=ml_score)

    try:
        message = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        logger.exception("Claude API call failed — degrading to ML-only")
        return None

    block = message.content[0]
    if not hasattr(block, "text"):
        logger.warning("Unexpected content block type from Claude: %s", type(block))
        return None
    raw: str = block.text
    result = parse_llm_response(raw)
    if result is None:
        logger.warning("Could not parse LLM response: %r", raw[:200])
    return result
