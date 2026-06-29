# API Gateway Service

A production-ready API Gateway service built with **Nginx** (as the core reverse proxy), **Kong**-compatible routing configuration, and a lightweight **Python/FastAPI** control-plane application. The project follows **hexagonal architecture** (ports and adapters) to keep domain logic decoupled from infrastructure concerns.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [Health Check](#health-check)
8. [Running Tests](#running-tests)
9. [Docker](#docker)

---

## Overview

The API Gateway Service is responsible for:

- **Routing** incoming API requests to the appropriate upstream services.
- **Security** — JWT validation, API-key enforcement, rate limiting, and CORS.
- **Traffic monitoring** — request/response logging, metrics exposure, and usage analytics.

---

## Architecture

The service follows the **Hexagonal Architecture** (Ports & Adapters) pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Driving Adapters                      │
│          (HTTP handlers, CLI, message consumers)         │
└────────────────────────┬────────────────────────────────┘
                         │  uses
┌────────────────────────▼────────────────────────────────┐
│                   Application Core                       │
│   domain/  ←  services/  ←  ports/ (interfaces)         │
└────────────────────────┬────────────────────────────────┘
                         │  uses
┌────────────────────────▼────────────────────────────────┐
│                   Driven Adapters                        │
│     (Nginx config writer, Kong Admin API, Tyk API,       │
│      metrics store, upstream registry)                   │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Package | Responsibility |
|---|---|---|
| Domain | `src/domain/` | Pure business entities and value objects |
| Ports | `src/ports/` | Abstract interfaces (Python ABCs) |
| Application Services | `src/services/` | Orchestrate domain logic via ports |
| Driving Adapters | `src/adapters/inbound/` | FastAPI routers, CLI entry-points |
| Driven Adapters | `src/adapters/outbound/` | Nginx, Kong, Tyk, metrics integrations |

---

## Technology Stack

| Component | Technology |
|---|---|
| Reverse Proxy | **Nginx** |
| API Gateway (primary) | **Kong** |
| API Gateway (secondary) | **Tyk** |
| Control Plane API | **FastAPI** (Python 3.11+) |
| ASGI Server | **Uvicorn** |
| Testing | **pytest** + **httpx** |
| Containerisation | **Docker** / **Docker Compose** |

---

## Project Structure

```
api-gateway-service/
├── src/
│   ├── domain/                  # Core entities & value objects
│   │   ├── __init__.py
│   │   ├── route.py             # Route entity
│   │   ├── upstream.py          # Upstream entity
│   │   └── policy.py            # Security / rate-limit policy
│   ├── ports/                   # Abstract interfaces (ports)
│   │   ├── __init__.py
│   │   ├── gateway_port.py      # GatewayPort ABC
│   │   ├── route_repository.py  # RouteRepository ABC
│   │   └── metrics_port.py      # MetricsPort ABC
│   ├── services/                # Application services
│   │   ├── __init__.py
│   │   ├── routing_service.py
│   │   ├── security_service.py
│   │   └── monitoring_service.py
│   ├── adapters/
│   │   ├── inbound/             # Driving adapters
│   │   │   ├── __init__.py
│   │   │   ├── http/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── app.py       # FastAPI application factory
│   │   │   │   ├── health.py    # /health router
│   │   │   │   └── routes_router.py
│   │   │   └── dependencies.py
│   │   └── outbound/            # Driven adapters
│   │       ├── __init__.py
│   │       ├── kong_adapter.py
│   │       ├── tyk_adapter.py
│   │       ├── nginx_adapter.py
│   │       └── in_memory_route_repo.py
│   └── main.py                  # Entry-point
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_routing_service.py
│   │   └── test_security_service.py
│   └── integration/
│       ├── __init__.py
│       └── test_health_endpoint.py
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       └── gateway.conf
├── kong/
│   └── kong.yml                 # Declarative Kong config
├── tyk/
│   └── tyk.conf                 # Tyk gateway config skeleton
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose v2

### Local Development (without Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd api-gateway-service

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Copy and configure environment variables
cp .env.example .env

# 5. Start the control-plane API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose (full stack)

```bash
cp .env.example .env
docker compose up --build
```

The control-plane API will be available at `http://localhost:8000`.  
Nginx will proxy traffic on port `80` / `443`.

---

## Environment Variables

See [.env.example](.env.example) for the full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Runtime environment |
| `APP_PORT` | `8000` | Control-plane API port |
| `KONG_ADMIN_URL` | `http://kong:8001` | Kong Admin API base URL |
| `TYK_GATEWAY_URL` | `http://tyk:8080` | Tyk Gateway base URL |
| `TYK_DASHBOARD_URL` | `http://tyk-dashboard:3000` | Tyk Dashboard URL |
| `NGINX_UPSTREAM_HOST` | `localhost` | Default upstream host |
| `JWT_SECRET` | *(required)* | Secret for JWT validation |
| `RATE_LIMIT_RPS` | `100` | Default requests-per-second limit |

---

## Health Check

```
GET /health
```

**Response (200 OK)**

```json
{
  "status": "ok",
  "service": "api-gateway-service",
  "version": "1.0.0"
}
```

---

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

---

## Docker

### Build

```bash
docker build -t api-gateway-service:latest .
```

### Run

```bash
docker run --env-file .env -p 8000:8000 api-gateway-service:latest
```
