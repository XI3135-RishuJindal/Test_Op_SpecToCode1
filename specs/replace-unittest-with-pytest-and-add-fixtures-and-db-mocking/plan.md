# PLAN: Replace unittest with pytest and Add Fixtures and DB Mocking

---

## Overview

**Migration Strategy: Strangler-Fig (incremental, file-by-file conversion)**

The existing `unittest`-based test suite will be migrated to `pytest` incrementally rather than in a single big-bang rewrite. Because `pytest` is fully compatible with `unittest.TestCase` subclasses, both styles can coexist in the same test run during the transition. This eliminates the risk of a prolonged period with no passing test suite.

**Justification:**
- The upgrade urgency is rated **medium**, indicating no immediate crisis but meaningful tech debt accumulation. A strangler-fig approach matches this risk profile: it delivers value continuously without requiring a freeze on feature development.
- The upgrade option is rated **moderate** effort. A big-bang rewrite would concentrate risk and require a feature freeze; incremental conversion does not.
- DB mocking infrastructure (fixtures, mock clients/sessions) can be introduced as a shared layer first, then consumed by converted test files progressively.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Install pytest and plugins; configure `pytest.ini` / `pyproject.toml`; verify existing `unittest` tests still pass under pytest runner | None | TODO (derive from confirmed person-days once tech analysis is complete) |
| 2 | Create shared fixture infrastructure: `conftest.py` files, DB session/connection mocking utilities, factory helpers | Phase 1 complete | TODO |
| 3 | Convert existing `unittest.TestCase` test files to pytest-native style (plain functions, `@pytest.fixture` injection, `assert` statements) | Phase 2 complete | TODO |
| 4 | Integrate DB mocking into converted tests; remove any remaining `unittest.mock` patches that are superseded by fixtures | Phase 3 in progress | TODO |
| 5 | Remove `unittest` imports and dead compatibility shims; enforce pytest-only style via linting rule; update CI gates | Phase 3 & 4 complete | TODO |

> **Note:** Effort estimates are marked TODO because the tech analysis did not supply confirmed person-days. Populate these cells once the codebase file count and test count are known.

---

## Component Changes

### 1. Test Configuration

**Files affected:**
- `pytest.ini` or `pyproject.toml` (`[tool.pytest.ini_options]` section) — **create or update**
- `setup.cfg` — remove any `[tool:pytest]` legacy block if consolidating into `pyproject.toml`

**Changes:**
- Add `testpaths`, `python_files`, `python_classes`, `python_functions` discovery settings.
- Configure `addopts` with coverage flags (e.g., `--cov --cov-report=term-missing`).
- Set `filterwarnings` to surface deprecation warnings from old `unittest` patterns.

---

### 2. `conftest.py` — Fixture Infrastructure (new files)

**Files affected:**
- `tests/conftest.py` — root-level shared fixtures
- `tests/<subpackage>/conftest.py` — scoped fixtures per test subdirectory (create as needed)

**Changes:**
- Define DB connection/session fixtures with appropriate scopes (`session`, `function`):
  ```python
  # Example structure — adapt to actual DB library once confirmed
  @pytest.fixture(scope="function")
  def db_session():
      ...
  ```
- Define mock DB fixtures using `pytest-mock` or `unittest.mock.patch` wrapped in fixtures.
- Define factory fixtures for common model/data objects.

**APIs modified:** N/A (new code)

---

### 3. Existing Test Files

**Files affected:** All files matching `test_*.py` or `*_test.py` under `tests/` (specific filenames TODO — not provided in context).

**Structural changes per file:**
- Remove `import unittest` and `class FooTest(unittest.TestCase):` wrappers.
- Replace `self.assertEqual(a, b)` → `assert a == b`, `self.assertRaises` → `pytest.raises`, etc.
- Replace `setUp` / `tearDown` methods with `@pytest.fixture` (autouse or explicit injection).
- Replace `unittest.mock.patch` decorators with `mocker` fixture from `pytest-mock` where appropriate.
- Replace `self.mock_*` instance attributes with fixture-injected mock objects.

**Specific class/method names:** TODO — not available in provided code context. Populate during Phase 3 discovery.

---

### 4. DB Mocking Layer

**Files affected:**
- `tests/conftest.py` (additions)
- Individual test files (consumers)

**Changes:**
- Introduce a `mock_db` or `fake_db_session` fixture that patches the DB connection factory at the appropriate import path.
- If an ORM is in use (TODO — ORM not confirmed in tech analysis), provide a transactional rollback fixture pattern:
  ```python
  @pytest.fixture
  def db_session(real_db_engine):
      connection = real_db_engine.connect()
      transaction = connection.begin()
      yield session_factory(bind=connection)
      transaction.rollback()
      connection.close()
  ```
- If no real DB is available in CI, provide a fully in-memory or mocked alternative (e.g., SQLite override or `MagicMock` session).

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pytest` | TODO (not in tech analysis) | TODO | N/A — new addition | Install via dev/test dependencies |
| `pytest-mock` | Not installed | TODO | N/A — new addition | Provides `mocker` fixture; replaces manual `unittest.mock.patch` decorators |
| `pytest-cov` | Not installed | TODO | N/A — new addition | Coverage reporting; configure `--cov` in `addopts` |
| `unittest` (stdlib) | Built-in | Removed (Phase 5) | Removal of `TestCase` base class usage | Incremental; coexists until Phase 5 |

> **Note:** All target versions are marked TODO because the tech analysis did not supply confirmed version numbers. Populate from `pip index versions pytest` or the project's resolved dependency lock file before beginning Phase 1.

---

## Infrastructure Changes

**CI/CD Pipeline:**
- Update the test execution command from `python -m unittest discover` (or equivalent) to `pytest` with configured options.
- Add a coverage gate: fail the build if coverage drops below the agreed threshold (TODO — threshold not defined in context; recommend establishing baseline in Phase 1 before enforcing).
- Ensure the CI environment installs dev/test dependencies including `pytest`, `pytest-mock`, and `pytest-cov`.

**Docker / Kubernetes / IaC:**
- TODO — no Docker, Kubernetes, or IaC context was provided. If tests run inside a container, the base image's dependency installation step must be updated to include new pytest plugins.

---

## Rollback Strategy

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Remove `pytest` and plugins from dev dependencies; revert `pytest.ini` / `pyproject.toml` changes; restore original test runner command in CI. All `unittest` tests remain untouched and runnable. |
| **Phase 2** | Delete newly created `conftest.py` files. No existing test files have been modified; no functional rollback risk. |
| **Phase 3** | Each converted test file should be committed individually (or in small batches). Revert specific commits for any file that regresses. The `unittest`-style files remain in git history and can be restored via `git checkout <sha> -- tests/path/to/test_file.py`. |
| **Phase 4** | Remove DB mock fixtures from `conftest.py`; revert individual test files to their Phase 3 state (pytest-native but without DB mock injection). |
| **Phase 5** | This phase is the point of no return for `unittest` removal. If rollback is needed, restore `unittest` imports and `TestCase` wrappers from git history. Recommend tagging the commit immediately before Phase 5 begins as `pre-pytest-cleanup` for easy reference. |

**General principle:** Because the strangler-fig approach keeps both styles runnable simultaneously through Phases 1–4, any phase can be rolled back without breaking the test suite.

---

## Testing Strategy

### Test Pyramid

| Layer | Approach | Tools | Coverage Target | CI Gate |
|-------|----------|-------|----------------|---------|
| **Unit** | Pure function tests, no I/O; DB calls replaced by mock fixtures | `pytest`, `pytest-mock` | TODO (establish baseline in Phase 1) | Fail on regression below baseline |
| **Integration** | Tests that exercise multiple units together; DB interactions use transactional rollback fixture or in-memory DB | `pytest`, DB fixture from `conftest.py` | TODO | Run on every PR |
| **Regression** | Full converted test suite must produce identical pass/fail results as the original `unittest` suite | `pytest` (with `unittest` compat layer active during transition) | 100% of previously passing tests must continue to pass | Enforced from Phase 1 onward |
| **Performance** | TODO — no performance testing context provided | TODO | TODO | TODO |

### Specific Practices
- **Baseline snapshot:** Before any conversion, run the existing suite and record the pass count. This becomes the regression floor.
- **Parallel runs (Phase 3):** During conversion, run both the original and converted versions of each test file and diff results before deleting the original.
- **Coverage diff:** After each phase, compare coverage reports to detect accidental coverage loss from fixture refactoring.
- **Linting:** Add `flake8-pytest-style` or `ruff` pytest rules to enforce fixture usage patterns and flag remaining `unittest` idioms in Phase 5.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| pytest installed and all existing tests green under new runner | Phase 1 | TODO | TODO |
| `conftest.py` with DB mock fixtures merged and reviewed | Phase 2 | TODO | TODO |
| 50% of test files converted to pytest-native style | Phase 3 | TODO | TODO |
| 100% of test files converted | Phase 3 | TODO | TODO |
| DB mocking integrated across all converted tests | Phase 4 | TODO | TODO |
| `unittest` fully removed; lint rule enforced in CI | Phase 5 | TODO | TODO |

> **Note:** All dates and owners are marked TODO. The tech analysis did not provide confirmed person-days or team assignments. Populate this table during sprint planning once Phase 1 discovery (test file count, complexity assessment) is complete.