.PHONY: backend-install backend-test backend-lint backend-format backend-typecheck
.PHONY: frontend-install frontend-test frontend-lint frontend-typecheck frontend-build
.PHONY: check

# ── Backend ──────────────────────────────────────────────────────────────────

backend-install:
	cd backend && uv sync

backend-test:
	cd backend && uv run pytest -v

backend-lint:
	cd backend && uv run ruff check .

backend-format:
	cd backend && uv run ruff format .

backend-typecheck:
	cd backend && uv run mypy app/

backend-serve:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

# ── Frontend ─────────────────────────────────────────────────────────────────

frontend-install:
	cd frontend && npm install

frontend-test:
	cd frontend && npm test

frontend-lint:
	cd frontend && npm run lint

frontend-typecheck:
	cd frontend && npm run typecheck

frontend-build:
	cd frontend && npm run build

frontend-serve:
	cd frontend && npm run dev

# ── Combined ─────────────────────────────────────────────────────────────────

check: backend-lint backend-typecheck backend-test frontend-lint frontend-typecheck frontend-test
	@echo "All checks passed."
