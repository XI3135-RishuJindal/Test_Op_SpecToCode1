# Spec: Replace unittest with pytest and Add Fixtures and DB Mocking

## Summary

This spec covers the migration of the existing test suite from Python's built-in `unittest` framework to `pytest`, along with the introduction of pytest fixtures for shared test setup/teardown and database mocking to isolate tests from live database dependencies. The expected outcome is a modernized, more maintainable test suite that leverages pytest's concise syntax, powerful fixture system, and improved assertion introspection, while eliminating reliance on real database connections during unit and integration testing.

---

## Motivation

- **Test framework modernization:** `unittest` is verbose and requires boilerplate class inheritance and `setUp`/`tearDown` methods. `pytest` reduces friction, improves readability, and is the de facto standard for Python testing.
- **Tech debt reduction:** The current test suite carries medium-urgency tech debt related to testing infrastructure. Lack of fixtures leads to duplicated setup code across test modules.
- **DB coupling risk:** Tests that depend on live or shared database connections are fragile, environment-sensitive, and slow. Introducing DB mocking removes this coupling and enables tests to run reliably in CI without database infrastructure.
- **Upgrade urgency:** Medium — no immediate EOL or CVE driver, but the debt compounds as the test suite grows.

> **Note:** Specific version numbers for pytest and related plugins are marked TODO pending confirmation from the project's dependency resolution.

---

## Current State

- Tests are written using Python's `unittest` module, with test classes inheriting from `unittest.TestCase`.
- Test setup and teardown are handled via `setUp()` and `tearDown()` instance methods (and optionally `setUpClass()` / `tearDownClass()`).
- Assertions use `unittest`-style methods: `self.assertEqual`, `self.assertRaises`, `self.assertTrue`, etc.
- Database interactions in tests rely on TODO (live connections, test databases, or in-memory SQLite — specifics not confirmed in provided context).
- No pytest fixtures are currently in use.
- Test discovery is driven by `unittest` conventions (test files and class naming patterns).
- TODO: Identify specific test modules, helper classes, and any existing mock/stub utilities present in the codebase.

---

## Proposed Changes

For each affected component, the following changes are proposed:

| Component | Before | After | Breaking? |
|---|---|---|---|
| Test base class | `unittest.TestCase` subclasses | Plain functions or classes (no inheritance required) | Y |
| Setup / teardown | `setUp()` / `tearDown()` methods | pytest fixtures (`@pytest.fixture`) with appropriate scope | Y |
| Assertions | `self.assertEqual(a, b)`, `self.assertRaises(...)`, etc. | Native `assert a == b`, `pytest.raises(...)` | Y |
| Test runner | `unittest` runner (e.g., `python -m unittest`) | `pytest` CLI | N (additive) |
| Database access in tests | Live DB connection or uncontrolled test DB | Mocked/patched DB layer using pytest fixtures and a mocking library (TODO: confirm `unittest.mock`, `pytest-mock`, or other) | Y |
| Shared test configuration | Ad-hoc or per-class setup | `conftest.py` with shared fixtures | N (additive) |
| DB fixture scope | N/A | Session-, module-, or function-scoped DB mock fixtures as appropriate | N (additive) |
| Test discovery config | TODO (setup.cfg / tox.ini / none) | `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` section | N |

**What is removed:**
- `unittest.TestCase` inheritance from all test classes.
- `setUp`, `tearDown`, `setUpClass`, `tearDownClass` methods (replaced by fixtures).
- `self.assert*` method calls.

**What is added:**
- `pytest` as a test dependency (version TODO).
- `pytest-mock` or equivalent for DB and dependency mocking (version TODO).
- `conftest.py` file(s) containing shared fixtures.
- DB mock fixtures that intercept database calls and return controlled responses.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Removal of `unittest.TestCase` base class | All existing test classes must be refactored | Convert each test class to a plain class or standalone functions; remove `TestCase` inheritance |
| `self.assert*` methods no longer available | All assertion calls will fail if not updated | Replace with plain `assert` statements and `pytest.raises` / `pytest.warns` context managers |
| `setUp` / `tearDown` methods no longer auto-invoked by pytest (without `TestCase`) | Test isolation may break if not migrated | Convert to pytest fixtures injected as function parameters; use `autouse=True` where global setup is needed |
| DB connection behavior changes | Tests previously relying on a real DB will need mocks | Introduce fixture-based DB mocks; TODO: define the exact DB abstraction layer to be mocked once codebase is confirmed |
| Test runner invocation change | CI scripts calling `python -m unittest discover` will break | Update CI configuration to invoke `pytest` instead; TODO: confirm CI platform and config file location |
| `setUpClass` / `tearDownClass` patterns | Class-scoped setup will not auto-run | Replace with `@pytest.fixture(scope="class")` or `scope="module"` fixtures |

---

## Acceptance Criteria

1. **Given** the migrated test suite, **when** `pytest` is invoked with no additional flags, **then** all previously passing tests pass without errors or failures.
2. **Given** a test that previously used `self.assertEqual(a, b)`, **when** the assertion fails, **then** pytest outputs a detailed diff showing the actual vs. expected values (confirming native assert rewriting is active).
3. **Given** a test module that previously used `setUp` and `tearDown`, **when** the equivalent pytest fixture is defined and injected, **then** setup runs before the test body and teardown runs after, verified by execution-order logging or a dedicated ordering test.
4. **Given** a test that exercises a database-dependent code path, **when** the test runs in CI with no database service available, **then** the test passes by using the DB mock fixture and does not attempt a real connection.
5. **Given** the DB mock fixture, **when** a test asserts on data returned from the database layer, **then** the mock returns the pre-configured controlled response and the assertion passes.
6. **Given** the full test suite, **when** `pytest` is run, **then** no test imports `unittest.TestCase` or calls `self.assert*` methods (verifiable via a linting rule or grep-based CI check).
7. **Given** shared fixtures defined in `conftest.py`, **when** any test in the same directory scope requests that fixture by name, **then** the fixture is resolved and injected without additional imports.
8. **Given** the CI pipeline, **when** a pull request is opened, **then** the `pytest` test run completes and reports pass/fail status as a required check.
9. **Given** a test that previously used `assertRaises`, **when** migrated to `pytest.raises(ExceptionType)`, **then** the test correctly catches the expected exception and fails if the exception is not raised.
10. **Given** the DB mock fixture with function scope, **when** two tests run sequentially, **then** each test receives an independent mock instance with no state leakage between them.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact pytest version to be pinned as a dependency? | TODO | TODO |
| 2 | Which DB mocking library will be used — `unittest.mock`, `pytest-mock`, `responses`, or a DB-specific tool (e.g., `pytest-postgresql`, `mongomock`)? | TODO | TODO |
| 3 | What database technology is in use (e.g., PostgreSQL, MySQL, SQLite, MongoDB)? This determines the appropriate mocking strategy. | TODO | TODO |
| 4 | Are there any tests that must retain `unittest.TestCase` compatibility (e.g., Django `TestCase` subclasses)? | TODO | TODO |
| 5 | What is the current CI platform and where are the test runner commands defined? | TODO | TODO |
| 6 | Are there existing mock or stub utilities in the codebase that should be preserved or replaced? | TODO | TODO |
| 7 | Should DB fixtures use function, module, or session scope by default? What are the isolation requirements? | TODO | TODO |
| 8 | Is `pyproject.toml` or `pytest.ini` the preferred configuration file for this project? | TODO | TODO |