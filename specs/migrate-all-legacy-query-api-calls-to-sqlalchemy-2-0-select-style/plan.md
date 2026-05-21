# PLAN: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

---

## Overview

**Migration Strategy: Strangler-Fig (incremental, module-by-module)**

The migration replaces legacy SQLAlchemy `session.query()` calls with the 2.0-style `select()` construct incrementally, one module or file at a time, rather than in a single big-bang rewrite.

**Justification:**
- The upgrade urgency is rated **medium**, indicating the codebase is functional but accumulating technical debt — a big-bang rewrite introduces unnecessary risk.
- The upgrade option is **moderate** effort, which aligns with an incremental approach: each module can be migrated, tested, and merged independently, keeping the main branch stable throughout.
- SQLAlchemy 2.0 provides a `SQLALCHEMY_WARN_20` legacy compatibility flag that allows both styles to coexist during transition, making strangler-fig directly supported by the framework.
- Rollback scope is limited to individual modules rather than the entire codebase.

> **TODO:** Confirm whether `SQLALCHEMY_WARN_20 = 1` / `legacy_query_interface` is currently enabled or suppressed in the application configuration.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & inventory all `session.query()` call sites; enable `SQLALCHEMY_WARN_20` deprecation warnings in CI | None | TODO: derive from moderate option person-days — estimated ~1–2 days |
| 2 | Migrate data-access layer / repository modules (core query logic) to `select()` style | Phase 1 complete | TODO: ~3–5 days |
| 3 | Migrate remaining call sites (views, services, utilities) | Phase 2 complete | TODO: ~2–3 days |
| 4 | Remove legacy compatibility shims; enforce 2.0-only style via linting/CI gate | Phase 3 complete | TODO: ~1 day |
| 5 | Regression, performance, and integration test pass; final review | Phase 4 complete | TODO: ~1–2 days |

> **TODO:** Exact person-day totals are not derivable from the provided upgrade option details. Populate from the formal estimate when available.

---

## Component Changes

> **TODO:** Specific file names, class names, and method names were not provided in the code context. The patterns below describe the structural changes required; file references must be populated once the codebase is inventoried in Phase 1.

### General Pattern: `session.query()` → `select()`

**Legacy style (to be removed):**
```python
# session.query() — SQLAlchemy 1.x Query API
results = session.query(User).filter(User.active == True).all()
scalar  = session.query(User).filter(User.id == user_id).one()
count   = session.query(User).filter(User.active == True).count()
```

**Target style (SQLAlchemy 2.0):**
```python
from sqlalchemy import select, func

# .all() equivalent
stmt    = select(User).where(User.active == True)
results = session.execute(stmt).scalars().all()

# .one() equivalent
stmt   = select(User).where(User.id == user_id)
scalar = session.execute(stmt).scalars().one()

# .count() equivalent
stmt  = select(func.count()).select_from(User).where(User.active == True)
count = session.execute(stmt).scalar_one()
```

### Key API Mapping

| Legacy (`session.query()`) | 2.0 Equivalent |
|---------------------------|----------------|
| `.all()` | `session.execute(stmt).scalars().all()` |
| `.one()` | `session.execute(stmt).scalars().one()` |
| `.one_or_none()` | `session.execute(stmt).scalars().one_or_none()` |
| `.first()` | `session.execute(stmt).scalars().first()` |
| `.count()` | `session.execute(select(func.count()).select_from(Model))` |
| `.filter()` | `.where()` |
| `.filter_by()` | `.where()` with explicit column references |
| `.join()` | `.join()` (syntax largely compatible) |
| `.options()` | `.options()` (unchanged) |
| `.with_entities()` | `select(col1, col2)` directly |
| `.update()` / `.delete()` | `sqlalchemy.update()` / `sqlalchemy.delete()` + `session.execute()` |

### Files Affected

> **TODO:** Populate with actual file paths after Phase 1 audit. Expected locations include:
> - `models/` or `db/` — ORM model definitions (likely no changes needed here)
> - `repositories/` or `dao/` — primary migration target
> - `services/` — secondary migration target
> - `views/` or `routes/` or `api/` — tertiary migration target
> - `tests/` — test fixtures and query assertions must be updated in parallel

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| SQLAlchemy | TODO (from tech analysis — not provided) | TODO (from tech analysis — not provided) | `session.query()` is removed in 2.0 final; deprecated with warnings in 1.4 | Enable `SQLALCHEMY_WARN_20=1` in Phase 1 to surface all legacy call sites before migration |

> **TODO:** Exact current and target version numbers were not provided in the tech analysis. Populate these from the formal tech analysis document before proceeding. Do not assume versions from training data.

> **TODO:** If any ORM extension libraries (e.g., `Flask-SQLAlchemy`, `SQLModel`, `SQLAlchemy-Utils`) are in use, their compatible versions must also be listed here after inventory.

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. Populate this section once the deployment environment is known.

The only infrastructure-adjacent change relevant to this task is:

- **CI/CD Pipeline:** Add `SQLALCHEMY_WARN_20=1` as an environment variable in the test runner configuration during Phase 1. This causes SQLAlchemy 1.4 to emit `RemovedIn20Warning` for every legacy call site, which should be treated as a CI failure (warnings-as-errors) to enforce migration progress.
  - **TODO:** Identify the CI configuration file (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`) to apply this change.

---

## Rollback Strategy

Each phase is independently reversible because the strangler-fig approach keeps legacy and new-style calls coexisting until Phase 4.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Remove `SQLALCHEMY_WARN_20=1` from CI environment. No code changes to revert. |
| **Phase 2** | Revert the repository/DAO module commits via `git revert` or branch reset. Legacy `session.query()` calls in those modules are restored. All other modules are unaffected. |
| **Phase 3** | Revert the service/view module commits via `git revert`. Repository modules may remain on 2.0 style or be reverted to match. |
| **Phase 4** | Revert removal of compatibility shims and linting rules. Re-enable `legacy_query_interface` if it was explicitly disabled. |
| **Phase 5** | No functional code changes in this phase; rollback is not applicable. If a defect is found, roll back to the last stable phase. |

**General principle:** Because no database schema changes are involved in this migration (it is purely a Python API change), there is no data migration to reverse. Any phase can be rolled back by reverting the relevant commits without risk to stored data.

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
- **Tools:** `pytest`, `pytest-mock`, SQLAlchemy's own `create_engine("sqlite:///:memory:")`.
- **Coverage Target:** TODO — establish baseline coverage before Phase 2 begins; target no regression below current baseline. Recommended minimum: **80% line coverage** on all modified files.
- **Approach:** For each converted method, assert that `session.execute()` is called with a `Select` object (not a `Query` object) and that return values are correctly unpacked via `.scalars()`.

#### Integration Tests
- **Scope:** End-to-end query execution against a real (test) database instance.
- **Tools:** `pytest`, `pytest-sqlalchemy` or equivalent fixture setup, test database matching production engine (PostgreSQL/MySQL/etc. — **TODO:** confirm engine from tech analysis).
- **Approach:** Run existing integration test suite unchanged after each phase. New-style queries must return identical result sets to the legacy queries they replace.
- **CI Gate:** Integration tests must pass before any phase branch is merged to main.

#### Regression Tests
- **Scope:** Full existing test suite run after each phase to detect unintended breakage.
- **Tools:** `pytest` with full suite; diff test results against pre-migration baseline.
- **CI Gate:** Zero new test failures permitted per phase merge.

#### Performance Tests
- **Scope:** Verify that migrated queries do not introduce latency regressions. SQLAlchemy 2.0-style queries are generally equivalent or faster, but bulk `.update()`/`.delete()` patterns may differ.
- **Tools:** TODO — identify existing performance/load test tooling (e.g., `locust`, `pytest-benchmark`).
- **CI Gate:** TODO — define acceptable latency thresholds once tooling is confirmed.

### Deprecation Warning Gate (Phase 1 specific)
- Configure `pytest` with `filterwarnings = error::sqlalchemy.exc.RemovedIn20Warning` in `pytest.ini` or `pyproject.toml`.
- This converts all legacy API usage into test failures, providing an automated inventory and a hard gate that prevents regression back to legacy style.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; deprecation warnings enabled in CI | Phase 1 | TODO | TODO |
| Repository/DAO layer fully migrated | Phase 2 | TODO | TODO |
| Services and views fully migrated | Phase 3 | TODO | TODO |
| Legacy API removed; lint rules enforced | Phase 4 | TODO | TODO |
| All tests passing; migration closed | Phase 5 | TODO | TODO |

> **TODO:** Absolute dates and owner assignments cannot be derived from the provided upgrade option details. Populate this table using the person-day estimates confirmed in the formal moderate-effort option and the team's sprint calendar.

---

*Document status: DRAFT — pending population of TODOs from formal tech analysis, code inventory (Phase 1), and team capacity planning.*