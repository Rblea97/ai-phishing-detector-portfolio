"""Integration tests for the FastAPI app (app/main.py)."""
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas import Feature, MLResult

# ── helpers ───────────────────────────────────────────────────────────────────

def _ml_result() -> MLResult:
    return MLResult(
        score=0.85,
        risk_level="high",
        top_features=[Feature(token="verify", weight=1.5)],
    )


# ── GET /api/samples ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_samples_returns_200() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/samples")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_samples_returns_list() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/samples")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_samples_have_required_fields() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/samples")
    sample = resp.json()[0]
    assert "id" in sample
    assert "label" in sample
    assert "subject" in sample
    assert "body" in sample


# ── POST /api/analyze ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_returns_200() -> None:
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello world."},
                )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analyze_response_has_ml_field() -> None:
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello world."},
                )
    body = resp.json()
    assert "ml" in body
    assert body["ml"]["score"] == 0.85
    assert body["ml"]["risk_level"] == "high"


@pytest.mark.asyncio
async def test_analyze_llm_none_when_no_key() -> None:
    """When LLM layer returns None, the response llm field should be null."""
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello world."},
                )
    assert resp.json()["llm"] is None


@pytest.mark.asyncio
async def test_analyze_includes_llm_result_when_present() -> None:
    from app.schemas import LLMResult

    llm = LLMResult(
        risk_level="high",
        reasoning="Suspicious credential request.",
        iocs=["urgency language"],
    )
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=llm):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Verify now", "body": "Click link."},
                )
    body = resp.json()
    assert body["llm"] is not None
    assert body["llm"]["risk_level"] == "high"
    assert body["llm"]["iocs"] == ["urgency language"]


@pytest.mark.asyncio
async def test_analyze_missing_body_returns_422() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/analyze", json={"subject": "No body here"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_accepts_optional_headers() -> None:
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello.", "headers": "From: a@b.com"},
                )
    assert resp.status_code == 200


# ── POST /api/analyze — header_analysis field ─────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_without_headers_has_null_header_analysis() -> None:
    """When headers field is absent, header_analysis in response must be null."""
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello world."},
                )
    body = resp.json()
    assert body["header_analysis"] is None


@pytest.mark.asyncio
async def test_analyze_with_clean_headers_has_empty_flags() -> None:
    """Clean headers (all auth pass, no domain mismatch) produce zero flags."""
    clean_headers = (
        "From: sender@goodcompany.com\r\n"
        "Reply-To: sender@goodcompany.com\r\n"
        "Return-Path: <sender@goodcompany.com>\r\n"
        "Authentication-Results: mx.example.com; spf=pass; dkim=pass; dmarc=pass"
    )
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello.", "headers": clean_headers},
                )
    body = resp.json()
    assert body["header_analysis"] is not None
    assert body["header_analysis"]["flags"] == []


# ── POST /api/analyze — siem_log field ───────────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_response_has_siem_log_key() -> None:
    """Every /api/analyze response must include a siem_log key."""
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Hello world."},
                )
    body = resp.json()
    assert "siem_log" in body
    assert body["siem_log"]["event_type"] == "email_threat_assessment"


@pytest.mark.asyncio
async def test_analyze_with_spf_fail_headers_has_spf_fail_flag() -> None:
    """SPF=fail in headers should produce an spf_fail flag in the response."""
    phishing_headers = (
        "From: admin@legitimate-looking.com\r\n"
        "Reply-To: admin@legitimate-looking.com\r\n"
        "Return-Path: <admin@legitimate-looking.com>\r\n"
        "Authentication-Results: mx.example.com; spf=fail smtp.mailfrom=evil.com;"
        " dkim=pass; dmarc=pass"
    )
    with patch("app.main.ml_analyze", return_value=_ml_result()):
        with patch("app.main.llm_analyze", return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(
                    "/api/analyze",
                    json={"subject": "Test", "body": "Click here.", "headers": phishing_headers},
                )
    body = resp.json()
    assert body["header_analysis"] is not None
    flag_names = [f["name"] for f in body["header_analysis"]["flags"]]
    assert "spf_fail" in flag_names
