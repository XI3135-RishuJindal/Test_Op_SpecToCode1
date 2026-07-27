## Prerequisites
- [ ] [XS] Confirm GitHub Advanced Security/CodeQL enablement for the repository in GitHub repository settings (Security & analysis)
- [ ] [XS] Verify CI is GitHub Actions and that `.github/workflows/` is present in the default branch

## Phase 1 — Preparation
- [ ] [S] Create a feature branch `chore/codeql-sast` from default branch in git (local repo)
- [ ] [XS] Inventory existing CI workflows to avoid conflicts with CodeQL triggers in `.github/workflows/`
- [ ] [XS] Decide baseline strategy (use GitHub code scanning “Fix”/“Dismiss” state as baseline) and record decision in `SECURITY.md`

## Phase 2 — Core Upgrade
- [ ] [S] Add CodeQL workflow for default scanning in `.github/workflows/codeql.yml`
- [ ] [XS] Configure CodeQL workflow triggers for `push`, `pull_request`, and a weekly `schedule` in `.github/workflows/codeql.yml`
- [ ] [XS] Configure baseline query set by selecting the `security-extended` query suite in `.github/workflows/codeql.yml`
- [ ] [XS] Configure CodeQL to upload results to GitHub Code Scanning in `.github/workflows/codeql.yml`

## Phase 3 — Testing & Validation
- [ ] [S] Run the CodeQL workflow on the default branch and confirm results appear under GitHub “Security → Code scanning alerts” (workflow run + UI verification)
- [ ] [S] Establish baseline by triaging current findings (dismiss/mark as “won’t fix” as appropriate) in GitHub Code Scanning alerts (repo UI)

## Phase 4 — CI/CD & Infrastructure
- [ ] [XS] Set required permissions for CodeQL workflow (`security-events: write`, minimal `contents: read`) in `.github/workflows/codeql.yml`
- [ ] [XS] Add a CI gate to fail the workflow on CodeQL execution errors (not on existing alerts) in `.github/workflows/codeql.yml`

## Phase 5 — Documentation & Rollout
- [ ] [XS] Document how to view/triage CodeQL findings and how the baseline is managed in `SECURITY.md`
- [ ] [XS] Add an entry describing the new SAST/CodeQL CI check in `CHANGELOG.md` (or N/A if file does not exist)