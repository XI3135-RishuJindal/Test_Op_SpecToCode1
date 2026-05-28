# CONSTITUTION
## Migrate Test Suite from unittest to pytest

---

## Project Identity

**Name:** Test Suite Migration — unittest → pytest

**Purpose:** Migrate the existing test suite from Python's built-in `unittest` framework to `pytest`, adopting pytest-native fixtures and mocking patterns throughout.

**High-Level Goal:** Deliver a fully pytest-compatible test suite with no reduction in test coverage, improved readability via fixtures, and consistent use of pytest mocking conventions — without altering production source code.

---

## Guiding Principles

1. **Prefer pytest-native fixtures over `setUp`/`tearDown` methods** because `unittest`-style lifecycle hooks are incompatible with pytest's composable fixture model and increase coupling between test cases.
2. **Prefer `pytest-mock` / `unittest.mock` via pytest integration over raw `unittest.mock.patch` decorators** because decorator-stacked patches reduce readability and cannot leverage pytest fixture injection.
3. **Prefer incremental, file-by-file migration over a single big-bang rewrite** because the upgrade urgency is medium, allowing safe, reviewable increments that keep the suite green at every step.
4. **Prefer preserving all existing test logic over rewriting test assertions** because the migration goal is framework replacement, not test redesign — scope creep must be actively resisted.
5. **Prefer `assert` statements over `self.assert*` methods** because pytest's assertion rewriting provides richer failure output and `self.assert*` calls require `unittest.TestCase` inheritance that should be removed.

---

## Constraints

- **Scope freeze:** Production source code is out of scope. No changes to non-test files unless strictly required to support test execution under pytest.
- **Timeline/Effort:** Moderate effort ceiling (exact person-days TODO — not provided in upgrade option). Work must be scoped to fit; no infrastructure or CI overhauls beyond what is needed to run pytest.
- **Technology mandate:** Target framework is `pytest`. The `pytest-mock` plugin is the approved mocking interface. No other test framework may be introduced.
- **Runtime/Language:** TODO — confirm Python version to ensure pytest version compatibility (pytest ≥ 7.x recommended for modern fixture and typing support).
- **Build tool:** TODO — confirm existing build/CI tooling (tox, Makefile, GitHub Actions, etc.) to update test-runner invocation correctly.
- **Coverage must not regress:** Every test that existed before migration must exist after migration. Deletion of tests is not permitted without explicit sign-off.

---

## Quality Standards

- **Coverage floor:** Test coverage must be ≥ the baseline measured immediately before migration begins. A pre-migration coverage report must be captured and stored as the reference.
- **Suite must pass green** at the end of every migrated file before the next file is started — no accumulation of failing tests mid-migration.
- **Code review:** Every PR migrating a test module requires at least one reviewer who can verify fixture correctness and that no test logic has been silently dropped.
- **No `unittest.TestCase` inheritance** remaining in any migrated file at merge time (verified via automated lint rule or grep gate in CI).
- **Documentation:** A `MIGRATION_NOTES.md` file must record any non-obvious migration decisions (e.g., shared fixture placement in `conftest.py`, mocking pattern changes) for future maintainers.
- **CI gate:** The pytest run must be the sole test-execution gate in CI post-migration. Parallel `unittest` runner invocations must be removed.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pytest` as the sole test framework | Stated goal of the modernization task | Accepted |
| ADR-002 | Use `pytest-mock` for mocking | Provides fixture-injected mocking consistent with pytest idioms; avoids decorator stacking | Accepted |
| ADR-003 | Migrate incrementally (file by file) | Medium urgency allows phased approach; keeps suite green continuously | Accepted |
| ADR-004 | Place shared fixtures in `conftest.py` | pytest's standard discovery mechanism; avoids import-based fixture sharing anti-patterns | Accepted |
| ADR-005 | Confirm Python & pytest version compatibility | Runtime version unknown — must be resolved before migration begins | Proposed / TODO |