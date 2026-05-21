# PLAN: Author and Apply Initial EF Core Migration Scripts

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental**

This plan covers the authoring and application of initial Entity Framework Core migration scripts for the target codebase. Given that the tech analysis does not specify a runtime, language version, or existing ORM baseline, the approach is conservative and incremental: migrations are authored, reviewed, and applied in a controlled sequence with explicit rollback points at each step.

Because the upgrade urgency is rated **medium** and the effort option is **moderate**, a big-bang schema cutover is avoided. Instead, migrations are gated behind a review checkpoint before being applied to any shared or production environment. This minimizes risk from schema drift or data loss on first application.

> **Note:** Several infrastructure and dependency details are absent from the provided context. These are marked as **TODO** throughout this document and must be resolved before execution begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit existing schema and domain models; confirm DbContext configuration | Access to codebase and existing DB schema (if any) | TODO (derive from moderate estimate once person-days are confirmed) |
| 2 | Author initial EF Core migration scripts (`InitialCreate` or equivalent) | Phase 1 complete; EF Core tooling installed | TODO |
| 3 | Review and validate generated migration scripts (Up/Down methods, SQL output) | Phase 2 complete; peer review process | TODO |
| 4 | Apply migrations to development environment; verify schema | Phase 3 sign-off; dev DB access | TODO |
| 5 | Apply migrations to staging/pre-production environment | Phase 4 verified; CI/CD pipeline access | TODO |
| 6 | Apply migrations to production environment | Phase 5 verified; change-approval gate | TODO |

> **TODO:** Populate effort column (person-days per phase) once the "moderate" upgrade option details are confirmed.

---

## Component Changes

### DbContext

- **What changes:** A `DbContext`-derived class must exist (or be created) with `DbSet<T>` properties for each entity. The `OnModelCreating` method should encode all Fluent API configurations.
- **Files affected:** TODO — specific file paths not available from context. Likely `*DbContext.cs` or `ApplicationDbContext.cs`.
- **APIs modified:** `DbContext.OnModelCreating(ModelBuilder)`, `DbContext.OnConfiguring(DbContextOptionsBuilder)` (if connection string is configured here).

### Migration Files

- **What changes:** EF Core tooling (`dotnet ef migrations add`) generates:
  - `Migrations/<timestamp>_InitialCreate.cs` — contains `Up()` and `Down()` methods.
  - `Migrations/<timestamp>_InitialCreate.Designer.cs` — snapshot metadata.
  - `Migrations/ApplicationDbContextModelSnapshot.cs` — cumulative model snapshot.
- **Files affected:** All files under the `Migrations/` directory (new, generated).
- **APIs modified:** N/A — generated code; not hand-authored except for corrections.

### Program / Startup (Migration Application)

- **What changes:** If migrations are applied at startup, `app.Services.GetRequiredService<ApplicationDbContext>().Database.Migrate()` (or equivalent) must be present. Alternatively, migrations are applied via CLI only.
- **Files affected:** TODO — `Program.cs`, `Startup.cs`, or a dedicated migration runner, depending on project structure.
- **APIs modified:** `IHost.MigrateDbContext<TContext>()` (if using extension pattern) or `DatabaseFacade.Migrate()`.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Microsoft.EntityFrameworkCore | TODO | TODO | TODO | Version numbers not provided in tech analysis — **TODO: confirm target EF Core version** |
| Microsoft.EntityFrameworkCore.SqlServer / Npgsql / Sqlite (provider) | TODO | TODO | TODO | Provider must match target database — **TODO: confirm DB provider** |
| Microsoft.EntityFrameworkCore.Tools | TODO | TODO | N/A (tooling only) | Required for `dotnet ef migrations add` CLI commands |
| Microsoft.EntityFrameworkCore.Design | TODO | TODO | N/A (design-time only) | Required as a dev dependency for migration generation |

> **Note:** All version numbers are marked TODO because the tech analysis explicitly states the language, runtime, and framework versions are unknown. Do **not** assume versions — resolve from the actual `.csproj` or `packages.config` before proceeding.

---

## Infrastructure Changes

- **Database:** TODO — target database engine (SQL Server, PostgreSQL, SQLite, etc.) is not specified in context. Connection string configuration location is unknown.
- **Docker base image:** TODO — not mentioned in context.
- **Kubernetes manifests:** TODO — not mentioned in context. If migrations are applied as a Kubernetes init container or Job, a manifest change will be required.
- **CI/CD pipeline:** TODO — pipeline tooling not specified. At minimum, a CI step should run `dotnet ef migrations script --idempotent` to generate and artifact the SQL script for audit. A gate should prevent deployment if migration script generation fails.
- **IaC:** TODO — not mentioned in context.

---

## Rollback Strategy

### Phase 1 (Audit) — Rollback
- No changes applied. Discard any draft notes. No action required.

### Phase 2 (Author Migrations) — Rollback
- Run `dotnet ef migrations remove` to delete the generated migration files before any `database update` has been executed.
- Delete `Migrations/` directory contents if tooling removal fails.
- Revert any changes to `DbContext` via version control (`git revert` or `git checkout`).

### Phase 3 (Review) — Rollback
- No schema changes applied. Reject the PR/review and return to Phase 2.

### Phase 4 (Apply to Dev) — Rollback
- Run `dotnet ef database update 0` to revert all migrations on the development database (executes all `Down()` methods in reverse order).
- Alternatively, restore the dev database from a pre-migration snapshot if one was taken.

### Phase 5 (Apply to Staging) — Rollback
- Run `dotnet ef database update <previous-migration-name>` (or `0` if this is the initial migration) against the staging connection string.
- Restore staging database from snapshot taken immediately before migration application.

### Phase 6 (Apply to Production) — Rollback
- **Prerequisite:** A verified database backup must exist before production migration is applied.
- Execute the idempotent rollback script generated by `dotnet ef migrations script <target> <previous> --idempotent` against production.
- If `Down()` migration is destructive (e.g., drops columns), restore from backup instead of running `Down()`.
- Redeploy the previous application version after schema rollback.

---

## Testing Strategy

### Unit Tests
- **Scope:** Validate entity configurations, relationships, and constraints defined in `OnModelCreating`.
- **Tool:** TODO (xUnit / NUnit / MSTest — confirm from project conventions).
- **Approach:** Use EF Core's `InMemory` provider or `Sqlite` in-memory to test model correctness without a real DB.
- **Coverage target:** TODO — confirm project coverage baseline.

### Integration Tests
- **Scope:** Verify that `Database.Migrate()` executes without error against a real (or containerized) database instance. Verify that all `DbSet<T>` CRUD operations succeed post-migration.
- **Tool:** TODO — confirm if Docker-based test DB (e.g., `testcontainers-dotnet`) is available.
- **Approach:** Spin up a clean database, apply migrations, run smoke queries, tear down.

### Regression Tests
- **Scope:** Confirm that existing application functionality (if any) is unaffected by schema changes.
- **Tool:** TODO — depends on existing test suite.
- **Approach:** Run full existing test suite against a migrated database.

### Migration Script Validation (CI Gate)
- **Tool:** `dotnet ef migrations script --idempotent` — must succeed in CI with exit code 0.
- **Gate:** Block merge/deploy if script generation fails or if `Migrations/` directory is out of sync with the model snapshot.
- **Command:** `dotnet ef migrations has-pending-model-changes` (EF Core 7+) or equivalent check.

### Performance
- N/A for initial migration authoring — schema creation performance is not a regression concern at this stage. TODO: revisit if migration applies to a database with existing large datasets.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Schema and model audit complete | Phase 1 | TODO | TODO |
| Initial migration scripts authored | Phase 2 | TODO | TODO |
| Migration scripts reviewed and approved | Phase 3 | TODO | TODO |
| Migrations applied to development | Phase 4 | TODO | TODO |
| Migrations applied to staging | Phase 5 | TODO | TODO |
| Migrations applied to production | Phase 6 | TODO | TODO |

> **TODO:** Populate all dates and owners once the moderate-option person-days estimate is confirmed and team assignments are made.