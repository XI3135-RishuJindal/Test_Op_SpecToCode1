## Prerequisites
N/A — not applicable to this task

## Phase 1 — Preparation
- [ ] [S] Capture current dependency lock/baseline by saving `git rev-parse HEAD` and existing dependency manifests/lockfiles in `SECURITY_PATCH_BASELINE.md`
- [ ] [S] Identify critical/high CVEs and affected direct dependencies by generating an SBOM/dependency report using the repo’s existing build tooling (no new tools) and recording findings in `SECURITY_PATCH_PLAN.md`
- [ ] [XS] Create patch branch for conservative upgrades in `git` as `chore/security-patch-minor-upgrades`

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
N/A — not applicable to this task

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Document remediated CVEs and upgraded packages with before/after versions in `SECURITY_PATCH_PLAN.md`
- [ ] [XS] Add release notes entry for dependency patch/minor upgrades in `CHANGELOG.md`