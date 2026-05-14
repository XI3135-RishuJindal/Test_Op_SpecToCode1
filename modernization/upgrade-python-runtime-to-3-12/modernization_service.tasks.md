# Modernization_Service.Tasks

## Prerequisites

- [ ] [XS] Identify current Python runtime version used in production and in all development/build environments.
- [ ] [S] Audit project for any direct dependencies on Python version-specific features or behavior.
- [ ] [S] Inventory all external Python dependencies (pip requirements, conda environments, etc.).

## Phase 1 — Preparation

- [ ] [S] Update local and CI environment configurations to allow installation and use of Python 3.12.
- [ ] [M] Review and document all places where the Python runtime version is specified (e.g., Dockerfiles, virtualenv scripts, Makefiles, CI pipelines).

## Phase 2 — Core Upgrade

- [ ] [M] Update Dockerfile(s), environment files, and scripts to reference Python 3.12.
- [ ] [M] Rebuild project environments (locally and in CI) using Python 3.12, ensuring all dependencies install successfully.
- [ ] [L] Address syntax and standard-library incompatibilities surfaced by the upgrade.

## Phase 3 — Testing & Validation

- [ ] [M] Run existing automated test suite under Python 3.12 and document failures.
- [ ] [M] Fix application issues and failing tests caused by the Python 3.12 upgrade.
- [ ] [M] Validate integration points (databases, APIs, etc.) for 3.12 compatibility.
- [ ] [S] Smoke test critical application workflows in an environment running Python 3.12.

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI/CD pipeline configuration to use Python 3.12 as the default runtime.
- [ ] [S] Ensure deployment infrastructure (Docker, serverless, PaaS, etc.) supports Python 3.12.
- [ ] [M] Deploy to a staging environment using Python 3.12 and verify stability.

## Phase 5 — Documentation & Rollout

- [ ] [S] Update internal documentation to state Python 3.12 is required (README, onboarding docs, etc.).
- [ ] [XS] Communicate Python 3.12 upgrade to relevant internal stakeholders and teams.
- [ ] [S] Guide team members on updating local development environments for Python 3.12.

## Post-Migration Cleanup

- [ ] [XS] Remove references or scripts related to the old Python runtime version.
- [ ] [XS] Decommission legacy deployment artifacts or environments using the old Python version.
- [ ] [XS] Close out Python version upgrade tracking tickets/issues.

---

_Note: All sections unrelated to upgrading the Python runtime to 3.12 are omitted or explicitly marked as not applicable._

### Non-applicable sections
N/A — not applicable to this task