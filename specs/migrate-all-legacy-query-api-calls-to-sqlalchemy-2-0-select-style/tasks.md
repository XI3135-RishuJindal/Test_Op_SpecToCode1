# TASKS: Migrate Legacy Query API to SQLAlchemy 2.0 `select()` Style

> **Scope:** Replace all SQLAlchemy legacy `Query` API usage (`session.query(...)`) with the SQLAlchemy 2.0 `select()` style throughout the codebase.
> **Urgency:** Medium
> **Option:** Moderate migration path

---

## Prerequisites

- [ ] [XS] Confirm SQLAlchemy version installed is ≥ 1.4 (required for `select()` compatibility shim) by running `pip show sqlalchemy` and recording the output
- [ ] [XS] Confirm Python environment is active and `pip` or equivalent package manager is accessible before beginning any dependency changes
- [ ] [XS] Verify test suite can be executed end-to-end locally (e.g., `pytest`) and produces a passing baseline before any changes are made
- [ ] [XS] Ensure write access to the repository and permission to open pull requests against the main branch

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated migration branch (e.g., `migrate/sqlalchemy-2-select-style`) from the current default branch to isolate all changes
- [ ] [S] Run a full-codebase grep/search for all occurrences of `session.query(`, `.filter(`, `.filter_by(`, `.first()`, `.all()`, `.one()`, `.one_or_none()`, `.scalar()` on `Query` objects and export results to a `migration-audit.txt` file for tracking
- [ ] [S] Run a full-codebase grep for `from sqlalchemy.orm import Query` and any direct subclassing of `Query` to identify custom query classes requiring special handling
- [ ] [XS] Enable SQLAlchemy's legacy query deprecation warnings by setting `SQLALCHEMY_WARN_20=1` (SQLAlchemy 1.4) or equivalent and capture the full warning output to `deprecation-warnings.txt`
- [ ] [XS] Record the current test suite pass/fail counts and coverage percentage as a regression baseline before any code changes

---

## Phase 2 — Core Upgrade

- [ ] [S] Upgrade SQLAlchemy to the latest 2.x release in the project's dependency file (e.g., `requirements.txt`, `pyproject.toml`, or `setup.cfg`) and resolve any direct version conflicts with pinned packages
- [ ] [M] Replace all `session.query(Model).filter(...)` patterns with `session.execute(select(Model).where(...))` equivalents, updating result access from `.all()` / `.first()` to `.scalars().all()` / `.scalars().first()` across all identified source files
- [ ] [M] Replace all `session.query(Model).filter_by(...)` patterns with `select(Model).where(Model.attr == value)` equivalents in all identified source files
- [ ] [S] Replace all `session.query(Model).get(pk)` calls with `session.get(Model, pk)` (the SQLAlchemy 2.0 canonical replacement) across all identified source files
- [ ] [S] Replace all `session.query(func.count(...))` and aggregate query patterns with `select(func.count(...))` equivalents and update scalar result extraction to use `session.execute(...).scalar()`
- [ ] [S] Replace all `session.query(Model.col1, Model.col2)` column-subset queries with `select(Model.col1, Model.col2)` and update result unpacking to use `.mappings()` or tuple access as appropriate
- [ ] [M] Refactor any custom `Query` subclasses to standalone functions or repository methods using `select()` style, removing inheritance from `sqlalchemy.orm.Query`
- [ ] [S] Add `from sqlalchemy import select` and `from sqlalchemy import func` imports (as needed) to every module modified, and remove now-unused `Query` imports
- [ ] [XS] Remove the `SQLALCHEMY_WARN_20=1` environment variable flag (or equivalent) from any local dev config files after migration is complete

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite (`pytest` or equivalent) against the migrated codebase and resolve all failures caused by changed result types (e.g., `Row` vs model instance, `ScalarResult` vs `list`)
- [ ] [S] Verify that no SQLAlchemy `LegacyAPIWarning` or `RemovedIn20Warning` deprecation warnings remain in test output after migration
- [ ] [S] Compare post-migration test pass/fail counts and coverage percentage against the pre-migration baseline recorded in Phase 1 and confirm no regression
- [ ] [S] Manually execute or review integration tests covering critical query paths (e.g., authentication, data retrieval, reporting) to confirm correct result shapes and values
- [ ] [XS] Confirm `migration-audit.txt` entries are fully resolved by re-running the original grep patterns and verifying zero remaining matches for `session.query(`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update the CI pipeline dependency installation step to install the upgraded SQLAlchemy 2.x version and confirm the pipeline resolves dependencies without conflicts
- [ ] [XS] Remove `SQLALCHEMY_WARN_20=1` from any CI environment variable configuration if it was added during the migration process

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry documenting the migration from SQLAlchemy legacy `Query` API to 2.0 `select()` style, including the SQLAlchemy version bumped to
- [ ] [XS] Update any internal developer documentation or README sections that reference `session.query()` patterns with the equivalent `select()` style examples
- [ ] [S] Conduct a pull request review with at least one other engineer, using `migration-audit.txt` as a checklist to confirm all identified call sites were addressed
- [ ] [XS] Monitor application error logs and query-related exceptions for 48 hours post-merge to catch any runtime result-handling regressions not covered by tests