# PLAN: Upgrade psycopg2 to psycopg3 (or Latest Stable psycopg2)

> **Spec reference:** Modernization Goal — Upgrade psycopg2 to latest stable or migrate to psycopg3
> **Option selected:** Moderate — incremental migration with compatibility shim where needed

---

## Overview

**Strategy: Feature-flag gated / Strangler-fig**

Because the runtime, build tool, and full dependency graph are not fully specified in the provided context, a big-bang replacement carries unnecessary risk. Instead, the plan adopts a **strangler-fig / feature-flag gated** approach:

1. First, pin and upgrade to the latest stable `psycopg2` (or `psycopg2-binary`) to eliminate any known CVEs or deprecation debt without changing the driver API surface.
2. In parallel, introduce `psycopg` (psycopg3) behind an environment-variable feature flag, allowing side-by-side validation.
3. Cut over fully once integration and regression tests pass under psycopg3.

**Justification:**
- Upgrade urgency is **medium** — no emergency forcing a big-bang cut-over.
- psycopg3 has a largely compatible but not identical API (e.g., `%s` → `%s` placeholders are preserved, but `cursor.mogrify`, `extras`, and async interfaces differ). A phased approach lets teams surface breakage incrementally.
- Effort estimate is **moderate** — phased delivery fits within that envelope without requiring a dedicated freeze window.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Audit & Baseline | Inventory every file that imports `psycopg2`; capture current test coverage baseline; document all psycopg2-specific API usages (`extras`, `extensions`, `DictCursor`, `execute_values`, `mogrify`, async, etc.) | Access to full codebase | 1–2 person-days |
| 2 — psycopg2 Stable Pin | Upgrade `psycopg2` / `psycopg2-binary` to latest stable; run full test suite; fix any immediate breakage | Phase 1 audit complete | 0.5–1 person-day |
| 3 — psycopg3 Compatibility Layer | Install `psycopg[binary]` (psycopg3) alongside psycopg2; introduce a thin `db/connection.py` factory controlled by `DB_DRIVER` env flag; adapt highest-risk call sites | Phase 2 green | 2–3 person-days |
| 4 — Migration of Call Sites | Systematically replace psycopg2-specific patterns (see Component Changes) across all modules; update type adapters, `COPY`, async usage | Phase 3 factory in place | 2–3 person-days |
| 5 — Validation & Cut-over | Full regression + performance benchmarks under psycopg3 only; remove psycopg2 dependency and feature flag; update docs | Phase 4 complete | 1 person-day |

**Total estimated effort: ~7–10 person-days** (moderate band).

---

## Component Changes

> ⚠️ Specific file and class names are marked **TODO** where the codebase was not provided in context. Replace TODOs with actuals during Phase 1 audit.

### Connection / Session Factory

| Item | Detail |
|------|--------|
| **Files affected** | `TODO: db/connection.py`, `TODO: app/database.py`, or equivalent session-management module |
| **What changes** | Extract all `psycopg2.connect(...)` calls into a single factory function. Add `DB_DRIVER` env-var branch: `"psycopg2"` → existing path; `"psycopg3"` → `psycopg.connect(...)` |
| **API modified** | `get_connection()` / `get_engine()` factory — signature unchanged externally |

### Cursor Usage

| psycopg2 pattern | psycopg3 equivalent | Notes |
|-----------------|--------------------|----|
| `psycopg2.extras.DictCursor` | `psycopg.rows.dict_row` row factory | Pass as `row_factory=dict_row` to `connect()` or `cursor()` |
| `psycopg2.extras.execute_values(cur, sql, vals)` | `cur.executemany(sql, vals)` or `psycopg.copy` | psycopg3 `executemany` uses server-side batching by default |
| `cur.mogrify(sql, params)` | Not available in psycopg3 | Replace with `psycopg.ClientCursor.mogrify` or remove usage |
| `psycopg2.extras.RealDictCursor` | `row_factory=dict_row` | Same as DictCursor path |
| `psycopg2.extensions.register_adapter` | `psycopg.adapt` / `psycopg.types` | Rewrite custom type adapters |

**Files affected:** TODO — all files identified in Phase 1 audit that call `cursor()`, `execute()`, `executemany()`, or `mogrify()`.

### Async Usage (if present)

| Item | Detail |
|------|--------|
| **psycopg2 async** | `psycopg2` async support via `psycopg2.extras.wait_select` or third-party wrappers (e.g., `aiopg`) |
| **psycopg3 async** | Native `await psycopg.AsyncConnection.connect(...)` — first-class, no wrapper needed |
| **Files affected** | TODO — any file using `async def` with database calls |

### ORM / Framework Integration (if present)

| Item | Detail |
|------|--------|
| **SQLAlchemy** | If SQLAlchemy is in use, update the connection URL dialect from `postgresql+psycopg2://` to `postgresql+psycopg://` and ensure SQLAlchemy ≥ 2.0 (psycopg3 support landed in 2.0) |
| **Django** | Change `ENGINE` in `DATABASES` from `django.db.backends.postgresql_psycopg2` to `django.db.backends.postgresql`; Django ≥ 4.2 supports psycopg3 natively |
| **Files affected** | TODO: `settings.py`, `alembic.ini`, or equivalent config files |

---

## Dependency Upgrade Plan

> ⚠️ The tech analysis did not supply explicit pinned version numbers. The table below uses the latest stable versions known from the task description. **Verify all versions against your actual `requirements.txt` / `pyproject.toml` before proceeding.**

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `psycopg2` / `psycopg2-binary` | TODO (from lockfile) | Latest stable 2.9.x (Phase 2) → **remove** (Phase 5) | Minor — see changelog | Pin to latest 2.9.x first; remove after psycopg3 cut-over |
| `psycopg` (psycopg3) | Not installed | Latest stable 3.x | Yes — see Component Changes | Install as `psycopg[binary]` for binary C extension; use `psycopg[c]` for source build |
| `psycopg[binary]` or `psycopg[c]` | N/A | Latest stable 3.x | N/A | Binary wheel preferred for CI speed; source build for production hardening |
| SQLAlchemy (if used) | TODO | ≥ 2.0 required for psycopg3 | Yes if upgrading from 1.x | TODO — confirm presence and version |
| Django (if used) | TODO | ≥ 4.2 recommended | TODO | TODO — confirm presence and version |
| `aiopg` (if used) | TODO | **Remove** | N/A | Replace with psycopg3 native async |

---

## Infrastructure Changes

> Most infrastructure details are not derivable from the provided context. Items below are best-practice recommendations; mark and resolve TODOs during Phase 1.

- **Docker base image:** TODO — confirm base image includes `libpq-dev` (required for `psycopg[c]` source build) or that the binary wheel is used. If using `psycopg[binary]`, no system library change is needed.
- **CI/CD pipeline:** Add a test matrix step that runs the full test suite with `DB_DRIVER=psycopg3` during Phase 3–4. Gate merge on both `psycopg2` and `psycopg3` passing until Phase 5 cut-over.
- **Environment variables:** Add `DB_DRIVER` (values: `psycopg2` | `psycopg3`, default: `psycopg2` during transition) to all environment configs (`.env.example`, Kubernetes `ConfigMap`/`Secret`, TODO).
- **Kubernetes manifests:** TODO — add `DB_DRIVER` env var to relevant `Deployment` manifests if applicable.
- **IaC (Terraform/Pulumi/etc.):** TODO — not mentioned in context.

---

## Rollback Strategy

### Phase 2 Rollback (psycopg2 stable pin)
1. Revert `requirements.txt` / `pyproject.toml` to the previous pinned `psycopg2` version.
2. Re-run `pip install -r requirements.txt` (or equivalent).
3. Re-deploy previous artifact. No code changes required.

### Phase 3 Rollback (psycopg3 compatibility layer introduced)
1. Set `DB_DRIVER=psycopg2` in all environment configs — immediately disables psycopg3 code path without a deployment.
2. If a deployment is needed, revert the `db/connection.py` factory commit.
3. Remove `psycopg[binary]` from dependencies and redeploy.

### Phase 4 Rollback (call-site migration in progress)
1. Set `DB_DRIVER=psycopg2` to revert to psycopg2 path instantly.
2. If individual call-site commits have been merged, use `git revert` on the relevant commits or restore from the Phase 3 branch tag.
3. Validate with smoke tests before re-deploying.

### Phase 5 Rollback (full cut-over)
1. Re-introduce `psycopg2-binary` to `requirements.txt`.
2. Restore `DB_DRIVER` feature flag in `db/connection.py` factory.
3. Set `DB_DRIVER=psycopg2` in environment.
4. Redeploy. This is the highest-cost rollback — Phase 5 should only be executed after extended parallel-run validation.

---

## Testing Strategy

### Test Pyramid

| Layer | What to test | Tools | Coverage Target | CI Gate |
|-------|-------------|-------|----------------|---------|
| **Unit** | Connection factory branching logic; type adapter registration; cursor wrapper behavior | `pytest`, `unittest.mock` to mock `psycopg2.connect` / `psycopg.connect` | ≥ 90% on new factory code | Block merge on failure |
| **Integration** | Real queries against a test PostgreSQL instance under both drivers; `DictCursor` equivalence; `execute_values` / `executemany` parity; transaction rollback behavior | `pytest` + `pytest-postgresql` or Docker Compose PostgreSQL service | All existing integration tests pass under both drivers | Block merge on failure |
| **Regression** | Full existing test suite executed with `DB_DRIVER=psycopg3`; no behavioral delta vs. `DB_DRIVER=psycopg2` | Existing test suite + `pytest --tb=short` | 100% of previously passing tests must pass | Block Phase 5 cut-over |
| **Performance** | Connection acquisition time; query throughput; async concurrency (if applicable) — psycopg3 should be equal or better | `pytest-benchmark` or `locust` / `pgbench` | No regression vs. psycopg2 baseline (≤ 5% latency increase acceptable) | Advisory gate — document results before Phase 5 |

### CI Configuration Notes
- Run integration tests against PostgreSQL TODO version (match production).
- Add a second CI job with `DB_DRIVER=psycopg3` from Phase 3 onward; both jobs must be green before merge.
- Store performance benchmark results as CI artifacts for trend comparison.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; all psycopg2 usages documented | Phase 1 | Day 2 | TODO |
| psycopg2 pinned to latest stable; CI green | Phase 2 | Day 3 | TODO |
| `db/connection.py` factory + `DB_DRIVER` flag merged | Phase 3 | Day 6 | TODO |
| All call sites migrated to psycopg3 | Phase 4 | Day 9 | TODO |
| Regression + performance validation complete | Phase 5 | Day 10 | TODO |
| psycopg2 dependency removed; feature flag deleted | Phase 5 | Day 10 | TODO |

> **Note:** Timeline assumes a single engineer working continuously. Adjust for part-time allocation or parallel team members. All dates are relative to project kick-off day.