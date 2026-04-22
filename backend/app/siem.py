"""
SIEM log synthesis.

Synthesises ML + LLM + header findings into a single SIEM-ingestible event
record suitable for Splunk, Elastic SIEM, or Azure Sentinel ingest.

Public surface
--------------
- ``build_siem_log()`` — build a SiemLogEntry from analysis layer outputs
"""
from __future__ import annotations

from datetime import UTC, datetime

from app.schemas import HeaderAnalysis, LLMResult, MLResult, SiemLogEntry


def _assign_mitre_technique(verdict: str, iocs: list[str]) -> str:
    """
    Map verdict + LLM-extracted IOCs to the most specific applicable ATT&CK technique.

    T1566.002 (Spearphishing Link) is assigned when a URL is detected in the IOC list,
    since the detector is text-based and the primary delivery vector in detected emails
    is credential-harvesting hyperlinks.  BEC-style phishing (wire-transfer fraud,
    impersonation without a payload URL) maps to the parent T1566.

    ATT&CK sub-technique reference: https://attack.mitre.org/techniques/T1566/
    """
    if verdict != "PHISHING":
        return "T1566"
    for ioc in iocs:
        if "http" in ioc.lower():
            return "T1566.002"  # Spearphishing Link — URL present in IOC
    return "T1566"  # Generic phishing (BEC, impersonation, no clear URL payload)


def build_siem_log(
    *,
    ml: MLResult,
    llm: LLMResult | None,
    header_analysis: HeaderAnalysis | None,
) -> SiemLogEntry:
    """
    Synthesise a SIEM-ingestible event record from all analysis layers.

    Parameters
    ----------
    ml:
        ML baseline result (always present).
    llm:
        LLM analysis result (None when API key absent or call failed).
    header_analysis:
        Parsed email header analysis (None when no headers submitted).

    Returns
    -------
    SiemLogEntry
        Always populated — never None.
    """
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    if ml.score >= 0.5:
        verdict = "PHISHING"
    elif ml.score < 0.4:
        verdict = "LEGITIMATE"
    else:
        verdict = "UNCERTAIN"

    severity = ml.risk_level.upper()
    iocs: list[str] = list(dict.fromkeys(llm.iocs)) if llm else []
    mitre_technique = _assign_mitre_technique(verdict, iocs)

    header_flags: list[str] = (
        [f.name for f in header_analysis.flags] if header_analysis else []
    )

    analyst_notes: str = llm.reasoning if llm else ""

    return SiemLogEntry(
        timestamp=timestamp,
        event_type="email_threat_assessment",
        verdict=verdict,
        severity=severity,
        confidence=ml.score,
        mitre_technique=mitre_technique,
        iocs=iocs,
        header_flags=header_flags,
        analyst_notes=analyst_notes,
    )
