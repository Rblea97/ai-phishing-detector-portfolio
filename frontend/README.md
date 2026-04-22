# AI Phishing Detector — Frontend

React 19 + TypeScript (Vite) frontend for the AI Phishing Detector portfolio project.

## Overview

Single-page application that submits email text to the backend API and renders results from three analysis layers side by side:

- **ML Baseline card** — phishing probability score, progress bar, top contributing TF-IDF tokens
- **Claude Analysis card** — LLM risk level, reasoning paragraph, extracted IOC list
- **Header Analysis card** — SPF/DKIM/DMARC badges, domain chain, header flags

## Tech Stack

| | |
|---|---|
| Framework | React 19 with hooks |
| Language | TypeScript 5.9 (strict mode) |
| Build tool | Vite 8 |
| Testing | Vitest + Testing Library |
| Linting | ESLint (TypeScript-aware rules) |

## Commands

```bash
npm install        # install dependencies
npm run dev        # dev server → http://localhost:5173
npm test           # run Vitest tests (16 tests)
npm run lint       # ESLint
npm run typecheck  # tsc --noEmit
npm run build      # production build → dist/
```

## Key Components

| Component | Purpose |
|---|---|
| `App.tsx` | Form, sample picker, state machine (idle → loading → done/error) |
| `MLResultCard.tsx` | Score bar + top feature token list |
| `LLMResultCard.tsx` | Risk badge + reasoning + IOC list; graceful degrade when LLM unavailable |
| `HeaderAnalysisCard.tsx` | SPF/DKIM/DMARC status badges + domain chain + header flags |
| `RiskBadge.tsx` | Reusable risk level indicator (high/medium/low) |
| `api/client.ts` | Typed fetch wrappers for `GET /api/samples` and `POST /api/analyze` |
| `types.ts` | TypeScript interfaces mirroring backend Pydantic schemas |

## Backend API

Expects the FastAPI backend running at `http://localhost:8000`. The `VITE_API_BASE_URL` environment variable overrides the default.

```typescript
// POST /api/analyze
interface AnalyzeRequest {
  subject: string
  body: string
  headers?: string   // optional raw email header block
}

interface AnalyzeResponse {
  ml: MLResult
  llm: LLMResult | null   // null when ANTHROPIC_API_KEY not set
  header_analysis: HeaderAnalysis | null
  siem_log: SiemLogEntry
}
```

See `src/types.ts` for the full type definitions.

## Deployment

Deployed to Render as a static site behind Nginx. The `nginx.conf` proxies `/api/*` requests to the backend service. See the root `render.yaml` for the full blueprint.

```bash
npm run build   # → dist/
# Nginx serves dist/ and proxies /api/ to the backend
```

---

Part of the [AI Phishing Detector](../README.md) portfolio project.
