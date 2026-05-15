## Prerequisites

N/A — not applicable to this task

## Phase 1 — Preparation

N/A — not applicable to this task

## Phase 2 — Core Upgrade

- [ ] [M] Enforce HTTPS redirect in server entrypoint/configuration file (e.g., main application file or web server config)
- [ ] [L] Add input validation logic to all external-facing request handlers (e.g., API controllers) in relevant source files

## Phase 3 — Testing & Validation

- [ ] [S] Create/extend unit and integration tests for HTTPS enforcement in server test files
- [ ] [S] Create/extend unit and integration tests for input validation code paths in controller/service test files

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [XS] Document HTTPS enforcement details in SECURITY.md
- [ ] [XS] Document input validation changes and new requirements in API documentation (e.g., README.md or openapi.yaml)