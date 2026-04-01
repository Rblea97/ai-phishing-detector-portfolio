# AI Phishing Detector — Product & Engineering Spec

**Version:** 1.0
**Date:** 2026-03-31
**Author:** Richard Blea
**Status:** Draft — awaiting review

---

## Portfolio Value Proposition

This project demonstrates defensive security engineering at the intersection of classical ML, modern LLM APIs, and production-grade full-stack development. It is designed to signal readiness for SOC analyst, AppSec, security engineer, GRC, and DevSecOps roles.

A hiring manager reviewing this project sees:
- **Security-first thinking** — threat modeling, false-positive awareness, defensive-only constraints
- **ML explainability** — not just a score, but *why* the model flagged something (feature weights, confidence, reasoning)
- **Full-stack range** — typed Python backend, TypeScript React frontend, REST API design, OpenAPI docs
- **Production habits** — linting, type checking, tests, environment-based config, CI-friendly structure
- **Responsible AI use** — transparent data provenance, no offensive tooling, graceful degradation

---

## Overview

A web application that accepts an email (subject + body) and runs it through two analysis layers in parallel:

1. **ML baseline** — TF-IDF vectorizer + Logistic Regression trained on a labeled dataset of phishing and legitimate emails. Returns a probability score and the top weighted tokens that drove the prediction.
2. **LLM layer** — The email text and ML score are sent to Claude (`claude-sonnet-4-6`) with a defensive-analysis system prompt. Returns a structured risk assessment, reasoning, and indicators of compromise (IOCs).

Results are displayed side-by-side so viewers can see how classical ML and LLM reasoning compare — and where they disagree.

---

## V1 Scope

V1 is a shippable, demo-able application covering the full detection pipeline from email input to dual-layer analysis output, with a live deploy and a local-run path.

### In Scope

- Email input form (subject + body) with a dropdown of pre-loaded demo samples
- ML analysis: score, risk level, top contributing tokens
- LLM analysis: risk level, reasoning, IOC list (graceful degrade if API key absent)
- Side-by-side results UI with loading state
- Six hand-crafted demo email samples including an intentionally ambiguous case
- Training pipeline (one-time script) + committed model artifact
- Model evaluation notebook (precision, recall, F1, AUC-ROC, confusion matrix)
- Live deploy: backend on Render, frontend on Vercel
- README with local setup, deploy-your-own instructions, and demo video link

### Out of Scope

See the [Out of Scope](#out-of-scope) section below.

---

## User Stories

**US-1 — Security reviewer**
As a SOC analyst reviewing this portfolio, I want to paste a suspicious email and see an instant risk assessment with reasoning, so I can evaluate whether this tool reflects real-world detection thinking.

**US-2 — Recruiter with no setup**
As a recruiter without a development environment, I want to open a live URL and try the demo with pre-loaded examples, so I can evaluate the project without any technical setup.

**US-3 — Technical interviewer**
As a hiring manager evaluating ML skills, I want to see which specific tokens drove the phishing prediction and how the model's confidence compares to the LLM's reasoning, so I can assess the candidate's understanding of explainability.

**US-4 — Developer reproducing the project**
As a developer cloning the repo, I want to run the backend and frontend locally with a single command per service, so I can verify the project works and explore the code.

**US-5 — Developer without an API key**
As a developer who hasn't configured an Anthropic API key, I want the app to still function with ML-only output and a clear "LLM unavailable" message, so the core experience isn't broken.

---

## Functional Requirements

### FR-1: Email Analysis Endpoint

- `POST /api/analyze` accepts `{ subject: string, body: string, headers?: string }`.
- The `headers` field is accepted but not processed in v1 (reserved for future use).
- ML and LLM layers execute in parallel; total response time is bounded by the slower layer.
- Response schema:
  ```json
  {
    "ml": {
      "score": 0.94,
      "risk_level": "high",
      "top_features": [{ "token": "verify", "weight": 2.31 }, ...]
    },
    "llm": {
      "risk_level": "high",
      "reasoning": "This email exhibits...",
      "iocs": ["urgency language", "credential harvesting link"]
    }
  }
  ```
- If `ANTHROPIC_API_KEY` is absent or the API call fails, `llm` is `null` — no 500 error.

### FR-2: Demo Samples Endpoint

- `GET /api/samples` returns the six hand-crafted demo emails.
- Each sample includes: `id`, `label` (phishing/legitimate/ambiguous), `subject`, `body`.

### FR-3: ML Layer

- Model: TF-IDF vectorizer + Logistic Regression trained on `data/emails.csv`.
- Training is a one-time offline step (`scripts/train_model.py`); the serialized artifact is committed to the repo.
- `risk_level` mapping: score ≥ 0.7 → `high`; 0.4–0.69 → `medium`; < 0.4 → `low`.
- Top features: up to 10 highest absolute-weight tokens for the predicted class.

### FR-4: LLM Layer

- System prompt is defined as a module-level constant in `backend/app/models/llm.py`.
- Prompt instructs Claude to return structured JSON only and constrains analysis to defensive use.
- Claude receives: email subject, body, and the ML score.
- Response is parsed into `risk_level`, `reasoning` (2–3 sentences), and `iocs` (string list).

### FR-5: Frontend

- Email form with subject field, body textarea, and "Try an example" sample picker.
- Analyze button triggers `POST /api/analyze`; loading skeleton renders while in-flight.
- Results panel: ML result on left, LLM result on right (stacked on mobile).
- ML panel: color-coded risk meter (green/yellow/red), ranked token list.
- LLM panel: risk level badge, reasoning paragraph, IOC bullet list.
- LLM panel shows "LLM analysis unavailable — set ANTHROPIC_API_KEY to enable" when `llm` is null.

### FR-6: OpenAPI Documentation

- FastAPI auto-generates `/docs` (Swagger UI) from Pydantic schemas.
- All request and response fields are typed and documented.

---

## Non-Functional Requirements

### NFR-1: Performance
- `POST /api/analyze` returns the ML result within 500ms (LLM layer excluded from this SLA — network latency is external).
- Frontend renders the loading skeleton within 100ms of form submission.

### NFR-2: Reliability
- The application must not return HTTP 500 due to an absent or failed LLM layer.
- The model artifact loads at startup; if it fails to load, the backend fails fast with a clear error rather than silently degrading.

### NFR-3: Code Quality
- `ruff check .` passes with zero warnings (backend).
- `mypy .` passes with zero errors (backend).
- `npm run typecheck` passes with zero errors (frontend).
- `npm run lint` passes with zero warnings (frontend).

### NFR-4: Reproducibility
- A developer with Python 3.12 + `uv` installed can run the backend with two commands: `uv sync` and `uvicorn app.main:app --reload`.
- A developer with Node.js installed can run the frontend with two commands: `npm install` and `npm run dev`.
- Running `python scripts/train_model.py` reproduces the committed model artifact.

### NFR-5: Deployability
- Backend deploys to Render via `render.yaml` committed to the repo.
- Frontend deploys to Vercel via standard Vite build (`npm run build`).
- No build step requires the `ANTHROPIC_API_KEY` — it is runtime-only.

---

## Threat Model / Safety Notes

**Defensive use only.** This application is designed exclusively for defensive security education and portfolio demonstration. The following constraints are enforced by design:

| Threat | Mitigation |
|---|---|
| Generating phishing content | Not possible — the system prompt instructs Claude to perform analysis only. No generation endpoint exists. |
| Real credential harvesting | Demo samples are synthetic and clearly labeled. No real email accounts, inboxes, or credentials are involved. |
| PII in training data | Only publicly licensed research datasets are used (SpamAssassin, CEAS 2008). `data/README.md` documents provenance and licensing. All synthetic rows are labeled `source: synthetic`. |
| Prompt injection via email body | The Claude system prompt frames the email as an artifact under analysis, not as instructions. The prompt constrains output to structured JSON. |
| API key exposure | `ANTHROPIC_API_KEY` is server-side only, set as an environment variable. It is never returned to the frontend or logged. |
| Misuse as an offensive tool | The application has no endpoints for generating phishing emails, no bulk-analysis API, and no authentication bypass path. |

---

## Acceptance Criteria

- [ ] `POST /api/analyze` returns an ML result in < 500ms (measured locally, LLM excluded)
- [ ] `POST /api/analyze` with no `ANTHROPIC_API_KEY` set returns `{ ml: {...}, llm: null }` with HTTP 200
- [ ] All 6 demo samples return from `GET /api/samples` and analyze without error
- [ ] Frontend renders ML panel, LLM panel, loading state, and LLM-unavailable state correctly
- [ ] `ruff check .` passes clean
- [ ] `mypy .` passes clean
- [ ] `npm run typecheck` passes clean
- [ ] `pytest` passes with the committed model artifact loaded (no mocking)
- [ ] Live backend URL is publicly accessible on Render
- [ ] Live frontend URL is publicly accessible on Vercel
- [ ] `notebooks/model_evaluation.ipynb` runs top-to-bottom without error and reports precision, recall, F1, AUC-ROC
- [ ] README includes: local setup steps, deploy-your-own instructions, demo video/GIF link

---

## Out of Scope

The following are explicitly excluded from v1. They may be considered for future iterations.

- **Email inbox integration** — no IMAP, OAuth, or live email fetching
- **User accounts / history** — no authentication, no persistence layer, no analysis history
- **Bulk / batch analysis** — no multi-email upload or API key for automated use
- **Adversarial robustness** — no red-teaming, evasion testing, or adversarial example generation
- **Model fine-tuning** — Claude is used off-the-shelf with a system prompt; no fine-tuning
- **Custom model architectures** — BERT, transformers, or neural nets are out of scope; LogReg is intentional for explainability
- **Phishing generation or offensive tooling** — strictly out of scope by design, not just by priority
- **Mobile app** — responsive web only
- **Internationalization** — English-language emails only

---

## Data Sources

| Dataset | Type | License | Use |
|---|---|---|---|
| SpamAssassin Public Corpus | Spam/ham emails | Apache 2.0 / public | Training |
| CEAS 2008 Phishing Dataset | Phishing emails | Academic/public research | Training |
| Hand-crafted synthetic samples | Labeled synthetic | N/A (original) | Demo UI + training gap-fill |

All data provenance documented in `data/README.md`.
