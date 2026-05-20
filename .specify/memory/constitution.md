# CONSTITUTION
## Test Suite Migration: unittest → pytest

---

## Project Identity

**Name:** Test Suite Modernization — pytest Migration
**Purpose:** Migrate the existing `unittest`-based test suite to `pytest`, introducing fixture-based setup/teardown, structured mocking patterns, and database isolation per test.
**High-Level Goal:** Eliminate legacy `unittest` boilerplate, improve test reliability through DB isolation, and establish a consistent, maintainable testing foundation for the project going forward.

---

## Guiding Principles

1. **Prefer pytest-native fixtures over `setUp`/`tearDown` methods** because `unittest`-style lifecycle methods couple test state to class inheritance, increasing maintenance debt.
2. **Prefer explicit DB isolation per test over shared state** because shared database state between tests causes non-deterministic failures and masks real defects.
3. **Prefer `pytest-mock` or `unittest.mock` via pytest integration over custom mock scaffolding** because consistency in mocking patterns reduces cognitive overhead across the test suite.
4. **Prefer incremental, file-by-file migration over a single big-bang rewrite** because the upgrade urgency is medium, allowing safe, reviewable increments without destabilizing the existing suite.
5. **Prefer keeping tests green at every commit over speed of migration** because a broken test suite during transition provides no safety net for the production codebase.
6. **Prefer removing duplication exposed during migration over carrying it forward** because the migration is an opportunity to address test tech debt, not just a mechanical translation.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is bounded to migration and refactoring of the existing test suite only. No new feature test coverage is in scope.
- **No scope expansion:** Test suite migration must not require or drive changes to production source code, except where production code is untestable and a minimal, isolated fix is required (must be flagged explicitly).
- **Compatibility:** Migrated tests must be executable via the `pytest` CLI without requiring `unittest` runner fallback.
- **DB isolation mechanism:** TODO — specific isolation strategy (transactions, test containers, in-memory DB, fixtures) must be confirmed once the runtime and DB technology are identified.
- **Runtime/language:** TODO — target Python version and dependency versions (e.g., `pytest`, `pytest-mock`, `pytest-django` or equivalent) must be confirmed from the actual project environment before migration begins.
- **Build tool integration:** TODO — CI pipeline configuration for running `pytest` must be confirmed and updated as part of this migration.

---

## Quality Standards

- **Test pass rate:** 100% of previously passing tests must pass after migration. Zero regressions permitted at merge.
- **Coverage floor:** Migrated test suite must maintain or exceed the pre-migration line coverage percentage. Coverage must be measured and reported (e.g., via `pytest-cov`).
- **DB isolation:** Every test that touches the database must use an isolation mechanism (transaction rollback, fixture teardown, or equivalent). No test may leave persistent state in the test database.
- **Code review:** Every migrated module requires at least one peer review before merge. Reviewer must verify fixture correctness and isolation, not just syntax.
- **No `unittest.TestCase` inheritance in new code:** All net-new test files written during or after migration must use plain pytest functions or classes without `unittest.TestCase`.
- **Documentation:** A `TESTING.md` file must be created documenting how to run the suite, the fixture conventions used, and the DB isolation approach chosen.
- **Deployment gate:** Migration PRs must pass CI (lint + full test suite) before merge. No manual overrides.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pytest` as the sole test runner | Removes `unittest` runner dependency; enables fixtures, parametrize, and richer plugin ecosystem | Accepted |
| ADR-002 | Migrate incrementally (module by module) | Medium urgency allows safe, reviewable increments; avoids a destabilizing big-bang rewrite | Accepted |
| ADR-003 | Enforce DB isolation at the test level via fixtures | Shared DB state is a primary source of flaky tests; isolation must be structural, not optional | Accepted |
| ADR-004 | Specific DB isolation strategy (transactions vs. containers vs. in-memory) | TODO — depends on runtime and DB stack, to be decided in spec.md once environment is confirmed | Proposed |
| ADR-005 | CI pipeline update to invoke `pytest` | Existing pipeline runner command must be updated; specifics depend on build tool (TODO) | Proposed |