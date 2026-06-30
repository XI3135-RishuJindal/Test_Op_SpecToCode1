# User Role Management Service

A Spring Boot microservice for creating, assigning, and managing user roles.
Built with **hexagonal architecture** (ports & adapters) using Java 17, Spring Boot 3, and Hibernate/JPA.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running Locally](#running-locally)
  - [Running with Docker](#running-with-docker)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Overview

The User Role Management Service is responsible for:

- **Creating and managing roles** — define named roles with optional descriptions.
- **Assigning roles to users** — link external user identifiers (from the authentication service) to roles.
- **Validating user roles** — expose a validation endpoint consumed by the authentication service.

---

## Architecture

The service follows **hexagonal architecture** (also known as ports & adapters):

```
┌─────────────────────────────────────────────────────────┐
│                    Inbound Adapters                      │
│          REST Controllers  (adapter/in/web)              │
└────────────────────────┬────────────────────────────────┘
                         │  Inbound Ports (domain/port/in)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Services                   │
│         RoleService / UserRoleService  (application/)    │
└────────────────────────┬────────────────────────────────┘
                         │  Outbound Ports (domain/port/out)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Outbound Adapters                      │
│        JPA Persistence Adapters  (adapter/out/)          │
└─────────────────────────────────────────────────────────┘
```

- **Domain layer** (`domain/`) — pure business entities, port interfaces, and domain exceptions. Zero framework dependencies.
- **Application layer** (`application/`) — use-case implementations that orchestrate domain logic.
- **Adapter layer** (`adapter/`) — inbound (REST) and outbound (JPA) adapters that connect the application to the outside world.

---

## Technology Stack

| Component       | Technology                    |
|-----------------|-------------------------------|
| Language        | Java 17                       |
| Framework       | Spring Boot 3.2               |
| ORM             | Hibernate / Spring Data JPA   |
| Database        | PostgreSQL 15                 |
| Migrations      | Flyway                        |
| Build tool      | Maven                         |
| Containerisation| Docker (multi-stage build)    |
| Testing         | JUnit 5, MockMvc, H2 (in-mem) |

---

## Getting Started

### Prerequisites

- Java 17+
- Maven 3.9+
- Docker & Docker Compose (optional, for containerised setup)
- PostgreSQL 15 (if running without Docker)

### Running Locally

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd user-role-management-service
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start PostgreSQL** (skip if you already have one running)

   ```bash
   docker run -d \
     --name postgres \
     -e POSTGRES_DB=userroledb \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=changeme \
     -p 5432:5432 \
     postgres:15-alpine
   ```

4. **Run the application**

   ```bash
   ./mvnw spring-boot:run
   ```

   The service starts on `http://localhost:8080`.

### Running with Docker

```bash
# Build the image
docker build -t user-role-management-service:latest .

# Run with environment variables
docker run -d \
  --name user-role-management \
  -p 8080:8080 \
  -e DB_URL=jdbc:postgresql://host.docker.internal:5432/userroledb \
  -e DB_USERNAME=postgres \
  -e DB_PASSWORD=changeme \
  user-role-management-service:latest
```

---

## API Reference

### Health

| Method | Path      | Description          |
|--------|-----------|----------------------|
| GET    | `/health` | Service liveness     |

### Roles

| Method | Path            | Description          |
|--------|-----------------|----------------------|
| POST   | `/api/roles`    | Create a role        |
| GET    | `/api/roles`    | List all roles       |
| GET    | `/api/roles/{id}` | Get role by ID     |
| PUT    | `/api/roles/{id}` | Update a role      |
| DELETE | `/api/roles/{id}` | Delete a role      |

### User Role Assignments

| Method | Path                                        | Description                    |
|--------|---------------------------------------------|--------------------------------|
| POST   | `/api/users/{userId}/roles`                 | Assign a role to a user        |
| GET    | `/api/users/{userId}/roles`                 | List roles for a user          |
| DELETE | `/api/users/{userId}/roles/{roleId}`        | Revoke a role from a user      |
| GET    | `/api/users/{userId}/roles/validate?roleName=` | Validate user has a role    |

---

## Configuration

All configuration is driven by environment variables. See [`.env.example`](.env.example) for the full list.

| Variable        | Default                                      | Description                    |
|-----------------|----------------------------------------------|--------------------------------|
| `SERVER_PORT`   | `8080`                                       | HTTP port                      |
| `DB_URL`        | `jdbc:postgresql://localhost:5432/userroledb`| JDBC connection URL            |
| `DB_USERNAME`   | `postgres`                                   | Database username              |
| `DB_PASSWORD`   | `changeme`                                   | Database password              |
| `JPA_DDL_AUTO`  | `validate`                                   | Hibernate DDL strategy         |
| `FLYWAY_ENABLED`| `true`                                       | Enable Flyway migrations       |
| `LOG_LEVEL`     | `INFO`                                       | Application log level          |

---

## Testing

```bash
# Run all tests
./mvnw test

# Run with coverage report
./mvnw verify
```

Tests use an **in-memory H2 database** (PostgreSQL-compatible mode) — no external dependencies required.

---

## Project Structure

```
src/
├── main/
│   ├── java/com/example/userrolemanagement/
│   │   ├── UserRoleManagementApplication.java
│   │   ├── adapter/
│   │   │   ├── in/web/                  # REST controllers (inbound adapters)
│   │   │   │   ├── HealthController.java
│   │   │   │   ├── RoleController.java
│   │   │   │   ├── UserRoleController.java
│   │   │   │   ├── GlobalExceptionHandler.java
│   │   │   │   └── dto/                 # Request/Response DTOs
│   │   │   └── out/persistence/         # JPA adapters (outbound adapters)
│   │   ├── application/
│   │   │   └── service/                 # Use-case implementations
│   │   │       ├── RoleService.java
│   │   │       └── UserRoleService.java
│   │   └── domain/
│   │       ├── exception/               # Domain exceptions
│   │       ├── model/                   # Domain entities
│   │       │   ├── Role.java
│   │       │   └── UserRole.java
│   │       └── port/
│   │           ├── in/                  # Inbound ports (use-case interfaces)
│   │           └── out/                 # Outbound ports (repository interfaces)
│   └── resources/
│       ├── application.yml
│       └── db/migration/                # Flyway SQL migrations
└── test/
    ├── java/com/example/userrolemanagement/
    │   ├── adapter/in/web/              # Controller integration tests
    │   └── application/service/         # Service unit tests
    └── resources/
        └── application-test.yml
```
