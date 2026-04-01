# Execution Batches

Derived from `docs/superpowers/plans/2026-03-31-phishing-detector.md`.
Each batch is 30–90 minutes, ends in a verifiable state, and maps to one or more plan tasks.

---

## Batch 1 — Backend Foundation
**Plan tasks:** 1 (Repo Scaffold), 2 (pyproject.toml), 3 (Schemas), 4 (Demo Samples)
**Estimated time:** ~40 min

**Objective:**
Stand up the backend package structure, install dependencies, define the full Pydantic API contract, and write the six demo email samples. No network calls, no ML — just layout and typed interfaces.

**Files touched:**
- Create: `.gitignore`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`, `backend/app/models/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/model/.gitkeep`, `backend/notebooks/.gitkeep`
- Create: `backend/app/schemas.py`
- Create: `backend/tests/test_schemas.py`
- Create: `backend/app/samples.py`

**Tests to add:**
- `backend/tests/test_schemas.py` — 7 tests covering `AnalyzeRequest`, `AnalyzeResponse`, `MLResult`, `LLMResult`, `Feature`, `SampleEmail`

**Commands to verify:**
```bash
cd backend
uv run pytest tests/test_schemas.py -v
# Expected: 7 passed

uv run python -c "from app.samples import SAMPLES; print(len(SAMPLES), 'samples loaded')"
# Expected: 6 samples loaded

uv run ruff check .
# Expected: no output (clean)
```

**Commit message suggestion:**
```
feat: backend scaffold, Pydantic schemas, and demo email samples
```

---

## Batch 2 — Training Data Pipeline
**Plan tasks:** 5 (Download Data), 6 (Training Script + Artifact)
**Estimated time:** ~60 min

**Objective:**
Write the data download script, pull the SpamAssassin corpus (~3,000 emails), build `data/emails.csv`, train the TF-IDF + Logistic Regression pipeline, and commit the serialized model artifact. After this batch the ML model is locked and reproducible.

**Files touched:**
- Create: `backend/scripts/download_data.py`
- Create: `backend/data/README.md`
- Create: `backend/data/emails.csv` (generated, then committed)
- Create: `backend/scripts/train_model.py`
- Create: `backend/model/pipeline.joblib` (generated, then committed)

**Tests to add:**
None in this batch — artifact correctness is verified by the training script's printed classification report. The ML unit tests in Batch 3 will exercise the artifact.

**Commands to verify:**
```bash
cd backend
uv run python scripts/download_data.py
# Expected: prints row counts, writes data/emails.csv

uv run python scripts/train_model.py
# Expected: prints classification_report, F1 for phishing > 0.85, saves pipeline.joblib

ls -lh model/pipeline.joblib
# Expected: file exists, 500KB–5MB

python -c "import joblib; p = joblib.load('model/pipeline.joblib'); print(type(p))"
# Expected: <class 'sklearn.pipeline.Pipeline'>
```

**Commit message suggestion:**
```
feat: training data pipeline and committed model artifact
```

---

## Batch 3 — Backend Analysis Layers
**Plan tasks:** 7 (ML Layer), 8 (LLM Layer)
**Estimated time:** ~60 min

**Objective:**
Implement `PhishingClassifier` (loads joblib, runs predict, extracts top TF-IDF features) and the async LLM `analyze()` function (calls Claude API, returns structured JSON, gracefully returns `None` when key is absent). Both are TDD.

**Files touched:**
- Create: `backend/app/models/ml.py`
- Create: `backend/tests/test_ml.py`
- Create: `backend/app/models/llm.py`
- Create: `backend/tests/test_llm.py`

**Tests to add:**
- `backend/tests/test_ml.py` — 6 tests: classifier loads, score in range, risk_level returned, risk_level matches score, top_features structure, obvious phishing scores > 0.5
- `backend/tests/test_llm.py` — 2 tests: returns `None` without API key, returns `None` on invalid key (no raise)

**Commands to verify:**
```bash
cd backend
uv run pytest tests/test_ml.py tests/test_llm.py -v
# Expected: 8 passed

uv run mypy app/models/
# Expected: Success: no issues found

uv run ruff check app/models/
# Expected: clean
```

**Commit message suggestion:**
```
feat: ML classifier and LLM analysis layer with graceful degrade
```

---

## Batch 4 — FastAPI App + API Tests
**Plan tasks:** 9 (FastAPI App + Integration Tests)
**Estimated time:** ~45 min

**Objective:**
Wire both analysis layers into FastAPI routes: `POST /api/analyze` (parallel ML + LLM, unified response) and `GET /api/samples`. Write integration tests using httpx's `ASGITransport` that hit the real app with the real model artifact. End state: backend runs end-to-end, all tests green, linting clean.

**Files touched:**
- Create: `backend/app/main.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_api.py`

**Tests to add:**
- `backend/tests/test_api.py` — 6 tests: analyze returns 200 + ML result, missing body returns 422, llm is null without API key, response structure validated, samples returns 6 items, `/docs` returns 200

**Commands to verify:**
```bash
cd backend
uv run pytest -v
# Expected: all 21 tests pass (7 schema + 6 ml + 2 llm + 6 api)

uv run ruff check .
# Expected: clean

uv run mypy app/
# Expected: clean

# Smoke test the live server
uv run uvicorn app.main:app --port 8000 &
sleep 3
curl -s http://localhost:8000/api/samples | python -m json.tool | head -10
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test","body":"Normal email."}' | python -m json.tool
kill %1
```

**Commit message suggestion:**
```
feat: FastAPI app with /api/analyze and /api/samples, full test suite green
```

---

## Batch 5 — Frontend Scaffold + Types
**Plan tasks:** 10 (Frontend Scaffold), 11 (Types + api.ts)
**Estimated time:** ~30 min

**Objective:**
Bootstrap the Vite + React + TypeScript project, configure Vitest with jsdom and `@testing-library/react`, write the TypeScript types that mirror the backend schemas, and write the `api.ts` fetch wrapper. End state: `npm run typecheck` and `npm run build` both pass on an empty-component app.

**Files touched:**
- Create: `frontend/` (via `npm create vite`)
- Modify: `frontend/vite.config.ts` (add Vitest config)
- Create: `frontend/src/test-setup.ts`
- Modify: `frontend/tsconfig.app.json` (add `vitest/globals` type)
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`
- Create: `frontend/.env.example`

**Tests to add:**
None in this batch — component tests follow in Batch 6. `api.ts` is validated by typecheck only.

**Commands to verify:**
```bash
cd frontend
npm run typecheck
# Expected: no errors

npm run build
# Expected: dist/ created, no errors

npm run dev &
sleep 3
curl -s http://localhost:5173 | grep -c "root"
kill %1
# Expected: 1 (root div present)
```

**Commit message suggestion:**
```
feat: Vite frontend scaffold with TypeScript types and API fetch wrapper
```

---

## Batch 6 — Frontend Components
**Plan tasks:** 12 (EmailForm), 13 (MLResult), 14 (LLMResult)
**Estimated time:** ~75 min

**Objective:**
Build and test all three leaf components TDD-style. `EmailForm` handles sample selection and form submission. `MLResult` renders the score meter and token list. `LLMResult` renders the risk badge, reasoning, IOC list — and the graceful "unavailable" state. Each component is independently tested before moving to the next.

**Files touched:**
- Create: `frontend/src/components/EmailForm.tsx`
- Create: `frontend/src/components/EmailForm.test.tsx`
- Create: `frontend/src/components/MLResult.tsx`
- Create: `frontend/src/components/MLResult.test.tsx`
- Create: `frontend/src/components/LLMResult.tsx`
- Create: `frontend/src/components/LLMResult.test.tsx`

**Tests to add:**
- `EmailForm.test.tsx` — 5 tests: renders fields, calls onSubmit, disables during loading, disables when empty, populates from sample selection
- `MLResult.test.tsx` — 5 tests: renders risk badge, score as %, token list, low-risk badge, progress bar aria attributes
- `LLMResult.test.tsx` — 5 tests: unavailable message when null, risk badge, reasoning text, IOC list items, no IOC heading when list empty

**Commands to verify:**
```bash
cd frontend
npm test
# Expected: 15 tests pass across 3 files

npm run typecheck
# Expected: clean

npm run lint
# Expected: clean
```

**Commit message suggestion:**
```
feat: EmailForm, MLResult, and LLMResult components with full test coverage
```

---

## Batch 7 — App Wiring + Styling
**Plan tasks:** 15 (ResultsPanel + App.tsx + CSS)
**Estimated time:** ~45 min

**Objective:**
Compose the leaf components into `ResultsPanel`, wire everything into `App.tsx` with loading/error state, and write the dark-mode CSS. End state: the app is visually complete — paste an email, click Analyze, see both panels. Requires the backend from Batch 4 running locally to smoke-test the full stack.

**Files touched:**
- Create: `frontend/src/components/ResultsPanel.tsx`
- Modify: `frontend/src/App.tsx` (replace Vite default)
- Modify: `frontend/src/App.css` (replace Vite default with project CSS)
- Modify: `frontend/src/main.tsx` (remove Vite boilerplate styles)

**Tests to add:**
No new test files — covered by existing component tests. Visual correctness verified by running the app.

**Commands to verify:**
```bash
cd frontend
npm test
# Expected: all 15 tests still pass

npm run typecheck && npm run lint && npm run build
# Expected: all clean, dist/ created

# Full-stack smoke test (requires backend running on :8000)
# Start backend: cd backend && uv run uvicorn app.main:app --port 8000 &
# Start frontend: npm run dev
# Open http://localhost:5173, select a demo sample, click Analyze
# Verify: ML panel renders score + tokens, LLM panel renders (or shows unavailable)
```

**Commit message suggestion:**
```
feat: ResultsPanel, App wiring, and dark-mode CSS — app visually complete
```

---

## Batch 8 — Notebook, Deploy Config, Final Gate
**Plan tasks:** 16 (Evaluation Notebook), 17 (Deployment Config + README)
**Estimated time:** ~60 min

**Objective:**
Write and execute the model evaluation notebook (confusion matrix, ROC curve, top-feature printout), add `render.yaml` for one-click Render deployment, and write the final README. Finish with the full acceptance-criteria quality gate: all backend tests, all frontend tests, all linters, and a production build.

**Files touched:**
- Create: `backend/notebooks/model_evaluation.ipynb`
- Create: `render.yaml`
- Create: `README.md`

**Tests to add:**
None new — the notebook itself is the artifact. Correctness verified by executing it.

**Commands to verify:**
```bash
# Execute notebook
cd backend
uv run jupyter nbconvert --to notebook --execute \
  notebooks/model_evaluation.ipynb \
  --output notebooks/model_evaluation.ipynb
# Expected: no errors, output cells populated

# Full acceptance gate
uv run pytest -v
# Expected: 21 tests pass

uv run ruff check .
# Expected: clean

uv run mypy app/
# Expected: clean

cd ../frontend
npm test
# Expected: 15 tests pass

npm run typecheck && npm run lint && npm run build
# Expected: all clean
```

**Commit message suggestion:**
```
feat: evaluation notebook, render.yaml, and README — v1 complete
```

---

## Summary

| Batch | Tasks | Focus | Est. Time | Ends With |
|---|---|---|---|---|
| 1 | 1–4 | Backend scaffold + schemas | ~40 min | 7 pytest tests green |
| 2 | 5–6 | Data download + model training | ~60 min | `pipeline.joblib` committed |
| 3 | 7–8 | ML layer + LLM layer (TDD) | ~60 min | 8 pytest tests green |
| 4 | 9 | FastAPI app + API tests | ~45 min | 21 pytest tests green, server smoke-tested |
| 5 | 10–11 | Frontend scaffold + types | ~30 min | `npm run build` clean |
| 6 | 12–14 | Three components (TDD) | ~75 min | 15 Vitest tests green |
| 7 | 15 | App wiring + CSS | ~45 min | Full-stack smoke test passes |
| 8 | 16–17 | Notebook + deploy + README | ~60 min | All acceptance criteria met |

**Total: ~7 hours across 8 sessions**
