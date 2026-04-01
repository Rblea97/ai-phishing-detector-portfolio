# AI Phishing Detector

A portfolio project demonstrating defensive security + ML engineering. Detects phishing emails using a dual-layer analysis pipeline:

1. **ML baseline** — TF-IDF + Logistic Regression with top-token explainability
2. **LLM layer** — Claude (`claude-sonnet-4-6`) for structured reasoning and IOC extraction

> **Status:** In development — see [`docs/execution-batches.md`](docs/execution-batches.md) for progress.

---

## Local Setup

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 18+

### Backend

```bash
cd backend
uv sync
uvicorn app.main:app --reload
# API at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

Set your Anthropic API key to enable the LLM layer (optional — app works without it):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

Or use the Makefile from the repo root:

```bash
make backend-install && make backend-serve
make frontend-install && make frontend-serve
```

---

## Development

```bash
make backend-lint       # ruff check
make backend-typecheck  # mypy
make backend-test       # pytest
make frontend-lint      # eslint
make frontend-typecheck # tsc --noEmit
make frontend-test      # vitest
make check              # run everything
```

---

## Docs

- [`docs/spec.md`](docs/spec.md) — product & engineering spec
- [`docs/execution-batches.md`](docs/execution-batches.md) — build plan broken into sessions
