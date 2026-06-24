# API Gateway / BFF Service

A production-ready **API Gateway / Backend-for-Frontend (BFF)** service built with **FastAPI** and following **hexagonal architecture** (ports & adapters).

It exposes public registration and email-verification APIs, enforces rate limits and request-size controls, propagates correlation IDs, routes requests to the identity service, and publishes structured access logs and OpenTelemetry traces.

---

## Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Observability](#observability)
- [Contributing](#contributing)

---

## Architecture

The service follows **hexagonal architecture** (also known as ports & adapters):

```
┌─────────────────────────────────────────────────────────┐
│                    Inbound Adapters                      │
│          (FastAPI routers: health, gateway)              │
└────────────────────────┬────────────────────────────────┘
                         │  calls
┌────────────────────────▼────────────────────────────────┐
│                  Application Layer                       │
│         HealthService  │  GatewayService                │
│         (implements inbound ports)                       │
└──────────┬─────────────────────────┬────────────────────┘
           │ uses outbound ports     │
┌──────────▼──────────┐  ┌──────────▼──────────────────┐
│  UpstreamClientPort │  │  RateLimiterPort / CachePort │
│  (HttpUpstreamClient│  │  (RedisRateLimiter)          │
│   via httpx)        │  │                              │
└─────────────────────┘  └──────────────────────────────┘
           │                         │
    Identity Service            Redis
```

**Key layers:**

| Layer | Path | Responsibility |
|---|---|---|
| Core | `app/core/` | Domain models, port interfaces, exceptions |
| Application | `app/application/` | Use-case orchestration (no framework deps) |
| Adapters — Inbound | `app/adapters/inbound/` | FastAPI routers |
| Adapters — Outbound | `app/adapters/outbound/` | httpx client, Redis rate limiter/cache |
| Infrastructure | `app/infrastructure/` | Config, logging, tracing, DI, middleware |

---

## Technology Stack

| Concern | Technology |
|---|---|
| HTTP framework | FastAPI + Uvicorn |
| Upstream HTTP | httpx (async) |
| Rate limiting | Redis (sliding-window Lua script) |
| Caching | Redis |
| Observability | OpenTelemetry SDK + OTLP exporter |
| Configuration | pydantic-settings |
| Testing | pytest + pytest-asyncio + httpx |

---

## Project Structure

```
.
├── app/
│   ├── main.py                        # FastAPI app factory
│   ├── entrypoint.py                  # Uvicorn entrypoint
│   ├── core/
│   │   ├── models.py                  # Domain models (frozen dataclasses)
│   │   ├── ports.py                   # Abstract port interfaces
│   │   └── exceptions.py             # Custom exception hierarchy
│   ├── application/
│   │   ├── health_service.py          # Health-check use case
│   │   └── gateway_service.py        # Proxy / gateway use case
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── health_router.py       # GET /health, GET /health/ready
│   │   │   └── gateway_router.py     # POST /api/v1/auth/*, generic proxy
│   │   └── outbound/
│   │       ├── http_upstream_client.py  # httpx-based upstream client
│   │       ├── redis_rate_limiter.py    # Sliding-window rate limiter
│   │       └── redis_cache.py          # Generic Redis cache
│   └── infrastructure/
│       ├── config.py                  # pydantic-settings configuration
│       ├── logging.py                 # Structured JSON logging
│       ├── tracing.py                 # OpenTelemetry setup
│       ├── middleware.py              # Correlation ID, access log, size limit
│       └── dependencies.py           # FastAPI dependency injection wiring
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── test_health.py                 # Health endpoint tests
│   ├── test_gateway.py               # Gateway proxy endpoint tests
│   ├── test_gateway_service.py       # GatewayService unit tests
│   └── test_models.py                # Domain model / exception tests
├── Dockerfile
├── .dockerignore
├── .env.example
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Redis 7+ (for rate limiting)
- Docker (optional)

### Local Development

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd api-gateway

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Configure environment
cp .env.example .env
# Edit .env as needed

# 5. Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# 6. Run the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### Docker

```bash
# Build
docker build -t api-gateway:latest .

# Run
docker run -p 8000:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e IDENTITY_SERVICE_URL=http://identity-service:8001 \
  api-gateway:latest
```

---

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `api-gateway` | Service name |
| `APP_VERSION` | `0.1.0` | Semantic version |
| `ENVIRONMENT` | `development` | `development` \| `staging` \| `production` |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `WORKERS` | `1` | Uvicorn worker count |
| `LOG_LEVEL` | `info` | Log level |
| `IDENTITY_SERVICE_URL` | `http://identity-service:8001` | Upstream identity service |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per window per IP |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Sliding-window duration (seconds) |
| `MAX_REQUEST_BODY_BYTES` | `1048576` | Max request body size (1 MiB) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(empty)_ | OTLP gRPC endpoint (empty = console) |
| `OTEL_SERVICE_NAME` | `api-gateway` | OTel service name |
| `CORS_ALLOW_ORIGINS` | `["*"]` | Allowed CORS origins |

---

## API Reference

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe — returns `{"status": "ok", "version": "..."}` |
| `GET` | `/health/ready` | Readiness probe — includes upstream details |

### Gateway

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Proxy to identity service — register a new user |
| `POST` | `/api/v1/auth/verify` | Proxy to identity service — verify email address |
| `*` | `/api/v1/{path}` | Generic upstream proxy |

**Request headers:**

| Header | Required | Description |
|---|---|---|
| `X-Correlation-ID` | No | Correlation ID (auto-generated if absent) |
| `X-Idempotency-Key` | No | Idempotency key forwarded to upstream |

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_health.py -v
```

Tests use `httpx.AsyncClient` with `ASGITransport` — no real network calls are made.  
Upstream and Redis adapters are replaced with `AsyncMock` fixtures.

---

## Observability

### Structured Logging

All log output is emitted as single-line JSON to stdout, suitable for ingestion by Loki, Datadog, or any log aggregator.

```json
{"timestamp": "2024-01-01T00:00:00+00:00", "level": "INFO", "logger": "app.infrastructure.middleware", "message": "access_log", "method": "POST", "path": "/api/v1/auth/register", "status_code": 201, "duration_ms": 12.34, "correlation_id": "abc-123"}
```

### Distributed Tracing

Set `OTEL_EXPORTER_OTLP_ENDPOINT` to send traces to an OpenTelemetry collector.  
When unset, spans are printed to stdout (development mode).

### Metrics

Latency and access-log data are emitted via the structured access log.  
For Prometheus metrics, add `prometheus-fastapi-instrumentator` and mount `/metrics`.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Run linting: `ruff check . && mypy app/`
4. Run tests: `pytest`
5. Open a pull request
