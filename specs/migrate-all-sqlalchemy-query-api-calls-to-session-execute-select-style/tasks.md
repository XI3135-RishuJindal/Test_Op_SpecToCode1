# Tasks: Migrate SQLAlchemy Query API → Session.execute(select()) Style

## Prerequisites

- [ ] [XS] Confirm SQLAlchemy version installed is ≥ 1.4 (required for `Session.execute(select())` compatibility) by running `pip show sqlalchemy` in the project environment
- [ ] [XS] Confirm Python environment is active and all dependencies install cleanly via `pip install -r requirements.txt` (or equivalent lockfile)
- [ ] [XS] Identify all files containing legacy Query API usage by running `grep -rn "\.query(" . --include="*.py"` and saving output as `query_api_audit.txt` for reference throughout migration

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated migration branch `migrate/sqlalchemy-query-to-execute` from the main branch
- [ ] [S] Run the full existing test suite and record the baseline pass/fail counts and coverage percentage in `migration-baseline.txt` before any code changes
- [ ] [S] Audit `query_api_audit.txt` and categorize every Query API call site by pattern type (e.g., `.query().filter()`, `.query().all()`, `.query().first()`, `.query().get()`, `.query().count()`, `.query().join()`, scalar vs. collection results) in a tracking spreadsheet or `migration-notes.md`
- [ ] [XS] Identify any use of `Query.get()` (deprecated in SQLAlchemy 2.0) separately, as it maps to `Session.get()` not `Session.execute(select())`, and flag those call sites in `migration-notes.md`
- [ ] [XS] Configure a CI gate (pre-commit hook or CI step) that runs `grep -rn "\.query(" . --include="*.py"` and fails if any legacy Query API calls remain, to prevent regressions during migration

---

## Phase 2 — Core Upgrade

- [ ] [M] Migrate all `.query(Model).filter(...).all()` call sites to `session.execute(select(Model).where(...)).scalars().all()` in each identified source file, working file-by-file per the audit list
- [ ] [M] Migrate all `.query(Model).filter(...).first()` call sites to `session.execute(select(Model).where(...)).scalars().first()` in each identified source file
- [ ] [S] Migrate all `.query(Model).get(pk)` call sites to `session.get(Model, pk)` in each identified source file (note: this is the correct 2.0-style replacement, not `select()`)
- [ ] [M] Migrate all `.query(Model).filter(...).one()` and `.one_or_none()` call sites to `session.execute(select(Model).where(...)).scalars().one()` / `.one_or_none()` in each identified source file
- [ ] [M] Migrate all `.query(Model).count()` call sites to `session.execute(select(func.count()).select_from(Model).where(...)).scalar()` in each identified source file, adding `from sqlalchemy import func` imports where missing
- [ ] [M] Migrate all `.query(Model).join(...).filter(...).all()` call sites to `session.execute(select(Model).join(...).where(...)).scalars().all()` in each identified source file
- [ ] [S] Migrate all `.query(Model).order_by(...).limit(...).offset(...)` call sites to `session.execute(select(Model).order_by(...).limit(...).offset(...)).scalars().all()` in each identified source file
- [ ] [S] Migrate all multi-column / tuple query patterns (e.g., `.query(Model.col1, Model.col2)`) to `session.execute(select(Model.col1, Model.col2).where(...))` returning `Row` objects instead of model instances, and update all downstream attribute access accordingly in each affected file
- [ ] [S] Replace all `from sqlalchemy.orm import Query` imports and any explicit `Query` type annotations with appropriate `Select` / `Result` types from `sqlalchemy` in each affected file
- [ ] [XS] Verify all files now use `from sqlalchemy import select` and that no bare `session.query(` strings remain by re-running the grep audit command

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite after migration and compare pass/fail counts and coverage against `migration-baseline.txt`; document any new failures in `migration-notes.md`
- [ ] [S] Fix any test failures caused by result-type changes (e.g., `Query` returned model instances directly; `execute().scalars()` returns `ScalarResult` — update assertions that relied on list indexing, tuple unpacking, or `Query`-specific methods)
- [ ] [S] Add or update unit tests for each migrated call-site pattern (filter/all, first, get, count, join) to assert correct return types and values using the new API in the project's test directory
- [ ] [XS] Confirm no `LegacyAPIWarning` or `MovedIn20Warning` warnings are emitted during the test run by enabling SQLAlchemy's `SQLALCHEMY_WARN_20=1` environment variable (if on 1.4) and checking test output

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Add the `grep -rn "\.query(" . --include="*.py"` regression check as a named CI step (e.g., `check-legacy-query-api`) in the project's CI pipeline configuration file so it runs on every pull request going forward

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CHANGELOG.md` (or equivalent) with an entry describing the migration from SQLAlchemy Query API to `Session.execute(select())` style, referencing the SQLAlchemy 2.0 migration guide URL (`https://docs.sqlalchemy.org/en/14/orm/queryguide.html`)
- [ ] [XS] Update any internal developer documentation or docstrings that reference `.query()` patterns to show the new `Session.execute(select())` equivalents
- [ ] [XS] Remove the migration branch tracking files (`query_api_audit.txt`, `migration-baseline.txt`, `migration-notes.md`) or move them to a `docs/migrations/` archive directory before merging