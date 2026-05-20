# Spec: Upgrade SQLAlchemy 1.3 → 2.0 and Migrate Models & Session Patterns

---

## Summary

This spec covers the upgrade of SQLAlchemy from version 1.3 to version 2.0, including the migration of all ORM model definitions, query patterns, and session management code to conform to the SQLAlchemy 2.0 API. The expected outcome is a codebase that runs exclusively on the SQLAlchemy 2.0 engine, eliminates all legacy 1.x compatibility shims, and passes the full test suite without deprecation warnings related to SQLAlchemy.

---

## Motivation

- **End-of-life / maintenance status:** SQLAlchemy 1.3 is no longer receiving bug fixes or security patches. SQLAlchemy 1.4 served as a transitional release; 2.0 is the current supported major version.
- **Security exposure:** Running an unmaintained ORM layer means any future database-layer CVEs will not receive upstream patches, creating unquantifiable security risk.
- **Deprecation debt:** SQLAlchemy 1.4 introduced `RemovedIn20Warning` deprecation warnings for every API that was removed in 2.0. Any codebase still on 1.3 has accumulated this debt without visibility into it, meaning the full scope of breaking changes is not yet surfaced.
- **API correctness:** SQLAlchemy 2.0 enforces stricter typing, explicit transaction control, and a unified `select()` construct, reducing the class of silent data bugs possible under the legacy query interface.
- **Upgrade urgency:** Rated **medium** — no active CVE is currently cited, but the unmaintained status creates compounding risk over time.
- **Ecosystem alignment:** Downstream libraries (e.g., Alembic, FastAPI/SQLModel, async drivers) have dropped or are dropping SQLAlchemy 1.x compatibility, creating integration friction.

---

## Current State

Based on the SQLAlchemy 1.3 API surface, the following patterns are expected to be present in the codebase. Specific class names, config keys, and schema elements are marked TODO where source code was not provided.

### ORM Models
- Declarative base created via `declarative_base()` from `sqlalchemy.ext.declarative`.
- Model classes inherit from this base and define `__tablename__`, `Column(...)`, and relationship definitions.
- `Column` type imports sourced from `sqlalchemy` top-level namespace.
- `relationship()` back-references defined using the string `backref=` argument.
- TODO: Enumerate specific model class names and their column/relationship definitions from source.

### Session Management
- Sessions created via `sessionmaker(bind=engine)` bound directly to an `Engine` instance.
- Session usage follows the `session.query(Model)` legacy query interface.
- Transactions managed implicitly (autocommit/autoflush defaults) or via `session.commit()` / `session.rollback()` called ad hoc.
- Scoped sessions (`scoped_session`) may be in use for request-scoped lifecycle management — TODO: confirm.

### Query Patterns
- Queries constructed using `session.query(Model).filter(...)`, `.filter_by(...)`, `.all()`, `.first()`, `.one()`, `.one_or_none()`.
- Bulk operations via `session.bulk_insert_mappings()` / `session.bulk_update_mappings()` — TODO: confirm usage.
- `Query.update()` and `Query.delete()` with `synchronize_session` parameter — TODO: confirm usage.

### Engine & Connection
- Engine created via `create_engine(url, ...)` — this call signature is largely unchanged but some keyword arguments differ in 2.0.
- Raw SQL executed via `engine.execute()` or `connection.execute(string_sql)` — both removed in 2.0.
- `engine.execute()` shortcut used in migration scripts or utility code — TODO: confirm.

### Configuration Keys
- `pool_size`, `max_overflow`, `pool_timeout`, `echo` passed to `create_engine()` — these remain valid in 2.0.
- `convert_unicode` parameter — removed in 2.0.
- TODO: Identify any `execution_options` or `connect_args` in use.

### Schema / Alembic Migrations
- TODO: Confirm Alembic version in use and whether `env.py` uses legacy `connection.execute()` patterns.

---

## Proposed Changes

### Summary Table

| Component | Before (1.3) | After (2.0) | Breaking? |
|---|---|---|---|
| Declarative base import | `sqlalchemy.ext.declarative.declarative_base()` | `sqlalchemy.orm.declarative_base()` or `DeclarativeBase` subclass | Y |
| Session factory binding | `sessionmaker(bind=engine)` | `sessionmaker(bind=engine)` still accepted; `Session(bind=...)` deprecated — migrate to `with Session(engine)` context manager pattern | Y |
| Legacy query interface | `session.query(Model).filter(...)` | `session.execute(select(Model).where(...))` with `select()` construct | Y |
| `Query.update()` / `Query.delete()` | `session.query(Model).filter(...).update(...)` | `session.execute(update(Model).where(...).values(...))` | Y |
| `engine.execute()` | `engine.execute(sql)` | Removed — use `with engine.connect() as conn: conn.execute(...)` | Y |
| Raw string SQL execution | `connection.execute("SELECT ...")` | `connection.execute(text("SELECT ..."))` — must wrap in `text()` | Y |
| `bulk_insert_mappings` / `bulk_update_mappings` | `session.bulk_insert_mappings(Model, data)` | `session.execute(insert(Model), data)` | Y |
| `backref` string shorthand | `relationship("Child", backref="parent")` | Explicit `back_populates=` on both sides (recommended); `backref` still works but emits warnings | N (soft) |
| `convert_unicode` engine param | `create_engine(url, convert_unicode=True)` | Parameter removed — drop it | Y |
| `autocommit` mode | `Session(autocommit=True)` | Removed — use explicit `with session.begin()` blocks | Y |
| Result row access | `row.column_name` attribute access on `RowProxy` | `row._mapping["column_name"]` or named-tuple style via `Row` | Y |
| `Query.get()` | `session.query(Model).get(pk)` | `session.get(Model, pk)` | Y |
| Alembic `env.py` connection pattern | `connection.execute(op.get_bind())` legacy patterns | Updated to use `connectable.connect()` with context manager | Y |

### What Is Removed
- All `session.query(...)` call sites replaced with `select()`-based execution.
- `engine.execute()` and `connection.execute(raw_string)` call sites removed.
- `convert_unicode` engine parameter removed.
- `Session(autocommit=True)` usage removed.
- `sessionmaker(bind=engine)` direct bind pattern replaced with explicit connection/context-manager patterns where applicable.

### What Is Added
- `select()`, `insert()`, `update()`, `delete()` constructs from `sqlalchemy` imported and used uniformly.
- `text()` wrapper applied to all raw SQL strings.
- `with Session(engine) as session:` / `with session.begin():` explicit transaction blocks introduced.
- `session.get(Model, pk)` replaces `session.query(Model).get(pk)`.
- TODO: Determine whether `MappedColumn` / `Mapped[T]` typed annotation style (2.0 native) will be adopted now or deferred.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `session.query()` removed from 2.0 strict mode | All query call sites | Replace with `session.execute(select(...).where(...))` and unpack results via `.scalars()` or `.all()` |
| `engine.execute()` removed | Any utility or script using shortcut execution | Replace with explicit `with engine.connect() as conn:` block |
| Raw string SQL without `text()` raises `ArgumentError` | Any ad-hoc SQL strings | Wrap all raw SQL strings in `text()` |
| `Session(autocommit=True)` removed | Any session configured with autocommit | Refactor to explicit `session.begin()` / `session.commit()` blocks |
| `declarative_base()` moved to `sqlalchemy.orm` | Model base class import | Update import path; old path emits deprecation warning in 1.4, removed in 2.0 |
| `RowProxy` replaced by `Row` | Any code accessing result rows by attribute or index | Use `.scalars()` for single-column results; use `row._mapping` or positional access for multi-column rows |
| `Query.get(pk)` removed | Any primary-key lookup via query interface | Replace with `session.get(Model, pk)` |
| `bulk_insert_mappings` / `bulk_update_mappings` removed | Bulk operation call sites | Replace with `session.execute(insert(Model), list_of_dicts)` |
| `convert_unicode` engine kwarg removed | `create_engine()` call sites | Remove the parameter entirely |
| Implicit transaction autobegin behavior changed | Code relying on implicit transaction state | Audit all `session.commit()` / `session.rollback()` call sites; wrap operations in explicit `begin()` blocks |
| Alembic `env.py` legacy patterns | Database migration execution | Update `env.py` to use `connectable.connect()` context manager per Alembic 2.0-compatible template — TODO: confirm Alembic version |

---

## Acceptance Criteria

1. **Given** the upgraded dependencies are installed, **when** the application process starts, **then** no `RemovedIn20Warning` or `LegacyAPIWarning` from SQLAlchemy appears in the log output or test output.

2. **Given** the full unit and integration test suite, **when** tests are executed against the upgraded codebase, **then** all tests that passed on SQLAlchemy 1.3 continue to pass with no new failures attributable to the ORM upgrade.

3. **Given** any model class definition, **when** the declarative base is inspected at import time, **then** no `SADeprecationWarning` is raised related to `declarative_base` import path or `backref` usage.

4. **Given** a database session, **when** a record is fetched by primary key, **then** `session.get(Model, pk)` returns the correct instance and no `session.query()` call is present in the codebase.

5. **Given** a raw SQL string is executed anywhere in the codebase, **when** that code path is exercised, **then** the string is wrapped in `text()` and no `ArgumentError` or `ObjectNotExecutableError` is raised.

6. **Given** a session performing a write operation, **when** the operation completes, **then** the transaction is explicitly committed or rolled back via a context manager or explicit call — no implicit autocommit behavior is relied upon.

7. **Given** the `create_engine()` call, **when** the engine is instantiated, **then** no `TypeError` is raised due to unrecognized keyword arguments (e.g., `convert_unicode` is absent).

8. **Given** a bulk insert operation, **when** a list of records is inserted, **then** the operation uses the 2.0 `insert()` construct and completes without error.

9. **Given** the Alembic migration environment, **when** `alembic upgrade head` is executed against a clean schema, **then** all migrations apply successfully without errors related to deprecated SQLAlchemy connection patterns.

10. **Given** CI is configured with `SQLALCHEMY_WARN_20=1` (or equivalent 2.0 strict-mode flag), **when** the test suite runs, **then** zero SQLAlchemy deprecation warnings are emitted and the CI check passes.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact list of ORM model classes and their relationships that need to be audited? | TODO | TODO |
| 2 | Is `scoped_session` in use for request lifecycle management (e.g., web framework integration)? If so, which web framework? | TODO | TODO |
| 3 | Will the team adopt the new SQLAlchemy 2.0 `Mapped[T]` / `MappedColumn` typed annotation style now, or defer to a follow-on task? | TODO | TODO |
| 4 | What version of Alembic is currently in use, and does `env.py` require updates for 2.0 compatibility? | TODO | TODO |
| 5 | Are async SQLAlchemy patterns (`AsyncSession`, `create_async_engine`) in scope for this upgrade, or strictly out of scope? | TODO | TODO |
| 6 | Are there any direct `psycopg2` / `cx_Oracle` / other DBAPI call sites that bypass SQLAlchemy and may be affected by connection handling changes? | TODO | TODO |
| 7 | Is `SQLALCHEMY_WARN_20` or `__allow_unmapped__` currently set anywhere in the codebase or test configuration? | TODO | TODO |
| 8 | What is the target SQLAlchemy 2.0 patch version (e.g., 2.0.x latest stable)? | TODO | TODO |