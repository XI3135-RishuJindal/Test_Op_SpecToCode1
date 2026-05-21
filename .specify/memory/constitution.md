# CONSTITUTION
## SQLAlchemy 2.0 Query API Migration

---

## Project Identity

**Name:** SQLAlchemy 2.0 Query API Migration

**Purpose:** Eliminate all usage of the legacy `Query` API (SQLAlchemy 1.x style) and replace every call site with the SQLAlchemy 2.0 `select()` construct and associated session execution patterns (`session.execute(select(...))`).

**High-Level Goal:** Achieve a codebase that is fully compatible with SQLAlchemy 2.0's new-style query interface, removing reliance on deprecated APIs that are removed in SQLAlchemy 2.0, thereby eliminating EOL risk and unblocking future upgrades.

---

## Guiding Principles

1. **Prefer `select()` + `session.execute()` over `session.query()` because** the legacy `Query` API is fully removed in SQLAlchemy 2.0 and continued use blocks the upgrade path.
2. **Prefer targeted, call-site-by-call-site migration over bulk automated rewrites because** automated codemods for ORM query patterns carry high risk of silent semantic drift that must be caught by tests.
3. **Prefer preserving existing return-type contracts over changing them because** downstream consumers of query results must not be broken by this migration.
4. **Prefer running SQLAlchemy's built-in `SQLALCHEMY_WARN_20` / legacy deprecation warnings as a gate because** they provide a reliable, low-cost signal that all legacy patterns have been removed before finalising the migration.
5. **Prefer incremental, module-by-module commits over a single large changeset because** smaller diffs reduce review risk and allow partial rollback without reverting the entire migration.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is limited to migrating existing query call sites only; no schema changes, no new features, and no ORM model restructuring are in scope.
- **Technology mandate:** All query code must be compatible with SQLAlchemy 2.0's `select()` API upon completion. No new code may use the legacy `Query` API.
- **Scope freeze:** The following are explicitly out of scope — database schema changes, model relationship restructuring, connection pool configuration, and application feature work.
- **Timeline:** TODO — specific person-days estimate not provided in the upgrade option; must be confirmed before work begins.
- **Runtime / build environment:** TODO — language runtime version and build tooling not specified in tech analysis; confirm target environment before starting.

---

## Quality Standards

- **Deprecation-warning gate:** Zero SQLAlchemy legacy `Query` API deprecation warnings emitted at runtime before the migration is considered complete. Verified by enabling `SQLALCHEMY_WARN_20=1` (or equivalent 2.0 deprecation mode) in CI.
- **Test coverage floor:** Every migrated module must have its existing test suite passing without modification to test assertions. No net reduction in passing tests is acceptable.
- **Code review:** Every changed module requires at least one reviewer who can verify ORM semantic equivalence between the old and new query form.
- **Documentation:** Each PR must include a brief note in its description confirming which legacy patterns were replaced and that return types are preserved.
- **Deployment gate:** Migration is not merged to the main branch until the deprecation-warning CI check passes clean across the full test suite.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt SQLAlchemy 2.0 `select()` style as the sole query pattern | Legacy `Query` API is removed in SQLAlchemy 2.0; migration is required to eliminate EOL risk | Accepted |
| ADR-002 | Use SQLAlchemy's built-in deprecation warning mode as the primary migration completeness signal | Provides an authoritative, low-overhead check directly from the library | Accepted |
| ADR-003 | Migrate incrementally by module rather than in a single changeset | Reduces review burden and limits blast radius of any semantic error | Accepted |
| ADR-004 | Target runtime version and build tooling | TODO — not determinable from current tech analysis; decision deferred | Proposed |