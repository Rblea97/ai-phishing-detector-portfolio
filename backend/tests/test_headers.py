"""
Tests for backend/app/headers.py — email header IOC parsing.

TDD: these tests are written FIRST before the implementation exists.
All tests should FAIL (RED) until headers.py is implemented.
"""
import pytest

# ── Test fixtures ─────────────────────────────────────────────────────────────

CLEAN_HEADERS = """From: sender@goodcompany.com
Reply-To: sender@goodcompany.com
Return-Path: <sender@goodcompany.com>
Authentication-Results: mx.example.com; spf=pass smtp.mailfrom=goodcompany.com; dkim=pass header.d=goodcompany.com; dmarc=pass"""

REPLY_TO_MISMATCH_HEADERS = """From: PayPal Support <support@paypal.com>
Reply-To: harvest@attacker.example.com
Return-Path: <support@paypal.com>
Authentication-Results: mx.example.com; spf=pass smtp.mailfrom=paypal.com; dkim=pass; dmarc=pass"""

SAME_REPLY_TO_HEADERS = """From: Alice <alice@corp.example.com>
Reply-To: alice@corp.example.com
Return-Path: <alice@corp.example.com>
Authentication-Results: mx.example.com; spf=pass; dkim=pass; dmarc=pass"""

RETURN_PATH_MISMATCH_HEADERS = """From: billing@trustedbank.com
Reply-To: billing@trustedbank.com
Return-Path: <bounces@differentdomain.net>
Authentication-Results: mx.example.com; spf=pass; dkim=pass; dmarc=pass"""

SPF_FAIL_HEADERS = """From: admin@legitimate-looking.com
Reply-To: admin@legitimate-looking.com
Return-Path: <admin@legitimate-looking.com>
Authentication-Results: mx.example.com; spf=fail smtp.mailfrom=evil.com; dkim=pass; dmarc=pass"""

SPF_SOFTFAIL_HEADERS = """From: news@newsletter.com
Reply-To: news@newsletter.com
Return-Path: <news@newsletter.com>
Authentication-Results: mx.example.com; spf=softfail smtp.mailfrom=newsletter.com; dkim=pass; dmarc=pass"""

SPF_PASS_HEADERS = """From: contact@verified.org
Reply-To: contact@verified.org
Return-Path: <contact@verified.org>
Authentication-Results: mx.example.com; spf=pass smtp.mailfrom=verified.org; dkim=pass; dmarc=pass"""

DKIM_FAIL_HEADERS = """From: newsletter@news.example.com
Reply-To: newsletter@news.example.com
Return-Path: <newsletter@news.example.com>
Authentication-Results: mx.example.com; spf=pass; dkim=fail header.d=news.example.com; dmarc=fail"""

DMARC_FAIL_HEADERS = """From: ceo@bigcorp.com
Reply-To: ceo@bigcorp.com
Return-Path: <ceo@bigcorp.com>
Authentication-Results: mx.example.com; spf=pass; dkim=pass; dmarc=fail"""


# ── extract_domain ─────────────────────────────────────────────────────────────


def test_extract_domain_plain_address() -> None:
    from app.headers import extract_domain

    assert extract_domain("user@example.com") == "example.com"


def test_extract_domain_display_name_format() -> None:
    from app.headers import extract_domain

    assert extract_domain("Display Name <user@example.com>") == "example.com"


def test_extract_domain_empty_string() -> None:
    from app.headers import extract_domain

    assert extract_domain("") is None


def test_extract_domain_returns_lowercase() -> None:
    from app.headers import extract_domain

    assert extract_domain("User@EXAMPLE.COM") == "example.com"


def test_extract_domain_no_at_sign() -> None:
    from app.headers import extract_domain

    assert extract_domain("not-an-email") is None


# ── parse_auth_result ──────────────────────────────────────────────────────────


def test_parse_auth_result_spf_pass() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("spf=pass smtp.mailfrom=good.com", "spf") == "pass"


def test_parse_auth_result_spf_fail() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("spf=fail smtp.mailfrom=evil.com", "spf") == "fail"


def test_parse_auth_result_spf_softfail() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("spf=softfail", "spf") == "softfail"


def test_parse_auth_result_dkim_fail() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("dkim=fail header.d=evil.com", "dkim") == "fail"


def test_parse_auth_result_dmarc_fail() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("dmarc=fail", "dmarc") == "fail"


def test_parse_auth_result_empty_string() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("", "spf") is None


def test_parse_auth_result_no_match_returns_none() -> None:
    from app.headers import parse_auth_result

    assert parse_auth_result("spf=pass dkim=pass", "dmarc") is None


def test_parse_auth_result_does_not_raise_on_malformed() -> None:
    from app.headers import parse_auth_result

    # Should not raise; returns None for garbage input
    result = parse_auth_result("!!!@@@###", "spf")
    assert result is None


def test_parse_auth_result_does_not_match_adkim_for_dkim() -> None:
    """adkim= in DMARC policy should NOT match when searching for dkim=."""
    from app.headers import parse_auth_result

    # "adkim=r" is a DMARC policy alignment mode, not an auth result
    # We want dkim=<result>, not adkim=<policy>
    result = parse_auth_result("adkim=r aspf=r", "dkim")
    assert result is None


# ── parse_headers edge cases ───────────────────────────────────────────────────


def test_parse_headers_none_returns_none() -> None:
    from app.headers import parse_headers

    assert parse_headers(None) is None


def test_parse_headers_empty_string_returns_none() -> None:
    from app.headers import parse_headers

    assert parse_headers("") is None


def test_parse_headers_does_not_raise() -> None:
    from app.headers import parse_headers

    # Should never raise regardless of input
    result = parse_headers("garbage input !!!@@@")
    # May return None or a result with None fields — just must not raise
    assert result is None or result is not None


# ── parse_headers clean email ──────────────────────────────────────────────────


def test_parse_headers_clean_no_flags() -> None:
    from app.headers import parse_headers

    result = parse_headers(CLEAN_HEADERS)
    assert result is not None
    assert result.flags == []


def test_parse_headers_clean_spf_pass() -> None:
    from app.headers import parse_headers

    result = parse_headers(CLEAN_HEADERS)
    assert result is not None
    assert result.spf == "pass"


def test_parse_headers_clean_dkim_pass() -> None:
    from app.headers import parse_headers

    result = parse_headers(CLEAN_HEADERS)
    assert result is not None
    assert result.dkim == "pass"


def test_parse_headers_clean_dmarc_pass() -> None:
    from app.headers import parse_headers

    result = parse_headers(CLEAN_HEADERS)
    assert result is not None
    assert result.dmarc == "pass"


def test_parse_headers_clean_from_domain() -> None:
    from app.headers import parse_headers

    result = parse_headers(CLEAN_HEADERS)
    assert result is not None
    assert result.from_domain == "goodcompany.com"


# ── parse_headers flag detection ──────────────────────────────────────────────


def test_parse_headers_reply_to_mismatch_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(REPLY_TO_MISMATCH_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "reply_to_mismatch" in flag_names


def test_parse_headers_same_reply_to_no_mismatch_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(SAME_REPLY_TO_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "reply_to_mismatch" not in flag_names


def test_parse_headers_return_path_mismatch_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(RETURN_PATH_MISMATCH_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "return_path_mismatch" in flag_names


def test_parse_headers_spf_fail_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(SPF_FAIL_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "spf_fail" in flag_names


def test_parse_headers_spf_fail_severity_high() -> None:
    from app.headers import parse_headers

    result = parse_headers(SPF_FAIL_HEADERS)
    assert result is not None
    spf_flags = [f for f in result.flags if f.name == "spf_fail"]
    assert len(spf_flags) == 1
    assert spf_flags[0].severity == "high"


def test_parse_headers_spf_softfail_flag() -> None:
    """SPF softfail should also raise the spf_fail flag."""
    from app.headers import parse_headers

    result = parse_headers(SPF_SOFTFAIL_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "spf_fail" in flag_names


def test_parse_headers_spf_pass_no_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(SPF_PASS_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "spf_fail" not in flag_names


def test_parse_headers_dkim_fail_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(DKIM_FAIL_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "dkim_fail" in flag_names


def test_parse_headers_dmarc_fail_flag() -> None:
    from app.headers import parse_headers

    result = parse_headers(DMARC_FAIL_HEADERS)
    assert result is not None
    flag_names = [f.name for f in result.flags]
    assert "dmarc_fail" in flag_names
