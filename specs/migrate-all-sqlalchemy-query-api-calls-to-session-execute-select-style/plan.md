# Plan: Migrate SQLAlchemy Query API to Session.execute(select()) Style

## Overview

**Migration Strategy: Strangler-Fig (incremental, module-by-module)**

The migration replaces the legacy SQLAlchemy Query API (`session.query(Model).filter(...).all()`) with the modern 2.0-style `session.execute(select(Model).where(...))` pattern. A strangler-fig approach is chosen because:

- Individual query call sites are independently replaceable without coordinated deployment.
- The two styles can coexist within the same codebase during transition (SQLAlchemy 1.4+ supports both).
- Risk is contained to one module at a time, allowing incremental validation.
- A big-bang rewrite is unjustified given medium upgrade urgency and the absence of a hard runtime deadline.

Each phase targets a logical slice of the codebase, is independently testable, and can be rolled back without affecting other phases.

> **NOTE:** Because the provided tech analysis does not include runtime version, build tool, specific file paths, or framework details, several fields below are marked **TODO**. These must be resolved during discovery before work begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Discovery & Inventory | Audit all Query API call sites; tag with `# TODO: migrate-query` comments; establish baseline test coverage | None | TODO person-days (derive from option once provided) |
| 2 — Infrastructure Prep | Pin SQLAlchemy to a 1.4.x or 2.x version that supports both styles; enable `SQLALCHEMY_WARN_20=1` deprecation warnings in CI; add `future=True` flag to `create_engine` | Phase 1 complete | TODO |
| 3 — Core Model Queries | Migrate query calls in primary data-access/repository layer files | Phase 2 complete | TODO |
| 4 — Service / Business Logic Layer | Migrate query calls embedded in service classes | Phase 3 complete | TODO |
| 5 — Utility / Helper Queries | Migrate ad-hoc queries in utility scripts, admin tools, background jobs | Phase 4 complete | TODO |
| 6 — Cleanup & Hardening | Remove legacy `Query` imports; enforce via linter rule; final regression run | Phase 5 complete | TODO |

> **TODO:** Populate effort column once the upgrade option's person-days estimate is provided.

---

## Component Changes

### General Pattern Change

**Before (Query API):**
```python
results = session.query(User).filter(User.active == True).all()
obj     = session.query(Order).filter_by(id=order_id).first()
count   = session.query(Invoice).filter(Invoice.status == "open").count()
```

**After (2.0 execute/select style):**
```python
from sqlalchemy import select, func

results = session.execute(select(User).where(User.active == True)).scalars().all()
obj     = session.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
count   = session.execute(select(func.count()).select_from(Invoice).where(Invoice.status == "open")).scalar()
```

### Key API Mapping

| Legacy Query API | Modern Equivalent |
|-----------------|-------------------|
| `.query(Model)` | `select(Model)` |
| `.filter(...)` | `.where(...)` |
| `.filter_by(...)` | `.where(Model.col == val)` |
| `.all()` | `.scalars().all()` |
| `.first()` | `.scalars().first()` |
| `.one()` | `.scalars().one()` |
| `.one_or_none()` | `.scalar_one_or_none()` |
| `.count()` | `select(func.count()).select_from(Model)` |
| `.get(pk)` | `session.get(Model, pk)` |
| `.join(...)` | `.join(...)` (same, on `select()`) |
| `.options(...)` | `.options(...)` (same, on `select()`) |
| `.order_by(...)` | `.order_by(...)` (same) |
| `.limit(n)` | `.limit(n)` (same) |
| `.offset(n)` | `.offset(n)` (same) |
| `.with_for_update()` | `.with_for_update()` (same) |
| `.distinct()` | `.distinct()` (same) |
| `.scalar()` | `.scalar()` on `session.execute(...)` |
| `.exists()` | `select(exists(...))` |

### Files / Classes Affected

> **TODO:** Populate with actual file paths, class names, and method names once the codebase inventory (Phase 1) is complete. The following are placeholder structural categories:

- **TODO: `db/repositories/*.py`** — Primary query call sites; highest priority.
- **TODO: `services/*.py`** — Service layer classes with embedded queries.
- **TODO: `models/*.py`** — Any class methods using `session.query(cls)`.
- **TODO: `tasks/*.py` / `jobs/*.py`** — Background workers with ad-hoc queries.
- **TODO: `utils/*.py`** — Helper functions performing queries.
- **TODO: `tests/`** — Test fixtures and factory helpers using Query API.

### `create_engine` Configuration Change

Add `future=True` to opt into SQLAlchemy 2.0 engine behavior during transition:

```python
# Before
engine = create_engine(DATABASE_URL)

# After (Phase 2)
engine = create_engine(DATABASE_URL, future=True)
```

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `sqlalchemy` | TODO (from tech analysis — not provided) | TODO (from tech analysis — not provided) | `session.query()` is removed in SQLAlchemy 2.0; deprecated with warnings in 1.4 | Set `SQLALCHEMY_WARN_20=1` env var in CI to surface all legacy call sites before upgrading; use `future=True` on engine |

> **TODO:** All version numbers must be sourced from the tech analysis once provided. Do not assume current or target versions.

---

## Infrastructure Changes

> **TODO:** Docker base image — not derivable from provided context.

> **TODO:** Kubernetes manifests — not derivable from provided context.

> **TODO:** IaC (Terraform/Pulumi/etc.) — not derivable from provided context.

### CI/CD Pipeline Changes (derivable from task)

- **Add deprecation warning gate (Phase 2):** Set environment variable `SQLALCHEMY_WARN_20=1` in the CI test job. Configure the test runner to treat SQLAlchemy `RemovedIn20Warning` as errors (`-W error::sqlalchemy.exc.RemovedIn20Warning`) so new legacy-style queries are caught automatically.
- **Add linter rule (Phase 6):** After migration is complete, add a `grep`-based or `ast`-based CI check that fails if `session.query(` appears in non-test source files.

```yaml
# Example CI env addition (adapt to actual CI system — TODO: identify CI tool)
env:
  SQLALCHEMY_WARN_20: "1"
```

---

## Rollback Strategy

Each phase is independently reversible because the two query styles coexist in SQLAlchemy 1.4.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1 — Discovery** | Remove `# TODO: migrate-query` annotations via `git revert` or branch deletion. No functional change was made. |
| **Phase 2 — Infra Prep** | Remove `future=True` from `create_engine` call. Remove `SQLALCHEMY_WARN_20=1` from CI environment. Revert SQLAlchemy pin if version was changed. |
| **Phase 3 — Core Queries** | `git revert` the commits covering the repository/data-access layer files. Tests must pass after revert before proceeding. |
| **Phase 4 — Service Layer** | `git revert` the commits covering service layer files. Validate with integration tests. |
| **Phase 5 — Utilities** | `git revert` the commits covering utility/job files. |
| **Phase 6 — Cleanup** | If the linter rule or import removal causes breakage, revert the cleanup commit. Re-add legacy `Query` imports as needed. |

**General rollback principle:** Because this is a strangler-fig migration, any phase can be reverted independently without requiring rollback of earlier phases, provided SQLAlchemy 1.4.x (which supports both APIs) remains pinned.

---

## Testing Strategy

### Test Pyramid

| Layer | Scope | Tools | Coverage Target | CI Gate |
|-------|-------|-------|----------------|---------|
| **Unit** | Individual query builder functions; result-mapping helpers | TODO (identify test framework — pytest assumed) | ≥ 80% line coverage on migrated files | Fail build on coverage drop |
| **Integration** | Repository/service methods against a real (test) database | TODO (identify DB — likely SQLite in-memory or Postgres test container) | All migrated query methods have at least one integration test | Fail build on any integration test failure |
| **Regression** | Full existing test suite run after each phase to confirm no behavioral change | Existing test suite | 100% of pre-migration tests must continue to pass | Fail build on any regression |
| **Performance** | Query execution plans; latency benchmarks for high-traffic queries | TODO (identify profiling tool — SQLAlchemy `echo=True`, `EXPLAIN ANALYZE`, or dedicated benchmark suite) | No query should regress by more than 10% in execution time | Advisory gate (warn, do not block) |

### Specific Validation Steps

1. **Before each phase:** Run the full test suite; record pass count as baseline.
2. **During migration:** For each converted call site, verify the return type is equivalent (`list` vs `ScalarResult`, single object vs `Row`, etc.).
3. **After each phase:** Re-run full suite; diff against baseline — zero new failures required to merge.
4. **`SQLALCHEMY_WARN_20=1` gate:** Zero `RemovedIn20Warning` warnings permitted in CI after Phase 2 is merged.
5. **Result shape audit:** Pay special attention to queries that previously returned `Query` objects passed to other functions — these must be fully evaluated (`.all()`, `.scalars().all()`) before the refactor, as `select()` returns a `Select` object, not an iterable.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Codebase inventory complete; all call sites tagged | Phase 1 | TODO | TODO |
| SQLAlchemy version pinned; CI warning gate active | Phase 2 | TODO | TODO |
| Core repository/data-access layer migrated | Phase 3 | TODO | TODO |
| Service layer migrated | Phase 4 | TODO | TODO |
| Utilities and background jobs migrated | Phase 5 | TODO | TODO |
| Legacy `Query` API fully removed; linter rule enforced | Phase 6 | TODO | TODO |

> **TODO:** All estimated completion dates and owner assignments must be derived from the upgrade option's person-days estimate and team staffing information, neither of which was provided. Populate before work begins.