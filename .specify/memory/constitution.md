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
2. **Prefer `pytest-mock` / `unittest.mock` via pytest integration over raw `unittest.mock.patch` decorators** because decorator-stacked patching reduces readability and makes fixture injection harder to trace.
3. **Prefer incremental, file-by-file migration over a single big-bang rewrite** because the upgrade urgency is medium, allowing safe, reviewable increments with no regression window.
4. **Prefer preserving all existing test logic over rewriting test intent** because the migration scope is tooling only — production behaviour must remain unchanged and unverified changes introduce risk.
5. **Prefer explicit `conftest.py` fixture organisation over module-level helpers** because centralised fixtures improve discoverability and reuse across the test suite.

---

## Constraints

- **Scope freeze:** Production source code is out of scope. No changes to non-test files unless strictly required by import side-effects surfaced during migration.
- **Coverage floor:** Test coverage must not decrease below its pre-migration baseline at any point during the migration (measured per-commit on the main migration branch).
- **Framework mandate:** Target framework is `pytest`. No introduction of additional test frameworks (e.g., `nose`, `hypothesis`) unless explicitly approved as a follow-on task.
- **Effort ceiling:** Moderate option — effort and timeline details not provided. TODO: confirm person-days estimate and deadline with project sponsor before sprint planning.
- **Runtime/language:** TODO — confirm Python version to ensure `pytest` version compatibility (minimum pytest 7.x recommended for modern fixture and mock support).
- **Build tool:** TODO — confirm existing build/CI tool (e.g., `tox`, `Makefile`, GitHub Actions) to update test-runner configuration correctly.

---

## Quality Standards

- **Coverage:** Post-migration coverage ≥ pre-migration baseline (line and branch). Measured via `pytest-cov`; CI gate blocks merge if coverage drops.
- **All tests must pass** under `pytest` with zero `xfail` markers added solely to paper over migration failures.
- **No `unittest.TestCase` subclasses** remaining in the migrated files (verified by automated lint rule or grep check in CI).
- **Code review:** Every migrated test module requires at least one peer review approval before merge.
- **`conftest.py` documented:** Each `conftest.py` file must include a module-level docstring describing the fixtures it provides.
- **CI must run the full pytest suite** on every pull request; no merges permitted with a red pipeline.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pytest` as the sole test runner | Stated goal of the modernization task | Accepted |
| ADR-002 | Use `pytest-mock` for mocking integration | Aligns mocking lifecycle with pytest fixtures, avoiding decorator sprawl | Accepted |
| ADR-003 | Migrate incrementally (file by file) | Medium urgency allows safe, reviewable increments; reduces regression risk | Accepted |
| ADR-004 | Keep production code unchanged | Migration scope is test tooling only; source changes are out of scope | Accepted |
| ADR-005 | Confirm Python runtime version before starting | pytest version compatibility depends on Python version; runtime is currently unknown | Proposed — TODO |
| ADR-006 | Confirm CI/build tool configuration | Test runner invocation must be updated; build tool is currently unknown | Proposed — TODO |