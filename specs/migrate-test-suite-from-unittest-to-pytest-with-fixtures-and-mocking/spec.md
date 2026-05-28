# Spec: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

## Summary

This spec covers the migration of the existing test suite from Python's built-in `unittest` framework to `pytest`, introducing pytest-native fixtures for test setup/teardown and replacing `unittest.mock` usage patterns with pytest-compatible mocking conventions. The expected outcome is a modernized test suite that is easier to read, maintain, and extend, with reduced boilerplate and improved test isolation through fixture composition.

## Motivation

- **Developer experience debt:** `unittest`-style tests require verbose class-based structure (`TestCase` subclasses, `setUp`/`tearDown` methods) that increases boilerplate and reduces readability compared to pytest's function-based approach.
- **Ecosystem alignment:** `pytest` is the de facto standard for Python testing, offering a richer plugin ecosystem (e.g., `pytest-cov`, `pytest-xdist`, `pytest-mock`) that `unittest` alone does not provide.
- **Fixture reusability:** `unittest`'s `setUp`/`tearDown` model does not support composable, scoped fixtures, leading to duplicated setup logic across test classes.
- **Upgrade urgency:** Rated **medium** — the existing tests are functional but represent ongoing maintenance friction and block adoption of modern testing tooling.
- **Mocking ergonomics:** Current `unittest.mock` usage patterns (e.g., manual `patch` context managers, `Mock` assertions) can be replaced with `pytest-mock`'s `mocker` fixture for cleaner, more consistent mock lifecycle management.

> **Note:** Specific CVEs, EOL dates, and runtime/build tool versions were not provided in the tech analysis. See Open Questions.

## Current State

The existing test suite is built on Python's `unittest` framework. Key characteristics of the current state include:

- **Test structure:** Tests are organized as classes inheriting from `unittest.TestCase`.
- **Setup/teardown:** Per-test and per-class setup is handled via `setUp`, `tearDown`, `setUpClass`, and `tearDownClass` methods.
- **Assertions:** Tests use `unittest`-style assertion methods such as `self.assertEqual`, `self.assertRaises`, `self.assertTrue`, `self.assertIn`, etc.
- **Mocking:** Mocking is performed using `unittest.mock.patch` (as decorators or context managers), `unittest.mock.Mock`, and `unittest.mock.MagicMock`.
- **Test discovery:** Tests are discovered and run via `unittest` discovery or a build-tool-specific runner.
- **Parameterization:** TODO — current use of `unittest`'s `subTest` or manual parameterization patterns needs to be inventoried.
- **Test configuration:** TODO — existing `unittest`-specific configuration (e.g., in `setup.cfg`, `tox.ini`, or equivalent) needs to be identified.

## Proposed Changes

For each affected component, the following changes are proposed:

| Component | Before | After | Breaking? |
|---|---|---|---|
| Test base class | `class MyTest(unittest.TestCase)` | Plain functions or classes without `TestCase` inheritance | N — pytest runs both styles; migration can be incremental |
| Setup/teardown | `setUp` / `tearDown` / `setUpClass` / `tearDownClass` methods | pytest fixtures with appropriate scope (`function`, `class`, `module`, `session`) | N — existing `setUp`/`tearDown` still execute under pytest |
| Assertion style | `self.assertEqual(a, b)`, `self.assertRaises(...)`, etc. | Native `assert a == b`, `pytest.raises(...)` | N — `unittest` assertions remain valid under pytest |
| Mocking | `unittest.mock.patch` decorators/context managers | `pytest-mock` `mocker` fixture (`mocker.patch`, `mocker.MagicMock`) | N — `unittest.mock` still works; migration is additive |
| Parameterization | `subTest` or manual loops | `pytest.mark.parametrize` decorator | N — can be migrated test-by-test |
| Test runner | `unittest` runner or build-tool equivalent | `pytest` CLI | N — pytest discovers and runs existing `unittest` tests |
| Test configuration | `unittest`-specific config keys | `pytest` configuration block (`pytest.ini` / `pyproject.toml` `[tool.pytest.ini_options]`) | N — additive config change |
| Coverage reporting | TODO — current coverage tooling unknown | `pytest-cov` plugin | TODO |
| Dependencies | No `pytest` dependency declared | `pytest` and `pytest-mock` added to test dependencies | N |

## Compatibility & Breaking Changes

pytest is designed to be backward-compatible with `unittest.TestCase`-based tests. Migration can therefore be performed incrementally without breaking the existing suite. The following specific compatibility points must be managed:

| Change | Impact | Migration Path |
|---|---|---|
| Removing `unittest.TestCase` inheritance | `self.assert*` methods become unavailable | Replace all `self.assert*` calls with native `assert` statements or `pytest` equivalents before removing the base class |
| Replacing `setUp`/`tearDown` with fixtures | Test-local state managed via `self` attributes is no longer available in plain functions | Refactor shared state into fixture return values or `yield` fixtures; update all references |
| Replacing `unittest.mock.patch` decorators with `mocker` | Mock objects previously injected as function arguments change their injection mechanism | Update function signatures to accept `mocker` fixture; replace decorator-injected mocks with `mocker.patch` calls inside the test body |
| `setUpClass` / `tearDownClass` | Class-scoped setup has no direct pytest decorator equivalent on the class | Replace with `@pytest.fixture(scope="class")` fixtures; ensure fixture is referenced by tests in the class |
| `self.assertRaises` as context manager | Syntax differs from `pytest.raises` | Replace with `with pytest.raises(ExceptionType):` blocks |
| `subTest` parameterization | `subTest` is not natively supported by pytest's output model | Replace with `@pytest.mark.parametrize`; verify all sub-cases are represented |
| Test discovery naming conventions | `unittest` discovery requires `test*.py` files and `test*` methods | pytest defaults are compatible; no change required unless non-standard naming was used |
| Build tool test command | Current runner invocation targets `unittest` | Update CI and local dev commands to invoke `pytest`; remove or update `unittest`-specific runner config |

## Acceptance Criteria

1. **Given** the migrated test suite, **when** `pytest` is invoked with no additional flags, **then** all tests that previously passed under `unittest` also pass under `pytest` with zero regressions.

2. **Given** a migrated test file, **when** it is inspected, **then** it contains no remaining `unittest.TestCase` subclasses (all classes have been converted or confirmed as intentionally retained with documented justification).

3. **Given** a migrated test file, **when** it is inspected, **then** it contains no `self.assertEqual`, `self.assertTrue`, `self.assertRaises`, or other `unittest`-style assertion methods — all assertions use native `assert` or `pytest.raises`/`pytest.warns` equivalents.

4. **Given** a test that previously used `unittest.mock.patch` as a decorator or context manager, **when** the migrated version is run, **then** the mock is applied and removed correctly within the test scope using the `mocker` fixture, and the test produces the same pass/fail result as before.

5. **Given** a test that previously used `setUp`/`tearDown`, **when** the migrated version is run, **then** the equivalent pytest fixture is invoked before and after the test body respectively, and test isolation is preserved.

6. **Given** a test that previously used `subTest` or manual parameterization, **when** the migrated version is run, **then** each parameter combination appears as a distinct test case in pytest's output, individually pass/fail reportable.

7. **Given** the CI pipeline, **when** the test suite is executed, **then** the pipeline uses `pytest` as the test runner and exits non-zero on any test failure.

8. **Given** the project's dependency manifest, **when** it is inspected, **then** `pytest` and `pytest-mock` are declared as test dependencies with pinned minimum versions.

9. **Given** the full migrated test suite, **when** `pytest` is run with coverage reporting enabled via `pytest-cov`, **then** a coverage report is generated and the overall coverage percentage does not decrease compared to the pre-migration baseline.

10. **Given** a new test written after migration, **when** it is added to the suite, **then** it follows the pytest fixture and assertion conventions established by this migration (verified by code review checklist or linter rule).

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current language runtime version (Python version)? This affects minimum supported `pytest` version. | TODO | TODO |
| 2 | What is the current build tool (e.g., `tox`, `nox`, `Makefile`, `poetry`, `setuptools`)? Required to update the test invocation command. | TODO | TODO |
| 3 | Are there any existing `pytest` plugins already in use (e.g., `pytest-django`, `pytest-asyncio`)? These may impose additional constraints on fixture design. | TODO | TODO |
| 4 | What is the current test coverage baseline percentage? Required to validate Acceptance Criterion 9. | TODO | TODO |
| 5 | Are there any tests using `unittest.mock.patch` on module-level or session-scoped state that would require `scope="module"` or `scope="session"` fixtures? | TODO | TODO |
| 6 | Is `pytest-mock` the approved mocking library, or is direct `unittest.mock` usage acceptable to retain in migrated tests? | TODO | TODO |
| 7 | Are there any tests currently skipped or expected-to-fail using `@unittest.skip` or `@unittest.expectedFailure`? These need mapping to `pytest.mark.skip` / `pytest.mark.xfail`. | TODO | TODO |
| 8 | Does the CI system have any constraints on the `pytest` invocation command or output format (e.g., JUnit XML reporting required)? | TODO | TODO |