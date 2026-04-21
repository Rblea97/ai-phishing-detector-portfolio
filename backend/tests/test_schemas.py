"""Tests for the Pydantic API request/response schemas."""
import pytest
from pydantic import ValidationError

from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Feature,
    LLMResult,
    MLResult,
    SampleEmail,
    SiemLogEntry,
)

# ── AnalyzeRequest ────────────────────────────────────────────────────────────


def test_analyze_request_requires_subject_and_body() -> None:
    req = AnalyzeRequest(subject="Hello", body="World")
    assert req.subject == "Hello"
    assert req.body == "World"
    assert req.headers is None


def test_analyze_request_accepts_optional_headers() -> None:
    req = AnalyzeRequest(subject="Hello", body="World", headers="From: a@b.com")
    assert req.headers == "From: a@b.com"


def test_analyze_request_missing_body_raises() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(subject="Hello")  # type: ignore[call-arg]


# ── Feature ───────────────────────────────────────────────────────────────────


def test_feature_has_token_and_weight() -> None:
    f = Feature(token="verify", weight=2.31)
    assert f.token == "verify"
    assert f.weight == 2.31


# ── MLResult ──────────────────────────────────────────────────────────────────


def test_ml_result_valid_risk_levels() -> None:
    for level in ("high", "medium", "low"):
        result = MLResult(score=0.5, risk_level=level, top_features=[])
        assert result.risk_level == level


def test_ml_result_score_out_of_range_raises() -> None:
    with pytest.raises(ValidationError):
        MLResult(score=1.5, risk_level="high", top_features=[])


def test_ml_result_invalid_risk_level_raises() -> None:
    with pytest.raises(ValidationError):
        MLResult(score=0.5, risk_level="critical", top_features=[])


def test_ml_result_with_features() -> None:
    result = MLResult(
        score=0.92,
        risk_level="high",
        top_features=[Feature(token="verify", weight=2.31)],
    )
    assert len(result.top_features) == 1
    assert result.top_features[0].token == "verify"


# ── LLMResult ─────────────────────────────────────────────────────────────────


def test_llm_result_valid() -> None:
    result = LLMResult(
        risk_level="high",
        reasoning="This email requests credentials via an external link.",
        iocs=["credential harvesting", "urgency language"],
    )
    assert result.risk_level == "high"
    assert len(result.iocs) == 2


def test_llm_result_empty_iocs_allowed() -> None:
    result = LLMResult(risk_level="low", reasoning="Appears legitimate.", iocs=[])
    assert result.iocs == []


def test_llm_result_invalid_risk_level_raises() -> None:
    with pytest.raises(ValidationError):
        LLMResult(risk_level="critical", reasoning="Bad.", iocs=[])


# ── AnalyzeResponse ───────────────────────────────────────────────────────────


def _siem_log() -> SiemLogEntry:
    return SiemLogEntry(
        timestamp="2026-04-21T00:00:00Z",
        event_type="email_threat_assessment",
        verdict="PHISHING",
        severity="HIGH",
        confidence=0.9,
        mitre_technique="T1566.001",
        iocs=[],
        header_flags=[],
        analyst_notes="",
    )


def test_analyze_response_llm_can_be_none() -> None:
    ml = MLResult(score=0.5, risk_level="medium", top_features=[])
    response = AnalyzeResponse(ml=ml, llm=None, siem_log=_siem_log())
    assert response.llm is None


def test_analyze_response_with_llm_result() -> None:
    ml = MLResult(score=0.9, risk_level="high", top_features=[])
    llm = LLMResult(risk_level="high", reasoning="Suspicious.", iocs=["urgency"])
    response = AnalyzeResponse(ml=ml, llm=llm, siem_log=_siem_log())
    assert response.llm is not None
    assert response.llm.iocs == ["urgency"]


# ── SampleEmail ───────────────────────────────────────────────────────────────


def test_sample_email_fields() -> None:
    s = SampleEmail(id="test-1", label="phishing", subject="Verify now", body="Click here")
    assert s.id == "test-1"
    assert s.label == "phishing"
    assert s.subject == "Verify now"
    assert s.body == "Click here"
