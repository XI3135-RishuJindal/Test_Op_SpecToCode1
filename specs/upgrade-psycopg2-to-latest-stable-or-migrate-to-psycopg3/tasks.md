# Tasks: Upgrade psycopg2 to Latest Stable or Migrate to psycopg3

> **Scope:** Migrate from `psycopg2` to `psycopg3` (`psycopg`) following the moderate upgrade path. Tasks are ordered for sequential AI-agent pickup.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with `psycopg` 3.x (requires Python ≥ 3.7) in the project runtime environment
- [ ] [XS] Confirm PostgreSQL server version is ≥ 9.6 (minimum supported by `psycopg` 3.x) by checking database connection config
- [ ] [XS] Verify `libpq` development headers are available on all build/CI hosts (required for `psycopg[c]` binary extension or `psycopg-binary` fallback)
- [ ] [XS] Ensure write access to `requirements.txt` / `pyproject.toml` / `setup.cfg` (whichever is the canonical dependency file in this project)
- [ ] [XS] Ensure CI pipeline has network access to PyPI to resolve the new `psycopg` package name

---

## Phase 1 — Preparation

- [ ] [S] Audit all direct and transitive references to `psycopg2` and `psycopg2-binary` across `requirements*.txt`, `pyproject.toml`, `setup.cfg`, and any `Pipfile` in the repository
- [ ] [S] Search codebase for every import of `psycopg2` (`import psycopg2`, `from psycopg2 import …`) and produce an inventory list of affected modules and files
- [ ] [S] Search codebase for usage of `psycopg2`-specific APIs that have breaking changes in psycopg3: `extras.execute_values`, `extras.execute_batch`, `DictCursor`, `RealDictCursor`, `Json` adapter, `register_adapter`, `AsIs`, and `mogrify()` — document each occurrence
- [ ] [XS] Create a dedicated feature branch (e.g., `upgrade/psycopg2-to-psycopg3`) from the main branch
- [ ] [S] Capture the current test suite pass/fail baseline and code coverage report on the feature branch before any changes, storing results as a reference artifact in CI

---

## Phase 2 — Core Upgrade

- [ ] [S] Replace `psycopg2` / `psycopg2-binary` entries with `psycopg[binary]>=3.1` (or `psycopg[c]>=3.1` for production C extension) in the canonical dependency file (`requirements.txt` or `pyproject.toml`)
- [ ] [XS] Remove any version pins or exclusions referencing `psycopg2` from `requirements*.txt`, `constraints.txt`, or equivalent files
- [ ] [M] Update every `import psycopg2` statement to `import psycopg` and every `from psycopg2 import X` to `from psycopg import X` across all identified source files
- [ ] [M] Replace `psycopg2.extras.execute_values(…)` calls with `psycopg3`-native `executemany()` or `copy()` API equivalents in all affected modules
- [ ] [M] Replace `psycopg2.extras.execute_batch(…)` calls with `executemany()` in all affected modules
- [ ] [S] Replace `psycopg2.extras.DictCursor` and `RealDictCursor` usage with `psycopg.rows.dict_row` / `psycopg.rows.namedtuple_row` row factories in all affected modules
- [ ] [S] Replace `psycopg2.extras.Json` adapter and `register_adapter` calls with `psycopg`'s built-in JSON support (`psycopg.types.json.set_json_dumps`) in all affected modules
- [ ] [S] Replace any `cursor.mogrify()` calls (removed in psycopg3) with equivalent query-composition using `psycopg.sql` module in all affected modules
- [ ] [S] Update connection string handling: replace `psycopg2.connect(dsn=…)` keyword argument patterns with `psycopg.connect(conninfo=…)` or keyword-argument form as required in all database initialisation/config modules
- [ ] [S] Update any `autocommit`, transaction, and `with connection` context-manager usage to match psycopg3 semantics (transactions are explicit by default; `connection.autocommit = True` is now a property set before first use) in all affected modules
- [ ] [XS] Update `AsIs` / `Literal` SQL composition references to use `psycopg.sql.Literal` and `psycopg.sql.Identifier` in all affected modules

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full unit and integration test suite against a live PostgreSQL instance and compare pass/fail counts to the Phase 1 baseline
- [ ] [S] Verify code coverage has not regressed below the Phase 1 baseline; investigate and fix any newly uncovered paths introduced by the migration
- [ ] [M] Write or update integration tests that explicitly exercise the replaced APIs (`executemany`, `dict_row`, JSON handling, `psycopg.sql` composition) to confirm correct behaviour
- [ ] [S] Perform a manual smoke test of all database-touching application entry points (e.g., API endpoints, CLI commands, background workers) against a staging PostgreSQL instance
- [ ] [XS] Confirm no `psycopg2` import or reference remains in the codebase using `grep -r "psycopg2" .` and resolve any remaining occurrences

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update `Dockerfile` (or equivalent container build file) to install `libpq-dev` / `libpq5` system packages required by `psycopg[c]`, or switch to `psycopg[binary]` to eliminate the system dependency
- [ ] [S] Update CI pipeline dependency-install step (e.g., `pip install -r requirements.txt`) to ensure `psycopg` resolves correctly and add a post-install assertion (`python -c "import psycopg"`) as a smoke check
- [ ] [XS] Remove any CI workarounds or pinned `psycopg2` versions from CI configuration files (e.g., `.github/workflows/*.yml`, `tox.ini`, `Makefile`)

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry describing the migration from `psycopg2` to `psycopg3`, noting any API behaviour changes relevant to contributors
- [ ] [XS] Update any developer setup documentation (e.g., `README.md`, `CONTRIBUTING.md`) that references `psycopg2` installation steps to reflect the new `psycopg` package name and system dependencies
- [ ] [S] Deploy to a staging environment and monitor database connection pool metrics, query error rates, and latency for at least one full business cycle before promoting to production
- [ ] [XS] After successful staging validation, merge the feature branch to main and tag the release