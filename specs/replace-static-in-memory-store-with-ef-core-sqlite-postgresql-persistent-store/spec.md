# Spec: Replace Static In-Memory Store with EF Core + SQLite/PostgreSQL Persistent Store

## Summary

This spec covers the replacement of the application's current static in-memory data store with a persistent data layer backed by EF Core, supporting both SQLite (for development/testing) and PostgreSQL (for production). The expected outcome is that all data previously held in volatile in-process memory survives application restarts, supports concurrent access, and is queryable through a standard ORM abstraction, eliminating the current data-loss-on-restart behaviour.

---

## Motivation

- **Data durability:** The static in-memory store loses all data on every application restart or crash. This is a functional defect in any environment beyond a single-session demo.
- **Scalability:** An in-memory store cannot be shared across multiple application instances (e.g., horizontal scaling, load-balanced deployments). This is a hard architectural blocker for production readiness.
- **Concurrency correctness:** Static in-memory collections are not thread-safe by default and do not provide transaction semantics, creating risk of data corruption under concurrent load.
- **Upgrade urgency:** Rated **medium** — the application is functional for single-instance, non-persistent use cases today, but the limitation actively blocks production deployment and any multi-user scenario.
- **Tech debt:** Continued investment in features built on top of the in-memory store increases the future migration cost.

---

## Current State

> **Note:** Specific class names, config keys, and schema elements are not available in the provided context. Items marked **TODO** must be confirmed during discovery before implementation planning begins.

| Element | Description |
|---|---|
| Data store type | Static in-memory collection (e.g., static field or singleton dictionary/list) |
| Store class(es) | TODO — confirm exact class names holding static state |
| Repository / service interfaces | TODO — confirm interface names that abstract (or directly expose) the in-memory store |
| Data models / entities | TODO — confirm entity class names and their properties |
| Configuration keys | None currently required for the store (no connection string, no provider config) |
| Persistence behaviour | None — all data is lost on process exit |
| Transaction support | None |
| Concurrency handling | TODO — confirm whether any locking exists today |
| Test doubles / fakes | TODO — confirm whether tests depend directly on the static store |

---

## Proposed Changes

### Overview

The static in-memory store is removed and replaced with an EF Core `DbContext` backed by SQLite (development/test) or PostgreSQL (production). Repository or service classes that currently read/write the static store are updated to use the `DbContext`. Database schema is managed via EF Core migrations.

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Data store implementation | Static in-memory collection | EF Core `DbContext` with SQLite or PostgreSQL provider | Y |
| Entity/model classes | Plain in-memory objects (no persistence annotations) | EF Core entity classes with key and relationship configuration | Y |
| Repository / service layer | Reads/writes static field directly | Reads/writes via EF Core `DbContext` or repository abstraction over it | Y |
| Configuration | No connection string or provider config | Connection string and provider selection required in application configuration | Y |
| Database schema | None (no schema exists) | Schema created and versioned via EF Core migrations | N (additive) |
| Dependency registration | Static store instantiated at class load time | `DbContext` registered in DI container with appropriate lifetime (scoped) | Y |
| Development environment | No setup required | SQLite database file used; no external service required | N |
| Production environment | No setup required | PostgreSQL instance required; connection string must be supplied | Y |
| Test setup | Tests may rely on static state between runs | Tests use an isolated SQLite in-memory database or test-scoped context; static state dependency removed | Y |

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Static store removed | Any code referencing the static field or class directly will fail to compile | All callers must be updated to use the new repository/service interface backed by EF Core |
| Entity classes gain persistence annotations or `IEntityTypeConfiguration` | Serialization or reflection-based code depending on plain model shape may break | TODO — audit all serialization and reflection usages of entity classes |
| DI lifetime change (static → scoped) | Code that resolves the store outside of a DI scope (e.g., background threads, static helpers) will fail at runtime | All store access must occur within a valid DI scope; static/singleton consumers must be refactored |
| Connection string now required at startup | Application will not start without valid database configuration | Connection string must be added to environment-specific configuration before deployment |
| PostgreSQL external dependency in production | Production deployments require a running PostgreSQL instance | Infrastructure provisioning and connection string management must be addressed before production rollout |
| Test isolation broken if tests shared static state | Tests that relied on a clean static store per test may now interfere with each other | Test suite must be updated to reset or recreate the database context between tests |
| Data from existing in-memory store is not migrated | All data currently in memory is ephemeral and will be lost on the next restart regardless | No data migration is required; document that existing runtime data is not preserved |

---

## Acceptance Criteria

1. **Given** the application is started for the first time with a valid connection string, **when** the application initialises, **then** the database schema is created automatically (or migrations are applied) without manual intervention, and the application reaches a healthy state.

2. **Given** one or more records have been written to the store, **when** the application process is stopped and restarted, **then** all previously written records are retrievable and their field values are identical to what was written.

3. **Given** the application is configured with a SQLite connection string, **when** the application runs, **then** all read and write operations complete successfully against the SQLite database without requiring an external database service.

4. **Given** the application is configured with a PostgreSQL connection string, **when** the application runs, **then** all read and write operations complete successfully against the PostgreSQL database.

5. **Given** two concurrent requests attempt to write to the store simultaneously, **when** both writes are processed, **then** both records are persisted correctly with no data corruption or lost update.

6. **Given** no connection string is provided in configuration, **when** the application attempts to start, **then** the application fails at startup with a clear, actionable error message indicating the missing configuration — it does not start in a degraded or data-loss state.

7. **Given** the full test suite is executed, **when** each test runs, **then** no test depends on or pollutes static in-memory state from another test, and all tests that exercise data persistence use an isolated database context.

8. **Given** the application has been running and data has been written, **when** a new EF Core migration is applied, **then** existing data is preserved and the schema is updated without data loss.

9. **Given** the static in-memory store class previously existed, **when** the codebase is compiled after this change, **then** there are zero remaining references to the removed static store — confirmed by a CI build with no compile errors or warnings related to the removed type.

10. **Given** the application is running under a load test with multiple concurrent users, **when** read and write operations are performed, **then** response times for store operations do not regress by more than TODO% compared to the in-memory baseline (acceptable regression threshold to be agreed by the team).

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What are the exact class names of the static in-memory store and all direct consumers? | TODO | TODO |
| 2 | What entity types and their properties need to be persisted? Are there relationships (one-to-many, many-to-many)? | TODO | TODO |
| 3 | Is there an existing repository or service interface abstraction, or does the static store get accessed directly throughout the codebase? | TODO | TODO |
| 4 | What is the target EF Core version to adopt? | TODO | TODO |
| 5 | Is SQLite acceptable for production in any deployment scenario, or is it strictly a dev/test provider? | TODO | TODO |
| 6 | Who is responsible for provisioning and managing the PostgreSQL instance in production? | TODO | TODO |
| 7 | How will the database connection string be supplied in production (environment variable, secrets manager, config file)? | TODO | TODO |
| 8 | Are there existing tests that depend on the static store's state? If so, how many and how tightly coupled are they? | TODO | TODO |
| 9 | Is there any existing data in the in-memory store that must be seeded into the new database as initial/reference data? | TODO | TODO |
| 10 | What is the acceptable performance regression threshold for store operations under load (referenced in Acceptance Criterion 10)? | TODO | TODO |
| 11 | Does the application run as multiple instances today or is it strictly single-instance? This affects urgency of the concurrency requirement. | TODO | TODO |