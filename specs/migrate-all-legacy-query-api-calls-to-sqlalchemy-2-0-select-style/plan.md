# PLAN: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

---

## Overview

**Migration Strategy: Strangler-Fig (incremental, module-by-module)**

The migration replaces legacy SQLAlchemy `session.query()` calls with the 2.0-style `select()` construct incrementally, one module or file at a time, rather than in a single big-bang rewrite.

**Justification:**
- The upgrade urgency is rated **medium**, indicating the codebase is functional but accumulating technical debt — a big-bang rewrite introduces unnecessary regression risk.
- The upgrade option is **moderate** effort, which is consistent with a phased approach that allows testing and validation between phases.
- SQLAlchemy 2.0 provides a `SQLALCHEMY_WARN_20` legacy compatibility flag, enabling parallel operation of old and new query styles during transition — this directly supports a strangler-fig approach.
- Rollback per phase is straightforward since old and new styles are syntactically isolated and can coexist within the same codebase during migration.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & inventory all `session.query()` call sites; enable `SQLALCHEMY_WARN_20=1` deprecation warnings; establish baseline test coverage | None | 2 person-days |
| 2 | Migrate data access layer (DAL) / repository modules — core query patterns first (simple selects, filters, joins) | Phase 1 complete | 3 person-days |
| 3 | Migrate remaining call sites (service layer, utility scripts, admin tooling) | Phase 2 complete | 2 person-days |
| 4 | Remove legacy compatibility shims; disable `SQLALCHEMY_WARN_20`; final regression and performance validation | Phase 3 complete | 1 person-day |

> **Note:** Total estimated effort is **~8 person-days**, consistent with a moderate-effort upgrade option. Exact per-file breakdown depends on audit results from Phase 1.

---

## Component Changes

### General Pattern Change

Every occurrence of the legacy Query API must be replaced with the 2.0 `select()` style:

**Before (legacy):**
```python
# session.query() style
results = session.query(User).filter(User.active == True).all()
record  = session.query(Order).filter_by(id=order_id).first()
count   = session.query(User).count()
```

**After (2.0 style):**
```python
from sqlalchemy import select, func

results = session.execute(select(User).where(User.active == True)).scalars().all()
record  = session.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
count   = session.execute(select(func.count()).select_from(User)).scalar()
```

### Key API Mapping

| Legacy Pattern | 2.0 Replacement |
|----------------|-----------------|
| `session.query(Model).all()` | `session.execute(select(Model)).scalars().all()` |
| `session.query(Model).first()` | `session.execute(select(Model)).scalars().first()` |
| `session.query(Model).one()` | `session.execute(select(Model)).scalars().one()` |
| `session.query(Model).filter(...)` | `select(Model).where(...)` |
| `session.query(Model).filter_by(...)` | `select(Model).where(...)` with explicit column equality |
| `session.query(Model).get(pk)` | `session.get(Model, pk)` *(2.0 preferred)* |
| `session.query(Model).count()` | `select(func.count()).select_from(Model)` |
| `session.query(Model).join(...)` | `select(Model).join(...)` |
| `session.query(Model).options(...)` | `select(Model).options(...)` |
| `session.query(Model).update(...)` | `session.execute(update(Model).where(...).values(...))` |
| `session.query(Model).delete(...)` | `session.execute(delete(Model).where(...))` |

### Files Affected

> **TODO:** Exact file list must be produced by the Phase 1 audit. The following are structural categories expected to contain call sites:

- **Data Access / Repository layer** — files responsible for database reads/writes (highest density of `session.query()` calls expected)
- **Service layer** — business logic files that call repositories or query directly
- **Model files** — any `__init__` or mixin methods on ORM models that use `session.query()`
- **Migration/seed scripts** — standalone scripts using legacy query style
- **Test fixtures and factories** — test helpers that construct or query records

### Imports to Update

Add to affected files:
```python
from sqlalchemy import select, update, delete, func, and_, or_
```

Remove where no longer needed:
```python
# session.query no longer needs to be imported explicitly
```

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| SQLAlchemy | TODO — confirm via `pip show sqlalchemy` or `requirements.txt` | TODO — confirm target (2.0.x) | `session.query()` is removed in 2.0; `Query.get()` removed; `autocommit` mode removed; `engine.execute()` removed | Enable `SQLALCHEMY_WARN_20=1` in Phase 1 to surface all deprecation warnings before upgrading; review [SQLAlchemy 2.0 migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) |

> **Note:** All version numbers are marked TODO because the tech analysis did not provide current or target version strings. These **must** be confirmed from the actual `requirements.txt`, `pyproject.toml`, or `setup.cfg` before Phase 1 begins. Do not assume versions from any other source.

---

## Infrastructure Changes

**TODO** — No infrastructure context was provided. The following items should be verified:

- **TODO:** Confirm whether CI pipeline runs SQLAlchemy deprecation warnings as errors (`-W error::DeprecationWarning`) — this gate should be added in Phase 1.
- **TODO:** Confirm Docker base image Python version is compatible with the target SQLAlchemy 2.0.x release.
- **TODO:** Confirm whether any ORM models are shared across services (microservice context) — if so, coordinate version pinning across service `requirements` files.
- **TODO:** Confirm whether Alembic is in use for migrations; Alembic 1.9+ is required for full SQLAlchemy 2.0 compatibility.

---

## Rollback Strategy

Each phase is independently reversible because old and new query styles coexist during migration.

### Phase 1 Rollback
- Remove `SQLALCHEMY_WARN_20=1` environment variable from local and CI environments.
- No code changes to revert; audit is read-only.

### Phase 2 Rollback
- Revert commits to the DAL/repository files migrated in Phase 2 using `git revert` or branch reset.
- The service layer and other modules remain on legacy style and continue to function.
- Re-run baseline test suite to confirm no regression.

### Phase 3 Rollback
- Revert commits to service layer and utility files migrated in Phase 3.
- DAL modules migrated in Phase 2 may remain on 2.0 style (they are backward-compatible with the rest of the codebase).
- Re-run integration tests to confirm.

### Phase 4 Rollback
- If compatibility shims were removed prematurely, restore them from the Phase 3 branch state.
- Re-enable `SQLALCHEMY_WARN_20=1` to re-identify any remaining legacy calls.
- Do **not** downgrade SQLAlchemy version unless Phases 2 and 3 are also fully reverted.

---

## Testing Strategy

### Test Pyramid

```
         [ Performance ]
        [  Regression   ]
       [ Integration     ]
      [ Unit              ]
```

#### Unit Tests
- **Scope:** Each migrated query method in isolation, using an in-memory SQLite database or mocked `Session`.
- **Tool:** `pytest` with `pytest-sqlalchemy` or direct `Session` fixtures.
- **Coverage target:** 100% of migrated query methods must have a passing unit test before the Phase PR is merged.
- **Assertion pattern:** Verify that `select()` statements produce the same result sets as the legacy `session.query()` calls they replace.

#### Integration Tests
- **Scope:** End-to-end data access flows — service calls through to database and back.
- **Tool:** `pytest` against a real test database (same engine as production, e.g., PostgreSQL in Docker).
- **Coverage target:** All repository/DAL public methods covered.
- **CI gate:** Integration test suite must pass before any Phase PR is merged to main.

#### Regression Tests
- **Scope:** Full application test suite run against the migrated codebase.
- **Tool:** Existing test suite (TODO — confirm framework); add `SQLALCHEMY_WARN_20=1` as an environment variable so any missed legacy calls surface as warnings/errors.
- **CI gate:** Zero new `SADeprecationWarning` or `RemovedIn20Warning` warnings after each phase.

#### Performance Tests
- **Scope:** Confirm that migrated queries do not introduce latency regressions on hot paths.
- **Tool:** TODO — confirm whether `pytest-benchmark` or a load testing tool (e.g., Locust) is in use.
- **Target:** Query execution time within ±10% of pre-migration baseline on critical read paths.
- **When:** Run at end of Phase 3 before Phase 4 cleanup begins.

### CI Gates Summary

| Gate | Phase | Condition |
|------|-------|-----------|
| Zero `RemovedIn20Warning` in migrated modules | 2, 3 | Enforced via `-W error::sqlalchemy.exc.RemovedIn20Warning` |
| Unit test coverage ≥ 100% on migrated files | 2, 3 | `pytest --cov` with coverage threshold |
| Integration tests pass | 2, 3, 4 | Required for PR merge |
| Zero legacy warnings in full codebase | 4 | Required for Phase 4 completion |

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; all `session.query()` call sites inventoried; `SQLALCHEMY_WARN_20` enabled in CI | 1 | End of Day 2 | TODO |
| DAL/repository modules fully migrated and tested | 2 | End of Day 5 | TODO |
| Service layer and utility scripts fully migrated and tested | 3 | End of Day 7 | TODO |
| Compatibility shims removed; full regression and performance sign-off; migration complete | 4 | End of Day 8 | TODO |

> **Note:** Day counts are cumulative from project start and derived from the moderate-effort estimate (~8 person-days total). Actual calendar dates depend on team scheduling and are marked TODO pending assignment.