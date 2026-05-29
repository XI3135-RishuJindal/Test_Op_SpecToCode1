# TASKS: Migrate Test Suite from unittest to pytest with Fixtures and Database Mocking

> **Scope:** Migrate existing `unittest`-based tests to `pytest` idioms, introduce pytest fixtures, and replace direct database calls with mocking.
> **Upgrade Option:** Moderate — incremental migration preserving test coverage throughout.

---

## Prerequisites

- [ ] [XS] Confirm Python version and pytest compatibility by running `python --version` and checking `pytest>=7.x` support in the local environment
- [ ] [XS] Verify write access to the repository and ability to open pull requests against the main branch
- [ ] [XS] Confirm `pip` or equivalent package manager is available and a `requirements.txt`, `pyproject.toml`, or `setup.cfg` file exists for dependency pinning
- [ ] [XS] Identify all test files by running `find . -name "test_*.py" -o -name "*_test.py"` and document the full list before any changes begin

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated migration branch `feat/pytest-migration` from the current default branch
- [ ] [S] Capture the current test baseline by running the full `unittest` suite with `python -m unittest discover` and saving the output (pass/fail counts, coverage if available) to `docs/test-baseline-unittest.txt`
- [ ] [S] Add `pytest`, `pytest-mock`, and `pytest-cov` as development dependencies in the project's dependency file (`requirements-dev.txt`, `pyproject.toml`, or `setup.cfg`), pinning to the latest stable versions (e.g., `pytest>=7.4`, `pytest-mock>=3.11`, `pytest-cov>=4.1`)
- [ ] [XS] Add a `pytest.ini` or `[tool.pytest.ini_options]` section in `pyproject.toml` configuring `testpaths`, `python_files`, `python_classes`, and `python_functions` to match the existing test discovery layout
- [ ] [XS] Verify that `pytest` can discover and run the existing `unittest.TestCase` tests without modification by executing `pytest --collect-only` and confirming zero collection errors
- [ ] [XS] Configure a CI gate (or local pre-commit check) that fails if collected test count drops below the baseline count captured in `docs/test-baseline-unittest.txt`

---

## Phase 2 — Core Upgrade

- [ ] [M] Convert `unittest.TestCase` test classes to plain pytest functions in each test file, removing `self` parameters and replacing `self.assert*` calls with bare `assert` statements — work file-by-file starting with the smallest/least-coupled test module
- [ ] [M] Replace `setUp` and `tearDown` methods with `@pytest.fixture` functions scoped appropriately (`function`, `module`, or `session`) in a shared `conftest.py` at the root of the test directory
- [ ] [S] Replace `setUpClass` / `tearDownClass` patterns with `@pytest.fixture(scope="module")` or `@pytest.fixture(scope="session")` fixtures in `conftest.py`
- [ ] [M] Introduce a `db_session` fixture in `conftest.py` that provides a mocked or in-memory database connection using `pytest-mock`'s `mocker` fixture or `unittest.mock.patch` as a pytest fixture, replacing any direct database instantiation in test files
- [ ] [M] Replace all `unittest.mock.patch` decorator usage on test methods with `mocker.patch(...)` calls inside pytest functions or dedicated `@pytest.fixture` wrappers in `conftest.py`
- [ ] [S] Replace `self.assertRaises(ExceptionType)` blocks with `pytest.raises(ExceptionType)` context managers in all affected test functions
- [ ] [S] Replace `self.assertIn`, `self.assertEqual`, `self.assertTrue`, and similar assertion methods with plain `assert` expressions and, where appropriate, `pytest.approx()` for numeric comparisons across all migrated test files
- [ ] [S] Remove all remaining `import unittest` statements and `unittest.TestCase` base class references from fully migrated test files, confirming each file still collects cleanly with `pytest --collect-only`
- [ ] [XS] Add a `conftest.py` at the project root (if not already present) and move any shared fixtures, mock factories, or test data builders into it

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full pytest suite with `pytest -v --tb=short` and confirm all previously passing tests still pass, comparing pass/fail counts against `docs/test-baseline-unittest.txt`
- [ ] [S] Run `pytest --cov=<source_package> --cov-report=term-missing` and confirm coverage is equal to or greater than the pre-migration baseline; document results in `docs/test-baseline-pytest.txt`
- [ ] [S] Verify database mocking is effective by asserting no real database connections are opened during the test run (e.g., check for absence of connection strings in logs, or assert mock call counts on the `db_session` fixture)
- [ ] [XS] Run `pytest --collect-only` and confirm the collected test count matches or exceeds the `unittest discover` baseline count
- [ ] [XS] Check for and resolve any pytest warnings (`PytestUnraisableExceptionWarning`, deprecation warnings) surfaced during the test run by reviewing `pytest -W error` output

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline test step to replace `python -m unittest discover` with `pytest --cov=<source_package> --cov-report=xml -q` in the pipeline configuration file (e.g., `.github/workflows/test.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`)
- [ ] [XS] Add `pytest-cov` XML report upload/artifact step to the CI pipeline so coverage results are stored per run
- [ ] [XS] Remove any CI steps or scripts that reference `unittest` discovery commands after confirming the pytest step is green

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry describing the migration from `unittest` to `pytest`, listing new dev dependencies and the introduction of `conftest.py` fixtures
- [ ] [S] Update the project's `CONTRIBUTING.md` or `docs/testing.md` to document how to run the pytest suite, how to use the `db_session` and other shared fixtures, and the convention for adding new fixtures in `conftest.py`
- [ ] [XS] Open the migration pull request against the main branch, referencing the baseline comparison documents (`docs/test-baseline-unittest.txt` vs `docs/test-baseline-pytest.txt`) in the PR description
- [ ] [XS] After merge, monitor the first CI run on the main branch to confirm no flaky tests or fixture-scope issues appear in the post-migration pipeline run