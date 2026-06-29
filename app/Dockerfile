FROM python:3.11-slim AS base

# ── System dependencies ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── Non-root user ────────────────────────────────────────────────────────────
RUN groupadd --gid 1001 appgroup \
 && useradd  --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# ── Dependencies (cached layer) ──────────────────────────────────────────────
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Application source ───────────────────────────────────────────────────────
COPY src/ ./src/

# ── Ownership ────────────────────────────────────────────────────────────────
RUN chown -R appuser:appgroup /app
USER appuser

# ── Runtime configuration ────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_PORT=8000 \
    APP_HOST=0.0.0.0

EXPOSE 8000

# ── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# ── Entry-point ──────────────────────────────────────────────────────────────
CMD ["sh", "-c", "uvicorn src.main:app --host ${APP_HOST} --port ${APP_PORT} --log-level info"]
