# TASKS: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

> **Scope:** Migrate existing `unittest`-based tests to `pytest` idioms, introducing fixtures and replacing `unittest.mock` usage with `pytest`-native or `pytest-mock` patterns.
> **Upgrade Option:** Moderate — incremental migration preserving test coverage throughout.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with `pytest>=7.x` and `pytest-mock>=3.x` in the local development environment
- [ ] [XS] Verify write access to the repository and permission to create feature branches and open pull requests
- [ ] [XS] Confirm CI pipeline can be triggered on feature branches before merging
- [ ] [XS] Ensure all current tests pass on `main` (or equivalent trunk branch) before migration begins — document any pre-existing failures as known issues

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch `migrate/unittest-to-pytest` from the current trunk
- [ ] [S] Audit all test files in the test directory — list every file using `unittest.TestCase`, `setUp`/`tearDown`, `self.assert*`, and `unittest.mock` — record findings in `docs/test-migration-inventory.md`
- [ ] [XS] Add `pytest`, `pytest-mock`, and `pytest-cov` to the project's dependency file (e.g., `requirements-dev.txt`, `pyproject.toml`, or `setup.cfg`) with pinned minimum versions (`pytest>=7.0`, `pytest-mock>=3.6`, `pytest-cov>=4.0`)
- [ ] [XS] Add a `pytest.ini` or `[tool.pytest.ini_options]` section in `pyproject.toml` configuring `testpaths`, `python_files`, `python_classes`, and `python_functions` to match the existing test layout
- [ ] [S] Capture the pre-migration test baseline: run the full suite with `python -m pytest --tb=short --co -q` (after installing pytest) and save the collected test count and any warnings to `docs/test-baseline-pre-migration.txt`
- [ ] [XS] Configure a CI gate on the feature branch that runs `pytest --tb=short` and fails the build on any test regression

---

## Phase 2 — Core Upgrade

- [ ] [S] Remove `unittest.TestCase` inheritance from the first batch of test classes — convert class-based test methods to standalone `pytest` functions, replacing `self.assertEqual`/`self.assertTrue`/etc. with plain `assert` statements in the first test module identified in the inventory
- [ ] [M] Convert `setUp` and `tearDown` methods across all test modules to `pytest` fixtures using `@pytest.fixture` with appropriate `scope` (`function`, `module`, or `session`) — place shared fixtures in a `conftest.py` at the relevant directory level
- [ ] [M] Replace all `unittest.mock.patch` decorator and context-manager usage with `pytest-mock`'s `mocker` fixture (`mocker.patch`, `mocker.patch.object`) across all test modules identified in the inventory
- [ ] [S] Replace `unittest.mock.MagicMock` and `unittest.mock.Mock` instantiation with `mocker.MagicMock` / `mocker.Mock` (or standalone `from unittest.mock import MagicMock` where `pytest-mock` is not warranted) — ensure no bare `unittest.mock` imports remain in migrated files
- [ ] [S] Convert `unittest.mock.patch` used as a class decorator on `TestCase` subclasses to `mocker.patch` calls inside the corresponding `pytest` fixture or test function body
- [ ] [S] Migrate `assertRaises` / `assertWarns` usage to `pytest.raises` and `pytest.warns` context managers across all test modules
- [ ] [S] Extract repeated test data setup (previously in `setUp`) into parameterized fixtures or `@pytest.mark.parametrize` decorators where applicable, reducing duplication across test modules
- [ ] [XS] Remove any remaining `import unittest` statements from fully migrated test files and confirm no `unittest.TestCase` subclasses remain
- [ ] [XS] Add a `conftest.py` at the project root (or top-level test directory) consolidating all session-scoped and module-scoped fixtures identified during conversion

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full migrated test suite with `pytest --tb=short -v` and confirm the collected test count matches the pre-migration baseline recorded in `docs/test-baseline-pre-migration.txt`
- [ ] [S] Run `pytest --cov=<source_package> --cov-report=term-missing` and compare coverage percentages against the pre-migration baseline — investigate and resolve any coverage regressions
- [ ] [XS] Run `pytest --co -q` and confirm zero collection warnings related to `unittest` discovery or deprecated APIs
- [ ] [XS] Verify that `pytest-mock`'s `mocker` fixture teardown correctly resets all patches between tests by running the suite twice in randomized order (`pytest-randomly` or `pytest -p no:randomly`) and confirming no order-dependent failures
- [ ] [XS] Confirm no test relies on `unittest.TestLoader` or `unittest.TestSuite` for discovery — remove or replace any such runner scripts

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/test.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`) to replace any `python -m unittest discover` commands with `pytest --tb=short --cov=<source_package>` and add a coverage threshold flag (`--cov-fail-under=<baseline_percent>`)
- [ ] [XS] Add `pytest-cov` coverage report artifact upload to the CI pipeline so HTML reports are available on each run
- [ ] [XS] Remove any CI steps that install or invoke `unittest`-specific tooling no longer needed after migration

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CONTRIBUTING.md` (or equivalent developer guide) to replace all references to `python -m unittest` with `pytest` invocation instructions and document the `conftest.py` fixture conventions adopted during migration
- [ ] [S] Write a `CHANGELOG` entry summarising the migration: pytest version adopted, fixtures introduced, mocking approach, and any test count or coverage changes
- [ ] [XS] Archive `docs/test-baseline-pre-migration.txt` and add `docs/test-baseline-post-migration.txt` capturing the final suite state for future regression reference
- [ ] [XS] Open a post-migration monitoring issue to track any flaky tests surfaced by the new runner over the first two weeks of use on `main`

---

> **Note:** Task sizing and file-specific names should be refined once the actual test directory structure and module names are confirmed from the migration inventory (`docs/test-migration-inventory.md`). Tasks in Phase 2 may be split into additional per-module PRs if the inventory reveals a large number of test files.