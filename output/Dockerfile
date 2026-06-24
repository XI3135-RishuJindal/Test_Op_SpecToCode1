# ============================================================
# Dockerfile — Account Management Service
# IBM Mainframe / COBOL on GnuCOBOL (open-source runtime)
# ============================================================
FROM ubuntu:22.04 AS base

LABEL maintainer="account-management-service"
LABEL description="Account Management Service — COBOL/IBM Mainframe (GnuCOBOL)"
LABEL version="1.0.0"

# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        gnucobol \
        libcob4 \
        libdb5.3 \
        python3 \
        python3-pip \
        python3-venv \
        make \
        && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────
WORKDIR /app

# ── Copy source ──────────────────────────────────────────────
COPY src/       ./src/
COPY tests/     ./tests/
COPY Makefile   ./Makefile
COPY .env.example .env.example

# ── Python test dependencies ─────────────────────────────────
COPY requirements-test.txt ./requirements-test.txt
RUN pip3 install --no-cache-dir -r requirements-test.txt

# ── Compile COBOL programs ───────────────────────────────────
FROM base AS builder

RUN make compile

# ── Runtime image ────────────────────────────────────────────
FROM base AS runtime

COPY --from=builder /app/bin/ ./bin/

# Environment defaults (override at runtime)
ENV SERVICE_NAME="account-management-service"
ENV SERVICE_VERSION="1.0.0"
ENV ACCT_VSAM_PATH="/data/accounts.dat"
ENV IMPORT_FILE_PATH="/data/import/customers.dat"
ENV LOG_LEVEL="INFO"
ENV HEALTH_CHECK_ENABLED="true"

# Data volume mount point
VOLUME ["/data"]

# Health check using the compiled ACCTHLTH program via wrapper
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 /app/tests/health_check.py || exit 1

CMD ["make", "run"]
