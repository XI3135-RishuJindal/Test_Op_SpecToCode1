## Prerequisites

- [ ] [XS] Obtain list of all files containing configuration settings with hardcoded secrets
- [ ] [XS] Ensure access to the repository and all configuration-related source files
- [ ] [XS] Prepare environment variable management tooling (e.g., .env loader, OS environment support) if required

## Phase 1 — Preparation

- [ ] [S] Audit all configuration files for hardcoded secrets in config/ and settings/ directories
- [ ] [XS] Create new feature branch `refactor/config-env-secrets` from main
- [ ] [XS] Capture current test baseline by running existing unit and integration tests

## Phase 2 — Core Upgrade

- [ ] [M] Refactor hardcoded secret keys in config/config.py to use environment variables
- [ ] [S] Refactor hardcoded secrets in settings/settings.py to reference environment variables
- [ ] [S] Remove hardcoded API key in app/secrets.py and replace with environment variable reference
- [ ] [XS] Update code in app/init.py to accept secrets from environment variables instead of direct values

## Phase 3 — Testing & Validation

- [ ] [XS] Add tests for missing/invalid environment variable scenarios in tests/test_config.py
- [ ] [XS] Verify all tests pass in CI with environment-provided secrets
- [ ] [XS] Compare test baseline before and after refactor for regressions

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update .env.example to include new secret environment variable keys
- [ ] [XS] Update CI pipeline YAML (e.g., .github/workflows/ci.yml) to set required secret environment variables
- [ ] [XS] Ensure Dockerfile and docker-compose.yml pass secret values via environment variables

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update README.md to document new environment variable configuration for secrets
- [ ] [XS] Add migration steps and troubleshooting for ops in docs/RUNBOOK.md
- [ ] [XS] Announce change in CHANGELOG.md and prepare post-migration monitoring checklist

---

For all unrelated components and tasks:  
N/A — not applicable to this task