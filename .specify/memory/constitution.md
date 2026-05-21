# CONSTITUTION
## Project: Replace unittest with pytest + Fixtures & DB Mocking

---

## Project Identity

**Name:** Test Framework Modernization — pytest Migration

**Purpose:** Replace the existing `unittest`-based test suite with `pytest`, introducing structured fixtures and database mocking patterns.

**High-Level Goal:** Deliver a fully migrated test suite that runs under `pytest`, with reusable fixtures and isolated DB mocking, improving test maintainability and developer productivity without altering production code behavior.

---

## Guiding Principles

1. **Prefer pytest-native patterns over unittest compatibility shims** because retaining `unittest.TestCase` subclasses defeats the purpose of migration and accumulates further tech debt.
2. **Prefer fixture-based setup/teardown over per-test boilerplate** because duplicated setup logic is the primary maintainability concern driving this migration.
3. **Prefer in-process DB mocking (e.g., `unittest.mock`, `pytest-mock`, or an in-memory DB) over live database calls in tests** because test isolation and determinism are non-negotiable for a reliable CI pipeline.
4. **Prefer incremental, file-by-file migration over a single big-bang rewrite** because the moderate effort ceiling requires risk to be contained and progress to remain reviewable.
5. **Prefer explicit fixture scope declarations (`function`, `session`, etc.) over implicit defaults** because uncontrolled fixture lifetimes cause hidden state leakage between tests.

---

## Constraints

| Category | Constraint |
|---|---|
| **Effort ceiling** | Moderate option — scope is limited to test-layer changes only; no production code modifications permitted |
| **Scope freeze** | Changes are confined to test files, test configuration, and CI test-runner configuration |
| **Technology mandate** | Target test runner is `pytest`; no other test framework may be introduced |
| **Compatibility** | Existing test coverage must not decrease as a result of migration |
| **Runtime / Language** | TODO — confirm Python version to ensure `pytest` version compatibility (recommend ≥ Python 3.8) |
| **Build tool** | TODO — confirm existing build/CI tool (e.g., tox, Makefile, GitHub Actions) to update runner commands |
| **DB stack** | TODO — confirm database technology (e.g., PostgreSQL, SQLite, ORM) to select appropriate mocking strategy |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Coverage floor** | Post-migration line coverage must be ≥ pre-migration baseline (no regression); measured via `pytest-cov` |
| **Test isolation** | Every test must pass when run in isolation (`pytest <file>::<test>`) and in full-suite order |
| **No live DB calls** | Zero tests may open a real database connection in CI; enforced by a mock/fixture audit in code review |
| **Fixture documentation** | Every shared fixture in `conftest.py` must include a one-line docstring stating its scope and purpose |
| **Code review gate** | All migrated test files require at least one peer review approval before merge |
| **CI gate** | Pull requests must pass the full `pytest` suite with zero failures and zero warnings treated as errors (`-W error`) before merge |
| **Migration completeness** | No `unittest.TestCase` subclasses may remain in the codebase at project close |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Adopt `pytest` as the sole test runner | Directly mandated by the modernization task | Accepted |
| ADR-002 | Use `conftest.py` for all shared fixtures | pytest's standard mechanism; avoids import coupling between test files | Accepted |
| ADR-003 | Use `pytest-mock` or `unittest.mock` for DB mocking | Keeps the dependency footprint minimal; no additional DB infrastructure required in CI | Proposed — confirm once DB stack is known (see TODO) |
| ADR-004 | Prohibit production code changes in this engagement | Effort is moderate; mixing refactors with test migration increases risk and scope | Accepted |
| ADR-005 | Migrate test files incrementally per module | Reduces merge conflict risk and keeps PRs reviewable within the effort ceiling | Accepted |

---

*TODOs must be resolved before sprint planning begins. All subsequent specs and task breakdowns must reference and remain within the bounds of this document.*