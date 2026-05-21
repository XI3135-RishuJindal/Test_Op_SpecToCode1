# CONSTITUTION

## Project Identity

**Name:** Persistent Store Migration
**Purpose:** Replace the application's static in-memory data store with a durable, EF Core-backed relational database using SQLite (development/lightweight) or PostgreSQL (production).
**High-Level Goal:** Eliminate data loss on process restart, enable concurrent access, and establish a maintainable data-access layer through Entity Framework Core — without breaking existing application behaviour.

---

## Guiding Principles

1. **Prefer EF Core DbContext over raw ADO.NET or Dapper** because the task mandates EF Core as the ORM layer; consistency in data-access patterns reduces future tech debt.
2. **Prefer SQLite for local/test environments and PostgreSQL for production** because a single provider lock-in would either sacrifice production reliability or complicate local development; provider abstraction via EF Core connection strings keeps both viable.
3. **Prefer additive schema migrations over destructive changes** because in-memory data has no migration history; all schema evolution must be captured in EF Core migration files to remain reproducible.
4. **Prefer interface-based repository abstractions over direct DbContext injection in business logic** because this preserves testability and allows the in-memory store to remain as a test double during the transition period.
5. **Prefer a feature-flag or parallel-run cutover over a hard switch** because the upgrade urgency is medium, allowing a controlled rollout that reduces risk of data-access regressions reaching production.

---

## Constraints

- **Effort ceiling:** Moderate option selected; scope is limited to replacing the in-memory store with EF Core + SQLite/PostgreSQL. No additional feature work, schema redesign beyond what the current model requires, or infrastructure changes outside database provisioning are in scope.
- **Technology mandates:**
  - ORM: Entity Framework Core (version TODO — confirm latest stable compatible with the project's runtime once runtime is identified).
  - Databases: SQLite (dev/test) and PostgreSQL (production). No other database engines are in scope.
  - Runtime/language: TODO — not determinable from current tech analysis; must be confirmed before dependency versions are locked.
- **Scope freeze:** The existing data model (entities and relationships) must be preserved as-is unless a breaking inconsistency is discovered during migration. Schema extensions are out of scope.
- **No downtime mandate:** TODO — deployment strategy (blue/green, rolling, maintenance window) must be confirmed with stakeholders before cutover planning.

---

## Quality Standards

- **Test coverage:** All repository/data-access classes must have ≥ 80% line coverage via unit tests using the EF Core in-memory provider or SQLite in-memory mode as test doubles.
- **Migration integrity:** Every EF Core migration must be reviewed and approved before merge; `dotnet ef migrations script` output must be inspected for destructive operations (DROP, TRUNCATE) and explicitly approved if present.
- **Code review:** All data-access changes require at least one peer review with explicit sign-off on the migration files and DbContext configuration.
- **Documentation:** A `DATA_STORE.md` file must be created documenting connection string configuration, how to run migrations, and how to switch between SQLite and PostgreSQL.
- **Deployment gate:** CI pipeline must run `dotnet ef database update` (or equivalent) against a SQLite test database and execute the full test suite before any merge to the main branch is permitted.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use EF Core as the ORM | Explicitly required by the modernization task | Accepted |
| ADR-002 | Support both SQLite and PostgreSQL via provider abstraction | SQLite for dev/test simplicity; PostgreSQL for production durability | Accepted |
| ADR-003 | Capture all schema changes as EF Core migration files | No prior migration history exists; reproducibility requires code-first migrations from day one | Accepted |
| ADR-004 | Runtime version and build tooling | TODO — tech analysis lists runtime as unknown; must be resolved before dependency versions are finalised | Proposed |
| ADR-005 | Deployment/cutover strategy | TODO — zero-downtime requirement not confirmed; stakeholder input required | Proposed |