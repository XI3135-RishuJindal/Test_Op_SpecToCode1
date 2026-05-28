# Spec: Migrate Test Suite from unittest to pytest with Fixtures and Mocking

## Summary

This spec covers the migration of the existing test suite from Python's built-in `unittest` framework to `pytest`, introducing pytest-native fixtures for test setup/teardown and replacing `unittest.mock` usage patterns with pytest-compatible mocking conventions. The expected outcome is a modernized test suite that leverages pytest's fixture system, cleaner assertion syntax, and improved test discoverability, while maintaining equivalent test coverage and all existing tests continuing to pass.

## Motivation

- **Developer experience debt:** `unittest`'s class-based, boilerplate-heavy structure increases the cost of writing and maintaining tests. pytest's function-based tests and fixture injection reduce friction and improve readability.
- **Ecosystem alignment:** pytest is the de facto standard for Python testing. The broader ecosystem of plugins (e.g., `pytest-cov`, `pytest-xdist`, `pytest-mock`) is built around pytest, not `unittest`.
- **Fixture reusability:** `unittest`'s `setUp`/`tearDown` methods are scoped to individual test classes and cannot be shared across modules without inheritance. pytest fixtures support session-, module-, class-, and function-level scoping with explicit dependency injection.
- **Mocking ergonomics:** `unittest.mock` used via `@patch` decorators or `setUp` assignments is verbose and tightly coupled to class structure. `pytest-mock`'s `mocker` fixture provides a cleaner, scope-aware alternative.
- **Upgrade urgency:** Medium — no EOL or CVE driver, but accumulated tech debt in test maintainability justifies prioritized migration.

> **Note:** Specific runtime, build tool, and framework versions are not provided in the tech analysis. Version constraints are marked TODO where applicable.

## Current State

The existing test suite is built on Python's `unittest` framework. Key characteristics of the current state include:

- **Test structure:** Tests are organized as classes inheriting from `unittest.TestCase`.
- **Setup/teardown:** Per-test and per-class setup is handled via `setUp`, `tearDown`, `setUpClass`, and `tearDownClass` methods.
- **Assertions:** Tests use `unittest.TestCase` assertion methods such as `assertEqual`, `assertRaises`, `assertTrue`, `assertIn`, `assertIsNone`, etc.
- **Mocking:** Mocking is performed via `unittest.mock.patch` (as decorators or context managers) and `unittest.mock.MagicMock` / `unittest.mock.Mock` instantiated in `setUp` blocks.
- **Test discovery:** Tests are discovered by the `unittest` runner using the `test_*.py` / `*_test.py` naming convention and `TestCase` subclass detection.
- **Test runner invocation:** TODO — specific runner command (e.g., `python -m unittest`, `nose`, CI pipeline command) not confirmed from provided context.
- **Parametrization:** TODO — whether `unittest`'s `subTest` or third-party parametrize utilities are currently in use is not confirmed.
- **Specific classes/modules affected:** TODO — inventory of `TestCase` subclasses and mock usage sites not provided in context.

## Proposed Changes

### Overview

Each `unittest.TestCase` subclass is converted to a collection of pytest-style test functions or, where grouping is warranted, pytest classes (without `TestCase` inheritance). `setUp`/`tearDown` logic is extracted into pytest fixtures. `unittest.mock` usage is replaced or wrapped using `pytest-mock`'s `mocker` fixture.

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Test base class | Inherits `unittest.TestCase` | Plain functions or classes with no `TestCase` inheritance | Y — `TestCase`-specific APIs removed |
| Setup/teardown | `setUp` / `tearDown` instance methods | pytest fixtures (function-scoped by default) | Y — method names no longer called by runner |
| Class-level setup | `setUpClass` / `tearDownClass` class methods | pytest fixtures with `scope="class"` | Y |
| Module-level setup | Not natively supported | pytest fixtures with `scope="module"` or `scope="session"` | N (additive) |
| Assertion style | `self.assertEqual(a, b)`, `self.assertRaises(...)`, etc. | Native `assert a == b`, `pytest.raises(...)` | Y — `self.assert*` methods unavailable outside `TestCase` |
| Mocking | `unittest.mock.patch` decorators / `MagicMock` in `setUp` | `pytest-mock` `mocker` fixture; `mocker.patch`, `mocker.MagicMock` | Y — decorator-based patches require refactoring |
| Test runner | `unittest` runner or equivalent | `pytest` CLI | N — pytest can still collect `unittest`-style tests during transition |
| Test parametrization | `subTest` context manager (if used) | `@pytest.mark.parametrize` decorator | Y — `subTest` not natively translated |
| Dependency declaration | TODO (build tool unknown) | `pytest` and `pytest-mock` added as test dependencies | N |
| CI pipeline invocation | TODO | Updated to invoke `pytest` | TODO |

### What Is Removed

- `unittest.TestCase` inheritance from all test classes.
- `setUp`, `tearDown`, `setUpClass`, `tearDownClass` method signatures (logic is preserved, relocated to fixtures).
- `self.assert*` assertion calls.
- `@unittest.mock.patch` decorator usage (replaced by `mocker.patch`).

### What Is Added

- `pytest` as the primary test framework dependency.
- `pytest-mock` as a test dependency for mocking support.
- `conftest.py` file(s) for shared fixture definitions.
- `@pytest.mark.parametrize` decorators where parametrization is needed.
- `pytest.raises` and `pytest.warns` context managers replacing `assertRaises` / `assertWarns`.

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Removal of `unittest.TestCase` inheritance | All existing test classes lose access to `self.assert*` methods and `TestCase` runner hooks | Replace `self.assert*` calls with plain `assert` statements; replace `assertRaises` with `pytest.raises` |
| `setUp` / `tearDown` no longer called automatically | Test setup logic will not execute if left as-is | Extract `setUp` body into a pytest fixture; inject fixture into test functions/methods by parameter name |
| `setUpClass` / `tearDownClass` no longer called automatically | Class-scoped setup logic will not execute | Convert to pytest fixtures with `scope="class"` defined in `conftest.py` or the test module |
| `@unittest.mock.patch` decorator on test methods | Patched arguments injected as positional parameters — incompatible with pytest fixture injection model | Replace with `mocker.patch(...)` calls inside the test body or a fixture; remove decorator |
| `unittest.mock.MagicMock` instantiated in `setUp` | Mock objects created in `setUp` are not available as fixtures | Move mock creation into a pytest fixture; inject via parameter |
| `subTest` parametrization (if present) | `subTest` is a `TestCase`-only API | Replace with `@pytest.mark.parametrize`; TODO — confirm whether `subTest` is in use |
| Test runner command change | CI and local developer scripts invoking `python -m unittest` will no longer be the canonical command | Update all invocation points to `pytest`; TODO — confirm all CI pipeline steps |
| Any `unittest.skip` / `unittest.expectedFailure` decorators | These decorators function differently outside `TestCase` | Replace with `pytest.mark.skip` and `pytest.mark.xfail` respectively |

> **Note:** pytest can collect and run `unittest.TestCase`-based tests during a transitional period, enabling incremental migration without breaking the suite mid-flight.

## Acceptance Criteria

1. **Given** the migrated test suite, **when** `pytest` is invoked with no additional flags, **then** all tests that passed under `unittest` also pass under `pytest` with zero regressions in pass/fail status.

2. **Given** the migrated test suite, **when** `pytest` is invoked, **then** no test file imports `unittest.TestCase` as a base class for any test class.

3. **Given** the migrated test suite, **when** `pytest` is invoked, **then** no test function or method contains a `self.assert*` call (e.g., `assertEqual`, `assertRaises`, `assertTrue`).

4. **Given** a test that previously used `@unittest.mock.patch` as a decorator, **when** the migrated test is executed under `pytest`, **then** the mock is applied correctly for the duration of the test and cleaned up afterward, verified by asserting mock call counts and return values match pre-migration behavior.

5. **Given** shared setup logic previously in `setUp` methods, **when** the migrated tests run, **then** the equivalent fixture is invoked once per test function (function scope) and the setup state is correctly initialized for each test, confirmed by tests that depend on that state passing.

6. **Given** class-scoped or module-scoped setup previously in `setUpClass`, **when** the migrated tests run, **then** the equivalent fixture executes exactly once per class or module respectively, verified by a counter or log assertion in the fixture.

7. **Given** any previously parametrized tests (via `subTest` or equivalent), **when** migrated to `@pytest.mark.parametrize`, **then** `pytest` reports one distinct test node per parameter set, and all parameter combinations that passed before continue to pass.

8. **Given** the updated dependency manifest, **when** the project's test dependencies are installed, **then** `pytest` and `pytest-mock` are present and importable at the versions specified (TODO — versions to be confirmed).

9. **Given** the CI pipeline, **when** a pull request is opened, **then** the pipeline invokes `pytest` (not `python -m unittest`) and reports pass/fail status correctly.

10. **Given** the migrated test suite, **when** `pytest --co -q` (collect-only) is run, **then** the number of collected test items is greater than or equal to the number of test methods that existed in the `unittest` suite, ensuring no tests were silently dropped during migration.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact runtime (Python version) and build tool (pip, poetry, pipenv, etc.) in use? This affects how `pytest` and `pytest-mock` are added as dependencies. | TODO | TODO |
| 2 | What is the current test runner invocation command in CI (e.g., `python -m unittest discover`, `nose`, `tox`)? All invocation points must be updated. | TODO | TODO |
| 3 | Is `unittest.mock.subTest` or any third-party parametrization library currently in use? This determines the scope of `@pytest.mark.parametrize` migration work. | TODO | TODO |
| 4 | Are there any tests that rely on `unittest.TestCase`-specific features beyond `setUp`/`tearDown` and assertions (e.g., `addCleanup`, `assertLogs`, `assertWarns`)? | TODO | TODO |
| 5 | What versions of `pytest` and `pytest-mock` should be pinned? Are there any upper-bound constraints from other dependencies? | TODO | TODO |
| 6 | Is migration expected to be done atomically (all at once) or incrementally (module by module)? This affects whether a transitional period with mixed `unittest`/pytest tests is acceptable. | TODO | TODO |
| 7 | Are there any custom `unittest` test runners, result formatters, or plugins currently in use that would need pytest equivalents? | TODO | TODO |
| 8 | What is the target code coverage threshold, and is `pytest-cov` the intended coverage tool post-migration? | TODO | TODO |