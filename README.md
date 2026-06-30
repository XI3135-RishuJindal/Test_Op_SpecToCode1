# Pharmacy Microservice

A Spring Boot microservice implementing **hexagonal architecture** (ports and adapters) to manage:

- **Prescriptions** — create, retrieve, refill, and cancel patient prescriptions
- **Medication Adherence** — track whether patients take their medications on schedule
- **Price Comparison** — compare medication prices across pharmacies

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Java 21 |
| Framework | Spring Boot 3.2 |
| Persistence | Spring Data JPA + Hibernate |
| Database | PostgreSQL (H2 for tests) |
| Migrations | Flyway |
| Build | Maven |
| Container | Docker (eclipse-temurin:21-jre-alpine) |

---

## Architecture

This service follows **Hexagonal Architecture** (Ports & Adapters):

```
src/main/java/com/pharmacy/
├── PharmacyApplication.java          # Entry point
│
├── domain/                           # Core domain — no framework deps
│   ├── model/                        # Entities & value objects
│   │   ├── Prescription.java
│   │   ├── PrescriptionStatus.java
│   │   ├── AdherenceRecord.java
│   │   ├── AdherenceStatus.java
│   │   └── MedicationPrice.java
│   └── exception/                    # Domain exceptions
│       ├── PrescriptionNotFoundException.java
│       └── AdherenceRecordNotFoundException.java
│
├── application/                      # Use-case orchestration
│   ├── port/
│   │   ├── in/                       # Inbound ports (use-case interfaces)
│   │   │   ├── PrescriptionUseCase.java
│   │   │   ├── CreatePrescriptionCommand.java
│   │   │   ├── AdherenceUseCase.java
│   │   │   ├── RecordAdherenceCommand.java
│   │   │   └── PriceComparisonUseCase.java
│   │   └── out/                      # Outbound ports (repository interfaces)
│   │       ├── PrescriptionRepository.java
│   │       ├── AdherenceRepository.java
│   │       └── MedicationPriceRepository.java
│   └── service/                      # Use-case implementations
│       ├── PrescriptionService.java
│       ├── AdherenceService.java
│       └── PriceComparisonService.java
│
└── adapter/
    ├── in/
    │   └── web/                      # REST controllers (inbound adapters)
    │       ├── HealthController.java
    │       ├── PrescriptionController.java
    │       ├── AdherenceController.java
    │       ├── PriceComparisonController.java
    │       └── GlobalExceptionHandler.java
    └── out/
        └── persistence/              # JPA adapters (outbound adapters)
            ├── PrescriptionEntity.java
            ├── PrescriptionJpaRepository.java
            ├── PrescriptionRepositoryAdapter.java
            ├── AdherenceRecordEntity.java
            ├── AdherenceRecordJpaRepository.java
            ├── AdherenceRepositoryAdapter.java
            └── MedicationPriceRepositoryAdapter.java
```

---

## API Endpoints

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Service health check |

### Prescriptions
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/prescriptions` | Create a prescription |
| GET | `/api/v1/prescriptions/{id}` | Get prescription by ID |
| GET | `/api/v1/prescriptions?patientId=` | List prescriptions by patient |
| POST | `/api/v1/prescriptions/{id}/refill` | Refill a prescription |
| DELETE | `/api/v1/prescriptions/{id}` | Cancel a prescription |

### Adherence
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/adherence` | Record a scheduled adherence event |
| PATCH | `/api/v1/adherence/{id}/taken` | Mark a dose as taken |
| GET | `/api/v1/adherence?patientId=` | List adherence records by patient |
| GET | `/api/v1/adherence/rate?patientId=` | Get adherence rate (%) |

### Price Comparison
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/prices?medicationName=` | Compare prices across pharmacies |
| GET | `/api/v1/prices/cheapest?medicationName=` | Get cheapest option |

---

## Getting Started

### Prerequisites

- Java 21+
- Maven 3.9+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker Compose)

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Start the database

```bash
docker compose up -d postgres
```

### 3. Run the application

```bash
mvn spring-boot:run
```

Or with Docker:

```bash
docker build -t pharmacy-microservice .
docker run -p 8080:8080 --env-file .env pharmacy-microservice
```

### 4. Verify health

```bash
curl http://localhost:8080/api/v1/health
```

---

## Running Tests

```bash
# Unit + integration tests (uses H2 in-memory)
mvn test

# With coverage report
mvn verify
```

---

## Environment Variables

See [`.env.example`](.env.example) for all supported variables.

| Variable | Default | Description |
|---|---|---|
| `DB_URL` | `jdbc:postgresql://localhost:5432/pharmacy_db` | JDBC connection URL |
| `DB_USERNAME` | `pharmacy_user` | Database username |
| `DB_PASSWORD` | — | Database password |
| `SERVER_PORT` | `8080` | HTTP server port |
| `LOG_LEVEL` | `INFO` | Application log level |

---

## License

MIT
