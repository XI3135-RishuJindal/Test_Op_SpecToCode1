# Spec: Migrate Test Suite from unittest to pytest

## Summary

This spec covers the migration of the existing test suite from Python's built-in `unittest` framework to `pytest`, introducing pytest-native fixtures for test setup and teardown, standardized mocking patterns, and database isolation mechanisms. The expected outcome is a modernized test suite that is easier to maintain, produces clearer failure output, supports parametrization, and enforces reliable DB state isolation between tests — without altering the behaviour of the production code under test.

---

## Motivation

- **Developer experience debt:** `unittest`-style tests require verbose boilerplate (`setUp`, `tearDown`, `self.assert*`) that slows test authoring and reduces readability. This is a medium-urgency tech debt item.
- **Missing DB isolation:** Without explicit DB isolation, tests that write to a database can leak state across test cases, causing order-dependent failures that are difficult to diagnose.
- **Limited fixture composability:** `unittest` does not support pytest's dependency-injected fixture model, making shared setup logic hard to reuse across test modules.
- **Ecosystem alignment:** The broader Python testing ecosystem (plugins, CI integrations, coverage tooling) is predominantly pytest-oriented. Remaining on `unittest` limits access to plugins such as `pytest-cov`, `pytest-xdist`, and `pytest-mock`.
- **Mocking inconsistency:** TODO — specific mocking patterns in use (e.g., `unittest.mock` call sites) were not provided in the context; inconsistencies are assumed based on typical `unittest` codebases.

---

## Current State

> **Note:** Specific class names, config keys, and schema elements were not provided in the tech analysis. The following describes the structural patterns expected in a `unittest`-based suite. TODO — confirm against actual codebase.

| Element | Current Pattern |
|---|---|
| Test base class | `unittest.TestCase` subclasses |
| Setup / teardown | `setUp()` / `tearDown()` instance methods; `setUpClass()` / `tearDownClass()` class methods |
| Assertions | `self.assertEqual`, `self.assertRaises`, `self.assertTrue`, etc. |
| Mocking | `unittest.mock.patch` decorators or context managers; `unittest.mock.MagicMock` |
| DB setup | TODO — specific DB fixture or transaction strategy not provided |
| Test discovery | TODO — build tool and discovery configuration not provided |
| Test runner invocation | TODO — CI pipeline command not provided |

---

## Proposed Changes

### Component-Level Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Test base class | `unittest.TestCase` subclass | Plain Python class or no base class; pytest collects by naming convention | Y — `self.assert*` methods no longer available |
| Setup / teardown | `setUp` / `tearDown` methods | `@pytest.fixture` functions with `yield`; scoped as `function`, `module`, or `session` | Y — method names not recognized by pytest without compatibility shim |
| Assertions | `self.assertEqual(a, b)` etc. | Plain `assert a == b` with pytest rewriting | Y — `self.*` assertion methods removed |
| Mocking | `unittest.mock.patch` decorators | `pytest-mock` `mocker` fixture; `mocker.patch()` calls | N — `unittest.mock.patch` still works; migration is incremental |
| DB isolation | TODO | Transactional fixture that rolls back after each test, or equivalent DB reset strategy | TODO — depends on DB layer |
| Test discovery config | TODO | `pytest.ini` / `pyproject.toml` `[tool.pytest.ini_options]` section | N — additive |
| Test runner | TODO | `pytest` invocation in CI | N — additive |
| Dependencies | `unittest` (stdlib) | `pytest`, `pytest-mock`; optionally `pytest-cov`, `pytest-xdist`, DB isolation plugin (TODO) | N — additive |

### What Is Removed
- `unittest.TestCase` inheritance from all test classes.
- `setUp` / `tearDown` / `setUpClass` / `tearDownClass` methods (replaced by fixtures).
- `self.assert*` assertion calls.

### What Is Added
- `pytest` as a test dependency.
- `pytest-mock` for the `mocker` fixture.
- Shared fixture definitions in `conftest.py` files at appropriate directory scopes.
- A DB isolation fixture providing transactional rollback or equivalent reset per test (TODO — specific implementation depends on ORM/DB driver).
- `pytest.ini` or equivalent configuration declaring test paths, markers, and options.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `self.assert*` methods removed | All existing assertion call sites fail | Replace each `self.assertX(...)` call with the equivalent plain `assert` expression |
| `setUp` / `tearDown` not auto-called by pytest | Per-test setup logic silently skipped | Convert to `@pytest.fixture(autouse=True)` at function scope, or explicit fixture parameters |
| `setUpClass` / `tearDownClass` not auto-called | Per-class setup logic silently skipped | Convert to `@pytest.fixture(scope="class", autouse=True)` |
| `unittest.TestCase.assertRaises` context manager | Replaced | Use `pytest.raises(ExceptionType)` context manager |
| Test class must not inherit `TestCase` | Inheriting `TestCase` disables pytest fixture injection | Remove `TestCase` inheritance; if both runners must coexist temporarily, use `pytest-unittest` compatibility mode |
| DB state leakage between tests | Tests may pass in isolation but fail in suite | Introduce DB isolation fixture; TODO — rollback vs. truncation strategy depends on DB layer |
| `unittest.mock.patch` as decorator on test methods | Works but bypasses `mocker` fixture lifecycle | Migrate to `mocker.patch()` inside test body or fixture; `unittest.mock.patch` decorator remains functional as an interim step |
| Test discovery rules | `unittest` discovers `test*.py` with `TestCase`; pytest uses `test_*.py` by default | Align file naming to `test_*.py` convention; configure `python_files` in pytest config if needed |

---

## Acceptance Criteria

1. **Given** the migrated test suite, **when** `pytest` is invoked with no additional flags, **then** all tests that previously passed under `unittest` also pass under `pytest` with zero failures and zero errors.

2. **Given** a test that previously used `self.assertEqual(a, b)`, **when** the assertion fails, **then** pytest outputs an introspected diff showing the actual values of `a` and `b` without requiring a custom message.

3. **Given** a test that requires a database connection, **when** the test writes a row to the database and the test completes (pass or fail), **then** the row is not present in the database when the next test begins.

4. **Given** two tests that each write conflicting data to the same DB table, **when** both tests are run in the same session, **then** neither test fails due to state left by the other.

5. **Given** a test that requires a mock of an external dependency, **when** the test uses the `mocker` fixture from `pytest-mock`, **then** the mock is automatically torn down after the test without requiring explicit `patch.stop()` calls.

6. **Given** the `conftest.py` fixture definitions, **when** a fixture is declared with `scope="session"`, **then** it is instantiated exactly once per test session as verified by a counter or log assertion in the fixture body.

7. **Given** the CI pipeline, **when** a pull request is opened, **then** the pipeline executes the test suite via `pytest` and reports pass/fail status, replacing any prior `unittest`-based runner invocation.

8. **Given** a test file that previously subclassed `unittest.TestCase`, **when** that class is inspected after migration, **then** it does not inherit from `unittest.TestCase` and all `self.assert*` calls have been replaced.

9. **Given** the pytest configuration file, **when** `pytest --co -q` (collect-only) is run, **then** the number of collected test items is equal to or greater than the number of test methods that existed in the `unittest` suite before migration (no tests silently dropped).

10. **Given** a test marked with a custom pytest marker (e.g., `@pytest.mark.integration`), **when** `pytest -m "not integration"` is run, **then** that test is excluded from the run and the exit code reflects only the remaining tests.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What database engine and ORM/driver are in use? This determines the correct DB isolation strategy (e.g., transaction rollback, `pytest-django` with `@pytest.mark.django_db`, SQLAlchemy session scoping, etc.). | TODO | TODO |
| 2 | Are there any tests that rely on `unittest.TestCase`-specific features (e.g., `subTest`, `addCleanup`) that have no direct pytest equivalent? | TODO | TODO |
| 3 | What is the current CI runner and test invocation command that must be replaced? | TODO | TODO |
| 4 | Is there a requirement to maintain backward compatibility with `unittest` runner during a transition period, or is a hard cutover acceptable? | TODO | TODO |
| 5 | Are there existing `setUpModule` / `tearDownModule` module-level hooks in use that need to be mapped to session- or module-scoped fixtures? | TODO | TODO |
| 6 | What is the target Python version? This affects which `pytest` version and plugins are compatible. | TODO | TODO |
| 7 | Are there any third-party test utilities or base classes (e.g., Django `TestCase`, Flask test client wrappers) that impose additional migration constraints? | TODO | TODO |
| 8 | Is `pytest-cov` or another coverage tool required as part of this migration, or is coverage tooling out of scope? | TODO | TODO |