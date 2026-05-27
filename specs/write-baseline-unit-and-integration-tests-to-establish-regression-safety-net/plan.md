# PLAN: Baseline Unit and Integration Test Suite

> **Spec reference:** Modernization Goal — Write baseline unit and integration tests to establish regression safety net
> **Option:** moderate
> **Status:** Draft

---

## Overview

**Strategy: Feature-flag gated / parallel-run (test-only)**

Since this task is purely additive — introducing tests against an existing codebase without modifying production code — the migration risk is low. No strangler-fig or big-bang restructuring of application code is required. The approach is:

1. Audit existing behaviour by reading current source files and manually characterising inputs/outputs.
2. Write tests in a dedicated test layer that runs in parallel with the existing build, gated behind a CI step that starts as *advisory* (non-blocking) and is promoted to *required* once a stable baseline coverage threshold is reached.

**Justification:** The upgrade option is rated `moderate` effort with `medium` urgency. Because the tech stack details are not fully resolved (language, runtime, and build tool are listed as *unknown* in the tech analysis), a cautious parallel-run approach avoids coupling test infrastructure decisions to a single toolchain assumption. Unknowns are explicitly marked as TODO so they can be resolved in Phase 1 before any test code is written.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Stack Discovery & Toolchain Decision** — Identify language, runtime, build tool, and existing test infrastructure (if any). Select test frameworks. Document findings. | Access to repository and CI system | TODO (derive once stack is confirmed; estimated 1–2 person-days) |
| 2 | **Test Infrastructure Setup** — Add test runner, assertion library, coverage tooling, and CI job (advisory gate). Create folder structure and conventions doc. | Phase 1 complete | TODO (estimated 1–2 person-days) |
| 3 | **Unit Test Baseline** — Write unit tests for all identifiable pure functions, utility modules, and business-logic components. Target initial coverage threshold. | Phase 2 complete | TODO (estimated 3–5 person-days) |
| 4 | **Integration Test Baseline** — Write integration tests covering primary entry points, API contracts, and data-layer interactions. | Phase 3 complete; test environment accessible | TODO (estimated 3–5 person-days) |
| 5 | **CI Gate Promotion & Coverage Enforcement** — Promote CI job from advisory to required. Enforce minimum coverage thresholds. Document baseline report. | Phase 4 complete; team sign-off | TODO (estimated 0.5–1 person-day) |

> **Total estimated effort:** ~9–15 person-days (moderate option). Exact allocation per phase is TODO pending stack confirmation in Phase 1.

---

## Component Changes

Because the language, runtime, and build tool are listed as **unknown** in the tech analysis, specific file paths, class names, and method names cannot be named at this time. The structural changes below are described generically and must be refined in Phase 1.

### Test Directory Structure (to be created)
- A top-level `tests/` (or language-conventional equivalent, e.g., `__tests__/`, `spec/`, `src/test/`) directory will be introduced.
- Sub-directories: `tests/unit/` and `tests/integration/`.
- A test configuration file (e.g., `jest.config.js`, `pytest.ini`, `build.gradle` test block — TODO: confirm) will be added at the project root.

### CI Configuration (to be modified)
- Existing CI pipeline file (TODO: identify — `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, etc.) will gain a new `test` job/stage.
- Coverage report artifact upload step will be added.

### Production Code (no structural changes)
- No production source files are modified in this task.
- If testability gaps are discovered (e.g., hard-coded dependencies, missing interfaces), they will be logged as follow-on tech-debt items and **not** resolved within this plan's scope.

> **TODO:** Once Phase 1 identifies specific files, classes, and methods, this section must be updated with concrete references.

---

## Dependency Upgrade Plan

> **Note:** The tech analysis reports language, runtime, build tool, and frameworks as *unknown*. No dependency versions are available from the provided context. All entries below are structural placeholders.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Test runner | TODO | TODO | TODO | To be selected in Phase 1 based on confirmed language/runtime |
| Assertion library | TODO | TODO | TODO | To be selected in Phase 1 |
| Mocking / stubbing library | TODO | TODO | TODO | To be selected in Phase 1 |
| Code coverage tool | TODO | TODO | TODO | To be selected in Phase 1 |
| Integration test harness (e.g., test containers, in-memory DB) | TODO | TODO | TODO | To be selected in Phase 1 based on data-layer findings |

> **Rule:** All version numbers must be sourced from the tech analysis once it is populated. No versions have been invented here.

---

## Infrastructure Changes

> All items are TODO because infrastructure details are absent from the provided context.

- **CI/CD pipeline:** TODO — Identify existing CI system and pipeline file. Add advisory `test` stage in Phase 2; promote to required gate in Phase 5.
- **Docker base image:** TODO — If tests run in a container, confirm base image and whether a separate test image is needed.
- **Kubernetes manifests:** N/A — not applicable to this task (test execution does not require Kubernetes changes).
- **IaC updates:** TODO — If a test environment (e.g., database, message broker) is required for integration tests, infrastructure provisioning scripts must be identified and updated.
- **Coverage reporting service:** TODO — Determine whether a coverage dashboard (e.g., Codecov, SonarQube) is already provisioned or needs to be added.

---

## Rollback Strategy

Because this task is purely additive (no production code is changed), rollback risk is minimal. Each phase is independently reversible:

| Phase | Rollback Steps |
|-------|---------------|
| 1 — Stack Discovery | No artifacts committed. Discard findings document. No rollback needed. |
| 2 — Test Infrastructure Setup | Revert the test configuration file and CI job addition via a single git revert or branch deletion. The CI job is advisory at this stage, so reverting does not affect production deployments. |
| 3 — Unit Test Baseline | Revert or delete `tests/unit/` directory and associated commits. CI gate is still advisory; no production impact. |
| 4 — Integration Test Baseline | Revert or delete `tests/integration/` directory and associated commits. Tear down any ephemeral test environment resources provisioned for this phase. |
| 5 — CI Gate Promotion | Revert the CI configuration change that made the test job required. This immediately restores the advisory-only state, unblocking any in-flight deployments. |

---

## Testing Strategy

> This section describes the test pyramid being *built* by this task, not tests of the tests themselves.

### Test Pyramid

```
        [ Performance ]        ← Out of scope for this baseline task
       [  Regression  ]        ← Covered by the full suite run on every PR (Phase 5)
      [ Integration   ]        ← Phase 4
     [   Unit         ]        ← Phase 3
```

### Unit Tests (Phase 3)
- **Scope:** Pure functions, utility helpers, business-logic classes, data-transformation routines.
- **Tools:** TODO — confirm after Phase 1 (e.g., Jest, pytest, JUnit, RSpec, Go test).
- **Coverage target (initial baseline):** 60% line coverage as a starting floor, rising to 70% before Phase 5 gate promotion. (Adjust based on actual codebase size discovered in Phase 1.)
- **CI gate:** Advisory in Phase 2–4; required (blocking) from Phase 5 onward.

### Integration Tests (Phase 4)
- **Scope:** Primary application entry points (HTTP handlers, CLI commands, queue consumers — TODO: confirm), database/repository layer interactions, external service boundaries (mocked or containerised).
- **Tools:** TODO — confirm after Phase 1 (e.g., Supertest, pytest + testcontainers, Spring Boot Test, httptest).
- **Coverage target:** Key happy-path and primary error-path scenarios for each entry point. Exact numeric target: TODO pending entry-point inventory.
- **CI gate:** Advisory in Phase 4; required from Phase 5 onward.

### Regression Gate (Phase 5)
- Full test suite (unit + integration) must pass on every pull request before merge.
- Coverage must not drop below the established baseline thresholds.
- Test results and coverage reports published as CI artifacts on every run.

### Performance Tests
- **N/A for this task.** Out of scope for the baseline safety-net effort. Log as a follow-on item.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Stack confirmed, test framework selected | 1 | TODO (Day 2 from start) | TODO |
| Test infrastructure merged, CI advisory job green | 2 | TODO (Day 4 from start) | TODO |
| Unit test baseline merged, 60% coverage achieved | 3 | TODO (Day 9 from start) | TODO |
| Integration test baseline merged, key paths covered | 4 | TODO (Day 14 from start) | TODO |
| CI gate promoted to required, baseline report published | 5 | TODO (Day 15 from start) | TODO |

> **Note:** All dates are expressed as relative offsets from project kick-off. Absolute calendar dates are TODO — assign once team capacity and start date are confirmed. Effort ranges derive from the `moderate` upgrade option (~9–15 person-days total).

---

*Document status: Draft — pending Phase 1 stack discovery to resolve all TODO items.*