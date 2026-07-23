## Prerequisites
- [ ] [XS] Confirm CI system access scope and permissions (read/write) for pipeline configuration in the CI platform UI/repo settings
- [ ] [XS] Confirm access to view CI logs/artifacts for end-to-end baseline validation in the CI platform UI
- [ ] [XS] Confirm access to repository default branch protection / required checks configuration in GitHub repository settings

## Phase 1 — Preparation
- [ ] [S] Capture current CI workflow inventory (names, triggers, jobs) in `.github/workflows/` (enumerate files and summarize in a PR note)
- [ ] [S] Record current required status checks and branch protection rules in GitHub repository settings (document results in `docs/ci-baseline.md`)
- [ ] [XS] Define baseline success criteria (what “end-to-end green” means) in `docs/ci-baseline.md`

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
- [ ] [M] Execute CI workflows end-to-end on the default branch and capture run links, durations, and pass/fail outcomes in `docs/ci-baseline.md`
- [ ] [S] Re-run CI on a representative pull request (non-default branch) and validate required checks behavior in GitHub checks UI (record in `docs/ci-baseline.md`)
- [ ] [S] Validate artifact/log retention and accessibility (download/view) for a full successful run and document in `docs/ci-baseline.md`

## Phase 4 — CI/CD & Infrastructure
- [ ] [S] Configure CI gating so merges require the baseline workflow(s) (update required checks in GitHub branch protection settings and document in `docs/ci-baseline.md`)
- [ ] [S] Add/refresh CI operational troubleshooting steps (where to find logs, how to re-run jobs, common failure triage flow) in `docs/runbook-ci.md`

## Phase 5 — Documentation & Rollout
- [ ] [M] Author operational runbook for CI baseline operations (ownership, escalation path, on-call expectations, SLAs/SLOs if any, rerun policy) in `docs/runbook-ci.md`
- [ ] [S] Document rollback/mitigation procedures for CI incidents (disable required check, revert workflow change, pin runners) in `docs/runbook-ci.md`
- [ ] [S] Define post-change monitoring/check cadence for CI health (daily/weekly signals to review, failure rate tracking approach) in `docs/runbook-ci.md`
- [ ] [XS] Update repository documentation index to link CI baseline and runbook docs in `README.md` (or `docs/README.md` if present)