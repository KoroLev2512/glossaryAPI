# syntax=docker/dockerfile:1.7-labs
FROM python:3.11-slim AS base

# Install uv (pip replacement) and build deps
RUN pip install --no-cache-dir uv==0.4.16

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY app ./app
COPY scripts ./scripts
COPY static ./static

# Install dependencies using uv
RUN uv venv && . .venv/bin/activate && uv pip install -e .

# Default runtime
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000

CMD . .venv/bin/activate && uvicorn app.main:app --host $HOST --port $PORT
