"""
FastAPI application entry point.

Routes
------
GET  /api/samples   — return pre-loaded demo emails for the UI picker
POST /api/analyze   — run ML + LLM analysis on a submitted email
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.llm import analyze as llm_analyze
from app.ml import analyze as ml_analyze
from app.samples import SAMPLES
from app.schemas import AnalyzeRequest, AnalyzeResponse


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    # Warm up: load the sklearn pipeline from disk before the first request.
    from app.ml import load_pipeline

    await asyncio.to_thread(load_pipeline)
    yield


app = FastAPI(
    title="AI Phishing Detector",
    description="Defensive ML + LLM phishing email analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/samples")
async def get_samples() -> list[dict[str, str]]:
    """Return pre-loaded demo email samples."""
    return [s.model_dump() for s in SAMPLES]


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze an email for phishing indicators.

    Runs the ML baseline and LLM layer concurrently.  The LLM result may be
    null if ``ANTHROPIC_API_KEY`` is not configured or the API call fails.
    """
    # ML inference is ~1 ms — run it first so the LLM prompt gets the real score.
    ml_result = await asyncio.to_thread(ml_analyze, subject=request.subject, body=request.body)

    llm_result = await asyncio.to_thread(
        llm_analyze,
        subject=request.subject,
        body=request.body,
        ml_score=ml_result.score,
    )
    return AnalyzeResponse(ml=ml_result, llm=llm_result)
