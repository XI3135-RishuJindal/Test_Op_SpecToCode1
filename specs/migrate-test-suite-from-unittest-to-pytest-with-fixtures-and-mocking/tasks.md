# TASKS: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

> **Scope:** Migrate existing `unittest`-based tests to `pytest` idioms, introducing fixtures and replacing `unittest.mock` usage with `pytest-mock` where appropriate.
> **Upgrade Option:** Moderate — incremental migration preserving test coverage throughout.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with pytest ≥ 7.x by running `python --version` and checking against [pytest compatibility matrix](https://docs.pytest.org/en/stable/changelog.html)
- [ ] [XS] Verify `pip` or project package manager access and ability to modify `requirements.txt` / `pyproject.toml` / `setup.cfg` (whichever is present)
- [ ] [XS] Confirm CI pipeline has permissions to install new test dependencies and run updated test commands
- [ ] [XS] Ensure all existing `unittest` tests pass on the current branch before migration begins — record baseline pass/fail counts

---

## Phase 1 — Preparation

- [ ] [S] Audit all test files in the test directory to inventory `unittest.TestCase` subclasses, `setUp`/`tearDown` methods, `unittest.mock` imports, and `self.assert*` calls — produce a migration checklist document (`docs/test-migration-checklist.md`)
- [ ] [XS] Create a dedicated migration branch `feat/pytest-migration` from the default branch
- [ ] [XS] Add `pytest`, `pytest-mock`, and `pytest-cov` as development dependencies in `requirements-dev.txt` or `pyproject.toml` `[dev]` extras, pinning to latest stable versions (e.g., `pytest>=7.4`, `pytest-mock>=3.12`, `pytest-cov>=4.1`)
- [ ] [XS] Add a `pytest.ini` or `[tool.pytest.ini_options]` section in `pyproject.toml` configuring `testpaths`, `python_files`, `python_classes`, and `python_functions` discovery settings
- [ ] [S] Capture full test baseline by running existing `unittest` suite with `python -m pytest --collect-only` to confirm pytest can discover all existing `TestCase` classes without modification (pytest supports `unittest.TestCase` natively — record collected test count as baseline)
- [ ] [XS] Configure CI gate to fail if collected test count drops below baseline during migration

---

## Phase 2 — Core Upgrade

- [ ] [M] Convert `setUp` and `tearDown` methods to `pytest` fixtures in the first batch of test files — replace `self.setUp` resource initialization with `@pytest.fixture` functions in a `conftest.py` at the appropriate directory level
- [ ] [M] Replace `unittest.TestCase` subclasses with plain test functions/classes (no inheritance) in the second batch of test files — remove `self` references and convert `self.assert*` calls to plain `assert` statements
- [ ] [M] Migrate `unittest.mock.patch` decorator and context-manager usages to `mocker.patch` via `pytest-mock`'s `mocker` fixture in all test files using mocking
- [ ] [S] Replace `unittest.mock.MagicMock` and `unittest.mock.Mock` instantiations with `mocker.MagicMock` / `mocker.Mock` where they appear inside test functions, ensuring mock teardown is handled automatically by `pytest-mock`
- [ ] [S] Extract repeated fixture setup shared across multiple test modules into a top-level `conftest.py`, converting duplicated `setUp` logic into scoped fixtures (`scope="function"`, `scope="module"`, or `scope="session"` as appropriate)
- [ ] [M] Convert `unittest.TestCase.assertRaises` usages to `pytest.raises` context managers across all test files
- [ ] [S] Convert `unittest.TestCase.assertLogs` and any `assertWarns` usages to `pytest`'s `caplog` and `recwarn` built-in fixtures respectively
- [ ] [XS] Remove all `if __name__ == "__main__": unittest.main()` blocks from test files now superseded by pytest runner

---

## Phase 3 — Testing & Validation

- [ ] [S] Run full pytest suite with `pytest --tb=short -q` and confirm collected test count matches the pre-migration baseline; investigate and resolve any collection errors or unexpected skips
- [ ] [S] Run `pytest --cov=<source_package> --cov-report=term-missing` and compare coverage percentages against the pre-migration baseline — coverage must not regress
- [ ] [XS] Run `pytest -x` (fail-fast) to surface and fix any remaining `unittest`-specific assertion failures caused by incomplete migration
- [ ] [XS] Verify `pytest-mock` mocker fixture correctly tears down all patches between tests by running the suite twice in sequence and confirming no state leakage
- [ ] [XS] Confirm no `import unittest` statements remain in migrated test files (except in any intentionally retained `unittest.TestCase` tests) using `grep -r "import unittest" tests/`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline test step to replace `python -m unittest discover` (or equivalent) with `pytest` invocation in the pipeline configuration file
- [ ] [XS] Update `pytest` invocation in CI to include `--cov`, `--cov-fail-under=<baseline_percentage>`, and `--junitxml=test-results.xml` flags for coverage enforcement and test reporting
- [ ] [XS] Remove any CI steps that installed or invoked `nose`, `unittest-xml-reporting`, or other test runners made redundant by this migration

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CONTRIBUTING.md` (or equivalent developer guide) to replace unittest run instructions with `pytest` commands, including how to run a single test, a module, and the full suite with coverage
- [ ] [XS] Add a `## Running Tests` section to `README.md` documenting the `pytest` invocation and coverage command
- [ ] [XS] Update `docs/test-migration-checklist.md` to mark all items complete and note any tests intentionally left as `unittest.TestCase` (with rationale)
- [ ] [XS] Merge `feat/pytest-migration` branch via PR, requiring CI green on the updated pipeline before merge
- [ ] [XS] Post-merge, monitor first 3 CI runs on the default branch to confirm no flaky tests introduced by fixture scoping changes