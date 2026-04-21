# AI Phishing Detector

[![Backend CI](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/backend.yml/badge.svg)](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/backend.yml)
[![Frontend CI](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/frontend.yml/badge.svg)](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/frontend.yml)
[![CodeQL](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/codeql.yml/badge.svg)](https://github.com/Rblea97/ai-phishing-detector-portfolio/actions/workflows/codeql.yml)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)

> A blue team email triage tool that detects phishing attempts, extracts Indicators of Compromise (IOCs), and explains *why* — built for SOC analyst workflows. Combines a 98.82%-accurate ML classifier (MITRE ATT&CK T1566) with Claude-powered threat reasoning.

**[LIVE DEMO →](https://phishing-detector-ui-s3bf.onrender.com)** &nbsp;|&nbsp; **[Watch Demo Video →](https://youtu.be/wYcv8Ve5-Sw)**

> **Role relevance:** Designed around the SOC Tier 1 analyst workflow — alert received → email triaged → IOCs extracted → severity scored → escalation decision supported.

---

## Demo

| Phishing Email | Legitimate Email |
|---|---|
| ![Phishing result](docs/screenshots/phishing-result.png) | ![Legit result](docs/screenshots/legit-result.png) |

| Header Analysis (SPF/DKIM/DMARC + domain chain) |
|---|
| ![Header analysis](docs/screenshots/header-analysis.png) |

---

## Why This Exists

Phishing is the **#1 initial access vector** across all major threat reports (CISA, Verizon DBIR 2025), mapped to [MITRE ATT&CK T1566](https://attack.mitre.org/techniques/T1566/). Most production detectors are black boxes — a SOC analyst sees a verdict but not *why*. This project addresses that gap: every prediction shows the specific tokens that drove the score alongside LLM reasoning, so analysts can triage faster and trust the output.

---

## Blue Team Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Threat Detection | ML classifier flags phishing with 96.17% F1 on the attack class |
| IOC Extraction | LLM layer extracts malicious URLs, urgency language, impersonation patterns |
| Anomaly Detection | TF-IDF feature weights surface statistically unusual token patterns |
| Alert Triage Support | Confidence scores + top-N suspicious tokens enable rapid analyst decisions |
| False Positive Management | 99.80% legitimate-class recall → ~0.20% FPR, minimizing analyst alert fatigue |
| MITRE ATT&CK Mapping | Detections map to [T1566.001](https://attack.mitre.org/techniques/T1566.001/) (Spear Phishing Link) and [T1566.002](https://attack.mitre.org/techniques/T1566.002/) (Attachment) |
| Explainability (XAI) | Every verdict shows the specific tokens driving the score — no black box |
| SIEM Integration | Every verdict emits a structured `SiemLogEntry` (verdict, severity, MITRE technique, IOCs) designed for Splunk / Elastic SIEM / Azure Sentinel ingest |

---

## How It Works

```mermaid
flowchart LR
    A["Email\nSubject + Body"] --> B["ML Layer\nTF-IDF + Logistic Regression"]
    B --> C["Risk Score\n+ Feature Weights"]
    A --> D["LLM Layer\nClaude claude-sonnet-4-6"]
    C --> D
    C --> E["React Frontend"]
    D --> E
```

**ML Layer** — A TF-IDF vectorizer (5,000 features, 1–2 grams) feeds a Logistic Regression classifier trained on the [SpamAssassin public corpus](https://spamassassin.apache.org/old/publiccorpus/) (2,972 labeled emails). The top contributing tokens and their weights are extracted from the model's coefficients and returned with every prediction. This is the explainability anchor.

**LLM Layer** — The email text and ML score are sent to Claude with a structured system prompt constrained to defensive analysis only. Claude returns a risk assessment, reasoning, and indicators of compromise (IOCs) in structured JSON. The LLM layer is optional — the app degrades gracefully to ML-only if no API key is present.

---

## Results

Evaluated on a held-out test set (20% of the SpamAssassin corpus, 595 emails, stratified split):

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Legitimate | 98.81% | 99.80% | 99.30% |
| Phishing | 98.88% | 93.62% | 96.17% |
| **Overall accuracy** | | | **98.82%** |
| **False Positive Rate** | | | **~0.20%** |

> A ~0.20% FPR means roughly 1 in 500 legitimate emails is incorrectly flagged as phishing — minimizing false alarms is a first-class design goal for SOC tooling.

<details>
<summary>Example SIEM log output</summary>

```json
{
  "timestamp": "2026-04-21T20:00:00Z",
  "event_type": "email_threat_assessment",
  "verdict": "PHISHING",
  "severity": "HIGH",
  "confidence": 0.97,
  "mitre_technique": "T1566.001",
  "iocs": ["verify your account immediately", "http://banklogin-verify.example/reset"],
  "header_flags": ["spf_fail", "reply_to_mismatch"],
  "analyst_notes": "Email exhibits classic credential-harvesting pattern..."
}
```

</details>

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Async, typed, self-documenting via OpenAPI |
| ML | scikit-learn (TF-IDF + LR) | Explainable coefficients, no GPU required |
| LLM | Anthropic Claude claude-sonnet-4-6 | Structured JSON output, defensive-only prompt |
| Frontend | React 19 + TypeScript (Vite) | Type-safe, fast build |
| Testing | pytest + Vitest | 124 backend tests, 16 frontend tests, 98% coverage |
| CI | GitHub Actions | Ruff, mypy, pytest, ESLint, tsc, Vitest on every push |
| Security scanning | CodeQL + Dependabot | SAST on Python + JS; weekly dependency updates |
| Deployment | Render (free tier) | Zero-config from `render.yaml` |

---

## Model Selection: Explainability Over Black-Box Accuracy

In SOC environments, a black-box model creates analyst distrust even when accurate — an analyst needs to explain a verdict to a stakeholder, not just report a score. I evaluated Naive Bayes before settling on Logistic Regression for two reasons: performance and auditability. NB is a common baseline for text classification and trains faster, but LR outperformed it on the phishing class (F1 +4.1 pp) because the features are not conditionally independent — many phishing emails use specific token combinations ("click here" + "verify account") rather than individual tokens that NB treats as unrelated. More importantly, LR's coefficients give directly interpretable feature weights: a positive coefficient means the token pushes toward phishing. That interpretability is the core value proposition of this tool for SOC use, so the model choice was driven by explainability requirements, not just accuracy.

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
# Windows PowerShell:
# $env:ANTHROPIC_API_KEY = "sk-ant-..."
```

Or copy `.env.example` to `.env` and fill in your key.

### Frontend

```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

---

## Running Tests

```bash
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm test
```

---

## Deployment

Deployed to [Render](https://render.com) via `render.yaml`. To deploy your own copy:

1. Fork this repo
2. Go to [render.com](https://render.com) → **New → Blueprint** → connect your fork
3. Set `ANTHROPIC_API_KEY` as an environment secret on the API service
4. Render builds and deploys both services automatically

The ML model artifact (`backend/model/pipeline.joblib`) is committed to the repo so no training step is needed at deploy time.

---

## Project Structure

```
backend/        FastAPI app, ML model, Claude API integration
frontend/       React/TypeScript UI
data/           Labeled email corpus (SpamAssassin, Apache 2.0)
scripts/        Playwright demo recording script
```

---

*Defensive and security-education use only. No phishing generation or offensive tooling.*
