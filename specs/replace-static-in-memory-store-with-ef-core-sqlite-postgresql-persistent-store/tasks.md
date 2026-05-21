# TASKS: Replace Static In-Memory Store with EF Core + SQLite/PostgreSQL Persistent Store

> **Scope:** Introduce EF Core as the ORM layer, replace all static in-memory collections with a database-backed persistent store, and wire up SQLite (development) and PostgreSQL (production) providers.
> **Note:** Tech analysis did not supply specific file names, runtime version, or build tool details. Task names below use the most common .NET/EF Core conventions; update paths to match actual project structure during kickoff.

---

## Prerequisites

- [ ] [XS] Confirm target .NET SDK version (minimum .NET 6 required for EF Core 7/8) and record it in a `DECISIONS.md` file at the repo root
- [ ] [XS] Confirm database targets: SQLite for local development and PostgreSQL for staging/production, and record connection-string environment variable names (`ConnectionStrings__DefaultConnection`) in `DECISIONS.md`
- [ ] [XS] Verify developer machines and CI runners have `dotnet ef` CLI tools installable (`dotnet tool install --global dotnet-ef`) and document the required version in `DECISIONS.md`
- [ ] [XS] Confirm PostgreSQL instance (or Docker Compose service) is available for integration testing and record the connection details in `.env.example`

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch `feature/ef-core-persistent-store` from `main` and push it to the remote
- [ ] [S] Audit all usages of the static in-memory store (e.g., `static List<T>`, `static Dictionary<K,V>`, or equivalent singleton collections) across the codebase and produce a written inventory in `DECISIONS.md` listing every class, property, and method that reads or writes the store
- [ ] [XS] Capture the current test suite pass/fail baseline by running the full test suite and saving output to `docs/test-baseline-before.txt`
- [ ] [XS] Add a CI branch protection rule (or update the existing pipeline config) to require all tests to pass on `feature/ef-core-persistent-store` before merge — update the relevant pipeline file (e.g., `.github/workflows/ci.yml`, `azure-pipelines.yml`, or `Jenkinsfile`)

---

## Phase 2 — Core Upgrade

- [ ] [S] Add EF Core NuGet packages to the project file: `Microsoft.EntityFrameworkCore`, `Microsoft.EntityFrameworkCore.Sqlite`, and `Npgsql.EntityFrameworkCore.PostgreSQL` — pin all three to the same major version consistent with the confirmed .NET SDK
- [ ] [S] Add EF Core design-time tooling package `Microsoft.EntityFrameworkCore.Design` to the project file (as a development/tools dependency) to enable `dotnet ef` migrations
- [ ] [M] Create `AppDbContext` class (e.g., in `Data/AppDbContext.cs`) inheriting `DbContext`, with one `DbSet<T>` property per entity currently held in the static store, and configure the schema via `OnModelCreating` using Fluent API
- [ ] [S] Define entity classes (e.g., in `Data/Entities/`) for each type currently stored in the static collection, adding primary-key properties and any required navigation properties identified in the Phase 1 inventory
- [ ] [S] Register `AppDbContext` in the DI container in `Program.cs` (or `Startup.cs`), reading the provider from an environment variable or config key (`Database__Provider`: `sqlite` | `postgres`) and the connection string from `ConnectionStrings__DefaultConnection`
- [ ] [S] Add `appsettings.Development.json` entry for SQLite connection string (`Data Source=app_dev.db`) and `appsettings.Production.json` placeholder for PostgreSQL connection string (value sourced from environment variable)
- [ ] [M] Create the initial EF Core migration by running `dotnet ef migrations add InitialCreate --output-dir Data/Migrations` and review the generated migration files for correctness against the entity definitions
- [ ] [L] Replace the static in-memory store read/write operations with EF Core repository or direct `AppDbContext` calls — update every class identified in the Phase 1 inventory, ensuring all queries are async (`ToListAsync`, `FindAsync`, `SaveChangesAsync`, etc.)
- [ ] [S] Delete (or archive to `_legacy/`) the static store class(es) and any initializer code that seeded the in-memory collection, confirming no remaining references compile
- [ ] [S] Add a database seeder class (e.g., `Data/DbSeeder.cs`) to replicate any hardcoded seed data previously in the static store, and invoke it from `Program.cs` on application startup in the `Development` environment only

---

## Phase 3 — Testing & Validation

- [ ] [M] Update existing unit tests that depended on the static store to use EF Core's `UseInMemoryDatabase` provider (via `Microsoft.EntityFrameworkCore.InMemory` package) or SQLite in-memory mode, replacing any direct static-collection setup/teardown
- [ ] [M] Write integration tests (e.g., in a new `Tests/Integration/` folder) that spin up a real SQLite database, apply migrations via `dbContext.Database.MigrateAsync()`, exercise all CRUD paths, and assert persistence across context instances
- [ ] [S] Run the full test suite and save output to `docs/test-baseline-after.txt`; diff against `docs/test-baseline-before.txt` and resolve any regressions before proceeding
- [ ] [XS] Verify `dotnet ef database update` applies the `InitialCreate` migration cleanly against a local SQLite file and a local PostgreSQL instance, and document the result in `DECISIONS.md`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline file (`.github/workflows/ci.yml` or equivalent) to run `dotnet ef database update` against a SQLite test database before executing the test step, using the `ConnectionStrings__DefaultConnection` environment variable
- [ ] [S] Add a PostgreSQL service container (or Docker Compose service definition in `docker-compose.yml`) to the CI pipeline for integration-test runs, and set the `ConnectionStrings__DefaultConnection` secret/env var to point to it
- [ ] [XS] Add `app_dev.db` and `*.db-shm` / `*.db-wal` SQLite file patterns to `.gitignore` to prevent local database files from being committed
- [ ] [S] Update `docker-compose.yml` (if present) to add a `postgres` service with a named volume for persistent storage, and update the application service's environment block with `ConnectionStrings__DefaultConnection` and `Database__Provider=postgres`

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CHANGELOG.md` with a new entry describing the replacement of the static in-memory store with EF Core + SQLite/PostgreSQL, listing breaking changes (e.g., data is no longer reset on restart) and migration steps for existing deployments
- [ ] [XS] Update `README.md` to document the new local setup steps: installing `dotnet-ef` tools, setting the connection string, and running `dotnet ef database update`
- [ ] [S] Write or update the deployment runbook (e.g., `docs/runbook.md`) with instructions for: applying EF Core migrations on first deploy (`dotnet ef database update` or `MigrateAsync` on startup), rolling back a migration (`dotnet ef migrations remove`), and backing up the PostgreSQL database before future migrations
- [ ] [XS] Confirm with the team whether `Database.MigrateAsync()` should run automatically on startup in production (acceptable for this scale) or be a manual step, and record the decision in `DECISIONS.md`
- [ ] [S] Perform a staged rollout: deploy to a staging environment, verify the migration applies cleanly, run smoke tests against all endpoints that previously used the static store, and sign off before merging to `main`

---

> **Open Questions to Resolve at Kickoff**
> 1. What is the exact .NET SDK and EF Core version to target?
> 2. Are there multiple projects in the solution that share the static store, or is it confined to one project?
> 3. Is there existing data in the static store that needs a one-time migration/export, or is it ephemeral by design?
> 4. Should the repository pattern be introduced as an abstraction over `AppDbContext`, or is direct context injection acceptable?