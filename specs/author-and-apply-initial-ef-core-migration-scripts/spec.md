# Spec: Author and Apply Initial EF Core Migration Scripts

## Summary

This spec covers the authoring and application of initial Entity Framework Core (EF Core) migration scripts for the project. The expected outcome is a versioned, repeatable database schema baseline established through EF Core's migration infrastructure, enabling schema changes to be tracked in source control and applied consistently across all environments.

## Motivation

- **Tech Debt:** The project currently lacks a formal, code-driven database migration strategy. Without EF Core migrations in place, schema changes are applied manually or through ad-hoc scripts, creating drift risk between environments and blocking reliable CI/CD pipelines.
- **Upgrade Urgency:** Medium — the absence of migration scripts is a foundational gap that must be resolved before dependent modernization work (e.g., model changes, schema evolution) can proceed safely.
- **Compliance / Repeatability:** Regulated and production environments require auditable, repeatable schema application. EF Core migrations satisfy this by embedding schema history in the database and in source control.
- **Specific Version Details:** TODO — exact EF Core version in use is not confirmed in the provided tech analysis. All version-specific migration tooling behavior should be validated once the version is confirmed.

## Current State

- **Migration Infrastructure:** No EF Core migrations folder or migration history table (`__EFMigrationsHistory`) is known to exist in the repository at this time.
- **DbContext(s):** TODO — specific `DbContext` class names, their registered connection strings, and configuration keys are not identified in the provided context.
- **Schema Source of Truth:** TODO — it is unclear whether the current schema is defined via an existing EF Core model, a raw SQL script, a legacy ORM, or a manually managed database. This must be confirmed before the initial migration can be authored.
- **Data Models / Entities:** TODO — the specific entity classes, table mappings, relationships, and any existing Fluent API or data annotation configurations are not provided in the context.
- **Configuration Keys:** TODO — connection string keys, environment-specific configuration sources, and any existing database provider configuration are not confirmed.
- **Existing Database State:** TODO — whether target environments already have a populated schema (requiring a baseline migration) or are greenfield (allowing a clean initial migration) is not confirmed.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Migration history tracking | No `__EFMigrationsHistory` table; schema changes untracked | `__EFMigrationsHistory` table present; all schema changes versioned | N — additive to existing schema |
| Migrations folder in source control | Absent | Initial migration file(s) and model snapshot present in repository | N |
| Schema application process | Manual / ad-hoc | Applied via EF Core migration tooling as part of deployment pipeline | N |
| DbContext configuration | TODO — current state unknown | Confirmed compatible with EF Core migration tooling | TODO |
| CI/CD pipeline | TODO — migration step absent or undefined | Migration application step included in deployment process | TODO |

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Introduction of `__EFMigrationsHistory` table | Adds a new system table to the target database | No action required for new databases; for existing databases, the baseline migration must be marked as already applied without re-running DDL — TODO: confirm approach based on existing schema state |
| Initial migration DDL vs. existing schema | If the database already has tables, running the initial migration may conflict with existing objects | TODO — determine whether to use an empty baseline migration (idempotent marker) or a full schema migration; depends on confirmed current schema state |
| Model snapshot added to source control | All future EF Core migrations will diff against this snapshot | All contributors must use EF Core tooling for subsequent schema changes; manual schema edits will cause snapshot drift |
| Connection string / provider configuration | TODO — changes to config keys may affect existing environment setups | TODO |

## Acceptance Criteria

1. **Given** the repository is checked out in a clean state, **when** the EF Core migration tooling is invoked to list migrations, **then** at least one migration is returned with a valid timestamp-based identifier and a corresponding model snapshot exists in source control.

2. **Given** a target database with no prior schema, **when** the initial migration is applied, **then** all expected tables and constraints are created and the `__EFMigrationsHistory` table contains exactly one row corresponding to the initial migration.

3. **Given** the initial migration has already been applied to a database, **when** the migration is applied again, **then** the operation completes without error and no duplicate schema objects or duplicate history rows are created.

4. **Given** a CI environment with a clean database, **when** the automated pipeline runs the migration step, **then** the pipeline exits successfully and the database schema matches the state defined by the EF Core model.

5. **Given** the initial migration has been applied, **when** the EF Core tooling is used to validate that the model and database schema are in sync, **then** no pending migrations are reported and no model/database mismatch errors are raised.

6. **Given** an existing database with a pre-existing schema (if applicable — TODO: confirm environment), **when** the baseline migration is applied using the appropriate idempotent strategy, **then** existing data is preserved, no duplicate objects are created, and the `__EFMigrationsHistory` table is correctly populated.

7. **Given** the migration scripts are present in source control, **when** a peer reviewer inspects the migration file and model snapshot, **then** the migration file contains only schema operations consistent with the defined entity model and no raw connection strings or environment-specific values are embedded.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact EF Core version in use (e.g., EF Core 6, 7, 8)? | TODO | TODO |
| 2 | What are the names of all `DbContext` classes that require migrations? | TODO | TODO |
| 3 | Does a database schema already exist in any target environment, or are all environments greenfield? | TODO | TODO |
| 4 | What database provider is in use (SQL Server, PostgreSQL, SQLite, etc.)? | TODO | TODO |
| 5 | What are the connection string configuration keys and how are they managed per environment? | TODO | TODO |
| 6 | Should the initial migration represent the full current schema, or should it be an empty baseline marker for an already-existing schema? | TODO | TODO |
| 7 | Is there an existing CI/CD pipeline step for database deployment, and if so, what tooling does it use? | TODO | TODO |
| 8 | Are there multiple deployment environments (dev, staging, prod) that each require the migration to be applied, and is there a promotion process? | TODO | TODO |
| 9 | Are there any existing seed data scripts or data-dependent schema objects (views, stored procedures, functions) that must be accounted for in or alongside the migration? | TODO | TODO |