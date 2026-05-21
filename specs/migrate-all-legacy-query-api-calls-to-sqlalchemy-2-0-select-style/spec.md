# Spec: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

---

## Summary

This spec covers the migration of all legacy SQLAlchemy `Session.query()` API calls to the SQLAlchemy 2.0-style `select()` construct across the codebase. The expected outcome is a codebase that uses only the modern Core-aligned `select()` interface for all ORM queries, eliminating reliance on the legacy `Query` object that was deprecated in SQLAlchemy 1.4 and removed in SQLAlchemy 2.0. This migration reduces technical debt, ensures forward compatibility with SQLAlchemy 2.x, and aligns query patterns with the current SQLAlchemy standard.

---

## Motivation

- **Deprecation and removal:** The `Session.query()` API was formally deprecated in SQLAlchemy 1.4 and fully removed in SQLAlchemy 2.0. Any codebase still using `Session.query()` is either pinned to a legacy version or running with deprecation warnings that will become hard failures upon upgrade.
- **Upgrade urgency:** Rated **medium** — the legacy API is functional under SQLAlchemy 1.4 with `future=True` mode or under 1.x without it, but continued use blocks any upgrade to SQLAlchemy 2.x and accumulates deprecation noise in logs and CI output.
- **Technical debt:** Continued use of the `Query` API creates an inconsistent query style across the codebase, making onboarding harder and increasing the surface area for subtle behavioral differences between legacy and modern query execution.
- **Behavioral alignment:** The 2.0 `select()` style uses the same execution path for both Core and ORM queries, reducing surprising edge cases in result handling, eager loading, and subquery behavior.

---

## Current State

The codebase currently uses the SQLAlchemy legacy `Session.query()` API. The following patterns are in scope for migration:

| Pattern | Description |
|---|---|
| `session.query(Model)` | Basic model query returning `Query` objects |
| `session.query(Model).filter(...)` | Filtered queries using `Query.filter()` |
| `session.query(Model).filter_by(...)` | Keyword-style filtered queries |
| `session.query(Model).all()` | Fetching all results |
| `session.query(Model).first()` | Fetching the first result |
| `session.query(Model).one()` | Fetching exactly one result |
| `session.query(Model).one_or_none()` | Fetching one or no result |
| `session.query(Model).count()` | Counting results |
| `session.query(Model).order_by(...)` | Ordered queries |
| `session.query(Model).join(...)` | Joined queries |
| `session.query(Model).options(...)` | Eager loading options |
| `session.query(Model).scalar()` | Scalar result queries |
| `session.query(col1, col2)` | Column-level projections |
| `session.query(Model).update(...)` | Bulk update via `Query.update()` |
| `session.query(Model).delete(...)` | Bulk delete via `Query.delete()` |

**Key behavioral notes of the current state:**
- `Query.all()` returns a plain `list` of model instances.
- `Query.first()` returns a model instance or `None`.
- `Query.one()` raises if zero or more than one row is found.
- `Query.count()` issues a `SELECT count(*)` subquery automatically.
- `Query.update()` and `Query.delete()` perform bulk DML with `synchronize_session` semantics.
- Result rows from column-level projections are `KeyedTuple` objects (legacy named tuples).

---

## Proposed Changes

For each affected component, the legacy `Session.query()` call is replaced with a `select()` construct executed via `session.execute()`, with result extraction adapted to the new `Result` API.

| Component | Before | After | Breaking? |
|---|---|---|---|
| Basic model fetch | `session.query(Model)` | `session.execute(select(Model))` with `.scalars()` | Y |
| Filter clause | `.filter(Model.col == val)` | `select(Model).where(Model.col == val)` | Y |
| Keyword filter | `.filter_by(col=val)` | `select(Model).filter_by(col=val)` | N — `filter_by` is retained in 2.0 |
| Fetch all | `.all()` | `.scalars().all()` | Y |
| Fetch first | `.first()` | `.scalars().first()` | Y |
| Fetch one | `.one()` | `.scalars().one()` | Y |
| Fetch one or none | `.one_or_none()` | `.scalars().one_or_none()` | Y |
| Count | `.count()` | `select(func.count()).select_from(Model)` executed via `session.execute(...).scalar()` | Y |
| Order by | `.order_by(...)` | `select(Model).order_by(...)` | N |
| Join | `.join(...)` | `select(Model).join(...)` | N — syntax compatible |
| Eager loading options | `.options(...)` | `select(Model).options(...)` | N — syntax compatible |
| Scalar result | `.scalar()` | `.scalar()` on `session.execute()` result | Y — execution path changes |
| Column projection | `session.query(col1, col2)` | `session.execute(select(col1, col2))` returning `Row` objects | Y — `KeyedTuple` replaced by `Row` |
| Bulk update | `Query.update({...})` | `session.execute(update(Model).where(...).values(...))` | Y |
| Bulk delete | `Query.delete()` | `session.execute(delete(Model).where(...))` | Y |
| `exists()` subquery | `session.query(Model).exists()` | `select(exists(select(Model).where(...)))` | Y |

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `Query` object no longer returned | Any code that stores a `Query` object and chains methods lazily must be rewritten to build the full `select()` statement before execution | Replace all `Query` chain storage with `select()` statement construction; execute once at the call site |
| `KeyedTuple` result rows replaced by `Row` | Code accessing projection results by index or attribute name via `KeyedTuple` interface may behave differently | Audit all column-projection queries; access `Row` fields by attribute name or index — the `Row` API is largely compatible but `isinstance` checks against `KeyedTuple` will fail |
| `.all()` / `.first()` / `.one()` called on `Result`, not `Query` | Callers must call `.scalars()` before terminal methods when expecting model instances | Add `.scalars()` before `.all()`, `.first()`, `.one()`, `.one_or_none()` on all `session.execute()` results returning ORM entities |
| `Query.count()` behavior | The legacy `.count()` wraps the query in a subquery automatically; the 2.0 equivalent must be written explicitly | Replace with `select(func.count()).select_from(...)` or `select(func.count(Model.id)).where(...)` |
| `Query.update()` / `Query.delete()` removed | Bulk DML via the `Query` API is gone | Replace with explicit `update()` / `delete()` Core constructs executed via `session.execute()`; verify `synchronize_session` strategy is explicitly set |
| `session.query(Model).exists()` pattern | The `Query.exists()` shorthand is removed | Rewrite using `exists()` construct within a `select()` |
| Subqueries derived from `Query` | `Query.subquery()` and `Query.cte()` are removed | Replace with `select(...).subquery()` and `select(...).cte()` on the `select()` construct directly |
| `Query` passed as a type hint or interface | Any function typed to accept or return `Query` objects | Update type annotations to `Select` (for unexecuted statements) or `ScalarResult` / `Result` (for executed results) |

---

## Acceptance Criteria

1. **Given** the codebase is scanned for `session.query(`, **when** the scan is run against all source files, **then** zero occurrences of `session.query(` are found.

2. **Given** a model fetch that previously used `session.query(Model).filter(...).all()`, **when** the migrated code is executed against a test database with known rows, **then** it returns the same list of model instances as the legacy call did.

3. **Given** a query that previously used `session.query(Model).first()`, **when** the migrated code is executed, **then** it returns a single model instance (not a `Row` wrapper) or `None` when no rows match.

4. **Given** a query that previously used `session.query(Model).one()` with exactly one matching row, **when** the migrated code is executed, **then** it returns that single model instance without error.

5. **Given** a query that previously used `session.query(Model).one()` with zero or multiple matching rows, **when** the migrated code is executed, **then** it raises `NoResultFound` or `MultipleResultsFound` respectively, matching the legacy behavior.

6. **Given** a count query that previously used `session.query(Model).count()`, **when** the migrated `select(func.count())` equivalent is executed, **then** it returns the same integer count for identical data.

7. **Given** a column-projection query that previously returned `KeyedTuple` rows, **when** the migrated query is executed, **then** result fields are accessible by the same attribute names on the returned `Row` objects.

8. **Given** a bulk update that previously used `Query.update({...})`, **when** the migrated `update()` construct is executed, **then** the same rows are modified with the same values and the session state is consistent (no stale in-memory objects).

9. **Given** a bulk delete that previously used `Query.delete()`, **when** the migrated `delete()` construct is executed, **then** the same rows are removed and the session state is consistent.

10. **Given** the full test suite is run after migration, **when** all tests execute, **then** zero SQLAlchemy `LegacyAPIWarning` or `RemovedIn20Warning` deprecation warnings are emitted.

11. **Given** the application is run with SQLAlchemy configured in `future=True` mode (1.4 compatibility check) or upgraded to SQLAlchemy 2.x, **when** all query paths are exercised, **then** no `AttributeError` or `InvalidRequestError` is raised due to missing `Query` API methods.

12. **Given** any function previously type-annotated with `Query` as a parameter or return type, **when** static type checking is run, **then** no type errors related to `Query` usage are reported.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current pinned version of SQLAlchemy in use? This determines whether `future=True` mode is available as an intermediate validation step. | TODO | TODO |
| 2 | Are there any dynamic query-building utilities or helper classes that wrap `Session.query()` internally (e.g., a repository base class or query builder)? These require a single coordinated change rather than call-site-by-call-site migration. | TODO | TODO |
| 3 | Are `Query.update()` / `Query.delete()` calls using `synchronize_session='evaluate'` or `'fetch'`? The correct replacement strategy differs between these modes and must be confirmed before migration. | TODO | TODO |
| 4 | Are there any external libraries or plugins (e.g., Flask-SQLAlchemy, FastAPI dependencies, pagination libraries) that internally use `Session.query()` and are not under this codebase's control? | TODO | TODO |
| 5 | Is there a target SQLAlchemy version to land on (e.g., 2.0.x, 2.1.x)? The exact target version affects which new APIs (e.g., `session.scalars()` shorthand) are available. | TODO | TODO |
| 6 | Are there existing integration or unit tests with sufficient coverage of query paths to validate behavioral equivalence after migration, or does a test gap analysis need to precede the migration? | TODO | TODO |