# Identity Registration & Verification Service

A production-ready microservice responsible for user registration, email verification, and account lifecycle management. Built with **NestJS** (TypeScript) following **hexagonal architecture** (ports & adapters).

---

## Table of Contents

- [Architecture](#architecture)
- [Responsibilities](#responsibilities)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Docker](#docker)
- [Project Structure](#project-structure)

---

## Architecture

This service follows **hexagonal architecture** (also known as ports & adapters):

```
src/
├── domain/           # Core business logic — entities, value objects, ports, events
├── application/      # Use cases (orchestrate domain + ports)
├── infrastructure/   # Adapters — TypeORM repositories, Argon2 hasher, token generator
└── interfaces/       # HTTP controllers, DTOs, exception filters
```

The domain layer has **zero framework dependencies**. All I/O is abstracted behind port interfaces (`IUserRepository`, `IPasswordHasher`, etc.) and injected at runtime by NestJS.

---

## Responsibilities

| Responsibility | Details |
|---|---|
| Registration | Accept commands with idempotency handling; validate DTOs; hash passwords (Argon2id) |
| Account state | Create users in `PENDING_VERIFICATION`; transition to `ACTIVE` on verification |
| Verification tokens | Generate signed, short-lived, single-use tokens (SHA-256 stored hash) |
| Outbox pattern | Write integration events transactionally alongside user data |
| Enumeration safety | Generic responses on all registration and verification endpoints |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | NestJS 10 (TypeScript) |
| ORM | TypeORM 0.3 |
| Database | PostgreSQL 15+ |
| Password hashing | Argon2id (OWASP recommended) |
| Observability | OpenTelemetry |
| Validation | class-validator / class-transformer |
| API docs | Swagger / OpenAPI 3 |

---

## Getting Started

### Prerequisites

- Node.js ≥ 20
- PostgreSQL 15+
- (Optional) Redis 7+

### Install dependencies

```bash
npm install
```

### Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Run in development

```bash
npm run start:dev
```

The service starts on `http://localhost:3000`.  
Swagger UI is available at `http://localhost:3000/api/docs`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | HTTP port |
| `NODE_ENV` | `development` | Runtime environment |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USERNAME` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | `changeme` | PostgreSQL password |
| `DB_NAME` | `identity_db` | Database name |
| `DB_SYNCHRONIZE` | `false` | Auto-sync schema (dev only) |
| `DB_SSL` | `false` | Enable TLS for DB connection |
| `VERIFICATION_TOKEN_TTL_MINUTES` | `60` | Token expiry in minutes |
| `REDIS_HOST` | `localhost` | Redis host (optional) |
| `REDIS_PORT` | `6379` | Redis port (optional) |
| `OTEL_SERVICE_NAME` | `identity-...` | OpenTelemetry service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318` | OTLP collector endpoint |

---

## API Reference

### `POST /v1/registration`

Register a new user account.

**Request body:**
```json
{
  "email": "alice@example.com",
  "password": "P@ssw0rd!",
  "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
  "captchaToken": "optional-captcha-token"
}
```

**Response `202 Accepted`:**
```json
{
  "message": "If this email is not already registered, a verification link has been sent."
}
```

---

### `POST /v1/verification/email`

Verify an email address using the token sent by email.

**Request body:**
```json
{
  "token": "<raw-token-from-email>"
}
```

**Response `200 OK`:**
```json
{
  "message": "Email verification processed."
}
```

---

### `GET /health`

Service health check (database ping).

**Response `200 OK`:**
```json
{
  "status": "ok",
  "info": { "database": { "status": "up" } }
}
```

---

## Running Tests

```bash
# Unit tests
npm test

# Unit tests with coverage
npm run test:cov

# End-to-end tests
npm run test:e2e
```

---

## Docker

### Build image

```bash
docker build -t identity-service:latest .
```

### Run container

```bash
docker run -p 3000:3000 \
  -e DB_HOST=host.docker.internal \
  -e DB_PASSWORD=changeme \
  identity-service:latest
```

### Docker Compose (example)

```yaml
version: '3.9'
services:
  identity-service:
    build: .
    ports:
      - "3000:3000"
    environment:
      DB_HOST: postgres
      DB_PASSWORD: changeme
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: identity_db
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## Project Structure

```
.
├── src/
│   ├── main.ts                          # Bootstrap
│   ├── app.module.ts                    # Root module
│   ├── domain/
│   │   ├── entities/                    # User, VerificationToken, OutboxEvent aggregates
│   │   ├── value-objects/               # Email, Password VOs
│   │   ├── enums/                       # AccountStatus
│   │   ├── events/                      # Domain events
│   │   ├── exceptions/                  # Domain exceptions
│   │   └── ports/                       # Output port interfaces
│   ├── application/
│   │   ├── registration/                # RegisterUserUseCase + module
│   │   └── verification/                # VerifyEmailUseCase + module
│   ├── infrastructure/
│   │   ├── config/                      # App & database config
│   │   ├── notifications/               # Log notification sender (stub)
│   │   ├── persistence/
│   │   │   ├── entities/                # TypeORM entities
│   │   │   └── repositories/            # TypeORM repository adapters
│   │   └── security/                    # Argon2 hasher, crypto token generator
│   └── interfaces/
│       └── http/
│           ├── filters/                 # Global exception filter
│           ├── health/                  # Health controller + module
│           ├── registration/            # Registration controller + DTO
│           └── verification/            # Verification controller + DTO
├── test/
│   ├── health.e2e-spec.ts               # E2E health check test
│   └── jest-e2e.json
├── Dockerfile
├── .dockerignore
├── .env.example
├── nest-cli.json
├── package.json
└── tsconfig.json
```
