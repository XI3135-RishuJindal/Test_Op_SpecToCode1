# Tasks: Migrate Test Suite from unittest to pytest with Fixtures, Mocking, and DB Isolation

> **Scope:** Migrate existing `unittest`-based tests to `pytest` idioms, introducing fixtures, `unittest.mock` → `pytest-mock` migration, and database isolation patterns.
> **Upgrade urgency:** Medium
> **Option:** Moderate — preserve test logic, modernise structure and tooling.

---

## Prerequisites

- [ ] [XS] Confirm Python version supports target pytest release (pytest ≥ 7.x requires Python ≥ 3.7) in local environment and CI runner
- [ ] [XS] Verify write access to the repository and permission to modify CI pipeline configuration files
- [ ] [XS] Confirm database credentials and a dedicated test database (or in-memory equivalent) are available for DB isolation work
- [ ] [XS] Ensure `pip` or the project's package manager can install new dev dependencies (`pytest`, `pytest-mock`, `pytest-cov`, `factory-boy` or equivalent fixture factories if used)

---

## Phase 1 — Preparation

- [ ] [S] Audit all existing test files under the test directory — catalogue every `unittest.TestCase` subclass, `setUp`/`tearDown` method, `self.assert*` call, and `unittest.mock` import, outputting a migration inventory spreadsheet or markdown table
- [ ] [S] Capture the current test baseline — run the full `unittest` suite, record pass/fail counts, coverage percentage (via `coverage run -m unittest discover`), and save output to `docs/test-baseline-unittest.txt`
- [ ] [XS] Create a dedicated migration branch `feat/pytest-migration` from the main branch
- [ ] [XS] Add `pytest`, `pytest-mock`, `pytest-cov`, and `pytest-xdist` (optional parallelism) to `requirements-dev.txt` (or `pyproject.toml` `[dev]` extras) with pinned minimum versions (e.g. `pytest>=7.4`, `pytest-mock>=3.11`, `pytest-cov>=4.1`)
- [ ] [XS] Add a `pytest.ini` (or `[tool.pytest.ini_options]` block in `pyproject.toml`) with `testpaths`, `python_files`, `python_classes`, and `python_functions` discovery settings matching the existing test directory layout
- [ ] [XS] Configure a CI gate in the pipeline config to run `pytest --tb=short -q` and fail on any regression against the baseline pass count before merging the migration branch

---

## Phase 2 — Core Upgrade

- [ ] [M] Convert all `unittest.TestCase` subclasses that contain only simple test methods (no shared state) to plain pytest functions — remove class inheritance, replace `self.assertEqual(a, b)` → `assert a == b`, `self.assertTrue(x)` → `assert x`, etc., across all affected test files
- [ ] [M] Convert `unittest.TestCase` subclasses that use `setUp` / `tearDown` to pytest classes or module-level `conftest.py` fixtures — replace `setUp` with `@pytest.fixture(autouse=True)` or explicit fixture parameters, and `tearDown` with fixture `yield` teardown blocks
- [ ] [S] Replace all `unittest.mock.patch` decorator and context-manager usages with `pytest-mock`'s `mocker.patch` fixture — update every `@patch(...)` decorator and `with patch(...) as mock_x:` block in test files to use `mocker.patch(...)` injected via the `mocker` fixture parameter
- [ ] [S] Replace all `unittest.mock.MagicMock()` and `unittest.mock.Mock()` instantiations in test files with `mocker.MagicMock()` / `mocker.Mock()` where the `mocker` fixture is already in scope, ensuring auto-reset between tests
- [ ] [M] Create a `conftest.py` at the top-level test directory — define shared fixtures for any objects constructed repeatedly across test classes (e.g. application client, service instances, configuration objects) extracted from `setUp` methods identified in the Phase 1 audit
- [ ] [M] Implement DB isolation fixtures in `conftest.py` — create a `db_session` fixture scoped to `function` that wraps each test in a transaction and issues a rollback on teardown (using the project's ORM session/connection API), replacing any manual `setUp`/`tearDown` DB reset logic found in the audit
- [ ] [S] Replace any `self.assertRaises(ExcType)` context-manager usages with `pytest.raises(ExcType)` blocks in all affected test files
- [ ] [XS] Remove all `if __name__ == "__main__": unittest.main()` blocks from test files now superseded by pytest discovery

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full pytest suite (`pytest --tb=short -q`) and confirm zero regressions against the baseline pass/fail count recorded in `docs/test-baseline-unittest.txt`
- [ ] [S] Run `pytest --cov=<source_package> --cov-report=term-missing` and verify coverage is equal to or greater than the baseline percentage captured in Phase 1
- [ ] [XS] Verify DB isolation by intentionally writing a dirty-data test and confirming subsequent tests do not observe the dirty state (i.e. rollback fixture is functioning correctly)
- [ ] [XS] Confirm `pytest-mock` auto-reset is working — verify that a mock patched in one test is not visible in a subsequent test by adding a canary assertion in a temporary test, then removing it
- [ ] [S] Review and resolve any `PytestUnraisableExceptionWarning`, `DeprecationWarning`, or `PytestCollectionWarning` entries in the pytest output, updating affected test files accordingly

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g. `.github/workflows/test.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`) — replace `python -m unittest discover` invocation with `pytest --tb=short -q --cov=<source_package> --cov-fail-under=<baseline_pct>`
- [ ] [XS] Add `pytest-cov` coverage report artifact upload step to the CI pipeline so HTML reports are stored per run
- [ ] [XS] Remove any CI steps that installed or invoked `coverage run -m unittest` now replaced by the pytest-cov integration

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CONTRIBUTING.md` (or equivalent developer guide) — replace all references to `python -m unittest` with `pytest` invocation instructions, and document the `db_session` and `mocker` fixture conventions
- [ ] [XS] Add a `CHANGELOG.md` entry describing the migration: pytest version adopted, removal of `unittest.TestCase` base classes, new fixture conventions, and DB isolation approach
- [ ] [XS] Open a pull request from `feat/pytest-migration` to main, request review from at least one other engineer familiar with the test suite, and confirm CI green before merge
- [ ] [XS] After merge, monitor the first three CI runs on main for flaky tests or unexpected failures and file issues for any instability introduced by fixture scoping changes