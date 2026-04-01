# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Portfolio showcase app for detecting phishing emails using defensive ML/AI. Intended for recruiter demos — prioritize code clarity, explainability, and local reproducibility over complexity.

**Constraints:**
- Defensive and security-education use only
- No phishing generation, no offensive tooling
- Synthetic demo data must be clearly labeled as such; no real credential harvesting simulations
- Every ML decision should be explainable (show feature importance, confidence scores, reasoning)

## Recommended Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Standard in ML/security roles; async, typed, self-documenting via OpenAPI |
| ML baseline | scikit-learn (TF-IDF + Logistic Regression) | Explainable, no GPU, runs offline |
| LLM analysis | Claude API (`claude-sonnet-4-6`) | Richer reasoning layer over the ML baseline |
| Frontend | React + TypeScript (Vite) | Employable stack; shows full-stack range |
| Testing | pytest (backend), Vitest (frontend) | |
| Linting | Ruff + mypy (backend), ESLint (frontend) | |
| Package mgmt | `uv` (backend), `npm` (frontend) | |

## Repository Layout (target)

```
backend/        FastAPI app, ML model, Claude API integration
frontend/       React/TypeScript UI
data/           Labeled synthetic demo dataset (clearly marked)
notebooks/      EDA and model training (optional, for explainability demos)
```

## Commands

All commands assume you are in the repo root unless noted.

### Backend

```bash
cd backend
uv sync                        # install dependencies
uvicorn app.main:app --reload  # dev server (http://localhost:8000)
pytest                         # run tests
pytest tests/test_foo.py::test_bar  # run single test
ruff check .                   # lint
ruff format .                  # format
mypy .                         # typecheck
```

### Frontend

```bash
cd frontend
npm install                    # install dependencies
npm run dev                    # dev server (http://localhost:5173)
npm test                       # run tests (Vitest)
npm run lint                   # ESLint
npm run typecheck              # tsc --noEmit
npm run build                  # production build
```

## Architecture Notes

The app has two analysis layers that run in parallel on each submitted email:

1. **ML baseline** — TF-IDF vectorizer + Logistic Regression trained on the synthetic dataset. Returns a probability score and the top N weighted features (tokens) that drove the prediction. This is the explainability anchor.

2. **LLM layer** — The email text and ML score are sent to Claude with a structured system prompt that constrains it to defensive analysis only. Claude returns a risk assessment, reasoning, and indicators of compromise (IOCs) in structured JSON.

The frontend displays both outputs side by side so a demo viewer can see how classical ML and LLM reasoning compare.

**Claude API usage:** The backend calls the API server-side. The `ANTHROPIC_API_KEY` env var must be set. The LLM layer is optional — the app degrades gracefully to ML-only if the key is absent.
