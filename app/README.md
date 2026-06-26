# Multi-factor Authentication Service

A production-ready **Multi-factor Authentication (MFA) Service** built with **Node.js**, **Express**, and **Twilio**. It manages the full OTP lifecycle — generation, delivery, and validation — following **hexagonal architecture** (ports & adapters) for maximum testability and adaptability.

---

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Docker](#docker)
- [Design Decisions](#design-decisions)

---

## Architecture

The service follows **hexagonal architecture** (also known as ports & adapters):

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP Adapters                        │
│          (Express routes, middleware)                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Domain Core                           │
│   Entities: OTP                                         │
│   Use-cases: generateOTP, validateOTP                   │
│   Ports: OTPRepository, NotificationService             │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
┌──────────▼──────────┐  ┌────────────▼──────────────────┐
│  Persistence Adapter│  │   Notification Adapter        │
│  InMemoryOTPRepo    │  │   TwilioNotificationService   │
│  (swap for Redis/DB)│  │   MockNotificationService     │
└─────────────────────┘  └───────────────────────────────┘
```

---

## Project Structure

```
.
├── src/
│   ├── app.js                          # Express app factory
│   ├── index.js                        # Entry point / server bootstrap
│   ├── domain/
│   │   ├── entities/
│   │   │   └── OTP.js                  # OTP domain entity
│   │   ├── ports/
│   │   │   ├── OTPRepository.js        # Persistence port (interface)
│   │   │   └── NotificationService.js  # Notification port (interface)
│   │   └── usecases/
│   │       ├── generateOTP.js          # Generate & send OTP use-case
│   │       └── validateOTP.js          # Validate OTP use-case
│   ├── adapters/
│   │   ├── http/
│   │   │   ├── routes/
│   │   │   │   ├── health.routes.js
│   │   │   │   └── otp.routes.js
│   │   │   └── middleware/
│   │   │       ├── errorHandler.js
│   │   │       └── requestLogger.js
│   │   ├── persistence/
│   │   │   └── InMemoryOTPRepository.js
│   │   └── notifications/
│   │       ├── TwilioNotificationService.js
│   │       └── MockNotificationService.js
│   └── infrastructure/
│       ├── container.js                # DI container / adapter wiring
│       └── logger.js                   # Winston logger
├── tests/
│   ├── health.test.js
│   ├── otp.test.js
│   └── unit/
│       ├── OTP.entity.test.js
│       ├── InMemoryOTPRepository.test.js
│       └── usecases.test.js
├── .env.example
├── .dockerignore
├── Dockerfile
└── package.json
```

---

## Getting Started

### Prerequisites

- Node.js ≥ 18
- npm ≥ 9
- (Optional) A Twilio account for real SMS delivery

### Installation

```bash
cp .env.example .env
# Edit .env with your values
npm install
npm start
```

The service starts on `http://localhost:3000` by default.

---

## Environment Variables

| Variable              | Required | Default | Description                                      |
|-----------------------|----------|---------|--------------------------------------------------|
| `PORT`                | No       | `3000`  | HTTP port the service listens on                 |
| `NODE_ENV`            | No       | —       | `production` enables Twilio & JSON logging       |
| `USE_TWILIO`          | No       | `false` | Set to `true` to force Twilio outside production |
| `OTP_TTL_SECONDS`     | No       | `300`   | OTP validity window in seconds                   |
| `TWILIO_ACCOUNT_SID`  | Yes*     | —       | Twilio Account SID (*required in production)     |
| `TWILIO_AUTH_TOKEN`   | Yes*     | —       | Twilio Auth Token (*required in production)      |
| `TWILIO_PHONE_NUMBER` | Yes*     | —       | Twilio sender phone number (E.164 format)        |
| `LOG_LEVEL`           | No       | `info`  | Winston log level                                |

---

## API Reference

### Health Check

```
GET /health
```

**Response 200**
```json
{
  "status": "ok",
  "service": "multi-factor-authentication-service",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

### Generate OTP

```
POST /api/v1/otp/generate
Content-Type: application/json
```

**Request body**
```json
{
  "userId": "user-123",
  "phoneNumber": "+15005550006"
}
```

**Response 201**
```json
{
  "otpId": "550e8400-e29b-41d4-a716-446655440000",
  "expiresAt": "2024-01-01T00:05:00.000Z"
}
```

---

### Validate OTP

```
POST /api/v1/otp/validate
Content-Type: application/json
```

**Request body**
```json
{
  "userId": "user-123",
  "code": "847291"
}
```

**Response 200**
```json
{ "valid": true }
```

or

```json
{ "valid": false, "reason": "OTP has expired." }
```

---

## Running Tests

```bash
# Run all tests
npm test

# With coverage report
npm run test:coverage
```

---

## Docker

### Build

```bash
docker build -t mfa-service .
```

### Run

```bash
docker run -p 3000:3000 --env-file .env mfa-service
```

---

## Design Decisions

- **Hexagonal architecture** keeps the domain free of framework and infrastructure concerns. Swap the persistence or notification adapter without touching business logic.
- **In-memory repository** is the default adapter. Replace it with a Redis or SQL adapter by implementing `OTPRepository` and updating `container.js`.
- **MockNotificationService** is used in non-production environments so tests never make real Twilio calls.
- **DI container** (`infrastructure/container.js`) is a simple service locator — no heavy framework needed at this scale.
