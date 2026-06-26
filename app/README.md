# Registration Service

A Spring Boot microservice that handles user registration, email format validation, duplicate detection, and email verification triggers.

## Architecture

This service follows **Hexagonal Architecture** (Ports & Adapters):

```
src/main/java/com/registration/
├── domain/                        # Core domain model & business logic
│   ├── model/                     # Domain entities and value objects
│   └── exception/                 # Domain-specific exceptions
├── application/                   # Application layer (use cases)
│   ├── port/
│   │   ├── in/                    # Inbound ports (use case interfaces)
│   │   └── out/                   # Outbound ports (repository/notification interfaces)
│   └── service/                   # Use case implementations
└── adapter/                       # Adapters (infrastructure)
    ├── in/
    │   └── web/                   # REST controllers (inbound adapters)
    └── out/
        ├── persistence/           # JPA repositories (outbound adapters)
        └── notification/          # Email notification adapter (outbound adapter)
```

## Responsibilities

- Receive user registration requests
- Validate email format and check for duplicates
- Trigger email verification upon successful registration

## Technology Stack

- **Java 21**
- **Spring Boot 3.2**
- **Spring Data JPA** (PostgreSQL in production, H2 in tests)
- **Spring Boot Mail** (email verification)
- **Spring Boot Actuator** (health check)
- **Maven**

## Prerequisites

- Java 21+
- Maven 3.9+
- PostgreSQL (for production)
- Docker (optional)

## Getting Started

### 1. Configure environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

### 2. Run locally

```bash
mvn spring-boot:run
```

### 3. Run with Docker

```bash
docker build -t registration-service .
docker run -p 8080:8080 --env-file .env registration-service
```

## API Endpoints

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | `/api/v1/registrations`     | Register a new user            |
| GET    | `/actuator/health`          | Health check                   |

### Register a User

**Request:**
```http
POST /api/v1/registrations
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "status": "PENDING_VERIFICATION"
}
```

**Error Responses:**
- `400 Bad Request` — invalid email format or missing required fields
- `409 Conflict` — email already registered

### Health Check

```http
GET /actuator/health
```

```json
{
  "status": "UP"
}
```

## Running Tests

```bash
mvn test
```

## Environment Variables

See `.env.example` for all supported environment variables.

## License

Internal use only.
