# CONSTITUTION
## SQLAlchemy 2.0 Query API Migration

---

## Project Identity

**Name:** SQLAlchemy 2.0 Query API Migration

**Purpose:** Eliminate all usage of the legacy `Query` API (SQLAlchemy 1.x style) and replace every call site with the SQLAlchemy 2.0 `select()` construct and associated session execution patterns (`session.execute(select(...))` ).

**High-Level Goal:** Achieve a codebase that is fully compatible with SQLAlchemy 2.0's new-style query interface, removing reliance on deprecated APIs that are removed in SQLAlchemy 2.0, thereby eliminating EOL risk and unblocking future upgrades.

---

## Guiding Principles

1. **Prefer `select()` + `session.execute()` over `session.query()` because** the legacy `Query` API is fully removed in SQLAlchemy 2.0 and continued use blocks the upgrade path.
2. **Prefer targeted, call-site-by-call-site migration over bulk automated rewrites because** automated codemods risk silently altering query semantics (eager loading, result shape, scalar vs. row behaviour).
3. **Prefer explicit result unpacking (`.scalars()`, `.scalar_one()`, `.all()`) over implicit result access because** SQLAlchemy 2.0 returns `Row` objects by default, and assuming the old result shape will cause runtime errors.
4. **Prefer preserving existing test coverage as a regression harness over rewriting tests first because** tests must remain green throughout the migration to detect semantic regressions immediately.
5. **Prefer incremental, reviewable commits per module over a single large changeset because** the medium urgency rating allows time for careful review and reduces the blast radius of any single error.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is limited to migrating existing query call sites only; no schema changes, no ORM model restructuring, and no new feature work may be bundled into this migration.
- **Technology mandate:** All query code must be compatible with SQLAlchemy 2.0's `select()` API upon completion. No new code may be written using the legacy `Query` API (`session.query()`).
- **Scope freeze:** The following are explicitly out of scope — database schema changes, ORM relationship redefinition, migration to async sessions, and performance tuning. These may be addressed in subsequent projects.
- **Runtime/build tooling:** TODO — specific Python runtime version and dependency pinning strategy to be confirmed before migration begins.
- **Timeline:** TODO — person-days estimate not provided in the upgrade option; must be established during planning.

---

## Quality Standards

- **Regression test pass rate:** 100% of pre-existing tests must pass after each module's migration is complete before that module is merged.
- **New test coverage:** Any call site that lacks a test must have a test added covering the basic query result before the migration of that call site is accepted.
- **Code review:** Every changed module requires at least one peer review with explicit sign-off that result unpacking semantics (scalar vs. row vs. list) are correct.
- **No legacy API in merged code:** CI must include a lint or grep check that fails if `session.query(` appears anywhere in application source after the migration is declared complete.
- **Documentation:** A migration notes file (`MIGRATION_NOTES.md`) must record any non-trivial semantic difference discovered at each call site (e.g., changed result shape, removed `.first()` implicit ordering).

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt SQLAlchemy 2.0 `select()` style as the sole query pattern | Legacy `Query` API is removed in SQLAlchemy 2.0; migration is required to eliminate EOL risk | Accepted |
| ADR-002 | Migrate incrementally per module, not in a single pass | Reduces risk of undetected semantic regressions; aligns with medium urgency and moderate effort scope | Accepted |
| ADR-003 | Add CI enforcement (grep/lint) to ban `session.query(` post-migration | Prevents regression to legacy patterns after migration is complete | Accepted |
| ADR-004 | Async session migration is out of scope | Not referenced in the upgrade option; bundling it would exceed the moderate effort ceiling | Accepted |
| ADR-005 | Specific Python runtime version and pinning strategy | TODO — not determinable from provided context; must be resolved in planning phase | Proposed |