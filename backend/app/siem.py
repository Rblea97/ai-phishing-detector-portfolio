"""
SIEM log synthesis.

Synthesises ML + LLM + header findings into a single SIEM-ingestible event
record suitable for Splunk, Elastic SIEM, or Azure Sentinel ingest.

Public surface
--------------
- ``build_siem_log()`` — build a SiemLogEntry from analysis layer outputs
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import HeaderAnalysis, LLMResult, MLResult, SiemLogEntry


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
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if ml.score >= 0.5:
        verdict = "PHISHING"
    elif ml.score < 0.4:
        verdict = "LEGITIMATE"
    else:
        verdict = "UNCERTAIN"

    severity = ml.risk_level.upper()
    mitre_technique = "T1566.001" if verdict == "PHISHING" else "T1566"

    # Deduplicate IOCs while preserving insertion order (Python 3.7+)
    iocs: list[str] = list(dict.fromkeys(llm.iocs)) if llm else []

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
