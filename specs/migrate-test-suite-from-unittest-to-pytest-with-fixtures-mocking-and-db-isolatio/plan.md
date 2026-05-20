# PLAN: Migrate Test Suite from unittest to pytest

> **Spec reference:** Migrate test suite from unittest to pytest with fixtures, mocking, and DB isolation
> **Option:** moderate
> **Status:** Draft

---

## Overview

**Strategy: Strangler-Fig (incremental migration)**

Because the tech analysis does not specify runtime, build tool, or existing test file count, a big-bang rewrite carries unquantifiable risk. The strangler-fig approach allows `unittest`-based tests and `pytest`-style tests to coexist in the same run (pytest natively collects both), so each module's tests can be migrated independently without breaking CI at any intermediate step.

Key justifications:
- **pytest is backward-compatible** with `unittest.TestCase` subclasses, meaning the existing suite continues to pass on day one of the migration.
- **Medium upgrade urgency** (per tech analysis) means there is no emergency forcing a single cutover window.
- **Effort estimate is moderate**, which aligns with an incremental approach that spreads risk across phases rather than concentrating it in one high-risk sprint.
- Each phase produces a shippable, green-CI state, giving the team natural pause points.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Bootstrap** — Install pytest and plugins; configure `pytest.ini` / `pyproject.toml`; verify existing `unittest` suite passes under pytest collection | None | TODO person-days (derive from option detail) |
| 2 | **Fixture Foundation** — Create `conftest.py` hierarchy; implement shared fixtures (DB session, app client, env config); establish DB isolation pattern (transaction rollback or test-DB teardown) | Phase 1 complete | TODO |
| 3 | **Incremental Test Migration** — Convert `unittest.TestCase` classes to plain pytest functions module-by-module; replace `setUp`/`tearDown` with fixtures; replace `self.assert*` with bare `assert` | Phase 2 complete | TODO |
| 4 | **Mocking Modernisation** — Replace `unittest.mock` manual patching with `pytest-mock` (`mocker` fixture); consolidate patch targets; add `freezegun` / `respx` / equivalent where identified | Phase 3 in progress (can overlap) | TODO |
| 5 | **Coverage Gates & CI Integration** — Enforce `pytest-cov` coverage thresholds in CI; remove legacy `unittest` runner invocations; final cleanup of dead imports | Phase 3 complete | TODO |

> **NOTE:** Specific person-day values are marked TODO because the upgrade option was provided without numeric detail and the codebase size is unknown. Populate these from the project's story-point mapping once the test file inventory is complete.

---

## Component Changes

### 1. Test Configuration Files

| File | Change |
|------|--------|
| `pytest.ini` or `pyproject.toml [tool.pytest.ini_options]` | **Create/update** — set `testpaths`, `python_files`, `python_classes`, `python_functions`, `addopts` (e.g., `--strict-markers`, `-ra`) |
| `setup.cfg` | Remove any `[tool:pytest]` or `[unittest]` runner config that conflicts |
| `.coveragerc` or `[tool.coverage]` | **Create/update** — set `source`, `omit`, `fail_under` threshold |

### 2. `conftest.py` Files

- **Root `conftest.py`** — session-scoped and module-scoped fixtures shared across the entire suite (e.g., database engine creation, environment variable overrides).
- **Per-package `conftest.py`** — narrower fixtures scoped to a subsystem (e.g., `tests/api/conftest.py`, `tests/services/conftest.py`).

Key fixtures to implement (names are canonical recommendations; adjust to match discovered code):

```
db_engine        (session scope)  — create engine once per session
db_session       (function scope) — begin transaction, yield, rollback → DB isolation
app_client       (function scope) — test HTTP client wrapping the application
mock_external    (function scope) — pre-configured mocker stubs for third-party calls
```

### 3. Existing Test Classes

For every file matching `test_*.py` or `*_test.py`:

- **Remove** `import unittest` and `class Foo(unittest.TestCase)` wrappers.
- **Replace** `def setUp(self)` → `@pytest.fixture(autouse=True)` or explicit fixture parameter.
- **Replace** `def tearDown(self)` → fixture `yield` + cleanup block.
- **Replace** `self.assertEqual(a, b)` → `assert a == b`.
- **Replace** `self.assertRaises(Exc)` → `pytest.raises(Exc)`.
- **Replace** `self.assertIn`, `self.assertTrue`, etc. → bare `assert` expressions.
- **Replace** `unittest.mock.patch` decorators → `mocker.patch(...)` via `pytest-mock`.

### 4. DB Isolation Pattern

```
# conftest.py (illustrative — adapt to actual ORM/driver)
@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

- Each test function receives a fresh, rolled-back transaction — no persistent state leaks between tests.
- If the project uses migrations (e.g., Alembic), a session-scoped fixture should run `alembic upgrade head` against a dedicated test database before the suite starts.

### 5. Mocking Layer

- **Current:** `unittest.mock.patch` as decorators or context managers on test methods.
- **Target:** `mocker.patch(...)` calls inside test functions or fixtures, provided by `pytest-mock`.
- `mocker` fixture auto-resets all patches after each test — no manual `patcher.stop()` required.

---

## Dependency Upgrade Plan

> **NOTE:** The tech analysis did not supply current or target version numbers. All versions below are marked TODO. Populate from the actual `requirements*.txt`, `Pipfile`, or `pyproject.toml` once inspected.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pytest` | TODO | TODO | TODO | Core runner; replaces `unittest` runner invocation |
| `pytest-cov` | TODO | TODO | TODO | Coverage integration; configure `--cov` in `addopts` |
| `pytest-mock` | TODO | TODO | TODO | Provides `mocker` fixture; wraps `unittest.mock` |
| `pytest-xdist` | TODO | TODO | TODO | Optional parallel execution; requires DB isolation to be correct first |
| `factory-boy` or `faker` | TODO | TODO | TODO | If test data factories are needed; evaluate against existing fixtures |
| `freezegun` | TODO | TODO | TODO | If time-dependent tests exist; check for existing usage |

---

## Infrastructure Changes

**CI/CD Pipeline**

- Replace the test invocation command from `python -m unittest discover` (or equivalent) to `pytest` with appropriate flags.
- Add coverage reporting step: `pytest --cov=<source_dir> --cov-report=xml --cov-fail-under=<threshold>`.
- Upload coverage artifact (e.g., `coverage.xml`) to coverage tracking service if one is in use.

**Docker / Build**

- TODO — Docker base image and build tool not specified in context. Verify that `pytest` and plugins are installed in the test image layer.

**IaC / Kubernetes**

- TODO — Not mentioned in context.

**Test Database**

- TODO — Database engine and provisioning mechanism not specified. Determine whether a dedicated test DB is spun up in CI (e.g., via Docker Compose service, GitHub Actions service container) and document the connection string injection pattern (environment variable name TBD).

---

## Rollback Strategy

Each phase leaves CI green, so rollback is always "revert to the last green phase."

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Delete `pytest.ini` / revert `pyproject.toml` changes; remove newly installed pytest packages from requirements; restore original CI test command. All `unittest` tests continue to pass. |
| **Phase 2** | Delete or empty `conftest.py` files added in this phase; revert any fixture imports added to test files. Phase 1 state is restored. |
| **Phase 3** | Each test file migration is a discrete commit or PR. Revert individual file commits to restore `unittest.TestCase` form for that module. Other migrated files are unaffected. |
| **Phase 4** | Revert `mocker.patch` changes back to `unittest.mock.patch` decorators on a per-file basis. `pytest-mock` can remain installed without harm. |
| **Phase 5** | Remove `--cov-fail-under` gate from CI `addopts` to un-block pipeline; restore previous coverage threshold or remove gate entirely. |

**General principle:** Because pytest collects `unittest.TestCase` tests natively, any partially migrated file is still executable. There is no state where the suite becomes uncollectable mid-migration.

---

## Testing Strategy

### Test Pyramid

```
         ┌──────────────┐
         │  Performance │  (optional, post-migration)
         ├──────────────┤
         │  Regression  │  Full suite run on every PR
         ├──────────────┤
         │ Integration  │  DB + service boundary tests with real fixtures
         ├──────────────┤
         │    Unit      │  Pure logic, fully mocked dependencies
         └──────────────┘
```

### Tools

| Layer | Tool | Notes |
|-------|------|-------|
| Unit | `pytest` + `pytest-mock` | No I/O; all external deps mocked via `mocker` |
| Integration | `pytest` + `db_session` fixture | Uses transaction-rollback isolation |
| Regression | Full `pytest` suite | Run on every PR and merge to main |
| Coverage | `pytest-cov` | Fail CI if below threshold |
| Performance | TODO | Not in scope for this migration; evaluate separately |

### Coverage Targets

- **Minimum gate (CI hard fail):** TODO — establish baseline from current coverage report before migration begins, then set gate at baseline − 0% (do not regress).
- **Target after migration:** TODO — agree with team; a common starting point is 80% line coverage.

### CI Gates

1. `pytest` exit code must be 0 (all tests pass).
2. `--cov-fail-under=<threshold>` enforced in `addopts`.
3. No `pytest` warnings treated as errors initially; add `--strict-markers` from Phase 1 to catch undefined marker usage early.
4. Linting of test files (e.g., `flake8` or `ruff`) should flag leftover `unittest` imports post-Phase 3 — add a custom rule or grep check in CI.

---

## Timeline

> Effort values are TODO pending numeric detail from the upgrade option and test file inventory.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| pytest installed; existing suite green under pytest runner | Phase 1 | TODO | TODO |
| `conftest.py` hierarchy and DB isolation fixture in place | Phase 2 | TODO | TODO |
| 50% of test files migrated to pytest style | Phase 3 | TODO | TODO |
| 100% of test files migrated to pytest style | Phase 3 | TODO | TODO |
| All mocking converted to `pytest-mock` | Phase 4 | TODO | TODO |
| Coverage gate enforced in CI; legacy runner removed | Phase 5 | TODO | TODO |

---

## Open Questions / TODOs

- [ ] Confirm language runtime and build tool to finalise dependency version table.
- [ ] Run `python -m pytest --collect-only` on the existing repo and record total test count to size the effort.
- [ ] Identify database engine (SQLite, PostgreSQL, etc.) to finalise DB isolation fixture implementation.
- [ ] Determine whether a test database service container exists in CI or needs to be added.
- [ ] Agree coverage threshold with team before enforcing the CI gate.
- [ ] Confirm whether `pytest-xdist` parallel execution is desired (requires DB isolation to be verified first).