# CONSTITUTION
## Project: Author and Apply Initial EF Core Migration Scripts

---

## Project Identity

**Name:** EF Core Initial Migration Authoring & Application

**Purpose:** Author and apply the initial Entity Framework Core migration scripts for the project's data layer, establishing a versioned, code-first database schema baseline.

**High-Level Goal:** Produce a working, repeatable set of EF Core migration scripts that can be applied to the target database, replacing or formalizing any prior ad-hoc schema management approach.

---

## Guiding Principles

1. **Prefer code-first migrations over manual SQL scripts** because EF Core migrations provide a versioned, auditable, and repeatable schema history that reduces drift between environments.
2. **Prefer idempotent, incremental migrations over destructive resets** because the upgrade urgency is medium and data safety during transition must be preserved.
3. **Prefer explicit migration naming conventions over auto-generated defaults** because clear names make the migration history readable and reviewable without inspecting diffs.
4. **Prefer validating migrations against a clean database before applying to shared environments** because unverified migrations applied to integration or staging databases create hard-to-reverse failures.
5. **Prefer keeping migration scripts in source control alongside application code** because co-location ensures schema changes are reviewed in the same pull request as the model changes that drive them.

---

## Constraints

- **Timeline & Effort:** Effort ceiling follows the `moderate` upgrade option. No scope expansion beyond authoring and applying the initial migration set is permitted under this budget.
- **Technology Mandates:**
  - Must use **Entity Framework Core** (version TODO — confirm target EF Core version with team).
  - Target runtime is TODO — confirm .NET version required for EF Core tooling compatibility.
  - Target database provider is TODO — confirm (SQL Server / PostgreSQL / SQLite / other).
- **Scope Freeze:** This task covers only the **initial** migration baseline. Subsequent feature migrations are out of scope.
- **No Breaking Schema Changes:** The initial migration must not destroy existing data in any shared environment without an explicit, approved data-migration plan.

---

## Quality Standards

- **Migration Validity:** Every migration must apply cleanly (`dotnet ef database update`) against a fresh, empty database with zero errors before merge.
- **Rollback Coverage:** Each migration must include a valid `Down()` method; migrations with empty or `throw`-only `Down()` bodies will not be accepted.
- **Code Review:** All migration files (`.cs` snapshot and migration class) must pass peer review by at least one team member before being merged to the main branch.
- **Test Gate:** At minimum, one integration test or smoke test must confirm the migrated schema matches the EF Core model (`dbContext.Database.EnsureCreated()` or model-validation equivalent) — TODO: confirm test framework in use.
- **Documentation:** A brief `MIGRATIONS.md` (or equivalent README section) must document how to run, roll back, and verify migrations locally.
- **No Pending Model Changes at Merge:** CI must confirm there are no unapplied model changes (`dotnet ef migrations has-pending-model-changes` or equivalent) at the point of merge.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use EF Core code-first migrations as the schema management mechanism | Aligns with the stated modernization goal; provides versioned, tooling-supported schema history | Accepted |
| ADR-002 | Initial migration establishes the full baseline schema in a single migration | Cleanest starting point for a new migration history; avoids partial-state ambiguity | Accepted |
| ADR-003 | Migration scripts committed to source control in the application repository | Ensures schema and model changes are reviewed together and remain in sync | Accepted |
| ADR-004 | Target EF Core version — TODO | Runtime and framework versions not specified in tech analysis; must be confirmed before work begins | Proposed |
| ADR-005 | Target database provider — TODO | Provider determines available migration features and SQL dialect; must be confirmed | Proposed |