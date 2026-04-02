# Portfolio Readiness Design

## Goal

Make the AI Phishing Detector repo maximally impressive to hiring managers and technical interviewers for entry-level security, SOC, DevSecOps, AppSec, and GRC roles in 2026 — with a live deployment, passing CI badge, security scanning, and an auto-recorded demo video.

## Context

Research findings (ISC2 2025, CyberDesserts Feb 2026) that directly inform this design:

- AI/ML in security is the #1 needed skill (41% of ISC2 respondents, up from #3 in 2024)
- Email/phishing defense is the #1 most-demanded technical skill (CyberDesserts Feb 2026)
- 87% of technical recruiters now weight GitHub profiles heavily
- CI/CD badge + no-secrets-in-repo are the top two technical screener signals
- A live demo URL on a resume is rare at entry level and is a conversation starter
- MITRE ATT&CK framework references show real-world context, not just tutorial knowledge
- Quantified results (F1, precision, recall) beat unquantified claims
- "What didn't work and why" is gold in technical interviews

## What Gets Built

### 1. README overhaul

**Structure (top to bottom):**

1. **Badge row** — CI passing, CodeQL passing, Python 3.12, React + TypeScript
2. **One-line hook** — "Detects phishing emails using a two-layer ML + LLM pipeline with full explainability."
3. **Demo section** — Loom video embed (placeholder link until recorded) + 2 screenshots (phishing result, legit result)
4. **Threat context** — 2–3 sentences: phishing = #1 initial access vector (CISA), MITRE ATT&CK T1566, why explainability matters for SOC triage
5. **How it works** — Mermaid architecture diagram showing: Email Input → ML Layer (TF-IDF + LR) → LLM Layer (Claude) → Frontend. Two sentences explaining each layer.
6. **Results** — F1, precision, recall, accuracy on the synthetic test set in a table
7. **Tech stack table** — Backend / Frontend / ML / LLM / Testing / Deployment columns
8. **What I tried** — 2–3 sentences on naive Bayes vs. logistic regression, why LR won (explainability + performance)
9. **Local setup** — existing instructions, cleaned up
10. **Deployment** — link to live Render URL

The README must work for two audiences:
- **Screener (10-second pass):** Badge row → hook → demo video → threat context answers "what security problem does this solve?"
- **Technical reviewer (2-minute pass):** Architecture diagram → results table → tech stack → "what I tried" answers "can this person engineer and think?"

### 2. GitHub Actions CI pipeline

Two workflow files:

**`.github/workflows/backend.yml`**
- Triggers: push and pull_request on any branch
- Steps: checkout → install uv → `uv sync` → `ruff check` → `mypy` → `pytest`
- Python version: 3.12

**`.github/workflows/frontend.yml`**
- Triggers: push and pull_request on any branch
- Steps: checkout → Node 22 setup → `npm ci` → `npm run lint` → `npm run typecheck` → `npm test` → `npm run build`

Both workflows produce the status badge shown in the README.

### 3. Security scanning

**`.github/dependabot.yml`**
- Weekly dependency updates for both `pip` (backend) and `npm` (frontend)
- Keeps the repo from going stale and signals active maintenance

**`.github/workflows/codeql.yml`**
- GitHub's free CodeQL SAST scan on push to master
- Languages: Python and JavaScript
- Produces the CodeQL badge
- Particularly appropriate signal for a security-focused project ("practices what it preaches")

### 4. Playwright demo recording script

**`scripts/record-demo.js`**

A Node.js script using Playwright that:
1. Launches Chromium with `recordVideo: { dir: 'scripts/video-out/' }` enabled
2. Opens `http://localhost:5173`
3. Waits for sample buttons to appear
4. Clicks the first phishing sample button
5. Clicks the Analyze button
6. Waits for the ML score and LLM result to render (polls for result card visibility)
7. Pauses 3 seconds so the viewer can read the output
8. Clicks the first legit sample button
9. Clicks Analyze again
10. Waits for results
11. Pauses 3 seconds
12. Closes browser — video saves automatically to `scripts/video-out/`

Output: a `.webm` file the user uploads to Loom (drag and drop).

**Dependencies:** `playwright` added as a dev dependency under a top-level `scripts/package.json` (isolated — does not touch frontend's package.json).

**Prerequisites to run:** both backend (`uvicorn`) and frontend (`npm run dev`) must be running locally with `ANTHROPIC_API_KEY` set.

### 5. Render deployment

`render.yaml` is already written. The user needs to:
1. Push repo to GitHub
2. Go to render.com → New → Blueprint → connect the repo
3. Set `ANTHROPIC_API_KEY` as an environment secret on the API service
4. Update the live URL in the README once Render assigns it

The README will have a placeholder `[LIVE DEMO →](https://your-render-url.onrender.com)` until the URL is known.

## What Is Not In Scope

- Adding new application features (the app is complete)
- A personal portfolio website
- Notebook / EDA section (already exists in `notebooks/`, not surfaced in README for now)
- Resume bullet points (out of scope for this repo; a separate deliverable)
- Voice-over on the demo video (user will add later)

## File Map

| File | Action |
|---|---|
| `README.md` | Full rewrite |
| `.github/workflows/backend.yml` | Create |
| `.github/workflows/frontend.yml` | Create |
| `.github/dependabot.yml` | Create |
| `.github/workflows/codeql.yml` | Create |
| `scripts/record-demo.js` | Create |
| `scripts/package.json` | Create |

## Acceptance Criteria

- [ ] README opens with badge row + one-line hook visible above the fold on GitHub
- [ ] README contains a Mermaid architecture diagram that renders on GitHub
- [ ] README contains a results table with F1, precision, recall, accuracy
- [ ] README references MITRE ATT&CK T1566
- [ ] GitHub Actions CI runs on push and both backend + frontend badges show passing
- [ ] CodeQL badge shows passing
- [ ] Dependabot config present for both pip and npm
- [ ] `scripts/record-demo.js` runs against local dev servers and produces a `.webm` file
- [ ] All existing tests continue to pass (no regressions)
- [ ] No secrets in repo (`.env` gitignored, confirmed)
