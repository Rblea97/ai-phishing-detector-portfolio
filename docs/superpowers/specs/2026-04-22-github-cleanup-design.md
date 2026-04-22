# GitHub Community Standards Cleanup — Design Spec

**Date:** 2026-04-22  
**Scope:** Option B — Full GitHub community standards + commit pending work  
**Repo:** `Rblea97/ai-phishing-detector-portfolio`

---

## Goals

1. Close the two critical GitHub gaps: missing LICENSE and missing SECURITY.md.
2. Complete the GitHub community standards checklist (LICENSE, security policy, contributing guide, PR template).
3. Commit all pending modified and untracked files so the working tree is clean.
4. Remove `docs/resume-bullets.md` from git tracking (personal career doc, not public-facing).

## Out of Scope

- CI/CD workflow changes (path filters, coverage reporting)
- Any source code edits beyond committing the already-modified `siem.py`, `test_siem.py`, and `frontend/README.md` as-is
- README edits
- Any changes to `render.yaml`, `docker-compose.yml`, `Makefile`, or `pyproject.toml`

---

## New Files

### `LICENSE`

MIT License. Copyright 2026 Richard Blea. Standard permissive license — allows recruiters, contributors, and the public to fork, use, and modify with attribution.

### `SECURITY.md`

Responsible disclosure policy. Key elements:
- Scope: the live demo at `phishing-detector-ui-s3bf.onrender.com`; the source code itself
- Report via email (rblea5297@gmail.com)
- No formal bug bounty program
- Out-of-scope: intentional offensive use, rate-limit abuse, social engineering of the author
- Expected response time: best-effort for a personal project
- Acknowledgment section

### `CONTRIBUTING.md`

Short, practical fork → branch → test → PR guide. Key elements:
- Fork and clone
- Create a feature branch
- Run `uv run pytest` (backend) and `npm test` (frontend) before submitting
- Open a PR with the template
- Defensive-only constraint: no phishing generation, no offensive tooling — contributions that add offensive capability will not be accepted
- Code style: follow existing Ruff + mypy (backend), ESLint + tsc (frontend) conventions

### `.github/PULL_REQUEST_TEMPLATE.md`

Minimal checklist PR template:
- Describe what changed and why
- Checkboxes: tests pass, linting clean, no hardcoded secrets or API keys, change is defensive/educational only

---

## Modified Files (committed as-is)

No edits are made to these files — they are committed from the current working tree state:

- `backend/app/siem.py`
- `backend/tests/test_siem.py`
- `frontend/README.md`

---

## Untracked Files (committed as-is)

These files are already linked from `README.md` but not yet in git:

- `docs/ARCHITECTURE.md`
- `docs/MODEL_CARD.md`
- `docs/attack-navigator-layer.json`

---

## Removed from Tracking

- `docs/resume-bullets.md` — removed via `git rm --cached`; entry added to `.gitignore`
- File stays on disk; only removed from git going forward

---

## Commit Plan

| # | Files | Commit message |
|---|---|---|
| 1 | `docs/ARCHITECTURE.md`, `docs/MODEL_CARD.md`, `docs/attack-navigator-layer.json`, `backend/app/siem.py`, `backend/tests/test_siem.py`, `frontend/README.md` | `docs: add architecture, model card, ATT&CK layer; update siem and frontend README` |
| 2 | `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md` | `chore: add GitHub community standard files` |
| 3 | `.gitignore`, `docs/resume-bullets.md` (removed via `git rm --cached`) | `chore: remove resume-bullets from tracking` |

---

## Success Criteria

- `github.com/Rblea97/ai-phishing-detector-portfolio/community` checklist shows: License ✅, Security policy ✅, Contributing ✅, Pull request template ✅
- `git status` shows clean working tree after all three commits
- `docs/resume-bullets.md` is absent from the remote repo
- `docs/ARCHITECTURE.md`, `docs/MODEL_CARD.md`, `docs/attack-navigator-layer.json` are visible on GitHub
- All existing CI checks still pass
