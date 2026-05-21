# Spec: Replace Static In-Memory Data Store with EF Core Repository Implementations

---

## Summary

This spec covers the replacement of the current static in-memory data store with persistent repository implementations backed by Entity Framework Core (EF Core). The expected outcome is that all data access previously handled through static, in-process collections is routed through EF Core repository classes, enabling durable persistence, proper transaction semantics, and a testable data access layer. The application's external behaviour and public interfaces remain unchanged for consumers of the repositories.

---

## Motivation

- **Data durability:** The existing static in-memory store loses all data on application restart, making it unsuitable for any production or staging environment.
- **Testability and separation of concerns:** Static state shared across the application makes unit and integration testing unreliable due to state leakage between tests.
- **Scalability:** A static in-memory store cannot support multi-instance deployments; all instances would maintain independent, divergent state.
- **Technical debt:** Reliance on static collections bypasses standard data access patterns (Unit of Work, Repository), making the codebase harder to maintain and extend.
- **Upgrade urgency:** Rated **medium** — the application is functional but the current approach is a known architectural liability that blocks future work (e.g., horizontal scaling, audit logging, reporting).

> **Note:** Specific CVEs, EOL dates, and framework version numbers were not provided in the tech analysis. See [Open Questions](#open-questions).

---

## Current State

The current data access layer relies on static in-memory collections (e.g., static `Dictionary`, `List`, or similar structures held in static fields or singleton classes) to store and retrieve application data.

Key characteristics of the current state:

| Aspect | Current Behaviour |
|---|---|
| Storage mechanism | Static in-memory collections (process-local) |
| Persistence | None — data is lost on restart |
| Concurrency handling | TODO — unknown whether thread-safety mechanisms exist |
| Transaction support | None |
| Repository abstraction | TODO — unknown whether repository interfaces currently exist |
| Dependency injection | TODO — unknown whether current store is injected or accessed statically |
| Data models / entities | TODO — specific entity class names not provided in context |
| Configuration keys | TODO — no connection string or store configuration currently exists |
| Query surface | TODO — specific query methods not identified in context |

> **TODO:** A code audit is required to enumerate all static store access points, entity types, and any existing interface contracts before implementation begins.

---

## Proposed Changes

### Overview

Each static in-memory store is replaced by an EF Core `DbContext` and a corresponding repository class implementing a defined repository interface. All callers that previously accessed static state directly will depend on the repository interface via dependency injection.

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Data store | Static in-memory collection(s) | EF Core `DbContext` with configured database provider | N — internal change |
| Repository layer | TODO (absent or ad-hoc static access) | Concrete EF Core repository classes implementing repository interfaces | N — interfaces preserved or introduced |
| Repository interfaces | TODO (may not exist) | Defined repository interfaces for each aggregate/entity | N — new contracts added |
| Dependency injection registration | TODO (static access or none) | Repository interfaces and `DbContext` registered in DI container | N |
| Database schema | None | EF Core migrations defining schema for all entities | N — additive |
| Configuration | No connection string | Connection string and provider configuration added | N — additive |
| Test doubles | Tests rely on shared static state | Tests use in-memory EF Core provider or mock repository interfaces | N — test-internal change |

### What Is Removed

- All static fields and static classes serving as in-memory data stores.
- Any direct static access patterns (e.g., `StaticStore.Items.Add(...)`) throughout the codebase.

### What Is Added

- EF Core `DbContext` class(es) with `DbSet<TEntity>` properties for each entity.
- Repository interface(s) defining the data access contract.
- EF Core repository implementation(s) fulfilling those interfaces.
- EF Core migration(s) establishing the initial database schema.
- Connection string configuration entry in application settings.
- DI registrations for `DbContext` and repository implementations.

---

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Static store removed | Any code accessing static store directly will fail to compile | All call sites must be updated to depend on the injected repository interface |
| Data not pre-populated on startup | If the application relied on static initializers to seed data, that data will be absent | A database seed/migration step must be defined to populate required initial data |
| No in-process state sharing | Code that relied on cross-request state via static collections will behave differently | All state must be persisted to and read from the database within each request scope |
| Repository interface introduced | Callers must accept the interface via constructor injection | Update constructors and DI registrations; no change to business logic if separation is clean |
| Connection string required at startup | Application will fail to start without a valid connection string | Connection string must be present in environment configuration before deployment |
| Test setup changes | Tests that mutated static state directly will break | Tests must be updated to use EF Core in-memory provider or mocked repository interfaces |

---

## Acceptance Criteria

1. **Given** the application is started with a valid database connection string configured, **when** the application initialises, **then** it starts successfully without errors and the EF Core `DbContext` connects to the target database.

2. **Given** a record is created through the repository, **when** the application is restarted, **then** the record is retrievable from the repository without re-insertion.

3. **Given** the static in-memory store has been removed, **when** the solution is compiled, **then** there are zero compilation errors and zero remaining references to the removed static store types or fields.

4. **Given** a repository interface is defined for each entity type, **when** a consumer class is inspected, **then** it depends on the repository interface (not the concrete EF Core implementation) via constructor injection.

5. **Given** two concurrent write operations are submitted for the same entity, **when** both are processed, **then** neither operation silently overwrites the other without detection (i.e., optimistic concurrency or equivalent is enforced).

6. **Given** the application is deployed to a fresh environment with no existing database, **when** EF Core migrations are run, **then** the schema is created successfully and the application operates without manual schema intervention.

7. **Given** the test suite is executed, **when** tests run against the repository layer, **then** all tests pass and no test depends on or mutates shared static state.

8. **Given** a repository operation fails due to a database error, **when** the error occurs, **then** the exception is propagated to the caller without leaving the application in an inconsistent static state.

9. **Given** the application configuration is missing the database connection string, **when** the application attempts to start, **then** it fails with a clear, actionable error message identifying the missing configuration.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the target database provider (SQL Server, PostgreSQL, SQLite, etc.)? | TODO | TODO |
| 2 | What are the specific entity/model class names and their relationships that must be mapped? | TODO | TODO |
| 3 | Do repository interfaces already exist, or must they be defined as part of this work? | TODO | TODO |
| 4 | Is thread-safety currently enforced on the static store, and does that behaviour need to be preserved? | TODO | TODO |
| 5 | What is the strategy for initial data seeding (migrations, seed scripts, application startup)? | TODO | TODO |
| 6 | Are there existing integration or unit tests that directly manipulate the static store that must be migrated? | TODO | TODO |
| 7 | What EF Core version will be adopted, and is it compatible with the target runtime version? | TODO | TODO |
| 8 | Is optimistic concurrency required, and if so, which entities need concurrency tokens? | TODO | TODO |
| 9 | What environments (dev, staging, prod) will this change be deployed to, and is there a migration execution strategy per environment? | TODO | TODO |
| 10 | Are there any soft-delete, audit-trail, or row-level security requirements that must be reflected in the EF Core configuration? | TODO | TODO |