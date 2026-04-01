# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies (production only, no dev group)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code and model artifact
COPY app/ app/
COPY model/ model/
COPY data/ data/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
