# AGENTS.md — Pharmacy Microservice

> **Purpose:** This file is the authoritative scaffold specification for the Pharmacy Microservice. Every AI agent working on this service must read and follow this document before writing a single line of code.

---

## 1. Stack

| Technology | Version (minimum) | Role |
|---|---|---|
| Java | 21 (LTS) | Primary language |
| Spring Boot | 3.3.x | Application framework, auto-configuration, embedded Tomcat |
| Spring Web (MVC) | (via Spring Boot) | REST API layer |
| Spring Data JPA | (via Spring Boot) | Repository abstraction over Hibernate |
| Hibernate | 6.x (via Spring Boot) | ORM / persistence provider |
| Spring Security | (via Spring Boot) | Authentication & authorisation |
| Spring Validation | (via Spring Boot) | Bean Validation (Jakarta) |
| Flyway | 10.x | Database schema migrations |
| PostgreSQL | 16.x | Primary relational database |
| MapStruct | 1.5.x | DTO ↔ Entity mapping (compile-time) |
| Lombok | 1.18.x | Boilerplate reduction (getters, builders, etc.) |
| SpringDoc OpenAPI | 2.x | Auto-generated OpenAPI 3.1 documentation |
| JUnit 5 | (via Spring Boot) | Unit and integration test framework |
| Mockito | (via Spring Boot) | Mocking framework |
| Testcontainers | 1.19.x | Ephemeral PostgreSQL for integration tests |
| JaCoCo | 0.8.x | Code coverage enforcement |
| Maven | 3.9.x | Build tool and dependency management |
| Docker / Docker Compose | 25.x / 2.x | Containerisation and local orchestration |
| GitHub Actions | — | CI/CD pipeline |

---

## 2. Project Structure

```
pharmacy-microservice/
├── .github/
│   └── workflows/
│       └── ci.yml                        # CI pipeline definition
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/pharmacy/
│   │   │       ├── PharmacyApplication.java          # Spring Boot entry point (@SpringBootApplication)
│   │   │       ├── config/
│   │   │       │   ├── SecurityConfig.java           # Spring Security filter chain & rules
│   │   │       │   ├── OpenApiConfig.java            # SpringDoc OpenAPI metadata
│   │   │       │   └── JpaConfig.java                # JPA/Hibernate tuning (auditing, naming strategy)
│   │   │       ├── prescription/
│   │   │       │   ├── controller/
│   │   │       │   │   └── PrescriptionController.java   # REST endpoints for prescriptions
│   │   │       │   ├── service/
│   │   │       │   │   ├── PrescriptionService.java      # Interface defining prescription use cases
│   │   │       │   │   └── PrescriptionServiceImpl.java  # Business logic implementation
│   │   │       │   ├── repository/
│   │   │       │   │   └── PrescriptionRepository.java   # Spring Data JPA repository
│   │   │       │   ├── domain/
│   │   │       │   │   └── Prescription.java             # JPA entity
│   │   │       │   ├── dto/
│   │   │       │   │   ├── PrescriptionRequest.java      # Inbound DTO (validated)
│   │   │       │   │   └── PrescriptionResponse.java     # Outbound DTO
│   │   │       │   └── mapper/
│   │   │       │       └── PrescriptionMapper.java       # MapStruct mapper interface
│   │   │       ├── adherence/
│   │   │       │   ├── controller/
│   │   │       │   │   └── AdherenceController.java
│   │   │       │   ├── service/
│   │   │       │   │   ├── AdherenceService.java
│   │   │       │   │   └── AdherenceServiceImpl.java
│   │   │       │   ├── repository/
│   │   │       │   │   └── AdherenceRecordRepository.java
│   │   │       │   ├── domain/
│   │   │       │   │   └── AdherenceRecord.java
│   │   │       │   ├── dto/
│   │   │       │   │   ├── AdherenceRecordRequest.java
│   │   │       │   │   └── AdherenceRecordResponse.java
│   │   │       │   └── mapper/
│   │   │       │       └── AdherenceMapper.java
│   │   │       ├── pricing/
│   │   │       │   ├── controller/
│   │   │       │   │   └── PriceComparisonController.java
│   │   │       │   ├── service/
│   │   │       │   │   ├── PriceComparisonService.java
│   │   │       │   │   └── PriceComparisonServiceImpl.java
│   │   │       │   ├── repository/
│   │   │       │   │   └── MedicationPriceRepository.java
│   │   │       │   ├── domain/
│   │   │       │   │   └── MedicationPrice.java
│   │   │       │   ├── dto/
│   │   │       │   │   ├── PriceComparisonRequest.java
│   │   │       │   │   └── PriceComparisonResponse.java
│   │   │       │   └── mapper/
│   │   │       │       └── PriceMapper.java
│   │   │       ├── common/
│   │   │       │   ├── exception/
│   │   │       │   │   ├── ResourceNotFoundException.java   # 404 domain exception
│   │   │       │   │   ├── BusinessRuleException.java       # 422 domain exception
│   │   │       │   │   └── GlobalExceptionHandler.java      # @RestControllerAdvice handler
│   │   │       │   ├── audit/
│   │   │       │   │   └── AuditableEntity.java             # @MappedSuperclass with createdAt/updatedAt
│   │   │       │   └── pagination/
│   │   │       │       └── PageResponse.java                # Generic paginated wrapper DTO
│   │   └── resources/
│   │       ├── application.yml                   # Base application configuration
│   │       ├── application-local.yml             # Local dev overrides
│   │       ├── application-test.yml              # Test profile configuration
│   │       └── db/
│   │           └── migration/
│   │               ├── V1__create_prescription_table.sql
│   │               ├── V2__create_adherence_record_table.sql
│   │               └── V3__create_medication_price_table.sql
│   └── test/
│       ├── java/
│       │   └── com/pharmacy/
│       │       ├── prescription/
│       │       │   ├── controller/
│       │       │   │   └── PrescriptionControllerTest.java   # @WebMvcTest slice test
│       │       │   ├── service/
│       │       │   │   └── PrescriptionServiceImplTest.java  # Pure unit test with Mockito
│       │       │   └── repository/
│       │       │       └── PrescriptionRepositoryIT.java     # @DataJpaTest with Testcontainers
│       │       ├── adherence/
│       │       │   ├── controller/
│       │       │   │   └── AdherenceControllerTest.java
│       │       │   ├── service/
│       │       │   │   └── AdherenceServiceImplTest.java
│       │       │   └── repository/
│       │       │       └── AdherenceRepositoryIT.java
│       │       ├── pricing/
│       │       │   ├── controller/
│       │       │   │   └── PriceComparisonControllerTest.java
│       │       │   ├── service/
│       │       │   │   └── PriceComparisonServiceImplTest.java
│       │       │   └── repository/
│       │       │       └── MedicationPriceRepositoryIT.java
│       │       └── integration/
│       │           └── PharmacyApplicationIT.java            # Full-stack @SpringBootTest + Testcontainers
│       └── resources/
│           └── application-test.yml                         # Testcontainers datasource overrides
├── docker/
│   └── postgres/
│       └── init.sql                          # DB init script for local compose only
├── Dockerfile                                # Multi-stage production image
├── docker-compose.yml                        # Local dev stack (app + postgres)
├── docker-compose.override.yml               # Developer-specific local overrides (git-ignored)
├── pom.xml                                   # Maven build descriptor
├── .mvn/
│   └── wrapper/
│       └── maven-wrapper.properties          # Pinned Maven wrapper version
├── mvnw / mvnw.cmd                           # Maven wrapper scripts
├── tasks.md                                  # Agent-generated task breakdown (created before coding)
├── .gitignore
└── AGENTS.md                                 # This file
```

---

## 3. Required Workflow

The agent **must** follow these steps in order. Do not skip or reorder steps.

### Step 1 — Read All Specifications
- Read this `AGENTS.md` file completely before any other action.
- Read all story-level spec documents provided for the current task.
- Do not begin implementation until both are fully understood.

### Step 2 — Create `tasks.md`
- Create a `tasks.md` file in the repository root.
- Break the work into atomic, numbered tasks derived from the specs.
- Each task must specify: what to create/modify, which layer it touches, and its acceptance criterion.
- Example format:
  ```markdown
  ## Tasks
  - [ ] 1. Create `Prescription` JPA entity with fields: id, patientId, medicationCode, dosage, status, issuedAt — AC: entity maps to `prescription` table via Flyway migration V1
  - [ ] 2. Create `PrescriptionRepository` extending `JpaRepository<Prescription, UUID>` — AC: findByPatientId query method present
  ...
  ```
- Do not write any source code until `tasks.md` is committed.

### Step 3 — Implement
- Work through `tasks.md` tasks sequentially; tick each checkbox on completion.
- Follow all coding conventions in Section 4.
- Write Flyway migrations before entity classes.
- Write the service interface before the implementation.
- Never hard-code secrets or environment-specific values; use `application.yml` placeholders with environment variable bindings.

### Step 4 — Write Tests
- For every new class, write the corresponding test class before marking the task complete.
- Follow the testing strategy in Section 5.
- Run `./mvnw test` locally and confirm zero failures before proceeding to the next task.

### Step 5 — Validate
- Run `./mvnw verify` to execute full build, tests, and JaCoCo coverage check.
- Confirm coverage is ≥ 90% on the JaCoCo report (`target/site/jacoco/index.html`).
- Run `docker compose up --build` and smoke-test all endpoints via the OpenAPI UI at `http://localhost:8080/swagger-ui.html`.
- Update `tasks.md` to mark all tasks complete.
- Commit with a conventional commit message, e.g. `feat(prescription): add prescription management endpoints`.

---

## 4. Coding Conventions

### General
- **Java style:** Follow Google Java Style Guide. Line length: 120 characters.
- **Package structure:** Feature-first (vertical slice) — each domain feature (`prescription`, `adherence`, `pricing`) is a self-contained package.
- **No circular dependencies** between feature packages. Shared code lives in `common/`.

### Naming
| Artefact | Convention | Example |
|---|---|---|
| Classes | `PascalCase` | `PrescriptionServiceImpl` |
| Methods & variables | `camelCase` | `findByPatientId` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_REFILLS_ALLOWED` |
| Database tables | `snake_case`, plural | `prescriptions` |
| Database columns | `snake_case` | `patient_id` |
| REST endpoints | `kebab-case`, plural nouns | `/api/v1/prescriptions` |
| Flyway scripts | `V{n}__{description}.sql` | `V1__create_prescription_table.sql` |
| DTOs | Suffix `Request` / `Response` | `PrescriptionRequest`, `PrescriptionResponse` |
| Mappers | Suffix `Mapper` | `PrescriptionMapper` |

### Architecture Patterns
- **Layered architecture within each feature:** `Controller → Service (interface) → ServiceImpl → Repository → Domain`.
- Controllers must **never** call repositories directly.
- Services must **never** return JPA entities — always map to DTOs via MapStruct before returning.
- Entities must **never** be used as request/response bodies in controllers.
- Use `@Transactional` on service implementation methods (read-only flag on query methods).
- All IDs must be `UUID` type (not auto-increment `Long`).
- Entities must extend `AuditableEntity` to inherit `createdAt` and `updatedAt` managed by Spring Data JPA auditing (`@EnableJpaAuditing`).

### Spring Specifics
- Use constructor injection only — no `@Autowired` on fields.
- Annotate controllers with `@RestController` and `@RequestMapping("/api/v1/{feature}")`.
- Validate all inbound DTOs with `@Valid` at the controller parameter level.
- Use `@NotNull`, `@NotBlank`, `@Size`, etc. (Jakarta Validation) on DTO fields.
- Return `ResponseEntity<T>` from all controller methods with explicit HTTP status codes.
- Use Spring's `Pageable` for all list endpoints; return `PageResponse<T>`.

### Error Handling
- Throw `ResourceNotFoundException` (extends `RuntimeException`) for 404 scenarios.
- Throw `BusinessRuleException` for domain rule violations (maps to 422).
- `GlobalExceptionHandler` (`@RestControllerAdvice`) must handle all exceptions and return a consistent JSON error body:
  ```json
  { "timestamp": "...", "status": 404, "error": "Not Found", "message": "...", "path": "..." }
  ```

### Lombok
- Use `@Data` only on DTOs. Use `@Getter`, `@Setter`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor` individually on entities to avoid unintended equals/hashCode on JPA entities.
- Never use `@EqualsAndHashCode` on JPA entities; implement `equals`/`hashCode` manually based on the business key or `id`.

---

## 5. Testing

### Test Categories

| Category | Annotation | Scope | Database |
|---|---|---|---|
| Unit — Service | `@ExtendWith(MockitoExtension.class)` | Service class in isolation | None (mocked repository) |
| Unit — Controller | `@WebMvcTest(XController.class)` | Controller + MVC layer | None (mocked service) |
| Integration — Repository | `@DataJpaTest` + Testcontainers | Repository + real DB | PostgreSQL (Testcontainers) |
| Integration — Full stack | `@SpringBootTest(webEnvironment = RANDOM_PORT)` + Testcontainers | Entire application | PostgreSQL (Testcontainers) |

### Rules
- Every `ServiceImpl` class must have a corresponding `*Test.java` using Mockito. Mock all dependencies.
- Every `Controller` class must have a corresponding `*Test.java` using `@WebMvcTest`. Use `MockMvc` for HTTP assertions. Mock the service layer with `@MockBean`.