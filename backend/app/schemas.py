"""Pydantic models for the /api/analyze and /api/samples endpoints."""
from pydantic import BaseModel, Field


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


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    subject: str
    body: str
    headers: str | None = Field(
        default=None,
        description="Raw email headers — accepted but not processed in v1",
    )


class AnalyzeResponse(BaseModel):
    """Unified response from POST /api/analyze."""

    ml: MLResult
    llm: LLMResult | None = Field(
        description="null when ANTHROPIC_API_KEY is absent or the API call fails"
    )


class SampleEmail(BaseModel):
    """A pre-loaded demo email served by GET /api/samples."""

    id: str
    label: str
    subject: str
    body: str
