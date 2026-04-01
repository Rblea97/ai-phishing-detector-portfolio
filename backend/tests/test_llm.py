"""Tests for the LLM analysis layer (app/llm.py)."""
import json
from unittest.mock import MagicMock, patch

from app.llm import analyze, build_prompt, parse_llm_response
from app.schemas import LLMResult

# ── build_prompt ──────────────────────────────────────────────────────────────


def test_build_prompt_includes_subject() -> None:
    prompt = build_prompt(subject="Verify your account", body="Click here.", ml_score=0.9)
    assert "Verify your account" in prompt


def test_build_prompt_includes_body() -> None:
    prompt = build_prompt(subject="Hello", body="This is the body text.", ml_score=0.5)
    assert "This is the body text." in prompt


def test_build_prompt_includes_ml_score() -> None:
    prompt = build_prompt(subject="Hello", body="Body.", ml_score=0.83)
    assert "0.83" in prompt


# ── parse_llm_response ────────────────────────────────────────────────────────


def test_parse_valid_response() -> None:
    raw = json.dumps({
        "risk_level": "high",
        "reasoning": "This email uses urgency and requests credentials.",
        "iocs": ["urgency language", "credential harvesting link"],
    })
    result = parse_llm_response(raw)
    assert isinstance(result, LLMResult)
    assert result.risk_level == "high"
    assert len(result.iocs) == 2


def test_parse_response_with_markdown_fence() -> None:
    """Claude sometimes wraps JSON in a markdown code fence."""
    raw = '```json\n{"risk_level": "low", "reasoning": "Looks fine.", "iocs": []}\n```'
    result = parse_llm_response(raw)
    assert result.risk_level == "low"
    assert result.iocs == []


def test_parse_invalid_json_returns_none() -> None:
    result = parse_llm_response("this is not json")
    assert result is None


def test_parse_invalid_risk_level_returns_none() -> None:
    raw = json.dumps({"risk_level": "critical", "reasoning": "Bad.", "iocs": []})
    result = parse_llm_response(raw)
    assert result is None


def test_parse_missing_field_returns_none() -> None:
    raw = json.dumps({"risk_level": "high", "iocs": []})  # missing reasoning
    result = parse_llm_response(raw)
    assert result is None


# ── analyze ───────────────────────────────────────────────────────────────────


def test_analyze_returns_none_when_no_api_key() -> None:
    """When ANTHROPIC_API_KEY is absent, analyze() should return None gracefully."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("app.llm._get_client", return_value=None):
            result = analyze(subject="Test", body="Test body.", ml_score=0.5)
    assert result is None


def test_analyze_returns_llm_result_on_success() -> None:
    """When the API returns valid JSON, analyze() returns a populated LLMResult."""
    mock_response_text = json.dumps({
        "risk_level": "high",
        "reasoning": "Suspicious credential request with urgency.",
        "iocs": ["urgency language", "external login link"],
    })

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=mock_response_text)]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("app.llm._get_client", return_value=mock_client):
        result = analyze(subject="Verify now", body="Click link.", ml_score=0.9)

    assert isinstance(result, LLMResult)
    assert result.risk_level == "high"
    assert len(result.iocs) == 2


def test_analyze_returns_none_on_api_error() -> None:
    """When the API raises an exception, analyze() returns None (graceful degrade)."""
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API unavailable")

    with patch("app.llm._get_client", return_value=mock_client):
        result = analyze(subject="Test", body="Test body.", ml_score=0.5)

    assert result is None


def test_analyze_returns_none_on_bad_response() -> None:
    """When Claude returns unparseable output, analyze() returns None."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Sorry, I cannot help with that.")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("app.llm._get_client", return_value=mock_client):
        result = analyze(subject="Test", body="Test body.", ml_score=0.5)

    assert result is None
