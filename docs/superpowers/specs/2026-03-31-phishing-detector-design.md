# AI Phishing Detector — Design Spec

**Date:** 2026-03-31
**Status:** Approved

## Overview

A portfolio showcase application that detects phishing emails using a dual-layer analysis approach: a classical ML baseline (TF-IDF + Logistic Regression) paired with an LLM reasoning layer (Claude API). Designed for security-focused roles — SOC analyst, GRC, AppSec, security engineer, DevSecOps. Intended for recruiter demos via live deploy and recorded walkthrough video.

## Target Audience

Security-focused hiring managers and technical recruiters evaluating candidates for SOC, GRC, AppSec, security engineering, and DevSecOps roles. The app demonstrates:
- Defensive security thinking and ML explainability
- Full-stack engineering range (Python backend + TypeScript frontend)
- Responsible AI use (defensive only, transparent data provenance)

## Architecture

```
User (browser)
     │
     ▼
React/TypeScript Frontend (Vite)
     │  POST /api/analyze  { subject, body, headers? }
     ▼
FastAPI Backend
     ├── ML Layer (scikit-learn)
     │     TF-IDF vectorizer → Logistic Regression
     │     Returns: score (0–1), top N weighted tokens
     │
     └── LLM Layer (Claude API, optional)
           Receives: email text + ML score
           Returns: risk_level, reasoning, iocs[]
           Degrades gracefully if ANTHROPIC_API_KEY absent
```

The two layers run in parallel (asyncio + thread pool for the synchronous sklearn call). The frontend receives a single unified response object. If the LLM layer is unavailable, `llm` is `null` and the frontend shows a clear "LLM analysis unavailable" state.

A `GET /api/samples` endpoint returns hand-crafted demo emails so the UI can populate a "Try an example" dropdown without hardcoding content in the frontend.

## Backend

### Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, routes
│   ├── models/
│   │   ├── ml.py        # TF-IDF + LogReg, feature extraction
│   │   └── llm.py       # Claude API call, prompt, response parsing
│   ├── schemas.py       # Pydantic request/response models
│   └── samples.py       # Hand-crafted demo email definitions
├── data/
│   └── emails.csv       # Labeled training data (synthetic + public subset)
├── scripts/
│   └── train_model.py   # One-time training script, saves model artifact
├── model/               # Serialized model files (joblib)
├── tests/
└── pyproject.toml       # uv-managed, ruff + mypy configured
```

### Key Decisions

- **Model artifact committed to repo.** The model is trained once via `scripts/train_model.py` and the serialized artifact (joblib) is committed. No runtime training. Small enough (kilobytes). Recruiters can reproduce training by running the script.
- **Claude system prompt as a module-level constant** in `llm.py`. Easy to read, easy to show in a code review. Instructs Claude to return structured JSON only, constraining it to defensive analysis.
- **Pydantic schemas in `schemas.py`** define the full request/response contract. This drives auto-generated OpenAPI docs at `/docs` — a free demo artifact.
- **Top features** extracted by pulling the highest absolute-weight TF-IDF tokens for the predicted class, capped at 10.
- **LLM graceful degrade:** if `ANTHROPIC_API_KEY` is absent or the API call fails, the response still returns with `llm: null`. No hard failure.

### API Contract

```
POST /api/analyze
Request:  { subject: str, body: str, headers?: str }  # headers accepted but not processed in v1
Response: {
  ml: { score: float, risk_level: str, top_features: [{ token: str, weight: float }] },
  llm: { risk_level: str, reasoning: str, iocs: str[] } | null
}

GET /api/samples
Response: [{ id: str, label: str, subject: str, body: str }]
```

## Frontend

### Structure

```
frontend/
├── src/
│   ├── App.tsx                  # Root, layout shell
│   ├── components/
│   │   ├── EmailForm.tsx        # Subject + body inputs, sample picker dropdown
│   │   ├── ResultsPanel.tsx     # Container for both analysis panels
│   │   ├── MLResult.tsx         # Risk score, top features list
│   │   └── LLMResult.tsx        # Risk level badge, reasoning, IOC list
│   ├── api.ts                   # Fetch wrapper for /api/analyze + /api/samples
│   └── types.ts                 # TypeScript types mirroring backend schemas
├── index.html
└── vite.config.ts
```

### UX Flow

1. User lands on the page — sees email input form and "Try an example" dropdown pre-populated from `/api/samples`
2. User pastes or selects an email, hits **Analyze**
3. Loading skeleton shows while request is in-flight
4. Both result panels appear side-by-side (stacked on mobile): ML on the left, LLM on the right
5. **ML panel:** risk score as a color-coded meter (green/yellow/red), top tokens ranked by weight (up to 10)
6. **LLM panel:** risk level badge, 2–3 sentence reasoning, bulleted IOC list — or "LLM analysis unavailable" if no API key

**Styling:** Plain CSS or Tailwind — no component library. Keeps code readable. Dark-mode-friendly.

## Data Strategy

### Training Data

Target: ~1,000–2,000 labeled rows (`label`, `subject`, `body` columns in `data/emails.csv`).

Sources (in priority order):
1. **SpamAssassin public corpus** — well-known, widely cited, clearly licensed
2. **CEAS 2008 phishing dataset** — standard academic benchmark
3. **Hand-written synthetic rows** — edge cases, gap-filling

All synthetic rows include a `source: synthetic` column. `data/README.md` documents every source, license, and preprocessing step.

### Demo Samples

Six hand-crafted emails served via `/api/samples`:

| # | Type | Purpose |
|---|---|---|
| 1 | Obvious phishing | Urgency + credential link — clear positive |
| 2 | Subtle spear-phishing | Personalized, low-urgency — tests nuance |
| 3 | Legitimate HR email | False-positive risk |
| 4 | Legitimate IT security notice | Mentions passwords — tricky false-positive |
| 5 | Business email compromise | No link, pure social engineering |
| 6 | Borderline / ambiguous | ML and LLM may disagree — intentional demo moment |

Sample #6 is intentional — it demonstrates why the dual-layer approach is valuable and gives interviewers a natural talking point.

## Deployment

| Service | Platform | Notes |
|---|---|---|
| Backend | Render (free tier) | `ANTHROPIC_API_KEY` set as env var |
| Frontend | Vercel (free tier) | `VITE_API_URL` points to Render backend |

A `render.yaml` is committed to the repo. The README includes a "Deploy your own" section. Model artifact is committed so Render does not need to run training on deploy.

## Evaluation

Documented in `notebooks/model_evaluation.ipynb`:

- **Split:** 80/20 stratified train/test
- **Metrics:** Precision, recall, F1, AUC-ROC (not just accuracy)
- **Confusion matrix:** Explicitly discusses false negative vs. false positive trade-off in a security context
- This notebook is a portfolio artifact — shows understanding of evaluation beyond raw accuracy

## Testing

- **Backend (pytest):** 3–5 tests covering `/api/analyze` — valid input, missing fields, LLM-absent graceful degrade. Loads committed model artifact (no mocking), so tests catch serialization issues.
- **Frontend (Vitest):** Tests for `EmailForm` submission behavior and `MLResult` rendering.

## Non-Goals (v1)

- Real-time email inbox integration (IMAP/OAuth)
- User accounts or history persistence
- Adversarial robustness testing / model red-teaming
- Fine-tuned LLM (Claude is used off-the-shelf with a system prompt)
- Phishing email generation or offensive tooling of any kind

## Technical Risks

| Risk | Mitigation |
|---|---|
| Render free tier cold starts (30s+) | Note in README; video demo avoids live cold start |
| Small training set limits model quality | SpamAssassin corpus is large enough; document limitations in notebook |
| Claude API rate limits on free/trial keys | Graceful degrade means demo still works; note in README |
| Dataset licensing edge cases | Use only clearly licensed public datasets; document in `data/README.md` |

## Acceptance Criteria (v1)

- [ ] `POST /api/analyze` returns ML result in < 500ms (LLM excluded from SLA)
- [ ] LLM layer absent: response returns with `llm: null`, no 500 error
- [ ] All 6 demo samples load and analyze without error
- [ ] Frontend renders both panels, loading state, and LLM-unavailable state
- [ ] `npm run typecheck` and `ruff check` both pass clean
- [ ] pytest passes with model artifact loaded
- [ ] Live deploy accessible via public URL
- [ ] `notebooks/model_evaluation.ipynb` runs top-to-bottom without error
- [ ] README includes local setup, deploy-your-own, and demo video link
