# CONSTITUTION
## Test Suite Migration: unittest → pytest

---

## Project Identity

**Name:** Test Suite Modernization — unittest to pytest

**Purpose:** Migrate the existing test suite from Python's built-in `unittest` framework to `pytest`, introducing fixture-based setup/teardown and database mocking patterns in place of ad-hoc or class-based equivalents.

**High-Level Goal:** Deliver a fully pytest-native test suite where all tests pass, database interactions are mocked or isolated via fixtures, and no `unittest.TestCase` dependencies remain in the migrated code.

---

## Guiding Principles

1. **Prefer pytest fixtures over `setUp`/`tearDown` methods** because `unittest`-style lifecycle methods are incompatible with pytest's composable fixture model and block adoption of scope-controlled resource management.

2. **Prefer explicit database mocking over live database calls in unit tests** because undeclared external dependencies make tests slow, brittle, and environment-sensitive — a core driver of this migration.

3. **Prefer incremental, file-by-file migration over a single big-bang rewrite** because the scope and language runtime are partially unknown (see Constraints), reducing the risk of a broken test suite mid-migration.

4. **Prefer removing `unittest.TestCase` inheritance entirely over wrapping it** because retaining `TestCase` subclasses prevents use of pytest fixtures as function arguments and perpetuates the debt being retired.

5. **Prefer `conftest.py`-scoped fixtures over module-level globals** because centralised fixture definitions enforce reuse, reduce duplication, and make dependency relationships explicit and auditable.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option selected; treat as a time-boxed, single-engineer effort. Exact person-days not provided — TODO: confirm with project lead before planning. |
| **Scope freeze** | Migration scope is limited to the existing test suite only. No new feature tests, no production code changes. |
| **Runtime/language** | TODO: Confirm Python version in use. pytest ≥ 7.x is the target; minimum supported version must be validated against the runtime. |
| **Build tool** | TODO: Identify existing test runner (e.g., `tox`, `Makefile`, CI pipeline) to ensure pytest is wired in as the replacement runner. |
| **No regression tolerance** | All tests that passed before migration must pass after. Net-new test failures introduced by migration are a blocking defect. |
| **Database mocking library** | TODO: Confirm approved mocking library (e.g., `pytest-mock`, `unittest.mock` via pytest, `factory_boy`, `responses`). Selection must be made before implementation begins. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test passage rate** | 100% of pre-migration passing tests must pass post-migration. Zero regressions accepted at merge. |
| **`unittest.TestCase` elimination** | 0 remaining `unittest.TestCase` subclasses in migrated test files at completion. |
| **Fixture coverage** | Every database interaction in the test suite must be mediated by a fixture or mock — no bare live DB calls in unit tests. |
| **Code review** | All migrated test files require at least one peer review approval before merging. |
| **`conftest.py` documentation** | Every fixture defined in `conftest.py` must include a docstring stating its scope and what it provides. |
| **CI gate** | pytest must be the sole test runner invoked in CI. The pipeline must fail on any test failure or unraisable warning treated as error (`-W error`). |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Adopt pytest as the sole test framework | Directly mandated by the modernization task; removes `unittest` dependency. | Accepted |
| ADR-002 | Use `conftest.py` for shared fixtures | pytest-native pattern; enables scope control and cross-module reuse without imports. | Accepted |
| ADR-003 | Mock database layer at the fixture level, not inline per test | Centralises mock configuration, prevents duplication, and enforces consistent isolation. | Accepted |
| ADR-004 | Migrate incrementally per file, not all at once | Partially unknown codebase (runtime/build tool TBD) warrants a lower-risk, verifiable approach. | Accepted |
| ADR-005 | Specific database mocking library selection | Not yet determined — depends on confirmed runtime and existing dependencies. | **TODO / Proposed** |