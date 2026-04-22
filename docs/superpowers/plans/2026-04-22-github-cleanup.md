# GitHub Community Standards Cleanup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Commit all pending work, add LICENSE/SECURITY.md/CONTRIBUTING.md/PR template, and remove `docs/resume-bullets.md` from git tracking so the repo passes the GitHub community standards checklist.

**Architecture:** Three sequential commits. No source code edits — pending files are committed as-is. All new files are config/documentation only.

**Tech Stack:** Git, Markdown

---

## File Map

| Action | Path | Purpose |
|---|---|---|
| Stage (no edit) | `docs/ARCHITECTURE.md` | Already exists untracked — add to git |
| Stage (no edit) | `docs/MODEL_CARD.md` | Already exists untracked — add to git |
| Stage (no edit) | `docs/attack-navigator-layer.json` | Already exists untracked — add to git |
| Stage (no edit) | `backend/app/siem.py` | Modified — commit as-is |
| Stage (no edit) | `backend/tests/test_siem.py` | Modified — commit as-is |
| Stage (no edit) | `frontend/README.md` | Modified — commit as-is |
| Create | `LICENSE` | MIT license |
| Create | `SECURITY.md` | Responsible disclosure policy |
| Create | `CONTRIBUTING.md` | Fork → branch → test → PR guide |
| Create | `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist template |
| Modify | `.gitignore` | Add `docs/resume-bullets.md` entry |
| Remove from tracking | `docs/resume-bullets.md` | `git rm --cached` — stays on disk |

---

## Task 1: Commit pending docs and source changes

**Files:**
- Stage (no edit): `docs/ARCHITECTURE.md`, `docs/MODEL_CARD.md`, `docs/attack-navigator-layer.json`
- Stage (no edit): `backend/app/siem.py`, `backend/tests/test_siem.py`, `frontend/README.md`

- [ ] **Step 1: Verify the files are in the expected state**

```bash
git status --short
```

Expected output includes these lines (order may vary):
```
 M backend/app/siem.py
 M backend/tests/test_siem.py
 M frontend/README.md
?? docs/ARCHITECTURE.md
?? docs/MODEL_CARD.md
?? docs/attack-navigator-layer.json
```

- [ ] **Step 2: Stage all six files**

```bash
git add docs/ARCHITECTURE.md docs/MODEL_CARD.md docs/attack-navigator-layer.json backend/app/siem.py backend/tests/test_siem.py frontend/README.md
```

- [ ] **Step 3: Verify staging**

```bash
git status --short
```

Expected: all six files show as `M` or `A` (green, staged), not `??` or red.

- [ ] **Step 4: Commit**

```bash
git commit -m "docs: add architecture, model card, ATT&CK layer; update siem and frontend README"
```

Expected output:
```
[master <hash>] docs: add architecture, model card, ATT&CK layer; update siem and frontend README
 6 files changed, ...
```

---

## Task 2: Add GitHub community standard files

**Files:**
- Create: `LICENSE`
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: Create `LICENSE`**

Create file at repo root with exact content:

```
MIT License

Copyright (c) 2026 Richard Blea

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Create `SECURITY.md`**

Create file at repo root with exact content:

```markdown
# Security Policy

## Scope

This security policy covers:
- The live demo at https://phishing-detector-ui-s3bf.onrender.com
- The source code in this repository

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing **rblea5297@gmail.com** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. (Optional) suggested fix

Please **do not** open a public GitHub issue for security vulnerabilities.

**Response time:** This is a personal portfolio project — I will respond as quickly as possible, typically within a few days.

## Out of Scope

The following are not considered vulnerabilities in this context:
- Rate limiting on the public demo API
- Social engineering attempts targeting the author
- Intentional offensive use of the tool (see [CONTRIBUTING.md](CONTRIBUTING.md))

## Acknowledgments

Security researchers who responsibly disclose issues will be acknowledged here.

---

*This project is defensive and security-education focused. No phishing generation or offensive tooling is in scope.*
```

- [ ] **Step 3: Create `CONTRIBUTING.md`**

Create file at repo root with exact content:

```markdown
# Contributing

Thanks for your interest in contributing to the AI Phishing Detector portfolio project.

## Defensive-Only Constraint

**This project is defensive and security-education focused.** Contributions that add phishing generation, bulk analysis endpoints, offensive payloads, or any capability that could be used to attack systems will not be accepted.

## How to Contribute

1. **Fork** this repository and clone your fork
2. **Create a branch** from `master`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Make your changes** following the existing code style
4. **Run tests** before submitting:
   ```bash
   # Backend
   cd backend && uv run pytest
   uv run ruff check .
   uv run mypy .

   # Frontend
   cd frontend && npm test
   npm run lint
   npm run typecheck
   ```
5. **Open a pull request** using the provided PR template

## Code Style

- **Backend:** Python 3.12+, formatted with Ruff, type-checked with mypy. Run `uv run ruff format .` before committing.
- **Frontend:** TypeScript, linted with ESLint. Run `npm run lint` before committing.

## Local Setup

See [README.md](README.md#local-setup) for full setup instructions.
```

- [ ] **Step 4: Create `.github/PULL_REQUEST_TEMPLATE.md`**

Create file at `.github/PULL_REQUEST_TEMPLATE.md` with exact content:

```markdown
## What changed and why

<!-- Describe your change in 1-3 sentences -->

## Checklist

- [ ] Tests pass (`cd backend && uv run pytest` / `cd frontend && npm test`)
- [ ] Linting clean (`uv run ruff check .` / `npm run lint`)
- [ ] Type check passes (`uv run mypy .` / `npm run typecheck`)
- [ ] No hardcoded secrets or API keys introduced
- [ ] Change is defensive/educational only — no offensive capabilities added
```

- [ ] **Step 5: Verify all four files exist**

```bash
ls LICENSE SECURITY.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md
```

Expected: all four paths printed without error.

- [ ] **Step 6: Stage and commit**

```bash
git add LICENSE SECURITY.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md
git commit -m "chore: add GitHub community standard files"
```

Expected:
```
[master <hash>] chore: add GitHub community standard files
 4 files changed, ...
```

---

## Task 3: Remove `resume-bullets.md` from git tracking

**Files:**
- Modify: `.gitignore` (add one line)
- Remove from tracking: `docs/resume-bullets.md` (file stays on disk)

- [ ] **Step 1: Add `docs/resume-bullets.md` to `.gitignore`**

Open `.gitignore`. Find the `# PAI internal files` section (currently at the bottom of the PAI block):

```
# PAI internal files
MEMORY/
Plans/
frontend/MEMORY/
```

Add `docs/resume-bullets.md` on a new line after `frontend/MEMORY/`:

```
# PAI internal files
MEMORY/
Plans/
frontend/MEMORY/
docs/resume-bullets.md
```

- [ ] **Step 2: Remove the file from git tracking (keep on disk)**

```bash
git rm --cached docs/resume-bullets.md
```

Expected output:
```
rm 'docs/resume-bullets.md'
```

- [ ] **Step 3: Verify the file is still on disk but untracked**

```bash
git status --short docs/resume-bullets.md && ls docs/resume-bullets.md
```

Expected:
```
docs/resume-bullets.md        ← ls confirms file exists on disk
```
`git status --short` should show nothing (file is now ignored via `.gitignore`).

- [ ] **Step 4: Stage and commit**

```bash
git add .gitignore
git commit -m "chore: remove resume-bullets from tracking"
```

Expected:
```
[master <hash>] chore: remove resume-bullets from tracking
 2 files changed, ...
```

---

## Final Verification

- [ ] **Confirm clean working tree**

```bash
git status
```

Expected: `nothing to commit, working tree clean`

- [ ] **Confirm commit history**

```bash
git log --oneline -5
```

Expected — top 4 commits should be:
```
<hash> chore: remove resume-bullets from tracking
<hash> chore: add GitHub community standard files
<hash> docs: add architecture, model card, ATT&CK layer; update siem and frontend README
<hash> docs: add GitHub cleanup design spec
```

- [ ] **Confirm community files exist at repo root**

```bash
ls LICENSE SECURITY.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md
```

Expected: all four paths printed without error.

- [ ] **Push to GitHub**

```bash
git push origin master
```

After push, verify at `https://github.com/Rblea97/ai-phishing-detector-portfolio/community` that the checklist shows License, Security policy, Contributing, and Pull request template all checked.
