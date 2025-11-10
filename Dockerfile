# Stage 1: Build stage
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync --locked

# Stage 2: Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY src/ ./src/
EXPOSE 8000
CMD ["./.venv/bin/fastapi", "run", "src/core/interface/server.py", "--forwarded-allow-ips='*'", "--root-path", "/expertise"]