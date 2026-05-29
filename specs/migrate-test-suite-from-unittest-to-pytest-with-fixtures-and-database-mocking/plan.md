# PLAN: Migrate Test Suite from unittest to pytest with Fixtures and Database Mocking

---

## Overview

**Migration Strategy: Strangler-Fig (Incremental)**

The test suite will be migrated incrementally from `unittest` to `pytest`, converting test modules one at a time while keeping the full suite green throughout. This approach is chosen because:

- `pytest` is fully backward-compatible with `unittest.TestCase` subclasses, allowing both styles to coexist during transition.
- A big-bang rewrite risks extended periods of broken CI and makes rollback difficult.
- The "moderate" effort classification indicates a mid-sized test suite where incremental delivery reduces risk without requiring a parallel-run infrastructure.
- Each converted module can be reviewed and merged independently, limiting blast radius per change.

> **Note:** The tech analysis did not supply language, runtime, build tool, framework, or version details. All version numbers, file paths, and tooling references below are marked as **TODO** where context is absent. Concrete values must be filled in once the codebase is inspected.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & Setup — inventory all test files, install pytest and required plugins, configure `pytest.ini` / `pyproject.toml`, verify existing `unittest` suite still passes under `pytest` runner | None | TODO person-days (derive from moderate option once confirmed) |
| 2 | Fixture Foundation — create `conftest.py` hierarchy; implement shared fixtures for database connections, mocks, and common test data; establish database mocking strategy (e.g., in-memory DB, mock library) | Phase 1 complete | TODO person-days |
| 3 | Incremental Test Conversion — convert `unittest.TestCase` classes to pytest-style functions module by module; replace `setUp`/`tearDown` with fixtures; replace `self.assert*` with plain `assert` | Phase 2 complete | TODO person-days |
| 4 | Database Mock Integration — replace any live database calls in tests with fixture-backed mocks; validate isolation between tests | Phase 3 in progress (can overlap) | TODO person-days |
| 5 | Cleanup & Hardening — remove `unittest` imports, enforce pytest-only patterns via linting, update CI pipeline, finalize coverage gates | Phases 3 & 4 complete | TODO person-days |

> **Total effort:** Derived from the "moderate" upgrade option. Exact person-days are **TODO** — populate from the upgrade option detail document once available.

---

## Component Changes

### Test Runner Configuration

- **Files affected:** `pytest.ini` or `pyproject.toml` (create/update), `setup.cfg` (if present)
- **Changes:**
  - Add `[tool.pytest.ini_options]` (or `[pytest]`) section specifying `testpaths`, `python_files`, `python_classes`, `python_functions`.
  - Configure `addopts` for coverage reporting (e.g., `--cov --cov-report=term-missing`).
  - Set `filterwarnings` to surface deprecation warnings from legacy `unittest` usage.
- **Specific config keys:** `testpaths`, `addopts`, `python_files = test_*.py *_test.py`, `python_classes = Test*`, `python_functions = test_*`

### `conftest.py` Files

- **Files affected:** `conftest.py` at repo root and per test-subdirectory (TODO — confirm directory structure)
- **Changes:**
  - Create root `conftest.py` with session-scoped and module-scoped fixtures for database setup/teardown.
  - Create per-package `conftest.py` files for domain-specific fixtures.
  - Migrate any `unittest` `setUpClass` / `setUpModule` logic into appropriately scoped pytest fixtures (`scope="class"`, `scope="module"`, `scope="session"`).

### Individual Test Modules

- **Files affected:** TODO — enumerate via `find . -name "test_*.py" -o -name "*_test.py"` on the actual repo.
- **Structural changes per module:**
  - Remove `import unittest` and `class FooTest(unittest.TestCase):` wrappers where converting to function-based tests.
  - Replace `self.assertEqual(a, b)` → `assert a == b`; `self.assertIn(x, y)` → `assert x in y`; `self.assertRaises(E)` → `pytest.raises(E)`; etc.
  - Replace `setUp(self)` → fixture injected as function parameter; `tearDown(self)` → fixture with `yield`.
  - Replace `self.mock*` / `unittest.mock.patch` decorator usage → `mocker` fixture (via `pytest-mock`) or explicit `monkeypatch` fixture.

### Database Mocking Layer

- **Files affected:** `conftest.py` (new fixtures), any module currently importing a live DB client directly.
- **Changes:**
  - Introduce a `db_session` fixture (or equivalent name — TODO confirm ORM/DB library) that provides either:
    - An in-memory database (e.g., SQLite for SQL ORMs), or
    - A mock/stub object via `unittest.mock.MagicMock` wrapped in a pytest fixture, or
    - A test-container-backed ephemeral database (TODO — confirm if Docker is available in CI).
  - All test functions requiring DB access receive the fixture via parameter injection rather than instantiating connections directly.
  - Existing helper methods that create DB state (e.g., `create_test_user()`, `seed_db()`) are refactored into fixtures or fixture factories using `pytest`'s `factory_as_fixture` pattern.

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not supply current or target version numbers. All versions are **TODO** and must be sourced from the actual `requirements.txt`, `Pipfile`, `pyproject.toml`, or equivalent manifest before implementation begins.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pytest` | TODO | TODO | TODO | Core runner replacement; backward-compatible with `unittest.TestCase` |
| `pytest-mock` | TODO | TODO | TODO | Provides `mocker` fixture as ergonomic wrapper around `unittest.mock` |
| `pytest-cov` | TODO | TODO | TODO | Coverage integration; replaces any standalone `coverage` invocation in CI |
| `pytest-xdist` | TODO | TODO | TODO | Optional: parallel test execution; add only if suite is slow |
| `factory_boy` or `faker` | TODO | TODO | TODO | Optional: fixture data generation; add if test data setup is complex |
| `unittest` (stdlib) | N/A (stdlib) | Retained during transition | None | Removed from imports only after full conversion in Phase 5 |

---

## Infrastructure Changes

- **CI/CD Pipeline:**
  - Update the test invocation command from `python -m unittest discover` (or equivalent) to `pytest` with appropriate flags.
  - Add `--cov` and `--cov-fail-under=<threshold>` (TODO — set threshold based on current coverage baseline) to CI test step.
  - Ensure `conftest.py` and `pytest.ini`/`pyproject.toml` are committed and picked up by the CI runner.
  - TODO — specific CI platform (GitHub Actions, GitLab CI, Jenkins, etc.) not identified; update the relevant workflow/pipeline file once confirmed.

- **Docker / Container:** TODO — not mentioned in context; confirm whether tests run inside a container and whether a test database container is needed.

- **Kubernetes:** N/A — not applicable to this task.

- **IaC:** N/A — not applicable to this task.

---

## Rollback Strategy

Each phase is independently reversible because `pytest` runs `unittest.TestCase` tests natively.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** (Setup) | Remove `pytest.ini`/`pyproject.toml` pytest config block; uninstall `pytest` and plugins; restore original test invocation command in CI. No test code has changed. |
| **Phase 2** (Fixtures) | Delete newly created `conftest.py` files. No existing test modules have been modified. Revert CI config if changed. |
| **Phase 3** (Conversion) | Each converted module is a discrete commit/PR. Revert individual module commits via `git revert <sha>` or restore from branch. Unconverted modules continue to run under pytest's `unittest` compatibility layer. |
| **Phase 4** (DB Mocking) | Revert `conftest.py` fixture changes and any test module edits that replaced live DB calls. Restore original DB setup helpers. Each module's DB mock change should be a separate commit for granular revert. |
| **Phase 5** (Cleanup) | If linting rules or CI gates cause failures, revert `pyproject.toml`/`setup.cfg` linting config changes. The test logic itself is already validated by this phase, so rollback risk is low. |

**General principle:** Feature branches per phase + squash-merge after green CI ensures `git revert <merge-sha>` is always available as a single-command rollback for any phase.

---

## Testing Strategy

### Test Pyramid

| Layer | Approach | Tools | Coverage Target | CI Gate |
|-------|----------|-------|----------------|---------|
| **Unit** | Pure function tests with no I/O; all DB/external calls mocked via fixtures | `pytest`, `pytest-mock` | TODO (establish baseline before migration; target ≥ current) | Fail build if coverage drops below baseline |
| **Integration** | Tests exercising multiple units together with an in-memory or containerized DB fixture | `pytest`, DB fixture in `conftest.py` | TODO | Run on every PR; must pass before merge |
| **Regression** | Full converted suite run against the same inputs as the original `unittest` suite to confirm behavioral equivalence | `pytest` with `-v` output diff against pre-migration run | 100% of previously passing tests must still pass | Enforced in Phase 3 & 4 CI steps |
| **Performance** | TODO — not in scope unless test suite runtime is a concern; consider `pytest-xdist` for parallelism | `pytest-xdist` (optional) | Suite runtime ≤ pre-migration baseline | TODO |

### Key Practices

- **Fixture scope discipline:** Use the narrowest scope possible (`function` by default) to ensure test isolation; escalate to `module` or `session` only for expensive setup (e.g., DB schema creation).
- **No shared mutable state:** Database fixtures must use transactions rolled back after each test, or recreate schema per test, to prevent inter-test contamination.
- **Coverage baseline:** Run `pytest --cov` on the unconverted suite (Phase 1) to record the baseline; enforce that no phase reduces coverage.
- **Linting:** Add `flake8-pytest-style` or `ruff` pytest rules (TODO — confirm linter in use) to enforce pytest idioms and flag residual `unittest` patterns post-Phase 5.

---

## Timeline

> All durations are **TODO** — populate from the "moderate" upgrade option's person-days breakdown once the detail document is available. The milestone sequence below is fixed; only the dates are unknown.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; pytest installed; all existing tests green under pytest runner | Phase 1 | TODO | TODO |
| `conftest.py` hierarchy in place; DB fixture strategy agreed and implemented | Phase 2 | TODO | TODO |
| 50% of test modules converted to pytest style | Phase 3 (mid) | TODO | TODO |
| 100% of test modules converted; no remaining `unittest.TestCase` subclasses | Phase 3 (complete) | TODO | TODO |
| All DB calls in tests routed through fixtures/mocks; no live DB dependency in unit tests | Phase 4 | TODO | TODO |
| `unittest` imports removed; linting enforced; CI gates active; migration complete | Phase 5 | TODO | TODO |

---

*Document status: DRAFT — version numbers, file paths, person-days, and infrastructure details marked TODO must be resolved during Phase 1 audit before Phase 2 begins.*