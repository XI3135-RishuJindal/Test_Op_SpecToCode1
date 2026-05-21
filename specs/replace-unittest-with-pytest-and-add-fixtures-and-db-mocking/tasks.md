# TASKS: Replace unittest with pytest, Add Fixtures and DB Mocking

---

## Prerequisites

- [ ] [XS] Confirm Python interpreter version in use and record it in `README.md` or a `CONTRIBUTING.md` note so all contributors target the same runtime
- [ ] [XS] Verify `pip` or the project's package manager is available and that the virtual environment can be activated before any install steps
- [ ] [XS] Confirm repository write access and ability to open pull requests against the main branch
- [ ] [XS] Identify the existing test entry-point (e.g., `python -m unittest discover`, `Makefile` target, or CI script command) so the replacement command can be mapped exactly

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `feat/pytest-migration`) from the current default branch before making any changes
- [ ] [S] Run the full existing `unittest` suite and capture a baseline report (pass count, fail count, skip count) to a file such as `docs/test-baseline.txt` for regression comparison later
- [ ] [XS] Add `pytest`, `pytest-mock`, and a DB mocking library (e.g., `pytest-postgresql`, `responses`, or `unittest.mock` shim as appropriate) to `requirements-dev.txt` (or `pyproject.toml` `[dev]` extras) with pinned minimum versions
- [ ] [XS] Audit all existing test files to list every `unittest.TestCase` subclass, `setUp`/`tearDown` method, and `self.assert*` call — record findings in a migration checklist comment or scratch doc to guide Phase 2 work

---

## Phase 2 — Core Upgrade

- [ ] [S] Install pytest and confirm it can discover and execute the existing `unittest`-style tests without modification (pytest is backward-compatible with `unittest.TestCase`; zero failures at this step is the gate)
- [ ] [M] Convert `unittest.TestCase` test classes to plain pytest functions, replacing `setUp`/`tearDown` with `@pytest.fixture` definitions in a `conftest.py` file at the appropriate package level
- [ ] [M] Replace all `self.assertEqual`, `self.assertRaises`, `self.assertIn`, and other `self.assert*` calls with plain `assert` statements and `pytest.raises` / `pytest.warns` context managers across all converted test files
- [ ] [M] Create shared fixtures in `conftest.py` for any repeated test data or object construction that was previously duplicated across `setUp` methods in multiple test classes
- [ ] [M] Implement DB mocking fixtures in `conftest.py` — define a session-scoped or function-scoped fixture that patches the database connection/session (using `pytest-mock` `mocker.patch`, a fake in-memory DB, or a dedicated library) so no test requires a live database connection
- [ ] [S] Replace any direct `unittest.mock.patch` decorator usage with equivalent `mocker.patch` calls (via `pytest-mock`) or `@pytest.fixture`-based patches to keep mocking style consistent throughout the test suite
- [ ] [XS] Add a `pytest.ini` (or `[tool.pytest.ini_options]` block in `pyproject.toml`) configuring `testpaths`, `python_files`, `python_classes`, and `python_functions` to match the project's file layout

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full pytest suite and confirm the pass/fail/skip counts match or improve upon the baseline captured in `docs/test-baseline.txt`
- [ ] [XS] Verify that no test touches a real database connection by running the suite with the DB host intentionally unreachable and confirming all tests still pass
- [ ] [XS] Check that pytest exit codes are correct (exit 0 on all-pass, non-zero on any failure) so CI gates will behave as expected
- [ ] [XS] Review pytest output for any `PytestUnraisableExceptionWarning` or deprecation warnings introduced by the migration and resolve or explicitly mark them

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline test step (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or equivalent) to replace the `unittest` discovery command with `pytest` and ensure the virtual environment installs `requirements-dev.txt` before running tests
- [ ] [XS] Remove any CI environment variables or service containers (e.g., a live Postgres service block) that were only needed because tests previously hit a real DB, replacing with the mock fixture approach confirmed in Phase 3

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` (or `CONTRIBUTING.md`) test-running instructions to replace the old `python -m unittest` command with `pytest` and document any useful flags (e.g., `-v`, `-x`, `--tb=short`)
- [ ] [XS] Add a `CHANGELOG.md` entry describing the migration from `unittest` to pytest, the addition of fixtures, and the DB mocking strategy adopted
- [ ] [XS] Open the pull request, request review, and confirm CI passes end-to-end on the feature branch before merging