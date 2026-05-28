# Plan: Upgrade psycopg2 to psycopg3 (or Latest Stable psycopg2)

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The migration from `psycopg2` to `psycopg3` (or to the latest stable `psycopg2`) is approached using a strangler-fig pattern with feature-flag gating. This allows the new database adapter to be introduced alongside the existing one, validated in isolation, and promoted incrementally without a hard cutover.

**Justification:**
- The upgrade urgency is rated **medium**, indicating no immediate critical failure but meaningful technical debt accumulation.
- psycopg3 introduces breaking API changes (cursor factories, `%s` vs `%b` parameter styles, connection string handling, async interface changes) that require careful, component-by-component validation rather than a big-bang swap.
- A strangler-fig approach minimizes production risk: the existing `psycopg2` code paths remain live until each migrated component is verified, enabling safe rollback at any phase boundary.
- If the decision is made to stay on `psycopg2` (latest stable patch), the scope reduces to a dependency pin update and regression test run — phases 3–5 collapse into a single phase.

> **Decision Gate (Phase 1):** Confirm whether the target is psycopg3 migration or psycopg2 latest-stable upgrade. The remainder of this plan covers the psycopg3 path as the primary track, with psycopg2-only notes where the paths diverge.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & Decision Gate — inventory all `psycopg2` usage sites, connection factories, cursor usage, and async patterns; confirm target version | None | 1–2 person-days |
| 2 | Environment Setup — install `psycopg[binary]` or `psycopg[c]` alongside `psycopg2`; configure CI to test both | Phase 1 complete | 0.5 person-days |
| 3 | Adapter Abstraction Layer — introduce a thin DB connection abstraction (if not present) to allow swapping the underlying driver | Phase 2 complete | 1–2 person-days |
| 4 | Incremental Migration — migrate connection factories, query execution sites, and cursor usage to psycopg3 API, module by module | Phase 3 complete | 2–4 person-days |
| 5 | Async & Advanced Feature Migration — migrate any `asyncpg`/async psycopg2 patterns to psycopg3 native async; update `COPY`, `NOTIFY`, binary types | Phase 4 complete | 1–2 person-days |
| 6 | Validation & Cutover — full regression suite, performance benchmarks, remove `psycopg2` dependency, update lockfiles | Phase 5 complete | 1 person-day |
| 7 | Cleanup — remove abstraction shims if no longer needed, update documentation and runbooks | Phase 6 complete | 0.5 person-days |

**Total estimated effort: ~7–12 person-days** (moderate option).

> **psycopg2 latest-stable only path:** Phases 3–5 are replaced by a single dependency version bump + lockfile update. Total effort: ~1–2 person-days.

---

## Component Changes

> **Note:** Specific file paths, class names, and method names are not available in the provided code context. The changes below are described structurally. All file references should be resolved during Phase 1 audit.

### Connection Factory / Database Initialization

- **What changes:** `psycopg2.connect(...)` calls must be replaced with `psycopg.connect(...)` (psycopg3 module name is `psycopg`).
- **Files affected:** Any module containing `import psycopg2` or `from psycopg2 import ...` — to be enumerated in Phase 1.
- **API change:** Connection string DSN format is compatible, but keyword argument handling differs. `psycopg2.extras`, `psycopg2.extensions` equivalents must be mapped to psycopg3 counterparts.

### Cursor Usage

- **What changes:** `cursor.execute()` parameter placeholder style changes from `%s` (psycopg2) to `%s` (still supported in psycopg3 by default) — **but** binary parameters use `%b`, and `mogrify()` is removed in psycopg3.
- **Files affected:** All files calling `cursor.execute()`, `cursor.executemany()`, `cursor.mogrify()`.
- **API change:** Remove all `cursor.mogrify()` calls; replace with query composition utilities or logging-safe alternatives.

### Row Factories / Result Handling

- **What changes:** `psycopg2.extras.DictCursor`, `RealDictCursor`, `NamedTupleCursor` are replaced by psycopg3 row factories (`psycopg.rows.dict_row`, `namedtuple_row`, `class_row`).
- **Files affected:** Any file instantiating cursors with `cursor_factory=` keyword argument.
- **API change:** `cursor_factory` parameter on `connect()` or `cursor()` is replaced by `row_factory` in psycopg3.

### Connection Pooling

- **What changes:** If `psycopg2` pooling (e.g., `psycopg2.pool.ThreadedConnectionPool`) is in use, migrate to `psycopg_pool` (separate package: `psycopg-pool`).
- **Files affected:** Any module managing connection pools.
- **API change:** Pool API is similar but not identical; `getconn()`/`putconn()` patterns may need updating to context-manager style.

### Async Database Access

- **What changes:** If async psycopg2 patterns exist (e.g., via `aiopg` or `psycopg2` with manual async wrappers), migrate to psycopg3's native `await psycopg.AsyncConnection.connect(...)`.
- **Files affected:** Any `async def` functions performing database I/O.
- **API change:** psycopg3 async connection and cursor are first-class; no third-party async wrapper needed.

### ORM / Framework Integration (e.g., SQLAlchemy, Django)

- **What changes:** If SQLAlchemy is in use, update the dialect from `postgresql+psycopg2://` to `postgresql+psycopg://`. If Django is in use, update `ENGINE` in `DATABASES` settings.
- **Files affected:** `settings.py`, `database.py`, SQLAlchemy engine creation files — TODO: confirm from codebase.
- **API change:** Connection URL scheme change; SQLAlchemy ≥ 2.0 supports psycopg3 natively.

---

## Dependency Upgrade Plan

> **Note:** Exact current pinned versions are not available in the provided tech analysis. Version fields marked TODO must be confirmed from the project's `requirements.txt`, `pyproject.toml`, or `Pipfile` during Phase 1.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `psycopg2` or `psycopg2-binary` | TODO (confirm from lockfile) | Remove after migration | N/A — being replaced | Keep pinned until Phase 6 cutover |
| `psycopg` (psycopg3) | Not installed | Latest stable (`3.x`) | Yes — see Component Changes | Install as `psycopg[binary]` for dev/test; `psycopg[c]` for production |
| `psycopg-pool` | Not installed | Latest stable | N/A — new dependency | Required only if connection pooling is used |
| `psycopg2-binary` (psycopg2-only path) | TODO | Latest stable `2.9.x` | None (patch upgrade) | Update pin in requirements file; run regression suite |

> **psycopg2-only upgrade note:** If staying on psycopg2, the target is the latest `2.9.x` release. Confirm exact version from PyPI at time of upgrade — do not rely on training-data version numbers.

---

## Infrastructure Changes

> Most infrastructure changes depend on deployment context not provided in the task context. Items below are derivable from the dependency change; all others are marked TODO.

- **Python environment:** Ensure the target Python version is compatible with psycopg3 (requires Python ≥ 3.7; psycopg3 ≥ 3.1 recommends Python ≥ 3.8). TODO: confirm runtime Python version.
- **System libraries:** `psycopg[c]` (C extension) requires `libpq-dev` (Debian/Ubuntu) or `postgresql-devel` (RHEL) at build time. If switching from `psycopg2-binary` to `psycopg[c]`, Dockerfile base image must include this package.
  - TODO: Confirm Docker base image and update `RUN apt-get install -y libpq-dev` or equivalent if needed.
- **Docker base image:** TODO — not provided in context. If using a slim Python image, verify `libpq` availability.
- **CI/CD pipeline:** Add a parallel test job in CI that installs `psycopg` (psycopg3) and runs the test suite during Phase 2–5. Remove `psycopg2` from the install step at Phase 6 cutover. TODO: confirm CI platform (GitHub Actions, GitLab CI, etc.).
- **Kubernetes manifests:** TODO — not provided in context. No expected changes unless environment variables for DB connection strings change format.
- **IaC (Terraform, Pulumi, etc.):** TODO — not provided in context.

---

## Rollback Strategy

Each phase boundary is an independently reversible rollback point.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** (Audit) | No code changes made; nothing to roll back. Discard audit notes if project is cancelled. |
| **Phase 2** (Env Setup) | Remove `psycopg` from `requirements.txt`/`pyproject.toml`; restore original dependency file from version control. Re-run `pip install` or equivalent. |
| **Phase 3** (Abstraction Layer) | Revert abstraction layer commits via `git revert` or branch deletion. The abstraction layer is additive; existing `psycopg2` code paths remain untouched. |
| **Phase 4** (Incremental Migration) | Each module migration is a discrete commit. Roll back individual modules by reverting their commits. Feature flag (env var or config key, e.g., `USE_PSYCOPG3=false`) can disable psycopg3 code paths without a redeploy if the abstraction layer is in place. |
| **Phase 5** (Async/Advanced) | Revert async migration commits. Restore previous async wrapper or `aiopg` dependency if applicable. |
| **Phase 6** (Cutover) | If post-cutover issues are detected: re-add `psycopg2` to dependencies, revert connection factory to `psycopg2.connect(...)`, redeploy. This is the last phase where rollback requires a dependency change. |
| **Phase 7** (Cleanup) | Cleanup is cosmetic; rollback is a non-issue. If abstraction shims were removed prematurely, restore from version control. |

**General rollback principle:** Maintain a `psycopg2`-compatible branch or tag at each phase boundary. Do not merge Phase N+1 until Phase N is validated in a staging environment.

---

## Testing Strategy

### Test Pyramid

| Layer | Scope | Tools | Coverage Target | CI Gate |
|-------|-------|-------|----------------|---------|
| **Unit** | Query construction, parameter binding, row factory mapping, connection factory logic | `pytest`, `unittest.mock` (mock DB connections) | ≥ 80% of DB utility functions | Block merge on failure |
| **Integration** | Actual DB round-trips: connect, execute, fetch, transaction commit/rollback, pool acquire/release | `pytest` + real PostgreSQL instance (Docker Compose in CI) | All critical query paths exercised | Block merge on failure |
| **Regression** | Full application test suite re-run against psycopg3 to catch behavioral differences (type coercion, encoding, error classes) | Existing test suite + `pytest` | No regression vs. psycopg2 baseline | Block merge on failure |
| **Performance** | Connection acquisition time, query throughput, pool saturation behavior | `pytest-benchmark` or `locust` | Within 10% of psycopg2 baseline | Advisory (non-blocking) in CI; blocking for release |

### Specific Testing Notes

- **Error class changes:** psycopg3 reorganizes exception hierarchy (e.g., `psycopg.errors.*` vs `psycopg2.errors.*`). Add regression tests for error handling code paths.
- **Type adapter changes:** psycopg3 changes how Python types map to PostgreSQL types (e.g., `datetime`, `UUID`, `JSON`, `bytea`). Add explicit round-trip tests for each custom type in use.
- **`mogrify()` removal:** Any tests relying on `cursor.mogrify()` output must be rewritten.
- **Async tests:** Use `pytest-asyncio` for async connection/cursor tests under psycopg3.
- **Dual-driver CI job:** During Phases 2–5, run CI with both `psycopg2` and `psycopg3` installed (separate jobs) to confirm parity before cutover.

---

## Timeline

> Effort derived from the moderate upgrade option estimate (~7–12 person-days total). Calendar dates are expressed as relative offsets from project kick-off (T+0). Assign owners during Phase 1 planning.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; target version confirmed (psycopg3 vs psycopg2 latest) | Phase 1 | T+2 days | TODO |
| CI environment running both drivers in parallel | Phase 2 | T+3 days | TODO |
| Abstraction layer merged to main | Phase 3 | T+5 days | TODO |
| All synchronous DB modules migrated to psycopg3 | Phase 4 | T+9 days | TODO |
| Async and advanced features migrated | Phase 5 | T+11 days | TODO |
| Full regression + performance validation passed; psycopg2 removed | Phase 6 | T+12 days | TODO |
| Cleanup and documentation complete | Phase 7 | T+13 days | TODO |

> **Note:** If the decision in Phase 1 is to upgrade psycopg2 to latest stable only (not migrate to psycopg3), Phases 3–5 are skipped and total calendar time reduces to approximately T+3–4 days.