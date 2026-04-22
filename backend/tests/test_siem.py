"""
Tests for SIEM log synthesis (app/siem.py).

Written FIRST — TDD Red phase. These tests MUST fail before siem.py exists.
"""
import pytest

from app.schemas import Feature, HeaderAnalysis, HeaderFlag, LLMResult, MLResult

# ── fixtures ──────────────────────────────────────────────────────────────────


def _ml(score: float, risk_level: str) -> MLResult:
    return MLResult(
        score=score,
        risk_level=risk_level,
        top_features=[Feature(token="verify", weight=1.0)],
    )


def _llm(iocs: list[str] | None = None) -> LLMResult:
    return LLMResult(
        risk_level="high",
        reasoning="Suspicious credential-harvesting pattern detected.",
        iocs=iocs or [],
    )


def _header_analysis(flag_names: list[str]) -> HeaderAnalysis:
    return HeaderAnalysis(
        from_domain="evil.example",
        reply_to_domain="other.example",
        return_path_domain="evil.example",
        spf="fail",
        dkim="pass",
        dmarc="fail",
        flags=[
            HeaderFlag(name=n, description="test flag", severity="high")
            for n in flag_names
        ],
    )


# ── verdict / severity ────────────────────────────────────────────────────────


def test_high_score_verdict_is_phishing() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.verdict == "PHISHING"


def test_high_score_severity_is_high() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.severity == "HIGH"


def test_low_score_verdict_is_legitimate() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.05, "low"), llm=None, header_analysis=None)
    assert log.verdict == "LEGITIMATE"


def test_low_score_severity_is_low() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.05, "low"), llm=None, header_analysis=None)
    assert log.severity == "LOW"


def test_mid_score_verdict_is_uncertain() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.45, "medium"), llm=None, header_analysis=None)
    assert log.verdict == "UNCERTAIN"


def test_mid_score_severity_is_medium() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.45, "medium"), llm=None, header_analysis=None)
    assert log.severity == "MEDIUM"


# ── MITRE technique ───────────────────────────────────────────────────────────
# T1566.002 = Spearphishing Link (URL in IOC list)
# T1566     = Generic Phishing  (BEC / no URL payload identified)
# https://attack.mitre.org/techniques/T1566/


def test_phishing_with_url_ioc_mitre_is_t1566_002() -> None:
    """URL in IOC list → Spearphishing Link (T1566.002), the most specific match."""
    from app.siem import build_siem_log

    llm = _llm(iocs=["http://bank-fake.example/reset", "urgency language"])
    log = build_siem_log(ml=_ml(0.97, "high"), llm=llm, header_analysis=None)
    assert log.mitre_technique == "T1566.002"


def test_phishing_without_url_ioc_mitre_is_t1566() -> None:
    """BEC-style phishing with no URL payload falls back to parent T1566."""
    from app.siem import build_siem_log

    llm = _llm(iocs=["wire transfer request", "executive impersonation"])
    log = build_siem_log(ml=_ml(0.97, "high"), llm=llm, header_analysis=None)
    assert log.mitre_technique == "T1566"


def test_phishing_with_no_llm_mitre_is_t1566() -> None:
    """No LLM output means no IOCs — fall back to generic T1566."""
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.mitre_technique == "T1566"


def test_non_phishing_verdict_mitre_is_t1566() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.05, "low"), llm=None, header_analysis=None)
    assert log.mitre_technique == "T1566"


def test_uncertain_verdict_mitre_is_t1566() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.45, "medium"), llm=None, header_analysis=None)
    assert log.mitre_technique == "T1566"


# ── IOCs ──────────────────────────────────────────────────────────────────────


def test_llm_iocs_present_in_siem_log() -> None:
    from app.siem import build_siem_log

    llm = _llm(iocs=["urgency language", "http://bank-fake.example/reset"])
    log = build_siem_log(ml=_ml(0.97, "high"), llm=llm, header_analysis=None)
    assert log.iocs == ["urgency language", "http://bank-fake.example/reset"]


def test_llm_none_iocs_is_empty_list() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.iocs == []


def test_llm_iocs_are_deduplicated() -> None:
    """Duplicate IOCs in llm output must be removed (order-preserving)."""
    from app.siem import build_siem_log

    llm = _llm(iocs=["urgency language", "urgency language", "fake link"])
    log = build_siem_log(ml=_ml(0.97, "high"), llm=llm, header_analysis=None)
    assert log.iocs == ["urgency language", "fake link"]


# ── header flags ──────────────────────────────────────────────────────────────


def test_header_flags_extracted_from_analysis() -> None:
    from app.siem import build_siem_log

    ha = _header_analysis(["spf_fail", "reply_to_mismatch"])
    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=ha)
    assert log.header_flags == ["spf_fail", "reply_to_mismatch"]


def test_header_analysis_none_gives_empty_flags() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.header_flags == []


# ── analyst notes ─────────────────────────────────────────────────────────────


def test_analyst_notes_equals_llm_reasoning() -> None:
    from app.siem import build_siem_log

    llm = _llm()
    log = build_siem_log(ml=_ml(0.97, "high"), llm=llm, header_analysis=None)
    assert log.analyst_notes == llm.reasoning


def test_analyst_notes_empty_when_llm_none() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.analyst_notes == ""


# ── metadata ──────────────────────────────────────────────────────────────────


def test_timestamp_is_nonempty_and_ends_with_z() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.timestamp
    assert log.timestamp.endswith("Z")


def test_confidence_equals_ml_score() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.73, "high"), llm=None, header_analysis=None)
    assert log.confidence == pytest.approx(0.73)


def test_event_type_is_email_threat_assessment() -> None:
    from app.siem import build_siem_log

    log = build_siem_log(ml=_ml(0.97, "high"), llm=None, header_analysis=None)
    assert log.event_type == "email_threat_assessment"
