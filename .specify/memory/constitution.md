# CONSTITUTION
## Regression Safety Net — Baseline Test Suite

---

## Project Identity

**Name:** Baseline Test Suite Initiative
**Purpose:** Establish a regression safety net for the existing codebase by writing baseline unit and integration tests before any further modernization work proceeds.
**High-Level Goal:** Achieve sufficient test coverage to detect unintended behavioral regressions introduced by future changes, providing confidence that modernization efforts do not break existing functionality.

---

## Guiding Principles

1. **Prefer testing observable behavior over internal implementation details** because the primary goal is regression detection, not code-structure enforcement — tests that break on safe refactors undermine the safety net.
2. **Prefer broad coverage at a shallow depth first over deep coverage of a narrow surface** because the upgrade urgency is medium and the codebase has unquantified tech debt; a wide net catches more regressions sooner.
3. **Prefer characterization tests ("golden path" assertions) over idealized correctness tests** because the current behavior — not the desired behavior — is the baseline to protect against regression.
4. **Prefer isolated unit tests for logic-heavy units and integration tests at system boundaries** because boundary behavior (I/O, external calls, data persistence) is where regressions most commonly surface during modernization.
5. **Prefer deterministic, repeatable tests over tests with external dependencies** because flaky tests erode trust in the safety net and will be ignored or deleted.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is bounded to writing baseline tests only; no refactoring, no new features, no dependency upgrades are in scope under this task.
- **Scope freeze:** Tests must reflect *current* behavior. Any deviation from current behavior discovered during test writing must be logged as a finding, not silently corrected.
- **Technology mandates:** TODO — runtime, language, build tool, and test framework are unknown. These must be confirmed before test implementation begins (see Decision Log).
- **No production changes:** This task produces test code only. No changes to production source files are permitted except trivial, non-behavioral adjustments required to make code testable (e.g., dependency injection seams), and each such change must be reviewed and logged.

---

## Quality Standards

- **Coverage floor:** Minimum 60% line coverage on all modules touched by the test suite upon task completion, measured by the project's designated coverage tool. TODO — confirm tooling.
- **Integration test gate:** At least one integration test must exist for each identified system boundary (e.g., database, external API, message queue). TODO — boundaries to be enumerated in spec.md.
- **Test reliability:** Zero tolerated flaky tests at merge time. Any non-deterministic test must be fixed or removed before the PR is accepted.
- **Code review:** Every test file requires at least one peer review approval before merge, with explicit confirmation that the test reflects current behavior, not aspirational behavior.
- **Documentation:** Each test file must include a header comment stating the module under test and the behavioral contract being asserted.
- **CI gate:** The full test suite must pass in CI on every pull request. A failing suite blocks merge with no exceptions.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Baseline tests will assert current behavior, not corrected behavior | Protects against regression during modernization; corrections are a separate concern | Accepted |
| ADR-002 | Production source changes are restricted to testability seams only | Prevents scope creep and ensures this task remains a pure safety-net effort | Accepted |
| ADR-003 | Test framework selection is deferred pending language/runtime confirmation | Language and runtime are unknown; framework cannot be chosen without this input | Proposed |
| ADR-004 | Coverage floor set at 60% line coverage | Balances breadth-first principle with moderate effort ceiling; can be raised in a follow-on task | Proposed |
| ADR-005 | System boundary inventory to be produced in spec.md before integration test work begins | Boundaries are unknown; integration tests cannot be scoped without enumeration | Proposed |