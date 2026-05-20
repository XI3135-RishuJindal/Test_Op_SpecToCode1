# Plan: SQLAlchemy 1.3 → 2.0 Migration

> **Spec reference:** Upgrade SQLAlchemy 1.3 to 2.0 and migrate models and session patterns
> **Strategy classification:** Moderate effort migration

---

## Overview

The migration adopts a **strangler-fig / feature-flag gated** approach rather than a big-bang rewrite. SQLAlchemy 2.0 ships a deliberate bridge mechanism — the `SQLALCHEMY_WARN_20` future-warnings mode available in SQLAlchemy 1.4 — that allows incremental elimination of legacy patterns before the final version pin is moved to 2.0.

**Rationale:**
- Urgency is **medium**, meaning production stability must be preserved throughout; a big-bang cut-over introduces unacceptable regression risk.
- SQLAlchemy 1.4 acts as a compatibility shim: it runs existing 1.3 code while emitting deprecation warnings for every pattern that breaks in 2.0, giving a measurable, file-by-file migration checklist.
- Each layer (engine, session, ORM models, query API) can be migrated and tested independently before the final 2.0 pin.
- Rollback at any phase requires only a dependency version revert, not a code revert, until Phase 4.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| **1 — Audit & Baseline** | Pin to SQLAlchemy 1.4; enable `SQLALCHEMY_WARN_20=1`; run full test suite; capture all deprecation warnings as a migration checklist | None | TODO person-days — derive from project warning count |
| **2 — Engine & Connection Layer** | Migrate `create_engine()` calls to use `future=True`; replace `engine.execute()` with explicit `with engine.connect() as conn` context managers; update connection-level `execute()` calls to `conn.execute(text(...))` | Phase 1 complete | TODO |
| **3 — Session & Unit-of-Work Patterns** | Replace `Session.execute(string)` with `Session.execute(text(...))`; migrate `session.query()` patterns to `select()` constructs; enforce `autocommit=False` explicitly; update `sessionmaker` / `scoped_session` configurations | Phase 2 complete | TODO |
| **4 — ORM Model Declarations** | Migrate `DeclarativeBase` usage to the 2.0 `DeclarativeBase` class API; add `Mapped[]` type annotations; replace `Column()` with `mapped_column()`; update relationship `lazy` defaults where behaviour changed | Phase 3 complete | TODO |
| **5 — Final Pin & Cleanup** | Bump dependency to SQLAlchemy `>=2.0,<3.0`; remove all 1.x compatibility shims; delete `future=True` flags (now default); run full regression and performance suite | Phase 4 complete | TODO |

> **Note:** Effort estimates are marked TODO because the upgrade option did not supply person-day figures and the tech analysis did not enumerate codebase size or warning volume. Populate after Phase 1 audit produces a concrete warning count.

---

## Component Changes

### Engine Initialisation

**What changes:** `create_engine()` must gain `future=True` in Phase 2 (no-op in 1.4, enforces 2.0 semantics). In Phase 5 the flag is removed as it becomes the default.

**Files affected:** Any module containing `create_engine(...)` calls.

**API changes:**
- `engine.execute(...)` → removed; replace with `with engine.connect() as conn: conn.execute(...)`
- `engine.scalar(...)` → removed; use `conn.scalar(...)`
- Raw string SQL must be wrapped: `conn.execute("SELECT 1")` → `conn.execute(text("SELECT 1"))`

---

### Session Factory & Scoped Sessions

**What changes:** Session configuration and execution patterns.

**Files affected:** Any module containing `sessionmaker(...)`, `scoped_session(...)`, or `Session(...)` instantiation.

**API changes:**
- `Session.execute("raw sql")` → `Session.execute(text("raw sql"))`
- `session.query(Model).filter(...)` → `session.execute(select(Model).where(...)).scalars()`
- `session.query(Model).get(pk)` → `session.get(Model, pk)`
- `session.query(Model).first()` → `session.execute(select(Model)).scalars().first()`
- `Session(autocommit=True)` → removed; use explicit `with session.begin()` blocks
- `Query.update()` / `Query.delete()` bulk operations → `update(Model)` / `delete(Model)` DML constructs

---

### ORM Model Declarations

**What changes:** Model base class and column declarations updated to 2.0 style.

**Files affected:** All files containing `Base = declarative_base()` and subclasses of that base.

**API changes:**

| 1.3 Pattern | 2.0 Pattern |
|-------------|-------------|
| `Base = declarative_base()` | `class Base(DeclarativeBase): pass` |
| `Column(Integer, primary_key=True)` | `id: Mapped[int] = mapped_column(primary_key=True)` |
| `Column(String, nullable=True)` | `name: Mapped[Optional[str]] = mapped_column()` |
| `relationship("Child")` | `children: Mapped[List["Child"]] = relationship()` |
| `@declared_attr` on mixins | Unchanged but verify compatibility |

> **Note:** `declarative_base()` still works in 2.0 as a legacy alias but emits deprecation warnings. Migrate to `DeclarativeBase` subclass for forward compatibility.

---

### Query Construction (Application Layer)

**What changes:** All `session.query()` call sites replaced with Core-style `select()` statements.

**Files affected:** TODO — enumerate after Phase 1 warning audit.

**API changes:**
- `session.query(Model).filter(Model.col == val)` → `select(Model).where(Model.col == val)`
- `session.query(func.count(Model.id))` → `select(func.count(Model.id))`
- Chained `.join()` semantics change: explicit `ON` clause now required in most cases

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `SQLAlchemy` | `1.3.x` | `2.0.x` | Yes — significant | Use 1.4 as intermediate step with `SQLALCHEMY_WARN_20=1`; see phase plan above |
| `alembic` | TODO — check lockfile | Latest compatible with SQLAlchemy 2.0 | Minor | Alembic ≥ 1.8 required for SQLAlchemy 2.0 support; verify `env.py` uses `engine.begin()` context |
| `databases` / async drivers (if used) | TODO | TODO | TODO | `aiosqlite`, `asyncpg` binding APIs changed in SQLAlchemy 2.0 async extension |
| ORM-adjacent libs (e.g. `flask-sqlalchemy`, `fastapi-sqlalchemy`) | TODO | TODO | TODO | Must verify each wrapper library supports SQLAlchemy 2.0; many required major version bumps |

> **All version numbers marked TODO** because the tech analysis did not supply a resolved dependency lockfile. Populate this table from the project's `requirements.txt`, `Pipfile.lock`, or `pyproject.toml` before beginning Phase 1.

---

## Infrastructure Changes

TODO — No infrastructure context was provided. Assess the following before Phase 1:

- **Docker base image:** Verify Python version in `Dockerfile`; SQLAlchemy 2.0 requires Python ≥ 3.7 (3.8+ recommended).
- **CI/CD pipeline:** Add a `SQLALCHEMY_WARN_20=1` environment variable to the Phase 1–3 CI job to surface deprecation warnings as test output.
- **Database drivers:** Confirm `psycopg2`, `pymysql`, `cx_Oracle`, or other DBAPI drivers are on versions compatible with SQLAlchemy 2.0 (check SQLAlchemy 2.0 dialect support matrix).
- **Kubernetes / IaC:** TODO — not mentioned in context.

---

## Rollback Strategy

### Phase 1 Rollback
- Revert `SQLAlchemy` pin from `1.4.x` back to `1.3.x` in the dependency file.
- Remove `SQLALCHEMY_WARN_20=1` environment variable.
- No code changes have been made; rollback is a single-line dependency revert.

### Phase 2 Rollback
- Revert `future=True` additions to `create_engine()` calls (or wrap in a config flag).
- Revert `engine.execute()` → `conn.execute()` changes if any were merged.
- Pin back to `SQLAlchemy 1.4.x` (still runs 1.3-style code).

### Phase 3 Rollback
- Revert session execution changes (`text()` wrapping, `select()` migrations) via git revert on the session-layer PR.
- Pin back to `SQLAlchemy 1.4.x`.

### Phase 4 Rollback
- Revert model declaration changes (`mapped_column`, `Mapped[]`, `DeclarativeBase`) via git revert on the models PR.
- Pin back to `SQLAlchemy 1.4.x`.
- **Note:** If Alembic migrations were generated during Phase 4, those must also be rolled back before reverting model code.

### Phase 5 Rollback
- Revert dependency pin from `>=2.0,<3.0` to `1.4.x`.
- Re-add `future=True` to `create_engine()` calls (required for 1.4 to behave like 2.0).
- This is the highest-risk rollback; avoid by ensuring Phase 4 is fully validated before executing Phase 5.

---

## Testing Strategy

### Unit Tests
- **Target:** All model classes, query-builder helpers, and session utility functions.
- **Tool:** `pytest` with `pytest-mock` for session mocking.
- **Coverage gate:** TODO — establish baseline coverage from current suite before Phase 1; do not allow coverage regression between phases.
- **Specific checks:** Assert `Mapped[]` annotations resolve correctly; assert `mapped_column()` defaults match previous `Column()` behaviour.

### Integration Tests
- **Target:** All database interaction paths — CRUD operations, transactions, bulk operations, relationship loading.
- **Tool:** `pytest` + real database instance (SQLite in-memory acceptable for most tests; use target production dialect for dialect-specific tests).
- **Coverage gate:** All existing integration tests must pass at each phase boundary before merging.
- **Specific checks:**
  - `session.get()` returns same result as legacy `session.query().get()`
  - `select()` constructs return equivalent result sets to replaced `session.query()` calls
  - Lazy/eager loading behaviour unchanged on all relationships

### Regression Tests
- **Target:** Full application smoke tests covering all database-touching endpoints or service methods.
- **Tool:** Existing regression suite (TODO — identify framework from project context).
- **Gate:** Zero new failures introduced at each phase merge.
- **Phase 1 specific:** Capture `DeprecationWarning` output as a baseline checklist; treat any *new* warning introduced after Phase 1 as a test failure.

### Performance Tests
- **Target:** High-volume query paths, bulk insert/update operations.
- **Tool:** TODO — no performance testing framework identified in context.
- **Gate:** No more than 5% regression in query throughput between 1.3 baseline and 2.0 final (SQLAlchemy 2.0 generally improves performance, but `select()` construct compilation overhead should be verified).
- **Timing:** Run performance baseline in Phase 1; compare again in Phase 5.

### CI Gates
- Phase 1 merge gate: test suite passes on SQLAlchemy 1.4 with `SQLALCHEMY_WARN_20=1`; warning report artifact published.
- Phase 2–4 merge gates: full test suite green; no new deprecation warnings introduced.
- Phase 5 merge gate: full test suite green on SQLAlchemy 2.0; performance comparison report reviewed and approved.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Dependency audit complete; warning inventory published | Phase 1 | TODO — set after repo access | TODO |
| Engine & connection layer migrated | Phase 2 | TODO | TODO |
| Session patterns migrated | Phase 3 | TODO | TODO |
| ORM models migrated | Phase 4 | TODO | TODO |
| SQLAlchemy 2.0 pin live in production | Phase 5 | TODO | TODO |

> **Note:** All timeline estimates are marked TODO because the upgrade option did not supply person-day figures and the codebase size is unknown. After Phase 1 produces a warning count, use the heuristic of **~0.5 hours per distinct warning location** to size Phases 2–4, plus fixed overhead of ~1 day each for Phase 1 audit and Phase 5 final validation.