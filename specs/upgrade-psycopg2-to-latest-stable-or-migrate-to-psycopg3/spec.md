# Spec: Upgrade psycopg2 to Latest Stable or Migrate to psycopg3

---

## Summary

This spec covers the evaluation and execution of upgrading the PostgreSQL database adapter from its current `psycopg2` version to either the latest stable `psycopg2` release or a full migration to `psycopg3` (the `psycopg` package). The expected outcome is a project that uses a supported, actively maintained PostgreSQL adapter with no regressions in database connectivity, query execution, or connection pool behaviour.

---

## Motivation

- **Active maintenance risk:** `psycopg2` is in maintenance-only mode. New features, performance improvements, and long-term security fixes are being directed exclusively to `psycopg3`.
- **Upgrade urgency:** Rated **medium** — no immediate CVE is blocking, but continued use of an unmaintained adapter increases exposure over time and accumulates technical debt.
- **Ecosystem alignment:** `psycopg3` introduces native async support, binary protocol by default, and improved type handling, which reduces the need for third-party workarounds currently common with `psycopg2`.
- **Dependency hygiene:** Staying on an older adapter version risks incompatibility with future PostgreSQL server versions and Python runtime upgrades.

> **Note:** Specific current pinned version of `psycopg2` in this project is **TODO** — must be confirmed from `requirements.txt`, `pyproject.toml`, or equivalent dependency manifest.

---

## Current State

The project currently depends on `psycopg2` (exact pinned version: **TODO**). The following integration points are known to be affected:

| Area | Detail |
|---|---|
| Database adapter package | `psycopg2` (or `psycopg2-binary`) |
| Connection interface | `psycopg2.connect()` / DSN string or keyword arguments |
| Cursor usage | Standard `cursor()` and `DictCursor` / `RealDictCursor` patterns |
| Transaction management | Explicit `commit()` / `rollback()` or context manager usage |
| Connection pooling | TODO — confirm whether `psycopg2.pool`, `pgbouncer`, `SQLAlchemy`, or another pool is in use |
| Async usage | TODO — confirm whether any async database calls exist |
| Type adapters / extensions | TODO — confirm use of `register_adapter`, `AsIs`, `Json`, custom `psycopg2.extras` types |
| ORM / query builder | TODO — confirm whether SQLAlchemy, Django ORM, or raw SQL is used; this affects migration scope significantly |

---

## Proposed Changes

### Option A — Upgrade psycopg2 to Latest Stable
Bump the pinned version of `psycopg2` (or `psycopg2-binary`) to the current latest stable release. No API changes are required.

### Option B — Migrate to psycopg3 (`psycopg`)
Replace `psycopg2` with the `psycopg` package. This involves API-level changes described in the table below.

> **Recommended path:** TODO — confirm with team whether async support or long-term maintainability justifies the migration cost of Option B over Option A.

| Component | Before (psycopg2) | After (psycopg3) | Breaking? |
|---|---|---|---|
| Package import | `import psycopg2` | `import psycopg` | Y |
| Connection factory | `psycopg2.connect(...)` | `psycopg.connect(...)` | Y |
| Async connection | Not natively supported | `await psycopg.AsyncConnection.connect(...)` | N (additive) |
| Cursor row factory | `RealDictCursor`, `DictCursor` via `cursor_factory` | `psycopg.rows.dict_row` / `tuple_row` row factories | Y |
| `executemany` behaviour | Iterates individual statements | Uses `executemany` with `COPY` optimisation by default | Y (behaviour) |
| Binary protocol | Off by default | On by default for supported types | Y (behaviour) |
| `mogrify()` method | Available on cursor | Removed; use `cursor.query` after execute | Y |
| `psycopg2.extras.Json` | Custom `Json` adapter class | Native `psycopg.types.json` integration | Y |
| Custom type adapters | `register_adapter` / `extensions` | `psycopg.adapt` / `Loader`/`Dumper` classes | Y |
| Connection pool | `psycopg2.pool.ThreadedConnectionPool` | `psycopg_pool.ConnectionPool` (separate package) | Y |
| `autocommit` default | `False` | `False` (same), but transaction handling API differs | Partial |
| SQLAlchemy dialect | `postgresql+psycopg2://` | `postgresql+psycopg://` | Y (config) |

---

## Compatibility & Breaking Changes

| Breaking Change | Migration Path |
|---|---|
| Package import name changes from `psycopg2` to `psycopg` | Update all import statements project-wide |
| `RealDictCursor` / `DictCursor` removed | Replace with `row_factory=psycopg.rows.dict_row` on connection or cursor |
| `mogrify()` removed from cursor | Replace usages with `cursor.query` attribute after execution, or format queries manually |
| `psycopg2.extras.Json` adapter | Migrate to native JSON support in `psycopg3`; confirm behaviour parity for `jsonb` columns |
| Custom `register_adapter` extensions | Rewrite using `psycopg3` `Loader`/`Dumper` protocol |
| `psycopg2.pool` classes | Replace with `psycopg_pool` package (`ConnectionPool`, `AsyncConnectionPool`) |
| SQLAlchemy connection string dialect | Update DSN/URL from `psycopg2` dialect to `psycopg` dialect |
| `executemany` optimisation change | Audit all `executemany` call sites for correctness under new batching behaviour |
| Binary protocol on by default | Verify that all custom type round-trips produce identical results; disable per-connection if needed |
| `psycopg2-binary` vs source build | TODO — confirm deployment environment; `psycopg3` recommends `psycopg[binary]` or `psycopg[c]` extras |

---

## Acceptance Criteria

1. **Given** the dependency manifest is updated, **when** the project dependencies are installed in a clean environment, **then** no version conflict or missing dependency error is raised and the correct adapter package version is installed.

2. **Given** the updated adapter is installed, **when** the application initialises its database connection, **then** a successful connection to the PostgreSQL server is established without errors.

3. **Given** a connected session, **when** a representative set of read queries (SELECT) is executed, **then** all queries return result sets that are byte-for-byte identical to the results produced by the previous adapter version on the same data.

4. **Given** a connected session, **when** a representative set of write queries (INSERT, UPDATE, DELETE) is executed within a transaction that is committed, **then** the data is persisted correctly and no integrity errors are raised.

5. **Given** a connected session, **when** a transaction is explicitly rolled back, **then** no data is persisted and the connection is returned to a clean, reusable state.

6. **Given** the connection pool is configured, **when** the application is placed under concurrent load (TODO: define concurrency level), **then** all requests acquire a connection within the configured timeout and no pool exhaustion or deadlock errors occur.

7. **Given** any `psycopg2`-specific type adapters or extensions were in use, **when** the equivalent `psycopg3` adapters are registered and data is round-tripped through the database, **then** the deserialised Python values are equal to the original values before serialisation.

8. **Given** the full test suite is executed against the updated adapter, **when** all tests complete, **then** zero test failures are introduced that were not present before the upgrade.

9. **Given** the application is running with the updated adapter, **when** a database connection error occurs (e.g., server unreachable), **then** the error is raised as the expected exception type and is handled correctly by existing error-handling code (or error-handling code is updated to match the new exception hierarchy).

10. **Given** Option B (psycopg3) is chosen and async database calls exist, **when** async query paths are exercised, **then** all async operations complete successfully without event-loop blocking or runtime warnings.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact currently pinned version of `psycopg2` in the project? | TODO | TODO |
| 2 | Is `psycopg2-binary` or the source-compiled `psycopg2` in use? What is the deployment/build environment? | TODO | TODO |
| 3 | Is Option A (version bump) or Option B (migrate to psycopg3) the preferred path? | TODO | TODO |
| 4 | Does the project use SQLAlchemy, Django ORM, or raw SQL? This significantly affects migration scope. | TODO | TODO |
| 5 | Are there any async database call sites that would benefit from `psycopg3` native async? | TODO | TODO |
| 6 | Which `psycopg2.extras` features are actively used (e.g., `Json`, `execute_values`, `LoggingConnection`)? | TODO | TODO |
| 7 | Is a connection pool managed by the application, or is an external pooler (e.g., PgBouncer) used? | TODO | TODO |
| 8 | What PostgreSQL server version is in use? Are there any server-version-specific features relied upon? | TODO | TODO |
| 9 | Are there CI pipeline steps that need to be updated to install the new adapter package or its system dependencies? | TODO | TODO |
| 10 | Is there a staging environment available to validate the migration before production rollout? | TODO | TODO |