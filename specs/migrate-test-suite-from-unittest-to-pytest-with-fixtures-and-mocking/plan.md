# PLAN: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

---

## Overview

**Migration Strategy: Strangler-Fig (Incremental)**

The test suite will be migrated from `unittest` to `pytest` incrementally, module by module, rather than in a single big-bang rewrite. This approach is justified because:

- `pytest` is fully compatible with existing `unittest.TestCase` subclasses, meaning old and new tests can coexist and run under the same `pytest` invocation throughout the migration.
- Risk is contained: if a migrated test module introduces regressions, only that module needs to be rolled back — the rest of the suite remains stable.
- The upgrade urgency is **medium**, which does not warrant the higher risk of a big-bang cutover.
- Effort is moderate; incremental delivery allows continuous validation without blocking other development work.

The migration proceeds in three phases: tooling setup, incremental test conversion, and cleanup/enforcement.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Tooling Setup | Install pytest and supporting plugins; configure `pytest.ini` / `pyproject.toml`; verify existing `unittest` tests pass under pytest runner | None | TODO (derive from upgrade option person-days — not provided) |
| 2 — Incremental Conversion | Convert `unittest.TestCase` classes to plain pytest functions/classes module by module; replace `setUp`/`tearDown` with fixtures; replace `unittest.mock` usage with `pytest-mock`; add `conftest.py` files | Phase 1 complete | TODO |
| 3 — Cleanup & Enforcement | Remove all remaining `unittest` imports; enforce pytest-only patterns via linting rules; update CI gates; finalize coverage configuration | Phase 2 complete | TODO |

> **Note:** Specific person-day estimates are marked TODO because the upgrade option detail was not provided and the codebase size/language runtime are not specified in the tech analysis.

---

## Component Changes

### Test Files (general pattern — specific filenames unknown)

> **TODO:** Enumerate actual test file paths once codebase context is available. The patterns below apply universally.

**What changes structurally:**

| Pattern | From (unittest) | To (pytest) |
|---------|----------------|-------------|
| Test class base | `class TestFoo(unittest.TestCase)` | `class TestFoo:` (no base class) |
| Setup method | `def setUp(self)` | `@pytest.fixture` in `conftest.py` or `def setup_method(self)` |
| Teardown method | `def tearDown(self)` | `yield`-based fixture or `def teardown_method(self)` |
| Class-level setup | `setUpClass` / `tearDownClass` | `@pytest.fixture(scope="class")` |
| Assertions | `self.assertEqual(a, b)` | `assert a == b` |
| Assertions | `self.assertRaises(Exc)` | `pytest.raises(Exc)` |
| Assertions | `self.assertIn(a, b)` | `assert a in b` |
| Assertions | `self.assertTrue(x)` | `assert x` |
| Mocking | `unittest.mock.patch` decorator / `MagicMock` | `mocker.patch` / `mocker.MagicMock` via `pytest-mock` |
| Skip decorators | `@unittest.skip` | `@pytest.mark.skip` |
| Parametrize | `subTest` / manual loops | `@pytest.mark.parametrize` |
| Test discovery | `unittest.main()` guard | Removed; pytest discovers automatically |

**Files affected:**
- All `test_*.py` / `*_test.py` files — TODO: list specific paths from repo
- `conftest.py` — **new file(s)** to be created at package and root level
- `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` section — **new or modified**
- `setup.cfg` — remove any `[tool:unittest]` sections if present
- CI pipeline configuration (e.g., `Makefile`, `.github/workflows/*.yml`, `tox.ini`) — update test invocation commands

**APIs modified:**
- Any helper/base test utilities that subclass `unittest.TestCase` must be refactored into pytest fixtures or plain helper functions.
- TODO: Identify specific shared base test classes from codebase context.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pytest` | TODO (not installed or version unknown per tech analysis) | TODO — specify target once tech analysis version is confirmed | N/A — new addition | Core test runner; replaces `unittest` runner |
| `pytest-mock` | Not installed | TODO | N/A — new addition | Provides `mocker` fixture; wraps `unittest.mock`; install via pip |
| `pytest-cov` | Not installed | TODO | N/A — new addition | Coverage reporting; replaces manual coverage invocation |
| `unittest` (stdlib) | Built-in | Retained during Phase 2; removed in Phase 3 | None | Stdlib module; no uninstall needed — simply stop importing it |
| `unittest.mock` (stdlib) | Built-in | Replaced by `pytest-mock` | None during transition | `mocker.patch` is the pytest-idiomatic equivalent |

> **Note:** All version numbers are marked TODO because the tech analysis did not supply current or target versions. Populate these from `pip show pytest` / `requirements.txt` / `pyproject.toml` before beginning Phase 1.

---

## Infrastructure Changes

**CI/CD Pipeline:**
- Update test invocation command from `python -m unittest discover` (or equivalent) to `pytest` with appropriate flags (e.g., `pytest --tb=short --cov=src --cov-report=xml`).
- Add coverage XML upload step if not present (for coverage gate enforcement).
- TODO: Identify specific CI platform (GitHub Actions, GitLab CI, Jenkins, etc.) and update the relevant workflow file(s).

**Configuration Files:**
- Add `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml`:
  ```ini
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py", "*_test.py"]
  python_classes = ["Test*"]
  python_functions = ["test_*"]
  addopts = "--tb=short --strict-markers"
  ```
- TODO: Docker base image changes — not applicable unless test environment is containerized; mark for review.
- TODO: Kubernetes manifest changes — N/A unless test jobs run in-cluster; confirm with team.
- TODO: IaC updates — not derivable from provided context.

---

## Rollback Strategy

### Phase 1 Rollback
- Remove `pytest`, `pytest-mock`, `pytest-cov` from dependencies (`pip uninstall` / revert `requirements*.txt` / `pyproject.toml`).
- Revert CI pipeline command back to `python -m unittest discover`.
- Remove `pytest.ini` / `[tool.pytest.ini_options]` block.
- All existing `unittest` tests remain untouched and runnable.

### Phase 2 Rollback (per module)
- Each test module is converted independently. If a converted module causes failures:
  - Revert that specific `test_*.py` file to its pre-conversion state via `git revert` or `git checkout <file>`.
  - Remove any fixtures added to `conftest.py` that were exclusive to that module.
  - The remaining already-converted modules are unaffected.
- Because pytest runs `unittest.TestCase` subclasses natively, partial rollback of individual files is safe.

### Phase 3 Rollback
- If enforcement rules (linting, CI gates) cause unexpected failures, disable the specific lint rule or CI gate check while the issue is investigated.
- Re-introduce `unittest` imports to affected files if needed as a temporary measure.
- TODO: Tag a git commit at the end of Phase 2 as a stable rollback point before beginning Phase 3 cleanup.

---

## Testing Strategy

### Test Pyramid

| Layer | Approach | Tools | Coverage Target | CI Gate |
|-------|----------|-------|----------------|---------|
| **Unit** | Converted pytest functions with fixtures and `mocker` | `pytest`, `pytest-mock` | TODO (establish baseline from current suite before migration) | Fail build if unit tests fail |
| **Integration** | Existing integration tests re-run under pytest runner | `pytest` | TODO | Fail build if integration tests fail |
| **Regression** | Full suite run after each phase to confirm no behavioral change | `pytest` with `--tb=long` | Must match pre-migration pass rate exactly | Fail build on any new failure vs. baseline |
| **Performance** | TODO — not applicable unless test suite run-time is a concern | TODO | TODO | TODO |

### Specific Practices

- **Baseline first:** Before any conversion, record the full `unittest` test run output (pass/fail counts, coverage %) as the acceptance baseline.
- **Fixture validation:** Each new `conftest.py` fixture must have at least one test that exercises it directly.
- **Mock hygiene:** Confirm all `mocker.patch` calls are scoped correctly (function vs. session scope) to prevent test pollution.
- **Coverage:** Use `pytest-cov` with `--cov-fail-under=<baseline_percent>` to prevent coverage regression. TODO: Set threshold once baseline is measured.
- **Marker registration:** Register all custom `@pytest.mark.*` markers in `pytest.ini` and use `--strict-markers` to catch typos.
- **No `unittest.main()` guards:** CI gate in Phase 3 should fail if any `if __name__ == "__main__": unittest.main()` pattern remains (enforceable via `grep` or a linting rule).

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| pytest and plugins installed; existing tests pass under pytest runner | Phase 1 | TODO | TODO |
| `conftest.py` root scaffold created; `pytest.ini` configured | Phase 1 | TODO | TODO |
| 50% of test modules converted to pytest style | Phase 2 | TODO | TODO |
| 100% of test modules converted; no `unittest.TestCase` subclasses remain | Phase 2 | TODO | TODO |
| All `unittest` imports removed; linting rules enforced | Phase 3 | TODO | TODO |
| CI gates updated; coverage threshold enforced; migration complete | Phase 3 | TODO | TODO |

> **Note:** All dates and person-day estimates are marked TODO. The upgrade option did not supply a specific effort estimate, and the codebase size and language runtime are unknown per the tech analysis. Populate this table after scoping the number of test files and establishing team capacity.