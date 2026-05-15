## Prerequisites

N/A — not applicable to this task

## Phase 1 — Preparation

- [ ] [S] Identify all existing unittests affected by dependency and API changes in the test/ and tests/ directories
- [ ] [XS] Create a baseline test result artifact by running the current unittest suite using existing build/test tooling

## Phase 2 — Core Upgrade

- [ ] [M] Update imports, mock usage, and assertions in test/ and tests/ to match upgraded dependency and API signatures
- [ ] [S] Refactor unittests with deprecated/unavailable API calls to new equivalents in test/ and tests/
- [ ] [S] Remove or replace tests that are no longer valid due to removed or reworked APIs in test/ and tests/
- [ ] [XS] Add missing unittests for any public APIs newly required by the upgrade in test/ and tests/

## Phase 3 — Testing & Validation

- [ ] [XS] Execute full unittest suite in test/ and tests/ to validate passing status after migration
- [ ] [XS] Compare post-upgrade test results to baseline and document any regressions for triage
- [ ] [XS] Verify unittest coverage has not decreased using available code coverage tools

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update CHANGELOG.md to summarize unittest updates and any removed/modified test cases
- [ ] [XS] Review and update README.md testing instructions to reflect any changes in test execution or coverage tools
- [ ] [XS] Communicate unittest refactor summary to the team via release notes or direct announcement