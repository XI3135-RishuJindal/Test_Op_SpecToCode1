# TASKS: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

---

## Prerequisites

- [ ] [XS] Confirm Python environment has SQLAlchemy installed and record the exact installed version by running `python -c "import sqlalchemy; print(sqlalchemy.__version__)"` in the project root
- [ ] [XS] Verify SQLAlchemy version is >= 2.0.0 (or >= 1.4.x with `future=True` flag enabled) before any migration work begins — check `requirements.txt`, `pyproject.toml`, or `setup.cfg`
- [ ] [XS] Confirm access to the full source tree and identify all Python files containing legacy query API usage by running `grep -rn "\.query\(" . --include="*.py"` from the project root
- [ ] [XS] Ensure a dedicated migration branch (e.g., `migrate/sqlalchemy-2-select-style`) is available and all contributors are aware of the freeze on merging new legacy-style query code during migration

---

## Phase 1 — Preparation

- [ ] [S] Audit all files containing `session.query(` calls using `grep -rn "session\.query\("` and produce a prioritized inventory list grouped by module, recording file path, line number, and query complexity (simple fetch, filter, join, subquery)
- [ ] [S] Audit all files containing `.filter(`, `.filter_by(`, `.first()`, `.all()`, `.one()`, `.one_or_none()` chained on legacy `Query` objects and append findings to the inventory list
- [ ] [XS] Identify any use of `Query.update()` or `Query.delete()` (bulk DML via legacy API) across the codebase using `grep -rn "\.query(.*)\.\(update\|delete\)("` and flag these separately as they require `update()` / `delete()` construct migration
- [ ] [XS] Capture the current test suite pass/fail baseline by running the full test suite and saving output to `migration-baseline-test-results.txt` in the repo root for regression comparison
- [ ] [XS] Enable SQLAlchemy's legacy query deprecation warnings by setting `SQLALCHEMY_WARN_20=1` (for 1.4.x) or confirming 2.0 engine raises `LegacyAPIWarning`, and run the test suite once to surface all warning locations — save output to `migration-warnings-baseline.txt`
- [ ] [XS] Configure CI to treat `LegacyAPIWarning` / `RemovedIn20Warning` as errors (add `-W error::sqlalchemy.exc.RemovedIn20Warning` to pytest invocation in `pytest.ini`, `pyproject.toml [tool.pytest.ini_options]`, or CI config) so regressions are caught automatically during migration

---

## Phase 2 — Core Upgrade

> Tasks are ordered from lowest-risk (simple fetches) to highest-risk (bulk DML, subqueries). Complete each group before proceeding to the next.

### 2a — Engine / Session Configuration

- [ ] [XS] Update `create_engine()` calls to remove `future=False` or add `future=True` in the engine initialization file (commonly `db.py`, `database.py`, or `core/db.py`) to opt into 2.0 connection behavior
- [ ] [XS] Replace any `Session(bind=engine)` or `sessionmaker(bind=engine)` patterns with the 2.0-compatible `sessionmaker(engine)` form in the session factory module

### 2b — Simple Single-Table Fetches

- [ ] [M] Migrate all `session.query(Model).all()` calls to `session.execute(select(Model)).scalars().all()` in every file identified in the Phase 1 inventory — update imports to include `from sqlalchemy import select`
- [ ] [M] Migrate all `session.query(Model).first()` calls to `session.execute(select(Model)).scalars().first()` across all affected files
- [ ] [M] Migrate all `session.query(Model).one()` and `.one_or_none()` calls to `session.execute(select(Model)).scalars().one()` / `.one_or_none()` across all affected files

### 2c — Filtered Queries

- [ ] [M] Migrate all `session.query(Model).filter(...)` chains to `session.execute(select(Model).where(...)).scalars()` equivalents, replacing `.filter()` with `.where()` in every affected file
- [ ] [M] Migrate all `session.query(Model).filter_by(**kwargs)` calls to `select(Model).filter_by(**kwargs)` (`.filter_by()` is retained on `Select` in 2.0) or explicit `.where()` clauses across all affected files

### 2d — Ordering, Limiting, and Offsetting

- [ ] [S] Migrate all `.order_by()`, `.limit()`, and `.offset()` clauses chained on legacy `Query` objects to equivalent clauses on `select()` constructs in all affected files (syntax is identical; ensure they are now chained on the `Select` object, not the result)

### 2e — Joins

- [ ] [L] Migrate all `session.query(Model).join(OtherModel, condition)` patterns to `select(Model).join(OtherModel, condition)` constructs in all affected files, verifying that joined-load behavior and result unpacking (e.g., `Row` vs scalar) is preserved
- [ ] [S] Migrate all `session.query(Model, OtherModel)` multi-entity queries to `select(Model, OtherModel)` and update result unpacking from tuple indexing to `row.Model` / `row.OtherModel` named-attribute access where applicable

### 2f — Aggregates and Scalar Results

- [ ] [S] Migrate all `session.query(func.count(...)).scalar()` calls to `session.execute(select(func.count(...))).scalar()` in all affected files
- [ ] [S] Migrate all `session.query(Model.column)` column-only projections to `select(Model.column)` and update result unpacking to use `.scalars()` or column-keyed `Row` access in all affected files

### 2g — Subqueries

- [ ] [M] Migrate all `session.query(...).subquery()` usages to `select(...).subquery()` constructs and update any parent queries that reference the subquery alias in all affected files

### 2h — Bulk DML (High Risk)

- [ ] [M] Migrate all `session.query(Model).filter(...).update({...})` bulk-update calls to `session.execute(update(Model).where(...).values(...))` using `from sqlalchemy import update` in all affected files — verify `synchronize_session` strategy is explicitly set
- [ ] [M] Migrate all `session.query(Model).filter(...).delete()` bulk-delete calls to `session.execute(delete(Model).where(...))` using `from sqlalchemy import delete` in all affected files — verify `synchronize_session` strategy is explicitly set

### 2i — ORM Relationship Loading

- [ ] [S] Audit and migrate any `session.query(Model).options(joinedload(...))` or `subqueryload(...)` calls to `select(Model).options(joinedload(...))` equivalents in all affected files, confirming loader strategy imports come from `sqlalchemy.orm`

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full test suite after each Phase 2 sub-group completion and compare output against `migration-baseline-test-results.txt` — record any new failures immediately before proceeding
- [ ] [S] Confirm zero `RemovedIn20Warning` / `LegacyAPIWarning` warnings remain in test output after all Phase 2 tasks are complete
- [ ] [S] Execute `grep -rn "session\.query\(" . --include="*.py"` and `grep -rn "\.query\(" . --include="*.py"` to verify no legacy `Query` API calls remain in the codebase
- [ ] [XS] Verify all result-unpacking code (loops, list comprehensions, tuple destructuring) that consumes query results still functions correctly by reviewing test coverage for each migrated module
- [ ] [M] Write or update integration tests for any bulk DML paths (`update()` / `delete()`) migrated in Phase 2h to assert row counts and session state are correct post-execution

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Remove the `SQLALCHEMY_WARN_20=1` environment variable (if set for 1.4 transition) from CI configuration now that migration to 2.0 style is complete
- [ ] [XS] Retain (or promote to permanent) the `-W error::sqlalchemy.exc.SAWarning` pytest flag in `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` to prevent future regressions to legacy API usage
- [ ] [XS] Update `requirements.txt`, `pyproject.toml`, or `setup.cfg` to pin SQLAlchemy to `>=2.0,<3.0` (or the appropriate lower bound confirmed in Prerequisites) to prevent accidental downgrade

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) documenting the migration from SQLAlchemy legacy `Query` API to 2.0 `select()` style, referencing the affected modules and the SQLAlchemy 2.0 migration guide URL (`https://docs.sqlalchemy.org/en/20/changelog/migration_20.html`)
- [ ] [XS] Update any internal developer documentation or `README` sections that contain code examples using `session.query()` to show the equivalent `select()` style
- [ ] [XS] Notify the team that all new query code must use `select()` style and add a note to the contributing guide (e.g., `CONTRIBUTING.md`) referencing the SQLAlchemy 2.0 query API as the project standard
- [ ] [XS] Monitor application error logs and APM tooling (if available) for any `sqlalchemy` related exceptions in the first 48 hours post-merge to catch any runtime regressions not covered by tests