# Plan: Replace Static In-Memory Store with EF Core + SQLite/PostgreSQL Persistent Store

## Overview

**Migration Strategy: Strangler-Fig (Incremental Replacement)**

The static in-memory store will be replaced incrementally using a strangler-fig approach. A new persistence layer (EF Core + SQLite for development, PostgreSQL for production) will be introduced alongside the existing store, with the application progressively routing reads and writes through the new layer until the in-memory store can be safely removed.

**Justification:**
- The upgrade option is rated **moderate** effort and **medium** urgency, making a big-bang replacement unnecessarily risky.
- The strangler-fig pattern allows the new data layer to be validated in isolation before the in-memory store is decommissioned, reducing the blast radius of any regression.
- Feature-flag gating on the repository abstraction boundary provides a clean rollback path at each phase without requiring a full revert.

> **Note:** Because the tech analysis does not specify the runtime, language, build tool, or existing framework versions, several specifics below are marked **TODO** and must be confirmed before implementation begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Foundation | Introduce EF Core packages, define `DbContext`, create initial migration, wire up DI with environment-based connection strings (SQLite dev / PostgreSQL prod) | None | TODO — derive from confirmed person-days estimate |
| 2 — Repository Abstraction | Extract `IRepository<T>` interface (or equivalent) from current in-memory store; implement `EfRepository<T>` backed by EF Core; keep in-memory implementation active | Phase 1 complete | TODO |
| 3 — Feature-Flag Cutover | Introduce a feature flag / configuration key (`UseEfStore`) to route all reads and writes through `EfRepository<T>`; run both implementations in parallel for smoke validation | Phase 2 complete | TODO |
| 4 — In-Memory Store Removal | Remove static in-memory store class and all dead code paths; remove feature flag; make EF Core the sole implementation | Phase 3 validated | TODO |
| 5 — Hardening & Observability | Add migrations CI gate, connection-resilience policies, health checks, and performance baselines | Phase 4 complete | TODO |

> **TODO:** Populate effort (person-days) for each phase once the upgrade option detail is confirmed.

---

## Component Changes

### 1. Data Context (`AppDbContext` — new file)
- **What changes:** New `DbContext` subclass is created.
- **Files affected:** `AppDbContext.cs` (new), `Migrations/` directory (new, auto-generated).
- **APIs modified:** None — additive only.
- **Key details:**
  - Declare `DbSet<T>` properties for each entity currently held in the in-memory store.
  - Override `OnModelCreating` to apply entity configurations.
  - TODO: Confirm entity names from existing codebase.

### 2. In-Memory Store (existing — to be replaced)
- **What changes:** The static store class (TODO: confirm class name, e.g., `InMemoryStore`, `StaticDataStore`) is first hidden behind the `IRepository<T>` interface, then deleted in Phase 4.
- **Files affected:** TODO — identify the file(s) containing the static store.
- **APIs modified:** All direct callers of the static store must be updated to depend on `IRepository<T>` via constructor injection.

### 3. Repository Interface & Implementations (new)
- **What changes:** A new `IRepository<T>` interface is introduced with standard CRUD methods (e.g., `GetByIdAsync`, `GetAllAsync`, `AddAsync`, `UpdateAsync`, `DeleteAsync`).
- **Files affected:**
  - `IRepository.cs` (new interface)
  - `EfRepository.cs` (new EF Core implementation)
  - `InMemoryRepository.cs` (adapter wrapping existing static store — temporary, removed in Phase 4)
- **APIs modified:** All service/controller classes that currently reference the static store directly must be refactored to accept `IRepository<T>`.

### 4. Dependency Injection Registration (existing startup/composition root)
- **What changes:** Register `AppDbContext` with the appropriate connection string; register `IRepository<T>` → `EfRepository<T>` (or `InMemoryRepository<T>` when feature flag is off).
- **Files affected:** TODO — confirm DI registration file (e.g., `Program.cs`, `Startup.cs`, `ServiceCollectionExtensions.cs`).
- **APIs modified:** `IServiceCollection` extension or `builder.Services` call site.

### 5. Configuration / App Settings
- **What changes:** Add connection string entries and feature flag key.
- **Files affected:** `appsettings.json`, `appsettings.Development.json`, `appsettings.Production.json` (or equivalent).
- **Config keys added:**
  - `ConnectionStrings:DefaultConnection`
  - `FeatureFlags:UseEfStore` (boolean, removed after Phase 4)

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Microsoft.EntityFrameworkCore | Not present | TODO — confirm from tech analysis | N/A (new dep) | Add core EF package |
| Microsoft.EntityFrameworkCore.Sqlite | Not present | TODO | N/A (new dep) | Development / test database provider |
| Microsoft.EntityFrameworkCore.Design | Not present | TODO | N/A (new dep) | Required for `dotnet ef migrations` tooling |
| Npgsql.EntityFrameworkCore.PostgreSQL | Not present | TODO | N/A (new dep) | Production database provider |
| dotnet-ef (global tool) | Not present | TODO | N/A (new dep) | CLI tool for migration management |

> **TODO:** All target version numbers must be populated from the confirmed tech analysis. Do not source from training data.

---

## Infrastructure Changes

- **Database (SQLite):** No infrastructure change required for development; SQLite database file path must be set in `appsettings.Development.json` (e.g., `Data Source=app_dev.db`).
- **Database (PostgreSQL — production):** TODO — confirm whether a PostgreSQL instance is already provisioned, or whether a new one must be created (e.g., managed cloud service, Docker Compose service, Kubernetes StatefulSet).
- **Docker:** TODO — if a `Dockerfile` exists, confirm base image includes the .NET runtime compatible with the target EF Core version. Add `dotnet ef database update` or migration-on-startup logic.
- **Docker Compose:** TODO — if `docker-compose.yml` exists, add a `postgres` service with a named volume for data persistence.
- **Kubernetes:** TODO — if Kubernetes manifests exist, add a `Secret` for the connection string and reference it via `secretKeyRef` in the application `Deployment`. Confirm whether a migration init-container is needed.
- **CI/CD Pipeline:** TODO — confirm pipeline tooling (GitHub Actions, Azure DevOps, etc.). Add a step to run `dotnet ef migrations has-pending-model-changes` as a CI gate to catch unapplied migrations.
- **IaC:** TODO — not mentioned in context.

---

## Rollback Strategy

### Phase 1 Rollback — Foundation
1. Remove the EF Core NuGet package references from the project file.
2. Delete `AppDbContext.cs` and the `Migrations/` directory.
3. Remove connection string entries from all `appsettings*.json` files.
4. Restore the project to its prior state via version control (`git revert` or branch deletion).

### Phase 2 Rollback — Repository Abstraction
1. Revert all service/controller classes to reference the static in-memory store directly (restore prior call sites via `git revert`).
2. Delete `IRepository.cs`, `EfRepository.cs`, and `InMemoryRepository.cs`.
3. The static store remains untouched throughout this phase, so no data loss risk.

### Phase 3 Rollback — Feature-Flag Cutover
1. Set `FeatureFlags:UseEfStore` to `false` in configuration (or environment variable override) — this immediately routes all traffic back to the in-memory implementation without a deployment.
2. If a deployment is required, redeploy the previous artifact from the artifact registry.
3. Verify application behavior against the in-memory store before investigating the EF Core issue.

### Phase 4 Rollback — In-Memory Store Removal
1. This phase is **irreversible at runtime** once the static store code is deleted; rollback requires a code revert.
2. Use `git revert` to restore the static store class and the `InMemoryRepository` adapter.
3. Re-add the `FeatureFlags:UseEfStore` configuration key and set it to `false`.
4. Redeploy. **Note:** Any data written exclusively to the persistent store during Phase 4 will not be present in the in-memory store after rollback — communicate this risk to stakeholders before executing Phase 4.

### Phase 5 Rollback — Hardening
1. Individual hardening items (health checks, resilience policies) can be reverted independently via feature branches.
2. CI gate failures block merge; no production rollback required.

---

## Testing Strategy

### Unit Tests
- **Target:** Repository implementations in isolation.
- **Approach:** Use EF Core's `UseInMemoryDatabase` provider (or SQLite in-memory mode) to unit-test `EfRepository<T>` without a real database process.
- **Coverage target:** TODO — confirm project-wide coverage target. Recommended minimum: **80% line coverage** on all new repository and context classes.
- **Tools:** TODO — confirm test framework (xUnit, NUnit, MSTest).

### Integration Tests
- **Target:** `AppDbContext` + `EfRepository<T>` against a real SQLite file or a PostgreSQL test container.
- **Approach:** Use `Testcontainers` (PostgreSQL container) for integration tests that mirror production behavior. Each test class creates and tears down its own database via `context.Database.EnsureCreated()` / `EnsureDeleted()`.
- **Tools:** TODO — confirm if `Testcontainers` is already in use. Recommended: `Testcontainers.PostgreSql` NuGet package.
- **CI gate:** Integration tests must pass before merge to the main branch.

### Regression Tests
- **Target:** All existing API endpoints / service methods that previously relied on the in-memory store.
- **Approach:** Re-run the full existing test suite with the EF Core implementation active (`UseEfStore = true`) to confirm behavioral parity.
- **Tools:** TODO — confirm if an existing regression suite exists.
- **CI gate:** Zero regression failures required for Phase 3 cutover approval.

### Performance Tests
- **Target:** Read/write latency for the most frequently called repository methods.
- **Approach:** Establish a baseline with the in-memory store before Phase 3; compare against EF Core + SQLite (dev) and EF Core + PostgreSQL (prod) after cutover.
- **Tools:** TODO — confirm performance testing tooling (BenchmarkDotNet, k6, NBomber, etc.).
- **Acceptance criteria:** P99 latency for repository operations must not exceed TODO ms (to be defined by stakeholders).

### Migration CI Gate
- Add `dotnet ef migrations has-pending-model-changes` to the CI pipeline; fail the build if the model has diverged from the last migration.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| EF Core packages added, `AppDbContext` created, initial migration generated | Phase 1 | TODO | TODO |
| `IRepository<T>` interface and both implementations merged | Phase 2 | TODO | TODO |
| Feature flag wired; parallel-run validation complete | Phase 3 | TODO | TODO |
| Static in-memory store deleted; codebase clean | Phase 4 | TODO | TODO |
| Health checks, resilience, CI gate, performance baseline in place | Phase 5 | TODO | TODO |

> **TODO:** All estimated completion dates must be derived from the confirmed upgrade option person-days estimate and team capacity. Dates are intentionally left blank until that input is available.