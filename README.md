# Identity Registration & Verification Service

A production-ready microservice responsible for user registration, email verification, and account activation. Built with **NestJS** (TypeScript) following **hexagonal architecture** (ports & adapters).

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Overview

This service handles:

| Responsibility | Detail |
|---|---|
| **Registration** | Accepts registration commands with idempotency handling |
| **DTO Validation** | Email normalisation, password policy, optional CAPTCHA |
| **Password Security** | Argon2id hashing (64 MiB memory cost, 3 iterations) |
| **Verification Tokens** | Signed, short-lived (60 min), single-use tokens |
| **Account Activation** | Transitions account `PENDING_VERIFICATION → ACTIVE` |
| **Outbox Pattern** | Integration events written transactionally to the outbox table |
| **Enumeration Safety** | Generic HTTP responses prevent email/token enumeration |

---

## Architecture

The service follows **hexagonal architecture** (ports & adapters):

```
src/
├── domain/                  # Pure business logic — no framework dependencies
│   ├── entities/            # User, VerificationToken aggregates
│   ├── enums/               # AccountStatus
│   ├── events/              # Domain events (UserRegistered, UserActivated)
│   ├── ports/               # Output port interfaces (repository, hasher, etc.)
│   └── value-objects/       # Email, Password value objects
│
├── application/             # Use-case orchestration
│   ├── commands/            # RegisterUserCommand, VerifyEmailCommand
│   ├── results/             # RegisterUserResult, VerifyEmailResult
│   └── use-cases/           # RegisterUserUseCase, VerifyEmailUseCase
│
├── infrastructure/          # Adapter implementations
│   ├── config/              # NestJS ConfigModule factories
│   ├── persistence/
│   │   ├── entities/        # TypeORM ORM entities
│   │   └── repositories/    # TypeORM repository adapters + outbox writer
│   └── security/            # Argon2id hasher, crypto token generator
│
└── interfaces/              # Driving adapters (HTTP)
    └── http/
        ├── health/          # GET /health
        ├── registration/    # POST /api/v1/registrations
        └── verification/    # POST /api/v1/verifications/email
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service + database health check |
| `POST` | `/api/v1/registrations` | Register a new user |
| `POST` | `/api/v1/verifications/email` | Verify email with one-time token |
| `GET` | `/api/docs` | Swagger / OpenAPI UI |

### Register User

```http
POST /api/v1/registrations
Content-Type: application/json

{
  "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "password": "Str0ng!Pass",
  "captchaToken": "optional-captcha-token"
}
```

**Response 202 Accepted**
```json
{
  "userId": "...",
  "status": "PENDING_VERIFICATION",
  "message": "If this email is not already registered, a verification link has been sent."
}
```

### Verify Email

```http
POST /api/v1/verifications/email
Content-Type: application/json

{
  "token": "<raw-token-from-email-link>"
}
```

**Response 200 OK**
```json
{
  "userId": "...",
  "status": "ACTIVE",
  "message": "Email verified successfully. Your account is now active."
}
```

---

## Getting Started

### Prerequisites

- Node.js 20+
- PostgreSQL 15+
- (Optional) Redis 7+

### Local Development

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your local values

# 3. Start in watch mode
npm run start:dev
```

The service will be available at `http://localhost:3000`.  
Swagger UI: `http://localhost:3000/api/docs`

### Docker

```bash
# Build image
docker build -t identity-service .

# Run with environment variables
docker run -p 3000:3000 \
  -e DB_HOST=host.docker.internal \
  -e DB_PASSWORD=changeme \
  -e JWT_SECRET=your-secret \
  identity-service
```

#### Docker Compose (example)

```yaml
version: '3.9'
services:
  identity-service:
    build: .
    ports:
      - "3000:3000"
    env_file: .env
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: identity_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: changeme
    ports:
      - "5432:5432"
```

---

## Configuration

All configuration is driven by environment variables. See [`.env.example`](.env.example) for the full list.

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | HTTP port |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USERNAME` | `postgres` | Database user |
| `DB_PASSWORD` | — | Database password |
| `DB_NAME` | `identity_db` | Database name |
| `DB_SYNCHRONIZE` | `false` | Auto-sync schema (dev only) |
| `JWT_SECRET` | — | JWT signing secret |
| `VERIFICATION_TOKEN_TTL_MINUTES` | `60` | Token validity window |
| `OTEL_SERVICE_NAME` | `identity-...` | OpenTelemetry service name |

---

## Testing

```bash
# Unit tests
npm test

# Unit tests with coverage
npm run test:cov

# E2E tests
npm run test:e2e
```

---

## Password Policy

Passwords must:
- Be 8–128 characters long
- Contain at least one uppercase letter
- Contain at least one lowercase letter
- Contain at least one digit
- Contain at least one special character

---

## Security Notes

- Passwords are hashed with **Argon2id** (64 MiB memory, 3 iterations, 4 parallelism).
- Verification tokens are 32-byte cryptographically random values, stored as SHA-256 hashes.
- All HTTP responses use **generic messages** to prevent email and token enumeration.
- The outbox pattern ensures integration events are never lost even if the message broker is temporarily unavailable.
