## Prerequisites

N/A — not applicable to this task

## Phase 1 — Preparation

- [ ] [S] Review existing test suite for coverage gaps and flaky tests in tests/unit and tests/integration
- [ ] [XS] Create `test_hardening` working branch from main in git

## Phase 2 — Core Upgrade

- [ ] [M] Refactor brittle assertions to use robust matchers in tests/unit/*
- [ ] [S] Isolate and mock slow or unreliable dependencies in tests/integration/*
- [ ] [S] Remove or fix nondeterministic test logic in tests/unit and tests/integration
- [ ] [S] Parametrize recurrent test patterns to minimize duplication in tests/unit/*
- [ ] [S] Apply consistent setup/teardown patterns using fixtures or lifecycle hooks in tests/integration/*

## Phase 3 — Testing & Validation

- [ ] [XS] Run full suite and verify all tests pass in CI
- [ ] [S] Measure and report test coverage delta for tests/unit and tests/integration
- [ ] [XS] Document and report any remaining flaky or skipped tests in README or TESTS.md

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update documentation on how to execute hardened tests in TESTS.md
- [ ] [XS] Summarize changes in CHANGELOG.md under "Test Hardening"
- [ ] [XS] Notify team of improved process and monitoring plan via project communication channel