"""Pydantic models for the /api/analyze and /api/samples endpoints."""
from pydantic import BaseModel, Field


class HeaderFlag(BaseModel):
    """A single suspicious indicator found in email headers."""

    name: str
    description: str
    severity: str = Field(pattern="^(high|medium|low)$")


class HeaderAnalysis(BaseModel):
    """Structured output of email header inspection."""

    from_domain: str | None
    reply_to_domain: str | None
    return_path_domain: str | None
    spf: str | None = Field(default=None, description="pass | fail | softfail | neutral | none")
    dkim: str | None = Field(default=None, description="pass | fail | none")
    dmarc: str | None = Field(default=None, description="pass | fail | none")
    flags: list[HeaderFlag]


class Feature(BaseModel):
    """A single TF-IDF token and its contribution weight."""

    token: str
    weight: float


class MLResult(BaseModel):
    """Output of the ML baseline analysis layer."""

    score: float = Field(ge=0.0, le=1.0, description="Phishing probability 0–1")
    risk_level: str = Field(pattern="^(high|medium|low)$")
    top_features: list[Feature]


class LLMResult(BaseModel):
    """Output of the Claude LLM analysis layer."""

    risk_level: str = Field(pattern="^(high|medium|low)$")
    reasoning: str = Field(description="2–3 sentence risk assessment")
    iocs: list[str] = Field(description="Indicators of compromise observed")


class SiemLogEntry(BaseModel):
    """SIEM-ingestible event record synthesised from all analysis layers."""

    timestamp: str = Field(description="ISO-8601 UTC timestamp")
    event_type: str = Field(default="email_threat_assessment")
    verdict: str = Field(description="PHISHING | LEGITIMATE | UNCERTAIN")
    severity: str = Field(pattern="^(HIGH|MEDIUM|LOW)$")
    confidence: float = Field(ge=0.0, le=1.0)
    mitre_technique: str
    iocs: list[str]
    header_flags: list[str]
    analyst_notes: str


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    subject: str
    body: str
    headers: str | None = Field(
        default=None,
        description="Raw email headers as plain text — paste the full header block from your email client",
    )


class AnalyzeResponse(BaseModel):
    """Unified response from POST /api/analyze."""

    ml: MLResult
    llm: LLMResult | None = Field(
        description="null when ANTHROPIC_API_KEY is absent or the API call fails"
    )
    header_analysis: HeaderAnalysis | None = Field(
        default=None,
        description="null when no headers were submitted",
    )
    siem_log: SiemLogEntry = Field(description="SIEM-ingestible event record")


class SampleEmail(BaseModel):
    """A pre-loaded demo email served by GET /api/samples."""

    id: str
    label: str
    subject: str
    body: str
