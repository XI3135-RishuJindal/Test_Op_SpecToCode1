## Prerequisites
- [ ] [XS] Confirm GitHub Actions is the active CI for the repository in `.github/workflows/`  
- [ ] [XS] Ensure repository admin access to enable GitHub Advanced Security / Secret Scanning settings in `Settings → Security & analysis` (repository configuration)

## Phase 1 — Preparation
- [ ] [XS] Create feature branch `chore/ci-gitleaks` from default branch (git branch operation)
- [ ] [S] Define gitleaks policy (allowlist + rules) in `.gitleaks.toml`
- [ ] [S] Capture baseline by running gitleaks locally and saving findings for triage in `reports/gitleaks.baseline.json`

## Phase 2 — Core Upgrade
- [ ] [S] Add gitleaks scan workflow for pull requests in `.github/workflows/gitleaks.yml`
- [ ] [S] Configure workflow to upload SARIF results to GitHub Code Scanning in `.github/workflows/gitleaks.yml`
- [ ] [S] Add optional baseline suppression (ignore known historical findings) via gitleaks config in `.gitleaks.toml`

## Phase 3 — Testing & Validation
- [ ] [XS] Validate workflow executes on PR events and reports results in PR checks via `.github/workflows/gitleaks.yml`
- [ ] [XS] Validate Code Scanning alerts are created from SARIF upload in GitHub Security tab (repository UI validation)
- [ ] [S] Seed a safe test secret pattern and verify detection + actionable file/line output, then remove test change in a dedicated commit touching `.gitleaks.toml`

## Phase 4 — CI/CD & Infrastructure
- [ ] [S] Add scheduled secret scan (e.g., nightly) to catch drift in `.github/workflows/gitleaks.yml`
- [ ] [XS] Configure workflow permissions required for SARIF upload (`security-events: write`) in `.github/workflows/gitleaks.yml`
- [ ] [XS] Add concurrency + timeouts to prevent runaway CI jobs in `.github/workflows/gitleaks.yml`

## Phase 5 — Documentation & Rollout
- [ ] [S] Document secret-scanning expectations and local developer run instructions in `README.md`
- [ ] [S] Add triage/runbook steps for handling findings (rotate credentials, purge history guidance, allowlist rules) in `docs/security/secret-scanning.md`
- [ ] [XS] Announce rollout plan (PR gating behavior, initial baseline handling) in `CHANGELOG.md`