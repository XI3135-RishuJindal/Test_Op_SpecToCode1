# Spec: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

---

## Summary

This spec covers the migration of all legacy SQLAlchemy `Session.query()` API calls to the SQLAlchemy 2.0-style `select()` construct across the codebase. The expected outcome is a codebase that is fully compatible with SQLAlchemy 2.0's recommended query interface, eliminating reliance on the legacy `Query` object that has been deprecated in SQLAlchemy 1.4 and removed in SQLAlchemy 2.0. This migration reduces technical debt, improves long-term maintainability, and positions the application for full SQLAlchemy 2.0 compatibility.

---

## Motivation

- **Deprecation and Removal:** The `Session.query()` API was formally deprecated in SQLAlchemy 1.4 and removed in SQLAlchemy 2.0. Continued use of the legacy API blocks any upgrade to SQLAlchemy 2.0 or later.
- **Technical Debt:** Reliance on the legacy `Query` object represents accumulated technical debt that increases the cost of future framework upgrades and makes the codebase harder to maintain.
- **Upgrade Urgency:** Rated **medium** — the migration is not immediately blocking production, but deferral increases the risk surface as SQLAlchemy 2.0 adoption becomes the ecosystem standard and third-party integrations drop support for 1.x patterns.
- **Ecosystem Alignment:** Libraries and tooling (e.g., async extensions, type stubs, IDE support) are increasingly built against the 2.0 `select()` API. Legacy patterns receive diminishing community and tooling support.
- **Correctness and Predictability:** The 2.0-style API provides more explicit, composable, and type-safe query construction, reducing the risk of subtle behavioral differences introduced by the `Query` object's implicit behaviors (e.g., automatic de-duplication, implicit joins).

---

## Current State

The codebase currently uses the SQLAlchemy 1.x `Session.query()` API as the primary mechanism for database queries. Key characteristics of the current state include:

- **Primary Query Interface:** `Session.query(Model)` is used to initiate queries, returning a `Query` object.
- **Filtering:** `.filter()` and `.filter_by()` methods on the `Query` object are used to apply WHERE clauses.
- **Result Retrieval:** `.all()`, `.first()`, `.one()`, `.one_or_none()`, `.scalar()`, and `.count()` are called on `Query` objects to retrieve results.
- **Ordering and Limiting:** `.order_by()`, `.limit()`, `.offset()` are chained on `Query` objects.
- **Joins:** `.join()` and `.outerjoin()` are called on `Query` objects.
- **Aggregation:** `.count()` and scalar subqueries are expressed via `Query` methods.
- **Eager Loading:** `.options()` with loader strategies (e.g., `joinedload`, `subqueryload`) are applied to `Query` objects.
- **Existence Checks:** Patterns such as `session.query(Model).filter(...).first() is not None` are used for existence checks.

> **TODO:** Identify the specific model classes, repository classes, service layer modules, and configuration keys involved once codebase access is available. Enumerate all call sites using a static analysis pass.

---

## Proposed Changes

For each affected component, the legacy `Session.query()` pattern is replaced with a `select()` construct executed via `Session.execute()` or `Session.scalars()`, with results extracted using the appropriate result-set method.

| Component | Before | After | Breaking? |
|---|---|---|---|
| Basic model query | `session.query(Model)` | `select(Model)` executed via `session.scalars()` | N (internal) |
| Filter application | `.filter(Model.col == val)` | `select(Model).where(Model.col == val)` | N (internal) |
| Filter by keyword | `.filter_by(col=val)` | `.where(Model.col == val)` | N (internal) |
| Fetch all results | `.all()` | `session.scalars(...).all()` | N (internal) |
| Fetch first result | `.first()` | `session.scalars(...).first()` | N (internal) |
| Fetch exactly one | `.one()` | `session.scalars(...).one()` | N (internal) |
| Fetch one or none | `.one_or_none()` | `session.scalars(...).one_or_none()` | N (internal) |
| Scalar value | `.scalar()` | `session.scalar(...)` | N (internal) |
| Row count | `.count()` | `select(func.count()).select_from(Model).where(...)` via `session.scalar()` | N (internal) |
| Ordering | `.order_by(...)` | `select(Model).order_by(...)` | N (internal) |
| Limit / Offset | `.limit(n).offset(m)` | `select(Model).limit(n).offset(m)` | N (internal) |
| Join | `.join(Related)` | `select(Model).join(Related)` | N (internal) |
| Outer join | `.outerjoin(Related)` | `select(Model).outerjoin(Related)` | N (internal) |
| Eager loading options | `.options(joinedload(...))` | `select(Model).options(joinedload(...))` | N (internal) |
| Existence check | `.filter(...).first() is not None` | `select(exists().where(...))` via `session.scalar()` | N (internal) |
| Multi-column / tuple select | `session.query(Model.a, Model.b)` | `select(Model.a, Model.b)` via `session.execute()` returning `Row` objects | Y — callers consuming tuple results must be updated |
| Legacy `Query` object passed as argument | Any function accepting a `Query` instance | Must accept a `Select` construct or pre-executed result set | Y — function signatures change |

---

## Compatibility & Breaking Changes

| Breaking Change | Description | Migration Path for Callers |
|---|---|---|
| `Query` object no longer returned | Any code that receives a `Query` object from a helper/repository method and chains further `.filter()`, `.order_by()`, etc. calls on it will break. | Callers must be updated to compose `select()` constructs before execution, or repository methods must accept and return `Select` objects for further composition. |
| Multi-column result shape | `session.query(Model.a, Model.b).all()` returns `KeyedTuple`; the 2.0 equivalent returns `Row` objects with different attribute access semantics. | Callers must be audited for `KeyedTuple`-specific access patterns and updated to use `Row` attribute or index access. |
| `.count()` method removal | `Query.count()` is a convenience method with no direct equivalent on `Select`. | Replace with an explicit `select(func.count()).select_from(...)` query. All call sites must be updated. |
| `Query` used in type annotations | Any function or variable typed as `Query[T]` will be invalid. | Update type annotations to `Select[T]` or the appropriate result type. |
| Pagination helpers depending on `Query` | Any utility (e.g., a pagination helper) that accepts a `Query` object and calls `.count()` or slices it will break. | Pagination utilities must be rewritten to accept `Select` constructs and issue separate count queries. TODO: identify all pagination utilities in the codebase. |
| Dynamic query composition via `Query` | Code that conditionally chains methods on a `Query` object across branches will break. | Refactor to build a `Select` construct incrementally using `where()`, `order_by()`, etc., before passing to `session.scalars()`. |

---

## Acceptance Criteria

1. **Given** the full codebase, **when** a static analysis scan is run for `session.query(` and `.query(`, **then** zero occurrences are found in application source files (excluding migration scripts and historical fixtures explicitly marked as legacy).

2. **Given** any repository or data-access method that previously returned a `Query` object, **when** the method is called, **then** it returns either a fully executed result set or a `Select` construct — never a `Query` instance.

3. **Given** a query that previously used `.filter()` on a `Query` object, **when** the equivalent `select().where()` query is executed against the same dataset, **then** it returns an identical result set (same rows, same order where order was specified).

4. **Given** a query that previously used `Query.count()`, **when** the replacement `select(func.count())` query is executed, **then** it returns the same integer count for the same dataset and filter conditions.

5. **Given** a multi-column query previously using `session.query(Model.a, Model.b)`, **when** the replacement `select(Model.a, Model.b)` query is executed and results are consumed, **then** all callers correctly access column values without `AttributeError` or `KeyError`.

6. **Given** any existence-check pattern previously using `.first() is not None`, **when** the replacement `exists()` query is executed, **then** it returns `True` or `False` consistent with the previous pattern for both matching and non-matching conditions.

7. **Given** the full test suite, **when** all tests are executed after the migration, **then** the test suite passes with no regressions relative to the pre-migration baseline.

8. **Given** any pagination utility that previously accepted a `Query` object, **when** it is invoked with a `Select` construct and a dataset, **then** it returns the correct page of results and the correct total count.

9. **Given** the application running under SQLAlchemy 2.0 (or 1.4 with `future=True` mode enabled), **when** any database operation is performed, **then** no `LegacyAPIWarning` or `RemovedIn20Warning` deprecation warnings are emitted.

10. **Given** eager-loading options previously applied via `Query.options()`, **when** the equivalent `select(Model).options()` query is executed, **then** the related objects are loaded without additional queries (verified via SQL query count assertions in tests).

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact SQLAlchemy version currently in use, and is it 1.4 (with `future` flag) or an earlier 1.x release? This determines whether `select()` is already available and whether `future=True` can be used as an intermediate validation step. | TODO | TODO |
| 2 | Are there any third-party libraries (e.g., Flask-SQLAlchemy, FastAPI integrations, admin panels) that depend on the `Query` API being present and would require their own upgrades as part of this migration? | TODO | TODO |
| 3 | Are there any pagination, filtering, or sorting utilities (e.g., custom `QueryBuilder` classes) that accept `Query` objects and need to be redesigned? | TODO | TODO |
| 4 | Is there an async (`AsyncSession`) usage in the codebase? If so, the migration must also account for `AsyncSession.execute(select(...))` patterns. | TODO | TODO |
| 5 | What is the target SQLAlchemy version post-migration — 1.4 (with `future=True`) as an intermediate step, or a direct jump to 2.x? | TODO | TODO |
| 6 | Are there raw SQL strings or `text()` constructs mixed with `Query` API calls that also need to be reviewed for 2.0 compatibility? | TODO | TODO |
| 7 | Is there a test coverage baseline established for data-access layer code? If coverage is low, additional tests may need to be written before migration to ensure regressions are caught. | TODO | TODO |