# CONSTITUTION
## SQLAlchemy 1.3 → 2.0 Migration

---

## Project Identity

**Name:** SQLAlchemy 2.0 Migration

**Purpose:** Upgrade the project's ORM layer from SQLAlchemy 1.3 to SQLAlchemy 2.0, migrating all models, session patterns, and query interfaces to the new API.

**High-Level Goal:** Eliminate reliance on the SQLAlchemy 1.x legacy API (which is no longer receiving feature development) and adopt the 2.0-style declarative models, `Session` patterns, and `select()`-based query syntax — resulting in a maintainable, forward-compatible data access layer.

---

## Guiding Principles

1. **Prefer 2.0-style `select()` queries over legacy `Query` API** because the `Query` object is deprecated in SQLAlchemy 2.0 and will raise errors if not migrated.
2. **Prefer explicit `Session` context management (`with Session(...) as session`) over implicit session patterns** because SQLAlchemy 2.0 removes autocommit and requires explicit transaction control.
3. **Prefer incremental migration with `SQLALCHEMY_WARN_20=1` compatibility flag enabled first** because it surfaces all 1.x deprecation warnings before the hard cutover, reducing the risk of runtime breakage.
4. **Prefer updating one model/module at a time over a big-bang rewrite** because the moderate effort ceiling requires contained, reviewable changesets that can be tested in isolation.
5. **Prefer retaining existing database schema unchanged** because this migration targets the ORM layer only; schema changes are out of scope and would expand risk and effort.
6. **Prefer `DeclarativeBase` (new-style) over `declarative_base()` (legacy factory)** because `declarative_base()` is deprecated in 2.0 and the new base class provides typed column support and cleaner inheritance.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is bounded to ORM/session layer changes only. No infrastructure, schema, or application-feature work is in scope.
- **Technology mandate:** Target library version is **SQLAlchemy 2.0.x** (latest stable 2.0 release). No downgrade or pinning to 1.4 is permitted as an end state.
- **Scope freeze:** Database schema must not change. No new models, tables, or relationships are to be introduced during this migration.
- **Runtime/language:** TODO — runtime version and language version must be confirmed before work begins to ensure SQLAlchemy 2.0 compatibility (requires Python ≥ 3.7; Python ≥ 3.8 recommended).
- **Build/dependency tooling:** TODO — confirm package manager (pip/poetry/pipenv) and whether a `requirements.txt` or `pyproject.toml` pin must be updated.

---

## Quality Standards

- **Deprecation warnings:** Zero `RemovedIn20Warning` or `LegacyAPIWarning` warnings must remain in the codebase at merge time (enforced via `SQLALCHEMY_WARN_20=1` in the test environment).
- **Test coverage:** All migrated model and session modules must maintain or exceed their pre-migration test coverage. No coverage regression is acceptable.
- **Code review:** Every PR touching model or session code requires at least one reviewer with SQLAlchemy familiarity. No self-merge.
- **Regression gate:** The full existing test suite must pass against the 2.0 engine before any module migration is considered complete.
- **Documentation:** Any custom session utilities, base classes, or query helpers introduced during migration must include inline docstrings explaining the 2.0 pattern used.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Upgrade directly to SQLAlchemy 2.0, not 1.4 as a stepping stone | 1.4 is itself in maintenance mode; migrating to 2.0 is the durable end state and avoids a two-step upgrade | Accepted |
| ADR-002 | Enable `SQLALCHEMY_WARN_20=1` as the first migration step | Surfaces all legacy API usage without breaking the application, enabling a safe audit before code changes | Accepted |
| ADR-003 | Schema changes are out of scope | Keeps effort within the moderate ceiling and isolates ORM-layer risk from data-layer risk | Accepted |
| ADR-004 | Runtime and build tool versions are unconfirmed | Insufficient information in tech analysis; must be resolved before migration begins | Proposed — TODO |