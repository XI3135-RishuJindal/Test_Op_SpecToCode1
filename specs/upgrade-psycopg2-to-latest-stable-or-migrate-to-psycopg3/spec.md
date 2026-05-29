# Spec: Upgrade psycopg2 to Latest Stable or Migrate to psycopg3

---

## Summary

This spec covers the evaluation and execution of upgrading the PostgreSQL database adapter from its current `psycopg2` version to either the latest stable `psycopg2` release or a full migration to `psycopg3` (the `psycopg` package). The expected outcome is a supported, actively maintained PostgreSQL adapter dependency that eliminates technical debt, maintains all existing database connectivity and query behaviour, and positions the project for future compatibility with modern Python runtimes and PostgreSQL features.

---

## Motivation

- **Maintenance risk:** `psycopg2` is in maintenance-only mode. Active feature development has moved to `psycopg3`. Remaining on an outdated `psycopg2` minor/patch version means accumulating unpatched bugs and missing performance improvements.
- **Upgrade urgency:** Rated **medium** — no immediate EOL cliff, but continued inaction increases migration complexity as the gap between `psycopg2` and `psycopg3` APIs widens.
- **Technical debt:** Dependency on a stagnant library creates friction when adopting newer PostgreSQL features (e.g., binary protocol improvements, async-native support, pipeline mode) that are only available in `psycopg3`.
- **Security posture:** Future CVEs affecting the PostgreSQL wire protocol or connection handling are more likely to receive timely patches in `psycopg3` than in `psycopg2`.
- **Python runtime compatibility:** `psycopg3` is designed for modern Python (3.7+) and provides first-class `asyncio` support, reducing risk of incompatibility as Python runtime versions advance.

> **Note:** Specific pinned version numbers for the current `psycopg2` installation are marked TODO below, as they were not provided in the tech analysis.

---

## Current State

- **Current adapter package:** `psycopg2` (exact installed version: TODO — confirm from `requirements.txt`, `pyproject.toml`, or `Pipfile`)
- **Current latest stable psycopg2:** `2.9.x` (TODO — confirm exact patch at time of execution)
- **Connection interface:** Database connections are established via `psycopg2.connect()` using a DSN or keyword arguments.
- **Cursor usage:** Standard `cursor()` and `DictCursor` / `RealDictCursor` patterns are in use (TODO — confirm cursor types used across the codebase).
- **Transaction management:** Explicit `connection.commit()` / `connection.rollback()` or context-manager-based transaction blocks.
- **Type adaptation:** `psycopg2` built-in type adapters for JSON, UUID, arrays, and custom `register_adapter` / `AsIs` patterns (TODO — confirm which custom adapters are registered).
- **Async usage:** TODO — confirm whether any code paths use `psycopg2` with `asyncio` (e.g., via `aiopg` or similar wrappers).
- **Connection pooling:** TODO — confirm whether `psycopg2.pool.ThreadedConnectionPool`, `SimpleConnectionPool`, or a third-party pool (e.g., `SQLAlchemy`, `pgbouncer`) is in use.
- **ORM / query builder:** TODO — confirm whether `psycopg2` is used directly or via an ORM layer (e.g., SQLAlchemy, Django ORM) that abstracts the adapter.

---

## Proposed Changes

### Decision Gate

Before detailing changes, the following decision must be resolved (see Open Questions):

| Option | Description |
|---|---|
| **Option A** | Upgrade `psycopg2` to latest stable `2.9.x` in-place — minimal change, no API migration required. |
| **Option B** | Migrate to `psycopg3` (`psycopg` package) — larger effort, unlocks async-native support and active development. |

The sections below describe changes for **both options**. The chosen option will be confirmed before plan.md is authored.

---

### Component Change Table

| Component | Before | After (Option A) | After (Option B) | Breaking? |
|---|---|---|---|---|
| Adapter package name | `psycopg2` (pinned, TODO version) | `psycopg2==2.9.x` (latest stable) | `psycopg>=3.1.x` (latest stable) | Option A: N / Option B: Y |
| Connection factory | `psycopg2.connect()` | `psycopg2.connect()` (unchanged) | `psycopg.connect()` | Option A: N / Option B: Y |
| Async connection | Not natively supported | Not natively supported | `psycopg.AsyncConnection` available | Option A: N / Option B: N (additive) |
| Cursor API | `cursor()`, `DictCursor`, `RealDictCursor` | Unchanged | `psycopg.rows.dict_row` / `namedtuple_row` row factories | Option A: N / Option B: Y |
| Type adaptation | `register_adapter`, `AsIs`, `extras` | Unchanged | `psycopg` type system (`adapt`, `Loader`, `Dumper`) | Option A: N / Option B: Y |
| Connection pooling | `psycopg2.pool.*` | Unchanged | `psycopg_pool` (separate package) | Option A: N / Option B: Y |
| Binary/text protocol | Text protocol default | Text protocol default | Binary protocol available as default option | Option A: N / Option B: N (opt-in) |
| `executemany` behaviour | Standard | Unchanged | `executemany` uses `pipeline` mode by default in psycopg3 | Option A: N / Option B: Y (behaviour change) |
| `autocommit` default | `False` | `False` | `False` (same default, but API surface differs) | Option A: N / Option B: N |

---

## Compatibility & Breaking Changes

All items below apply to **Option B (psycopg3 migration)** unless noted. Option A introduces no breaking changes.

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Package import changes from `psycopg2` to `psycopg` | All files importing the adapter | Replace import statements; `psycopg` provides a compatibility shim (`psycopg2` compat layer) for common patterns — TODO confirm shim coverage for this codebase |
| `DictCursor` / `RealDictCursor` removed | Any code using these cursor subclasses | Replace with `psycopg` row factory pattern (`dict_row`, `namedtuple_row`) passed at connection or cursor creation time |
| `register_adapter` / `AsIs` type adaptation API removed | Any custom type adapters | Rewrite using `psycopg` `Dumper` / `Loader` classes |
| `psycopg2.pool` removed | Any code using built-in connection pools | Migrate to `psycopg_pool` package (separate install); API is similar but not identical |
| `executemany` pipeline behaviour change | Bulk insert / update code paths | Validate that pipeline mode produces identical results; disable pipeline mode per-statement if behaviour differs |
| `mogrify()` method removed from cursor | Any code using `mogrify` for query debugging or construction | Replace with `psycopg` `cursor.query` attribute or explicit parameter binding inspection |
| `copy_from` / `copy_to` / `copy_expert` API changed | Any COPY-based bulk data operations | Migrate to `psycopg` `copy()` context manager API |
| `extras` module (`execute_values`, `execute_batch`, etc.) removed or changed | Any code using `psycopg2.extras` | Replace with native `psycopg3` equivalents (`executemany` with pipeline, `copy`) — TODO audit all `extras` usages |
| `NOTIFY` / `LISTEN` async handling | Any pub/sub or notification listeners | Migrate to `psycopg3` async notification API |
| Thread-safety model changes | Multi-threaded connection usage | TODO — confirm threading model in use and validate against psycopg3 connection thread-safety guarantees |

---

## Acceptance Criteria

1. **Given** the project dependency manifest, **when** the CI pipeline installs dependencies, **then** no version of `psycopg2` below `2.9.x` (Option A) or no `psycopg2` package at all (Option B) is present in the resolved environment.

2. **Given** a configured PostgreSQL test database, **when** the application initialises its database connection, **then** a connection is established successfully with no errors and the adapter reports the expected server version.

3. **Given** all existing database integration tests, **when** the full test suite is executed against the upgraded adapter, **then** zero test regressions are introduced compared to the baseline test run on the previous adapter version.

4. **Given** any code path that previously used `DictCursor` or `RealDictCursor` (Option B only), **when** a query is executed and results are fetched, **then** rows are returned as dictionaries with column-name keys, identical in structure to the previous behaviour.

5. **Given** any registered custom type adapters (TODO — enumerate), **when** values of those types are written to and read from the database, **then** the round-tripped values are equal to the originals with no type coercion errors.

6. **Given** any code path using connection pooling, **when** concurrent requests acquire and release connections from the pool, **then** no connection leaks, deadlocks, or pool exhaustion errors occur under the existing load test parameters.

7. **Given** any bulk data operation previously using `copy_from`, `copy_to`, or `execute_values` (Option B only), **when** that operation is executed with the migrated API, **then** the row count and data integrity of the result match the pre-migration baseline.

8. **Given** the application running in its standard configuration, **when** a database transaction is committed or rolled back, **then** ACID guarantees are preserved and no uncommitted data is visible to concurrent readers.

9. **Given** the CI pipeline, **when** the dependency vulnerability scan runs, **then** no known CVEs are reported against the installed adapter package version.

10. **Given** the application under its normal operational load, **when** query throughput is measured over a defined benchmark period, **then** p95 query latency does not increase by more than 10% compared to the pre-upgrade baseline.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact currently pinned version of `psycopg2` in the project? | TODO | TODO |
| 2 | Has a decision been made between Option A (psycopg2 upgrade) and Option B (psycopg3 migration)? | TODO | TODO |
| 3 | Is `psycopg2` used directly or exclusively through an ORM/framework abstraction (e.g., SQLAlchemy, Django)? If via ORM, the ORM's own psycopg3 support must be confirmed. | TODO | TODO |
| 4 | Are there any async code paths currently using `psycopg2` via `aiopg` or another wrapper? | TODO | TODO |
| 5 | Which custom type adapters are registered via `register_adapter` or `psycopg2.extras`? | TODO | TODO |
| 6 | Which connection pooling mechanism is in use (`psycopg2.pool`, SQLAlchemy pool, external pgbouncer, etc.)? | TODO | TODO |
| 7 | Are there any COPY-based bulk data operations (`copy_from`, `copy_to`, `copy_expert`) in the codebase? | TODO | TODO |
| 8 | Does the project have an existing database integration test suite with sufficient coverage to validate adapter behaviour? If not, what is the minimum coverage threshold required before proceeding? | TODO | TODO |
| 9 | What is the target Python runtime version? (Relevant to confirming psycopg3 compatibility.) | TODO | TODO |
| 10 | Are there any deployment environments (e.g., AWS Lambda layers, Docker base images) where the `libpq` C library version may constrain the adapter version? | TODO | TODO |