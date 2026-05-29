# Tasks: Upgrade psycopg2 to Latest Stable or Migrate to psycopg3

> **Scope:** Migrate from `psycopg2` to `psycopg3` (`psycopg`) following the moderate upgrade path. Tasks are ordered for sequential AI-agent pickup.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with `psycopg` 3.x (requires Python ≥ 3.7) in the project runtime environment
- [ ] [XS] Confirm PostgreSQL server version is ≥ 9.6 (required by `psycopg` 3.x) by querying `SELECT version()` against all target database environments
- [ ] [XS] Verify `libpq` development headers are available on all build and CI hosts (required to build `psycopg[c]` binary extension)
- [ ] [XS] Ensure write access to the project's dependency manifest file (`requirements.txt`, `pyproject.toml`, `Pipfile`, or equivalent) and CI pipeline configuration

---

## Phase 1 — Preparation

- [ ] [S] Audit all `import psycopg2` and `from psycopg2` statements across the entire codebase and produce a flat inventory list of affected files and modules
- [ ] [S] Audit all usages of `psycopg2`-specific APIs — including `psycopg2.extras`, `psycopg2.extensions`, `psycopg2.pool`, `DictCursor`, `RealDictCursor`, `execute_values()`, `register_adapter()`, and `AsIs` — and document each call site with its file path and line number
- [ ] [XS] Create a dedicated feature branch (e.g., `upgrade/psycopg2-to-psycopg3`) from the main integration branch
- [ ] [S] Capture the current test suite pass/fail baseline on the feature branch before any dependency changes, recording output to `test-baseline.txt` for regression comparison in Phase 3
- [ ] [XS] Pin the existing `psycopg2` version explicitly in the dependency manifest to prevent unintended upgrades during the migration window

---

## Phase 2 — Core Upgrade

- [ ] [XS] Replace `psycopg2` with `psycopg[binary]` (or `psycopg[c]` for production builds) in the dependency manifest (`requirements.txt` / `pyproject.toml` / `Pipfile`), removing the old `psycopg2` entry entirely
- [ ] [S] Replace all `import psycopg2` statements with `import psycopg` and all `from psycopg2 import ...` statements with `from psycopg import ...` across every file identified in the Phase 1 audit
- [ ] [M] Migrate all `psycopg2.extras` usages to `psycopg` equivalents — replace `execute_values()` with `executemany()` or `copy()`, replace `DictCursor` / `RealDictCursor` with `psycopg.rows.dict_row` / `psycopg.rows.real_dict_row` row factories in every affected call site
- [ ] [M] Migrate all `psycopg2.extensions` and `psycopg2.pool` usages — replace `SimpleConnectionPool` / `ThreadedConnectionPool` with `psycopg_pool.ConnectionPool` (add `psycopg-pool` to the dependency manifest), and replace `register_adapter()` / `AsIs` with `psycopg` type dumpers/loaders in every affected module
- [ ] [S] Update all connection string construction and `connect()` call sites to use `psycopg.connect()` keyword arguments, resolving any parameter name differences (e.g., `async_` keyword, `autocommit` flag now set on the connection object) in every affected file
- [ ] [S] Migrate any asynchronous database code from `psycopg2` + third-party async wrappers (e.g., `aiopg`) to `psycopg.AsyncConnection` and `await conn.execute()` patterns in every affected async module
- [ ] [XS] Remove `psycopg2-binary` and any transitional shim packages from the dependency manifest after all call sites have been migrated

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite against a live PostgreSQL instance and compare results to `test-baseline.txt`, investigating and resolving any new failures introduced by the migration
- [ ] [S] Write or update integration tests to exercise the migrated connection pool (`psycopg_pool.ConnectionPool`), `dict_row` row factory, and `executemany()` / `copy()` bulk-insert paths in the relevant test modules
- [ ] [S] Validate all SQL parameter placeholder usage — psycopg3 uses `%s` (same as psycopg2) but rejects `%` literals not escaped as `%%`; scan and fix any raw SQL strings with unescaped `%` characters across all query-building modules
- [ ] [XS] Confirm no residual `psycopg2` imports remain in the codebase by running `grep -r "psycopg2" .` and verifying zero matches outside of comments and the changelog

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or equivalent) to install `libpq-dev` (Debian/Ubuntu) or `postgresql-libs` (Alpine/RHEL) system packages before the Python dependency install step
- [ ] [S] Update any `Dockerfile` or container build files to replace `psycopg2-binary` installation steps with `psycopg[c]` and ensure `libpq` headers are present in the build stage, then removed from the final runtime image if using multi-stage builds
- [ ] [XS] Verify that the CI database service container (PostgreSQL) version satisfies the ≥ 9.6 requirement in all pipeline job definitions and upgrade the service image tag if necessary

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry documenting the migration from `psycopg2` to `psycopg` 3.x, listing any breaking API changes encountered and the psycopg3 equivalents used
- [ ] [XS] Update any internal runbooks, README database-setup sections, or developer onboarding docs that reference `psycopg2` installation steps to reflect the new `psycopg[binary]` / `psycopg[c]` + `libpq` requirements
- [ ] [S] Deploy to a staging environment, run smoke tests against all database-backed endpoints or jobs, and confirm no connection errors, cursor errors, or type-casting regressions appear in application logs before promoting to production

---

> **Note:** If a full migration to psycopg3 is deemed too risky within the current sprint, an intermediate option is to upgrade `psycopg2` to its latest stable release (currently `2.9.x`) by updating only the version pin in the dependency manifest — this requires no code changes but should be treated as a temporary measure with a tracked follow-up ticket for the full psycopg3 migration.