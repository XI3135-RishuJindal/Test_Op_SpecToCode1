# TASKS: Replace Static In-Memory Data Store with EF Core Repository Implementations

> **Scope:** Migrate from static in-memory data store to EF Core-backed repository implementations.
> **Urgency:** Medium
> **Note:** Language, runtime, and build tool were not specified in the tech analysis. Task descriptions assume a .NET/C# project (the natural target for EF Core). Adjust file paths and tooling references to match your actual project structure.

---

## Prerequisites

- [ ] [XS] Confirm .NET SDK version installed locally matches the project's `global.json` or target framework moniker in the `.csproj` file
- [ ] [XS] Verify EF Core NuGet packages (`Microsoft.EntityFrameworkCore`, provider package, and `Microsoft.EntityFrameworkCore.Tools`) are available in the package feed used by the project
- [ ] [XS] Confirm a target database engine (e.g., SQL Server, PostgreSQL, SQLite) has been selected and a connection string is available for local development and CI environments
- [ ] [XS] Ensure the executing identity (local dev and CI service account) has DDL permissions on the target database schema
- [ ] [XS] Create a feature branch (e.g., `feature/efcore-repository-migration`) from the main integration branch before beginning any code changes

---

## Phase 1 — Preparation

- [ ] [S] Audit all usages of the static in-memory data store across the codebase — identify every class, method, and file that reads from or writes to the static store, and produce a migration hit-list
- [ ] [S] Document the current data shapes (fields, types, relationships) held in the static store to serve as the schema source of truth for EF Core entity design
- [ ] [XS] Capture the current passing test suite as a baseline — record test count, pass rate, and any skipped tests in `docs/migration-baseline.md`
- [ ] [XS] Add or confirm a `DbContext` NuGet package reference (`Microsoft.EntityFrameworkCore` + chosen provider) in the project `.csproj` file without removing the existing static store yet
- [ ] [XS] Configure a `ConnectionStrings:Default` entry in `appsettings.Development.json` and a corresponding placeholder in `appsettings.json` (no secrets in source control)

---

## Phase 2 — Core Upgrade

- [ ] [M] Define EF Core entity classes that mirror the data shapes documented in Phase 1 — create one file per aggregate root under `Data/Entities/` (e.g., `Data/Entities/ProductEntity.cs`)
- [ ] [M] Create the `AppDbContext` class in `Data/AppDbContext.cs` — register all entity `DbSet<T>` properties and apply any required `OnModelCreating` configurations (keys, indexes, relationships)
- [ ] [S] Register `AppDbContext` in the DI container in `Program.cs` (or `Startup.cs`) using `AddDbContext<AppDbContext>` with the connection string from `IConfiguration`
- [ ] [M] Define repository interfaces (e.g., `IProductRepository`) in `Abstractions/` that match the read/write contract currently fulfilled by the static store
- [ ] [M] Implement each repository interface as an EF Core-backed class (e.g., `Data/Repositories/ProductRepository.cs`) using injected `AppDbContext` — cover all CRUD operations present in the static store
- [ ] [S] Register all repository implementations in the DI container in `Program.cs` (or `Startup.cs`), replacing any direct registrations of the static store
- [ ] [S] Replace every injection or direct reference to the static in-memory store in service/controller classes with the corresponding repository interface — update constructor signatures and call sites
- [ ] [S] Add an EF Core initial migration using `dotnet ef migrations add InitialSchema` — review the generated migration file in `Data/Migrations/` for correctness against the documented schema
- [ ] [XS] Remove the static in-memory data store class(es) from the codebase once all references have been replaced and the build is green
- [ ] [S] Seed reference/test data via an `IHostedService` or `DbContext.Database.EnsureCreated()` call in the development environment to replace any static seed data previously held in the in-memory store

---

## Phase 3 — Testing & Validation

- [ ] [M] Update existing unit tests that depended on the static store — replace static store setup with EF Core `InMemoryDatabase` provider or a mock of the repository interface, one test class at a time
- [ ] [S] Write integration tests for each repository implementation using EF Core `InMemoryDatabase` or a local SQLite database — cover Create, Read, Update, and Delete paths for every entity
- [ ] [S] Run the full test suite and compare results against the baseline captured in `docs/migration-baseline.md` — all previously passing tests must continue to pass
- [ ] [XS] Verify no residual references to the removed static store exist by running a solution-wide search and confirming zero results
- [ ] [XS] Perform a manual smoke test against the local development database — exercise each data-access path end-to-end and confirm data persists across application restarts

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration to provision a database service (e.g., a SQL Server or PostgreSQL container) and inject the `ConnectionStrings:Default` value as a CI environment secret/variable
- [ ] [S] Add an EF Core migration apply step (`dotnet ef database update`) to the CI pipeline so the schema is always current before integration tests run
- [ ] [XS] Confirm the CI pipeline runs the full test suite (unit + integration) and fails the build on any test failure

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CHANGELOG.md` with an entry describing the replacement of the static in-memory store with EF Core repositories, listing affected modules
- [ ] [S] Update or create a developer setup runbook in `docs/dev-setup.md` — document the required database setup steps, migration commands (`dotnet ef migrations add`, `dotnet ef database update`), and connection string configuration
- [ ] [XS] Communicate the breaking change (removal of static store, new DB dependency) to all team members and confirm no parallel branches still depend on the removed static store
- [ ] [XS] Monitor application logs and database error rates for 48 hours after deployment to the first non-production environment — confirm no unexpected query errors or missing-migration issues