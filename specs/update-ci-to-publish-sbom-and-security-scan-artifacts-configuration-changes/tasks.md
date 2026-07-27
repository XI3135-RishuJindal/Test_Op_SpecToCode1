## Prerequisites
N/A — not applicable to this task

## Phase 1 — Preparation
- [ ] [S] Identify current CI workflow/pipeline definition file(s) (e.g., `.github/workflows/*.yml` or equivalent) and document existing artifact publish steps in the CI config file(s)

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
- [ ] [XS] Validate CI publishes SBOM and security scan artifacts by running the workflow and confirming artifact upload entries in the CI run logs for the CI config file(s)

## Phase 4 — CI/CD & Infrastructure
- [ ] [M] Add SBOM generation and artifact upload steps in the CI configuration file(s) (e.g., `.github/workflows/*.yml`) to publish the produced SBOM file(s) as build artifacts
- [ ] [M] Add security scan execution and artifact upload steps in the CI configuration file(s) (e.g., `.github/workflows/*.yml`) to publish scan result file(s) as build artifacts
- [ ] [S] Configure CI artifact retention and naming for SBOM and security scan outputs in the CI configuration file(s) (e.g., `.github/workflows/*.yml`)

## Phase 5 — Documentation & Rollout
- [ ] [XS] Document how to locate/download the SBOM and security scan artifacts from CI in `README.md` (or existing CI docs file, if present)