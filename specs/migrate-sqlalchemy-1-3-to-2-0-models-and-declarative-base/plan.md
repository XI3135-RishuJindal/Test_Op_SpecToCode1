# Plan: Migrate SQLAlchemy 1.3 to 2.0 — Models and Declarative Base

---

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The migration will proceed incrementally using SQLAlchemy 2.0's built-in compatibility bridge (`SQLALCHEMY_WARN_20=1` and `future=True` engine flag) as a strangler-fig mechanism. This allows the codebase to run against SQLAlchemy 1.4 in "2.0 compatibility mode" first, surface all deprecation warnings, and then complete the final cut-over to SQLAlchemy 2.0.

**Justification:**
- The upgrade urgency is rated **medium**, indicating no immediate production blocker but meaningful tech debt accumulation.
- A big-bang rewrite carries unnecessary risk given that SQLAlchemy 1.4 provides a full deprecation shim — skipping it would eliminate the safety net.
- The strangler-fig approach allows individual models and query sites to be migrated and tested in isolation, reducing regression surface at each step.
- Rollback at any phase is straightforward because 1.4 and 2.0-style code can coexist during the transition window.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & Inventory — catalogue all models, `declarative_base()` usages, `Session` patterns, and legacy query API calls | None | TODO person-days (derive from option) |
| 2 | Upgrade to SQLAlchemy 1.4 with `future=True`; enable `SQLALCHEMY_WARN_20=1`; fix all emitted deprecation warnings | Phase 1 complete | TODO person-days |
| 3 | Migrate `declarative_base()` → `DeclarativeBase` / `MappedAsDataclass` (2.0 style); update `Column` → `mapped_column`; add `Mapped[T]` type annotations | Phase 2 clean (zero warnings) | TODO person-days |
| 4 | Replace all legacy `Session.query()` calls with `select()` / `Session.execute()`; update relationship declarations | Phase 3 complete | TODO person-days |
| 5 | Final cut-over: upgrade package pin to SQLAlchemy `>=2.0`; remove 1.4 shim flags; full regression run | Phase 4 complete | TODO person-days |
| 6 | Observability & Stabilisation — monitor query performance, fix any N+1 or lazy-load regressions surfaced by 2.0 stricter defaults | Phase 5 deployed | TODO person-days |

> **Note:** Specific person-day estimates are marked TODO because the upgrade option detail was not provided. Populate from the approved effort estimate before finalising this plan.

---

## Component Changes

### 2.1 Declarative Base

**What changes:**
- `declarative_base()` (legacy function API) is replaced by the new class-based `DeclarativeBase`.
- All model classes that currently inherit from the old base must inherit from the new base class.

**Files affected:** TODO — identify via `grep -r "declarative_base" .`

**Before (1.3/1.4 style):**
```python
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

**After (2.0 style):**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
```

**APIs modified:**
- `sqlalchemy.ext.declarative.declarative_base` → `sqlalchemy.orm.DeclarativeBase`
- `Column(Type, ...)` → `mapped_column(...)` with `Mapped[T]` annotation
- `relationship("ModelName")` string references → direct type references where possible; `Mapped[List["ModelName"]]` annotations required

---

### 2.2 Session and Engine

**What changes:**
- `create_engine()` gains `future=True` in Phase 2 (already the default in 2.0).
- `sessionmaker` usage is unchanged in signature but `Session.query()` calls must be replaced.
- `Session.execute(select(Model))` replaces `Session.query(Model).filter(...)`.

**Files affected:** TODO — identify via `grep -r "Session.query\|create_engine\|sessionmaker" .`

**APIs modified:**
- `session.query(User).filter(User.id == 1).first()` → `session.execute(select(User).where(User.id == 1)).scalar_one_or_none()`
- `session.query(User).all()` → `session.execute(select(User)).scalars().all()`
- `create_engine(url)` → `create_engine(url, future=True)` (Phase 2), then remove `future=True` flag (Phase 5, it is the default)

---

### 2.3 Relationship Declarations

**What changes:**
- `relationship()` calls must be annotated with `Mapped[...]` in 2.0 style.
- `backref` string shorthand is deprecated; replace with explicit `back_populates`.
- Lazy loading behaviour is unchanged by default but `lazy="dynamic"` is removed in 2.0 — replace with `lazy="select"` + explicit `select()` queries or `lazy="write_only"`.

**Files affected:** TODO — identify via `grep -r "relationship\|backref\|lazy=" .`

**APIs modified:**
- `relationship("Child", backref="parent")` → explicit `back_populates` on both sides with `Mapped[List["Child"]]` annotation
- `lazy="dynamic"` → `lazy="write_only"` or refactored to explicit queries

---

### 2.4 Alembic Migrations (if present)

**What changes:**
- Alembic must be upgraded to a version compatible with SQLAlchemy 2.0 (see Dependency Upgrade Plan).
- `env.py` `target_metadata` assignment is unaffected.
- Auto-generated migrations may produce diff noise due to type annotation changes — review all auto-generated scripts before applying.

**Files affected:** `alembic/env.py`, `alembic/versions/*.py` (review only, no bulk edits required)

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `sqlalchemy` | 1.3.x | 2.0.x | Yes — `Session.query()` removed; `declarative_base()` moved; `lazy="dynamic"` removed; `Column` still works but `mapped_column` preferred | Use 1.4 as intermediate step with `future=True` and `SQLALCHEMY_WARN_20=1` to surface all breakage before final cut-over |
| `alembic` | TODO (current pin) | TODO (2.0-compatible) | Minor — ensure `alembic >= 1.9.0` for SQLAlchemy 2.0 support | TODO — confirm current version from `requirements.txt` or `pyproject.toml` |
| `greenlet` | TODO | TODO | Required by SQLAlchemy async; version constraint changes in 2.0 | TODO — only relevant if async sessions are used |
| `typing_extensions` | TODO | `>= 4.2.0` | None | Required for `Mapped` / `mapped_column` type machinery in Python < 3.11 |

> **Note:** All version numbers marked TODO must be confirmed from the project's `requirements.txt`, `pyproject.toml`, or `setup.cfg` before this plan is executed. Do not source versions from memory.

---

## Infrastructure Changes

**Docker base image:** TODO — not derivable from provided context. Confirm Python runtime version in `Dockerfile`; SQLAlchemy 2.0 requires Python ≥ 3.7 (3.8+ recommended).

**Kubernetes manifests:** TODO — no manifest context provided. No expected changes unless environment variables (e.g. `DATABASE_URL`) are affected.

**CI/CD pipeline:**
- Add `SQLALCHEMY_WARN_20=1` as an environment variable in the CI test job during Phase 2; treat warnings as errors (`-W error::DeprecationWarning` in pytest config or `filterwarnings = error` in `pytest.ini`).
- Remove `SQLALCHEMY_WARN_20=1` after Phase 5 cut-over.
- Pin `sqlalchemy>=1.4,<2.0` in CI during Phases 2–4; change to `sqlalchemy>=2.0,<3.0` in Phase 5.

**IaC:** TODO — not mentioned in context.

---

## Rollback Strategy

### Phase 1 (Audit)
- No code changes made; rollback is a no-op.

### Phase 2 (Upgrade to 1.4 + warnings)
- Revert `requirements.txt` / `pyproject.toml` pin from `sqlalchemy>=1.4` back to `sqlalchemy>=1.3,<1.4`.
- Remove `future=True` from `create_engine()` calls.
- Remove `SQLALCHEMY_WARN_20=1` from CI environment.
- Re-run test suite to confirm green.

### Phase 3 (Declarative Base migration)
- Each model file should be migrated in a separate commit or PR.
- Revert individual model files via `git revert` or branch reset.
- The old `Base = declarative_base()` and new `class Base(DeclarativeBase)` can coexist temporarily if both are imported correctly — use this as a short-term safety net.

### Phase 4 (Query API migration)
- Each query site migrated in isolation (per module/service boundary).
- Revert individual modules via `git revert`.
- `Session.query()` still works in SQLAlchemy 1.4 — no runtime breakage if a revert is needed mid-phase.

### Phase 5 (Final cut-over to 2.0)
- Revert `requirements.txt` pin from `sqlalchemy>=2.0` back to `sqlalchemy>=1.4,<2.0`.
- Re-add `future=True` to `create_engine()` if needed for 1.4 compatibility mode.
- Confirm test suite passes on 1.4 before declaring rollback complete.

### Phase 6 (Stabilisation)
- Performance regressions: add explicit `lazy="select"` or `joinedload()` hints to affected relationships.
- No dependency rollback required at this phase.

---

## Testing Strategy

### Unit Tests
- **Tool:** `pytest`
- **Scope:** Individual model classes — test `__tablename__`, column types, defaults, and `__repr__` if defined.
- **Coverage target:** 100% of model files touched in Phase 3.
- **CI gate:** Must pass before any Phase 3 PR is merged.

### Integration Tests
- **Tool:** `pytest` + `pytest-sqlalchemy` (or equivalent in-repo fixture) against a real database (SQLite in-memory acceptable for schema tests; match production dialect for query tests).
- **Scope:** All `Session.execute()` / `select()` call sites migrated in Phase 4; relationship traversals; cascade behaviours.
- **Coverage target:** All query paths that previously used `Session.query()`.
- **CI gate:** Must pass on both SQLAlchemy 1.4 (Phases 2–4) and 2.0 (Phase 5).

### Regression Tests
- **Tool:** Existing test suite run unmodified.
- **Scope:** Full suite executed after each phase merge.
- **Special gate (Phase 2):** Run with `SQLALCHEMY_WARN_20=1` and `filterwarnings = error::DeprecationWarning` in `pytest.ini` — zero warnings required before advancing to Phase 3.

### Performance Tests
- **Tool:** TODO — confirm existing performance/load test tooling from project context.
- **Scope:** Key query paths, especially any that used `lazy="dynamic"` (replaced in Phase 3/4) and bulk operations.
- **CI gate:** Phase 6 — compare query counts and latency against Phase 1 baseline; flag regressions > 10% for review.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; all affected files catalogued | Phase 1 | TODO | TODO |
| SQLAlchemy 1.4 pinned; zero deprecation warnings in CI | Phase 2 | TODO | TODO |
| All models migrated to `DeclarativeBase` + `mapped_column` | Phase 3 | TODO | TODO |
| All `Session.query()` calls replaced with `select()` | Phase 4 | TODO | TODO |
| SQLAlchemy 2.0 pin live; shim flags removed; full regression green | Phase 5 | TODO | TODO |
| Performance baseline confirmed; stabilisation complete | Phase 6 | TODO | TODO |

> **Note:** All estimated completion dates and owner assignments are marked TODO. Populate using the approved person-days from the upgrade option and the team's sprint calendar before circulating this plan for sign-off.