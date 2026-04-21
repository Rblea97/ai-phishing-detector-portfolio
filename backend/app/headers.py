"""
Email header parsing and IOC flag detection.

Parses raw email header blocks to extract authentication results
(SPF, DKIM, DMARC) and detect common phishing indicators such as
Reply-To / Return-Path domain mismatches.

Public surface
--------------
- ``extract_domain()``    — parse an email address string to its domain
- ``parse_auth_result()`` — extract protocol result from Authentication-Results
- ``parse_headers()``     — main entry point; returns HeaderAnalysis or None
"""
from __future__ import annotations

import email.parser
import email.utils
import re

from app.schemas import HeaderAnalysis, HeaderFlag


def extract_domain(address: str) -> str | None:
    """
    Parse an RFC 2822 address string and return the lowercased domain.

    Handles both plain ``user@domain.com`` and display-name format
    ``Display Name <user@domain.com>``.  Returns None for empty or
    unparseable input.
    """
    if not address:
        return None
    _, addr = email.utils.parseaddr(address)
    if "@" not in addr:
        return None
    domain = addr.split("@", 1)[1].lower()
    return domain if domain else None


def parse_auth_result(value: str, protocol: str) -> str | None:
    """
    Extract the authentication result for a specific protocol from an
    Authentication-Results header value string.

    Parameters
    ----------
    value:
        The full text of the Authentication-Results header value,
        e.g. ``"mx.example.com; spf=fail smtp.mailfrom=evil.com; dkim=pass"``.
    protocol:
        One of ``"spf"``, ``"dkim"``, or ``"dmarc"``.

    Returns
    -------
    str | None
        The result word (e.g. ``"pass"``, ``"fail"``, ``"softfail"``),
        or None if the protocol is absent from the value or the value is empty.
    """
    if not value:
        return None
    # Negative lookbehind prevents matching 'adkim' when searching for 'dkim'
    pattern = re.compile(rf"(?<![a-z]){re.escape(protocol)}=(\w+)", re.IGNORECASE)
    match = pattern.search(value)
    if match:
        return match.group(1).lower()
    return None


def parse_headers(raw: str | None) -> HeaderAnalysis | None:
    """
    Parse a raw email header block and return structured IOC analysis.

    Parameters
    ----------
    raw:
        The full raw header block as a string (everything before the blank
        line that separates headers from body).  May be None or empty.

    Returns
    -------
    HeaderAnalysis | None
        Structured result, or None if ``raw`` is None or empty.
    """
    if not raw or not raw.strip():
        return None

    parser = email.parser.HeaderParser()
    msg = parser.parsestr(raw)

    from_domain = extract_domain(msg.get("From", ""))
    reply_to_domain = extract_domain(msg.get("Reply-To", ""))
    return_path_domain = extract_domain(msg.get("Return-Path", ""))

    auth_results_value = msg.get("Authentication-Results", "")
    spf = parse_auth_result(auth_results_value, "spf")
    dkim = parse_auth_result(auth_results_value, "dkim")
    dmarc = parse_auth_result(auth_results_value, "dmarc")

    flags: list[HeaderFlag] = []

    # Reply-To mismatch: Reply-To domain differs from From domain
    if reply_to_domain and from_domain and reply_to_domain != from_domain:
        flags.append(
            HeaderFlag(
                name="reply_to_mismatch",
                description=(
                    f"Reply-To domain ({reply_to_domain}) differs from "
                    f"From domain ({from_domain}) — common in phishing"
                ),
                severity="high",
            )
        )

    # Return-Path mismatch: Return-Path domain differs from From domain
    if return_path_domain and from_domain and return_path_domain != from_domain:
        flags.append(
            HeaderFlag(
                name="return_path_mismatch",
                description=(
                    f"Return-Path domain ({return_path_domain}) differs from "
                    f"From domain ({from_domain}) — bounce path may be harvesting"
                ),
                severity="medium",
            )
        )

    # SPF fail or softfail
    if spf in ("fail", "softfail"):
        flags.append(
            HeaderFlag(
                name="spf_fail",
                description=(
                    f"SPF check result: {spf} — sending server is not "
                    "authorised to send on behalf of the From domain"
                ),
                severity="high",
            )
        )

    # DKIM fail
    if dkim == "fail":
        flags.append(
            HeaderFlag(
                name="dkim_fail",
                description=(
                    "DKIM signature verification failed — message may have "
                    "been tampered with in transit"
                ),
                severity="high",
            )
        )

    # DMARC fail
    if dmarc == "fail":
        flags.append(
            HeaderFlag(
                name="dmarc_fail",
                description=(
                    "DMARC policy check failed — message does not align with "
                    "the domain owner's published authentication policy"
                ),
                severity="high",
            )
        )

    return HeaderAnalysis(
        from_domain=from_domain,
        reply_to_domain=reply_to_domain,
        return_path_domain=return_path_domain,
        spf=spf,
        dkim=dkim,
        dmarc=dmarc,
        flags=flags,
    )
