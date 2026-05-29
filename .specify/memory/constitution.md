# CONSTITUTION
## SQLAlchemy 1.3 → 2.0 Migration: Models and Declarative Base

---

## Project Identity

**Name:** SQLAlchemy 1.3 → 2.0 Migration — Models and Declarative Base

**Purpose:** Modernize the project's ORM layer by migrating all SQLAlchemy model definitions and declarative base usage from the 1.3 API to the 2.0 API, eliminating deprecated patterns and aligning with the current supported release.

**High-Level Goal:** Produce a codebase where all SQLAlchemy models, declarative base declarations, and directly related ORM constructs conform to the SQLAlchemy 2.0 API — with no reliance on legacy 1.x compatibility shims — while keeping all existing functionality intact and all tests passing.

---

## Guiding Principles

1. **Prefer `DeclarativeBase` (2.0-style) over `declarative_base()` (1.x factory) because** the legacy factory is removed in 2.0 and continued use blocks the upgrade entirely.
2. **Prefer explicit `Mapped[T]` type annotations over untyped `Column()` declarations because** 2.0 enforces typed mapping as the canonical pattern and untyped columns produce deprecation warnings that become errors.
3. **Prefer incremental, model-by-model migration over a single big-bang rewrite because** smaller changesets reduce regression risk and allow targeted testing at each step.
4. **Prefer running the SQLAlchemy 1.4 `SQLALCHEMY_WARN_20` deprecation flag in CI before cutting over because** it surfaces all 2.0-incompatible call sites without requiring a full version bump upfront.
5. **Prefer preserving existing schema and column names exactly because** the migration scope is the ORM layer only; schema changes are out of scope and would expand risk unnecessarily.
6. **Prefer removing `session.execute(query)` legacy Query API usage in models because** the `Query` object is legacy in 2.0 and any model-level query helpers must use the new `select()` / `Session.execute()` pattern.

---

## Constraints

- **Scope freeze:** Changes are limited to model files, declarative base definitions, and directly coupled ORM helpers. Application logic, database schema, and non-ORM query layers are out of scope.
- **Timeline/Effort:** Moderate effort ceiling (exact person-days TODO — not provided in upgrade option). No scope expansion beyond models and declarative base is permitted within this budget.
- **Target version:** SQLAlchemy `>=2.0`, `<3.0`. No intermediate pinning to 1.4 in the final state.
- **Runtime/Language:** TODO — runtime and language versions not specified in tech analysis; confirm Python version compatibility with SQLAlchemy 2.0 (Python 3.7+ required by SQLAlchemy 2.0).
- **No legacy compatibility layers in production:** `sqlalchemy.ext.declarative.declarative_base` and `sqlalchemy.orm.Query` must not appear in production model code after migration.
- **Backwards compatibility of public model interfaces:** Column names, table names, and relationship names exposed to the rest of the application must not change.

---

## Quality Standards

- **Test coverage:** All model files touched by the migration must maintain or exceed their pre-migration test coverage. Coverage must not drop below the existing baseline (TODO — record baseline before migration begins).
- **Deprecation-warning gate:** CI must run with `SQLALCHEMY_WARN_20=1` (on 1.4) or equivalent 2.0 strict mode; zero SQLAlchemy deprecation warnings permitted in the test suite at merge time.
- **Code review:** Every PR touching model files requires at least one reviewer with SQLAlchemy 2.0 familiarity. No self-merge.
- **Static typing:** All migrated models must pass `mypy` (or the project's existing type checker — TODO confirm) without `# type: ignore` suppressions introduced by this migration.
- **Regression gate:** The full existing test suite must pass against the 2.0 dependency before any PR is merged.
- **Documentation:** Each model file must include an inline comment or module docstring noting the SQLAlchemy 2.0 migration completion status upon merge.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `DeclarativeBase` class-based base over `declarative_base()` factory | `declarative_base()` is removed in SQLAlchemy 2.0; `DeclarativeBase` is the 2.0 canonical replacement | Accepted |
| ADR-002 | Use `Mapped[T]` with `mapped_column()` for all column definitions | Required by SQLAlchemy 2.0 typed mapping system; eliminates untyped `Column()` deprecation warnings | Accepted |
| ADR-003 | Migrate scope limited to models and declarative base only | Upgrade option specifies this boundary; expanding scope exceeds effort ceiling and introduces unrelated risk | Accepted |
| ADR-004 | Validate migration using SQLAlchemy 1.4 `SQLALCHEMY_WARN_20` flag before final cutover | Provides a safe incremental validation step without requiring an immediate hard version bump | Accepted |
| ADR-005 | Target SQLAlchemy version pinned to `>=2.0,<3.0` | Ensures 2.0 API compliance without prematurely adopting an unreleased major version | Accepted |
| ADR-006 | Python minimum version requirement | SQLAlchemy 2.0 requires Python ≥ 3.7; exact project runtime version TODO — must be confirmed before migration starts | Proposed |