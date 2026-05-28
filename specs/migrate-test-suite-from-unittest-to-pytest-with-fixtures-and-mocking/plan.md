# PLAN: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

---

## Overview

**Migration Strategy: Strangler-Fig (incremental, module-by-module)**

The test suite will be migrated incrementally from `unittest` to `pytest`, converting test modules one at a time while keeping the full suite green throughout. This approach is chosen because:

- `pytest` is natively compatible with existing `unittest.TestCase` subclasses, meaning unconverted tests continue to run without modification during the transition.
- Risk is contained: a broken conversion in one module does not block the rest of the suite.
- The upgrade urgency is **medium**, which does not justify a high-risk big-bang rewrite.
- Rollback is straightforward at any phase — unconverted modules remain functional.

> **NOTE:** The tech analysis did not supply language, runtime, build tool, framework details, or specific version targets. Where these are absent, this plan marks gaps as **TODO** and provides guidance conditional on the most common Python/pytest context implied by the task. Adjust all specifics once the codebase is confirmed.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & inventory existing test suite; document all `unittest` patterns in use (TestCase subclasses, `setUp`/`tearDown`, `mock.patch`, `assertX` calls) | None | TODO (derive from actual file count once codebase is confirmed) |
| 2 | Install and configure `pytest` and supporting plugins; establish `pytest.ini` / `pyproject.toml` config; verify all existing `unittest` tests pass under `pytest` runner | Phase 1 complete | TODO |
| 3 | Migrate shared setup/teardown to `pytest` fixtures; create `conftest.py` files at appropriate directory levels | Phase 2 complete | TODO |
| 4 | Convert `unittest.TestCase` subclasses to plain `pytest` test functions/classes, module by module; replace `assertX` with plain `assert`; replace `unittest.mock` with `pytest-mock` | Phase 3 complete | TODO |
| 5 | Replace `mock.patch` decorators with `mocker` fixture; consolidate fixture scopes; remove all remaining `unittest` imports | Phase 4 complete | TODO |
| 6 | Validate full suite; enforce coverage gates; update CI pipeline; remove `unittest` runner configuration | Phase 5 complete | TODO |

> **TODO:** Populate effort estimates (person-days) once the upgrade option details and codebase size are confirmed.

---

## Component Changes

### Test Configuration

- **Files affected:** `pytest.ini` or `pyproject.toml` (create/update), `setup.cfg` (if present)
- **Changes:**
  - Add `[tool.pytest.ini_options]` (pyproject.toml) or `[pytest]` (pytest.ini) section.
  - Set `testpaths`, `python_files`, `python_classes`, `python_functions` discovery rules.
  - Configure `addopts` for verbosity, coverage reporting (e.g., `--cov --cov-report=term-missing`).
  - Remove any `unittest`-specific runner configuration (e.g., `python -m unittest discover` scripts).

### `conftest.py` Files

- **Files affected:** New `conftest.py` at root and per-subdirectory as needed.
- **Changes:**
  - Extract repeated `setUp` logic from `TestCase` classes into `@pytest.fixture` functions.
  - Scope fixtures appropriately: `function` (default), `class`, `module`, or `session`.
  - Centralize shared mock objects and test data factories here.

### Test Modules (per-module conversion)

- **Files affected:** All `test_*.py` / `*_test.py` files (TODO: enumerate from codebase).
- **Structural changes per module:**

  | Before (unittest) | After (pytest) |
  |---|---|
  | `class TestFoo(unittest.TestCase):` | `class TestFoo:` or standalone functions |
  | `def setUp(self):` | `@pytest.fixture` (autouse or explicit) |
  | `def tearDown(self):` | `yield`-based fixture cleanup |
  | `self.assertEqual(a, b)` | `assert a == b` |
  | `self.assertRaises(Exc, fn)` | `with pytest.raises(Exc):` |
  | `self.assertIn(a, b)` | `assert a in b` |
  | `self.assertTrue(x)` | `assert x` |
  | `@unittest.mock.patch('mod.obj')` | `mocker.patch('mod.obj')` via `pytest-mock` |
  | `unittest.mock.MagicMock()` | `mocker.MagicMock()` or `unittest.mock.MagicMock()` (both valid) |
  | `self.skipTest('reason')` | `pytest.skip('reason')` |
  | `@unittest.skip('reason')` | `@pytest.mark.skip(reason='reason')` |

- **APIs modified:** No production APIs are modified. Changes are confined to test code.

### Mocking Layer

- **Files affected:** Any test file using `unittest.mock.patch`, `MagicMock`, `patch.object`, `patch.dict`.
- **Changes:**
  - Introduce `pytest-mock`'s `mocker` fixture as the primary mocking interface.
  - Replace `@patch` decorator stacks with `mocker.patch(...)` calls inside test body or fixture.
  - `mocker` automatically resets all patches after each test — remove manual `patcher.stop()` calls where present.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|---|---|---|---|---|
| `pytest` | TODO (not installed or version unknown) | TODO — confirm from tech analysis | N/A (new addition) | Install via `pip install pytest`; add to `dev-dependencies` / `requirements-dev.txt` |
| `pytest-mock` | TODO | TODO | N/A (new addition) | Provides `mocker` fixture; replaces `unittest.mock.patch` decorator pattern |
| `pytest-cov` | TODO | TODO | N/A (new addition) | Coverage integration; configure via `pyproject.toml` `[tool.coverage]` |
| `unittest` (stdlib) | stdlib | stdlib (retained during transition) | None | Stdlib module; no removal needed until Phase 5 cleanup |
| `unittest.mock` (stdlib) | stdlib | stdlib (retained; `mocker` wraps it) | None | `pytest-mock` delegates to `unittest.mock` internally |

> **TODO:** All version numbers must be confirmed from the actual tech analysis once provided. Do not pin versions based on this document alone.

---

## Infrastructure Changes

**CI/CD Pipeline:**
- Update test execution command from `python -m unittest discover` (or equivalent) to `pytest`.
- Add coverage gate: fail build if coverage drops below threshold (TODO: set threshold based on current baseline).
- Example CI step change:
  ```yaml
  # Before
  - run: python -m unittest discover -s tests

  # After
  - run: pytest --cov --cov-fail-under=TODO
  ```
- TODO: Identify CI platform (GitHub Actions, GitLab CI, Jenkins, etc.) and update the specific workflow/pipeline file.

**Docker / Build Images:**
- TODO: Confirm whether `pytest` and plugins need to be added to a test-stage Docker image layer.
- TODO: Confirm whether `requirements-dev.txt` or equivalent is `COPY`-ed into the test image.

**IaC:**
- TODO: Not determinable from provided context.

---

## Rollback Strategy

Each phase is independently reversible because `pytest` runs `unittest.TestCase` tests natively.

| Phase | Rollback Steps |
|---|---|
| **Phase 1** (Audit) | No code changes made; nothing to roll back. |
| **Phase 2** (Install pytest) | Remove `pytest`, `pytest-mock`, `pytest-cov` from dependencies; restore original test runner command in CI. No test files were modified. |
| **Phase 3** (conftest.py / fixtures) | Delete new `conftest.py` files; restore `setUp`/`tearDown` methods in any partially converted modules. Revert via `git checkout -- tests/`. |
| **Phase 4** (Convert TestCase classes) | `git revert` or `git checkout` the specific test module(s) converted in that batch. All other modules remain unaffected. |
| **Phase 5** (Remove unittest imports) | `git revert` the cleanup commit. Re-adding `import unittest` and `unittest.mock` restores prior state immediately. |
| **Phase 6** (CI gate update) | Revert CI configuration file to previous test command; remove coverage gate temporarily if it causes false failures. |

**General principle:** Every phase should be committed as a discrete, reviewable PR. This ensures `git revert <PR-merge-commit>` is always a valid rollback action.

---

## Testing Strategy

### Test Pyramid

| Layer | Approach | Tools | Coverage Target | CI Gate |
|---|---|---|---|---|
| **Unit** | Each converted test module must pass identically before and after conversion | `pytest`, `pytest-mock` | TODO (match or exceed pre-migration baseline) | Fail PR if any test regresses |
| **Integration** | Run full suite under `pytest` runner against real dependencies/fixtures | `pytest` with appropriate markers (e.g., `@pytest.mark.integration`) | TODO | Run on merge to main branch |
| **Regression** | Diff test results (pass/fail/count) between `unittest` runner and `pytest` runner on same commit | `pytest --tb=short`, result comparison script | 0 regressions permitted | Block merge if regression count > 0 |
| **Performance** | Measure suite execution time before and after migration | `pytest-benchmark` (optional) or CI timing | No more than 10% slowdown | Advisory; non-blocking initially |

### Specific Practices

- **Parallel conversion validation:** During Phases 3–5, run both `python -m unittest discover` and `pytest` in CI simultaneously and compare exit codes. Divergence must be resolved before proceeding.
- **Fixture correctness:** Each new fixture must have at least one test that validates its setup and teardown behavior (use `pytest --setup-show` during development).
- **Mock isolation:** After Phase 5, audit for any test that relies on mock state leaking between tests (a common `unittest.mock.patch` footgun). Use `mocker` fixture's automatic reset to enforce isolation.
- **Coverage baseline:** Run `pytest-cov` at the start of Phase 2 to record the pre-migration coverage baseline. This becomes the minimum gate for Phase 6.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|---|---|---|---|
| Audit complete; all unittest patterns documented | Phase 1 | TODO | TODO |
| pytest installed; all existing tests green under pytest runner | Phase 2 | TODO | TODO |
| `conftest.py` fixtures created; setUp/tearDown migrated | Phase 3 | TODO | TODO |
| All TestCase classes converted to pytest style | Phase 4 | TODO | TODO |
| All unittest.mock replaced with mocker; no unittest imports remain | Phase 5 | TODO | TODO |
| CI updated; coverage gate enforced; migration complete | Phase 6 | TODO | TODO |

> **TODO:** Populate all dates and owners once team capacity, codebase size, and the upgrade option's person-days estimate are confirmed. Phases 3–5 should be time-boxed per batch of modules rather than scheduled as single large steps.

---

*Document status: DRAFT — pending confirmation of language runtime, build tool, dependency versions, CI platform, and person-days estimate from upgrade option details.*