# CONSTITUTION
## Project: Replace Static In-Memory Data Store with EF Core Repository Implementations

---

## Project Identity

**Name:** EF Core Repository Migration
**Purpose:** Replace all static in-memory data storage with Entity Framework Core repository implementations backed by a persistent database.
**High-Level Goal:** Eliminate the static in-memory data store, introduce a proper EF Core `DbContext` and repository layer, and ensure all data access flows through typed repository interfaces — improving persistence, testability, and maintainability.

---

## Guiding Principles

1. **Prefer repository interfaces over direct `DbContext` access** because callers must remain decoupled from the persistence mechanism to preserve testability and allow future store changes.
2. **Prefer explicit EF Core migrations over manual schema scripts** because tracked migrations are the only reliable way to keep the database schema in sync with the model across environments.
3. **Prefer dependency-injected repositories over static or singleton data holders** because the existing static store is the root cause of the tech debt being addressed; any new static access pattern reintroduces the same problem.
4. **Prefer in-memory EF Core provider (or SQLite in-memory) for unit tests over mocking `DbContext` directly** because this reduces brittle test setup while still exercising LINQ query translation.
5. **Prefer incremental, interface-compatible replacement over a big-bang rewrite** because the moderate effort ceiling requires risk to be contained — existing consumers of the data store should require minimal changes.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is limited to replacing the in-memory store and introducing the EF Core repository layer. No additional feature work is in scope.
- **Technology mandate:** Entity Framework Core must be used as the ORM. No alternative ORMs (Dapper, NHibernate, etc.) are in scope for this task.
- **Scope freeze:** Database engine selection (SQL Server, PostgreSQL, SQLite, etc.) must be confirmed before implementation begins. TODO: confirm target database provider with project stakeholders.
- **Runtime/Language:** TODO — runtime and language versions are unspecified in the tech analysis. Confirm minimum EF Core-compatible runtime (e.g., .NET 6+) before work starts.
- **No breaking changes to public contracts:** Repository interfaces exposed to the rest of the application must preserve existing method signatures where they exist, or introduce new interfaces that existing consumers can adopt without restructuring call sites.

---

## Quality Standards

- **Test coverage:** All repository implementations must have integration tests covering at minimum: Create, Read, Update, Delete operations. Coverage floor for the new repository layer: **80% line coverage**.
- **Code review:** Every pull request touching `DbContext`, repository implementations, or migration files requires at least **one peer review approval** before merge.
- **Migration hygiene:** Every schema change must be accompanied by a named EF Core migration file committed to source control. No `EnsureCreated()` calls in production code paths.
- **Deployment gate:** The application must start successfully and all existing smoke/integration tests must pass against the new repository layer before the static store is removed from the codebase.
- **Documentation:** A brief data-access README must be added (or updated) describing the `DbContext`, registered repositories, and how to run/apply migrations locally.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt EF Core as the ORM for the repository layer | Directly specified by the modernization task; addresses the static in-memory store tech debt | Accepted |
| ADR-002 | Introduce repository interfaces as the abstraction boundary | Decouples consumers from EF Core internals; enables test doubles without mocking `DbContext` | Accepted |
| ADR-003 | Use EF Core migrations for all schema management | Ensures reproducible, version-controlled schema evolution across all environments | Accepted |
| ADR-004 | Target database provider TBD | Runtime and infrastructure details absent from tech analysis | **TODO — Proposed** |
| ADR-005 | Static in-memory store to be deleted only after all consumers are migrated and tests pass | Reduces risk of regression during incremental rollout | Accepted |