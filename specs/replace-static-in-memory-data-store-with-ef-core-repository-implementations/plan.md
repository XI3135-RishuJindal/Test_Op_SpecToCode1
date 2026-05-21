# PLAN: Replace Static In-Memory Data Store with EF Core Repository Implementations

---

## Overview

**Migration Strategy: Strangler-Fig (Incremental Replacement)**

The static in-memory data store will be replaced incrementally using a strangler-fig approach. Each repository implementation is replaced one at a time behind a shared interface contract, allowing the application to remain functional throughout the migration. New EF Core-backed repository implementations are introduced alongside existing static stores, then swapped in via dependency injection registration.

**Justification:**
- The upgrade option is rated **moderate** effort and **medium** urgency, making a big-bang replacement unnecessarily risky.
- Static in-memory stores are typically scattered across multiple classes; incremental replacement reduces the blast radius of any single change.
- Interface-backed repositories (assumed from standard repository pattern) allow parallel implementations without modifying consuming code.
- Rollback per repository is independently achievable by reverting the DI registration for that specific type.

> **TODO:** Confirm whether existing repository interfaces (e.g., `IRepository<T>`, `IUserRepository`, etc.) are already defined or need to be introduced as part of this effort.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & Interface Extraction — Identify all static in-memory stores; extract or confirm repository interfaces for each | None | TODO: derive from option person-days |
| 2 | EF Core Setup — Add EF Core packages, define `DbContext`, configure connection string, create initial migrations | Phase 1 complete | TODO: derive from option person-days |
| 3 | Repository Implementation — Implement EF Core-backed repository classes for each identified store | Phase 2 complete | TODO: derive from option person-days |
| 4 | DI Wiring & Swap — Replace static store registrations with EF Core implementations in the DI container | Phase 3 complete | TODO: derive from option person-days |
| 5 | Data Seeding — Migrate any seed/fixture data from static stores into EF Core seed configuration or migration seeds | Phase 4 complete | TODO: derive from option person-days |
| 6 | Validation & Cleanup — Integration testing, remove static store classes, finalize | Phases 1–5 complete | TODO: derive from option person-days |

> **TODO:** Populate effort column once person-days estimate is provided from the upgrade option.

---

## Component Changes

### Static In-Memory Store Classes
- **What changes:** Static classes or singleton objects holding in-memory collections (e.g., `List<T>`, `Dictionary<K,V>` fields) are removed.
- **Files affected:** TODO — identify all files containing static collection fields used as data stores (e.g., `*Store.cs`, `*Repository.cs`, `*Data.cs`).
- **APIs modified:** Any `static` method signatures on store classes become instance methods on the new EF Core repository implementations.

### Repository Interfaces
- **What changes:** If not already present, introduce `IRepository<T>` or domain-specific interfaces (e.g., `IOrderRepository`, `IProductRepository`).
- **Files affected:** TODO — confirm existing interface files or create new ones under a `Repositories/` or `Abstractions/` folder.
- **APIs modified:** Interface methods must match the existing static method signatures to avoid changes in consuming code (e.g., `GetById(int id)`, `GetAll()`, `Add(T entity)`, `Update(T entity)`, `Delete(int id)`).

### EF Core DbContext
- **What changes:** A new `AppDbContext` (or equivalent) class is introduced, inheriting from `Microsoft.EntityFrameworkCore.DbContext`.
- **Files affected:** New file — `AppDbContext.cs` (or TODO: confirm naming convention from existing codebase).
- **APIs modified:** `DbSet<T>` properties added per entity; `OnModelCreating` configured for entity mappings and seed data.

### EF Core Repository Implementations
- **What changes:** New concrete classes implementing repository interfaces, using `AppDbContext` for all data access.
- **Files affected:** New files per entity — e.g., `EfOrderRepository.cs`, `EfProductRepository.cs` (TODO: confirm entity names from codebase).
- **APIs modified:** All CRUD operations delegate to `DbContext.Set<T>()` or typed `DbSet<T>` properties.

### Dependency Injection Registration
- **What changes:** DI container registrations updated to bind interfaces to EF Core implementations instead of static stores.
- **Files affected:** `Program.cs`, `Startup.cs`, or equivalent composition root file (TODO: confirm file name).
- **APIs modified:** `services.AddSingleton<IXRepository, StaticXStore>()` replaced with `services.AddScoped<IXRepository, EfXRepository>()`. Lifetime changes from singleton to scoped are expected and must be verified for thread-safety implications.

### Configuration
- **What changes:** Database connection string added to application configuration.
- **Files affected:** `appsettings.json`, `appsettings.Development.json`; environment-specific overrides (TODO: confirm config structure).
- **APIs modified:** `builder.Configuration.GetConnectionString("DefaultConnection")` wired into `DbContext` options.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Microsoft.EntityFrameworkCore | Not present | TODO | N/A — new dependency | Add core EF Core package |
| Microsoft.EntityFrameworkCore.SqlServer / Sqlite / Npgsql | Not present | TODO | N/A — new dependency | Choose provider based on target database (TODO: confirm DB engine) |
| Microsoft.EntityFrameworkCore.Tools | Not present | TODO | N/A — new dependency | Required for `dotnet ef migrations` CLI tooling |
| Microsoft.EntityFrameworkCore.Design | Not present | TODO | N/A — new dependency | Required at design time for migration generation |

> **TODO:** All version numbers must be confirmed from the tech analysis once runtime and framework versions are provided. Do not assume versions from training data.

> **TODO:** Confirm target database engine (SQL Server, PostgreSQL, SQLite, etc.) to select the correct EF Core provider package.

---

## Infrastructure Changes

> **TODO:** No infrastructure context was provided. The following items require confirmation before implementation:

- **Database server:** TODO — confirm whether a database server (SQL Server, PostgreSQL, etc.) is provisioned or needs to be added to the environment.
- **Docker:** TODO — if the application runs in Docker, confirm whether a database container (e.g., `mcr.microsoft.com/mssql/server`, `postgres`) needs to be added to `docker-compose.yml`.
- **Connection strings in CI/CD:** TODO — confirm how connection strings are injected in CI pipelines (secrets manager, environment variables, pipeline variables).
- **Migration execution:** TODO — confirm whether EF Core migrations run at application startup (`context.Database.Migrate()`) or as a separate CI/CD step (`dotnet ef database update`).
- **Kubernetes:** TODO — not mentioned in context; confirm if applicable.
- **IaC:** TODO — not mentioned in context; confirm if applicable.

---

## Rollback Strategy

### Phase 1 Rollback (Audit & Interface Extraction)
- No runtime behavior changes occur in this phase.
- Revert: Delete any newly created interface files; no DI or runtime changes to undo.

### Phase 2 Rollback (EF Core Setup)
- Remove added NuGet package references from the project file.
- Delete `AppDbContext.cs` and any generated `Migrations/` folder.
- Revert `appsettings.json` connection string additions.
- No consuming code has changed; application continues using static stores.

### Phase 3 Rollback (Repository Implementation)
- Delete newly created EF Core repository implementation files (e.g., `EfXRepository.cs`).
- DI registrations have not yet been swapped; static stores remain active.
- No impact to running application.

### Phase 4 Rollback (DI Wiring & Swap) — **Highest Risk Phase**
- Revert DI registration changes in `Program.cs` / `Startup.cs` to re-bind interfaces to static store implementations.
- This is the single actionable step required to restore prior behavior immediately.
- Each repository can be rolled back independently — revert one binding at a time if partial rollback is needed.

### Phase 5 Rollback (Data Seeding)
- Remove seed data from `OnModelCreating` or migration seed files.
- Roll back the associated EF Core migration: `dotnet ef migrations remove`.

### Phase 6 Rollback (Cleanup)
- If static store classes have been deleted, restore from version control (`git revert` or `git checkout <commit> -- <file>`).
- Re-register static store in DI container.

---

## Testing Strategy

### Unit Tests
- **Target:** Each EF Core repository implementation tested against an in-memory EF Core provider (`UseInMemoryDatabase`) or SQLite in-memory mode.
- **Coverage target:** TODO — confirm project coverage baseline; recommended minimum 80% on new repository classes.
- **Tools:** TODO — confirm test framework (xUnit, NUnit, MSTest assumed for .NET; confirm from codebase).
- **Key cases:** `GetById` with existing and missing IDs, `GetAll` with empty and populated sets, `Add`/`Update`/`Delete` with valid and invalid inputs.

### Integration Tests
- **Target:** Repository implementations tested against a real database instance (e.g., SQL Server LocalDB, PostgreSQL test container via Testcontainers).
- **Tools:** TODO — confirm if Testcontainers or a dedicated test database is available.
- **Key cases:** Full CRUD lifecycle per entity, transaction rollback behavior, concurrent access.

### Regression Tests
- **Target:** All existing application behaviors that previously relied on static stores must produce identical outputs after the swap.
- **Approach:** Run existing test suite in full after each Phase 4 DI swap for a given repository.
- **CI gate:** Full regression suite must pass before merging any Phase 4 PR.

### Performance Tests
- **Target:** Confirm that EF Core query performance is acceptable relative to in-memory store baselines.
- **Tools:** TODO — confirm if BenchmarkDotNet or load testing tools (k6, NBomber) are in use.
- **Key concern:** N+1 query patterns; ensure `Include()` / `AsNoTracking()` are used appropriately in read-heavy paths.

### CI Gates
- TODO: Confirm CI platform (GitHub Actions, Azure DevOps, Jenkins, etc.).
- Recommended gates: unit tests pass → integration tests pass → coverage threshold met → no EF Core migration conflicts detected (`dotnet ef migrations has-pending-model-changes`).

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| All static stores identified; interfaces confirmed or created | Phase 1 | TODO | TODO |
| EF Core packages added; `DbContext` defined; initial migration generated | Phase 2 | TODO | TODO |
| All EF Core repository implementations written and unit tested | Phase 3 | TODO | TODO |
| DI registrations swapped; regression suite passing | Phase 4 | TODO | TODO |
| Seed data migrated; data seeding verified in dev environment | Phase 5 | TODO | TODO |
| Static store classes removed; all tests passing; PR merged | Phase 6 | TODO | TODO |

> **TODO:** Populate all estimated completion dates once person-days are confirmed from the upgrade option and team capacity is known.

> **TODO:** Assign owners once team structure is confirmed.