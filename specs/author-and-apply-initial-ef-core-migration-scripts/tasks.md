# TASKS — Initial EF Core Migration Scripts

> **Scope:** Author and apply the initial EF Core migration scripts.
> **Upgrade Option:** Moderate
> **Urgency:** Medium

---

## Prerequisites

- [ ] [XS] Confirm EF Core CLI tooling is installed (`dotnet ef` version ≥ the version referenced in the project's `.csproj` / `packages.config`) on all developer machines and CI agents
- [ ] [XS] Verify database connection strings for development, staging, and production environments are accessible and correctly configured in `appsettings.json` / environment variable secrets before migration work begins
- [ ] [XS] Confirm the target database server (SQL Server / PostgreSQL / SQLite — whichever is in use) is reachable from the migration execution environment and that the executing identity has `CREATE TABLE` / `ALTER TABLE` / `CREATE INDEX` DDL permissions

---

## Phase 1 — Preparation

- [ ] [S] Audit existing `DbContext` class(es) and all registered entity types to produce a complete inventory of tables, relationships, and indexes that the initial migration must cover
- [ ] [S] Create a dedicated feature branch (e.g., `feature/ef-core-initial-migration`) from `main` / `master` and confirm branch protection rules allow migration script commits
- [ ] [XS] Capture a baseline snapshot of the current database schema (via `mysqldump`, `pg_dump`, `sqlcmd`, or equivalent) and commit it to `docs/schema-baseline/` for regression comparison
- [ ] [XS] Add or confirm an `.efignore` / `DbContextFactory` implementation (e.g., `IDesignTimeDbContextFactory<AppDbContext>`) in the data project so `dotnet ef` can instantiate the context at design time without a running host

---

## Phase 2 — Core Upgrade

- [ ] [M] Scaffold the initial EF Core migration by running `dotnet ef migrations add InitialCreate --project <DataProject> --startup-project <StartupProject>` and review the generated `Migrations/<timestamp>_InitialCreate.cs` and `Migrations/<timestamp>_InitialCreate.Designer.cs` files for correctness against the baseline schema snapshot
- [ ] [S] Edit `Migrations/<timestamp>_InitialCreate.cs` — `Up()` method — to add any missing indexes, unique constraints, default values, or computed columns that EF Core's scaffolder did not infer from the model annotations
- [ ] [S] Edit `Migrations/<timestamp>_InitialCreate.cs` — `Down()` method — to ensure full rollback fidelity (drop tables in reverse dependency order, restore sequences/identity seeds where applicable)
- [ ] [XS] Verify the `Migrations/<ModelSnapshot>.cs` file accurately reflects the full intended schema and commit all three generated files (`InitialCreate.cs`, `InitialCreate.Designer.cs`, `<DbContext>ModelSnapshot.cs`) in a single atomic commit
- [ ] [S] Apply the migration to the **development** database using `dotnet ef database update --project <DataProject> --startup-project <StartupProject>` and confirm all tables, columns, and constraints match the baseline snapshot

---

## Phase 3 — Testing & Validation

- [ ] [M] Write or update integration tests (in the existing test project) that spin up an in-memory or localdb instance, call `dbContext.Database.Migrate()`, and assert that all expected tables and key columns exist post-migration
- [ ] [S] Execute the full existing test suite against the migrated development database and confirm zero regressions; document any failures in `docs/migration-test-results.md`
- [ ] [S] Perform a manual diff between the baseline schema snapshot (`docs/schema-baseline/`) and the post-migration schema dump to confirm no unintended DDL changes (extra columns, dropped indexes, renamed constraints)
- [ ] [XS] Test the `Down()` rollback path by running `dotnet ef database update 0` on a scratch database and verifying the schema is fully removed without errors

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Add a CI pipeline step (in the existing pipeline config file — e.g., `.github/workflows/`, `azure-pipelines.yml`, or equivalent) that runs `dotnet ef migrations script --idempotent --output artifacts/migration.sql` and uploads the generated SQL script as a build artifact
- [ ] [S] Add a CI validation step that runs `dotnet ef migrations has-pending-model-changes` (or equivalent) to fail the build if a developer modifies an entity without generating a corresponding migration
- [ ] [XS] Update the deployment runbook / pipeline to include the `dotnet ef database update` command (or equivalent idempotent SQL script execution) as a pre-deployment step before the application binary is swapped

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CHANGELOG.md` with an entry describing the addition of EF Core migration infrastructure and the `InitialCreate` migration
- [ ] [S] Write or update `docs/runbooks/database-migrations.md` to document: how to add future migrations, how to apply them locally and in CI/CD, and how to roll back using the `Down()` path
- [ ] [XS] Apply the migration to the **staging** environment, verify schema parity with development, and obtain sign-off from a second engineer before scheduling production rollout
- [ ] [S] Apply the migration to **production** during a scheduled maintenance window, monitor application startup logs and error rates for 30 minutes post-deployment, and confirm no migration-related exceptions appear

---

> **Note:** Task sizes assume a single engineer. Adjust if the `DbContext` entity count is large (> 50 entities), in which case Phase 2 tasks should be re-estimated as `[L]`.