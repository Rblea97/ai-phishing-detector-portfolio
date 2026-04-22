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