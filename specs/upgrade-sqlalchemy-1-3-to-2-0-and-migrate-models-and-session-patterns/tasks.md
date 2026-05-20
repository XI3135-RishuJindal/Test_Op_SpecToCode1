# Tasks: Upgrade SQLAlchemy 1.3 → 2.0 and Migrate Models & Session Patterns

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility (SQLAlchemy 2.0 requires Python 3.7+; 3.8+ recommended) in local and CI environments
- [ ] [XS] Confirm `pip` or `pip-tools` / `poetry` / `pipenv` is available and pinned in the project's dependency management file (`requirements.txt`, `pyproject.toml`, or `Pipfile`)
- [ ] [XS] Ensure a dedicated feature branch (e.g., `upgrade/sqlalchemy-2`) is created from the current default branch before any changes begin
- [ ] [XS] Verify database access credentials and a local or CI-accessible test database are available for integration test runs

---

## Phase 1 — Preparation

- [ ] [S] Audit all direct and transitive dependencies that pin or constrain SQLAlchemy 1.3 (e.g., `Flask-SQLAlchemy`, `alembic`, `databases`, `SQLModel`) in `requirements.txt` / `pyproject.toml` and document version compatibility with SQLAlchemy 2.0
- [ ] [S] Enable SQLAlchemy 1.4 legacy deprecation warnings as errors by setting `SQLALCHEMY_WARN_20=1` (env var) and `legacy_style_query_interface` flags in the existing engine/session setup file to surface all 2.0-incompatible call sites before upgrading
- [ ] [M] Run the full existing test suite with `SQLALCHEMY_WARN_20=1` active and capture a baseline report of all emitted `RemovedIn20Warning` warnings, saving output to `docs/sqlalchemy-migration/warnings-baseline.txt`
- [ ] [XS] Capture current test suite pass/fail counts and code coverage percentage as a pre-upgrade baseline, saving to `docs/sqlalchemy-migration/test-baseline.txt`
- [ ] [XS] Pin SQLAlchemy to `>=1.4,<2.0` temporarily in the dependency file to enable the 1.4 bridge/compatibility layer before the final 2.0 bump

---

## Phase 2 — Core Upgrade

> Tasks are ordered by dependency chain: engine/session infrastructure first, then declarative models, then query call sites, then any ORM relationship patterns.

- [ ] [S] Upgrade SQLAlchemy from `1.3.x` to `1.4.x` (latest 1.4 patch) in `requirements.txt` / `pyproject.toml` and resolve any immediate import or startup errors
- [ ] [M] Migrate engine creation from `create_engine()` with legacy `pool_pre_ping`, `connect_args`, and `execution_options` kwargs to the SQLAlchemy 2.0-compatible signatures in the engine factory module; replace any `engine.execute()` calls with explicit `with engine.connect() as conn: conn.execute()`
- [ ] [M] Migrate session factory from `Session(bind=engine)` / `sessionmaker(bind=engine)` legacy patterns to `sessionmaker(bind=engine)` with `autocommit=False, autoflush=False` explicit flags, and replace all bare `session.execute(string_sql)` calls with `session.execute(text("..."))` in the session setup module
- [ ] [M] Replace all `Query`-style ORM calls (e.g., `session.query(Model).filter(...)`) with the 2.0 `select()` / `session.execute(select(Model).where(...))` style across all model query modules, working file by file
- [ ] [S] Migrate all `Column`-based declarative model classes to use `mapped_column()` and `Mapped[type]` type annotations in the models package, updating `__tablename__`, primary keys, and nullable flags accordingly
- [ ] [S] Replace all uses of `relationship()` with legacy `backref=` string shortcuts with explicit `back_populates=` on both sides of each relationship in the models package
- [ ] [S] Remove all uses of `Query.get()` (deprecated) and replace with `session.get(Model, pk)` across all repository/service modules
- [ ] [S] Migrate any raw-string SQL passed directly to `session.execute()` or `connection.execute()` to use `sqlalchemy.text()` wrappers in all affected service and repository modules
- [ ] [S] Update `alembic` (if present) to a version compatible with SQLAlchemy 2.0 in `requirements.txt` / `pyproject.toml` and verify `env.py` uses `engine.begin()` context manager pattern instead of deprecated `engine.connect()` + `connection.execute()` pattern
- [ ] [M] Bump SQLAlchemy from `1.4.x` to `2.0.x` (latest stable) in `requirements.txt` / `pyproject.toml` and resolve any remaining hard errors surfaced by the final version bump
- [ ] [S] Remove the `SQLALCHEMY_WARN_20=1` environment variable flag and any 1.4 compatibility shims added during Phase 1 from all config and environment files

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full unit and integration test suite against SQLAlchemy 2.0 and compare pass/fail counts against the baseline captured in `docs/sqlalchemy-migration/test-baseline.txt`; fix any regressions
- [ ] [S] Verify that no `RemovedIn20Warning` or `LegacyAPIWarning` warnings remain in test output by running with `warnings.filterwarnings("error", category=sqlalchemy.exc.RemovedIn20Warning)` in `pytest.ini` or `conftest.py`
- [ ] [S] Execute all Alembic migration scripts (`alembic upgrade head` and `alembic downgrade base`) against a clean test database and confirm no errors
- [ ] [S] Verify code coverage has not regressed below the pre-upgrade baseline percentage recorded in `docs/sqlalchemy-migration/test-baseline.txt`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline dependency-install step to install SQLAlchemy 2.0.x (remove any `<2.0` upper-bound pins) in the CI configuration file (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`)
- [ ] [XS] Remove the `SQLALCHEMY_WARN_20=1` environment variable from all CI job environment configurations
- [ ] [XS] Confirm the CI test job enforces `warnings-as-errors` for SQLAlchemy legacy warnings so regressions are caught automatically in future PRs

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Write a `CHANGELOG` entry documenting the SQLAlchemy 1.3 → 2.0 upgrade, listing breaking pattern changes (Query API removal, `text()` requirement, `mapped_column()` adoption) and any application-level behaviour changes
- [ ] [S] Update the project's developer setup guide / `README` to reflect the new SQLAlchemy 2.0 session and query patterns, removing any 1.x code examples
- [ ] [XS] Archive the migration artefacts (`warnings-baseline.txt`, `test-baseline.txt`) in `docs/sqlalchemy-migration/` and link them from the `CHANGELOG` entry for future reference
- [ ] [XS] Monitor application error logs and database query performance metrics for 48 hours post-deployment to confirm no latent session-handling or connection-pool regressions