# TASKS: Integrate Bandit and pip-audit into GitHub Actions CI Pipeline

## Prerequisites

- [ ] [XS] Confirm Python is available in the repository and identify the Python version pinned in the project (check `.python-version`, `pyproject.toml`, `setup.cfg`, or `runtime.txt`)
- [ ] [XS] Confirm repository has an existing GitHub Actions workflow directory at `.github/workflows/` and identify the relevant CI workflow file(s) to modify
- [ ] [XS] Verify repository has a `requirements.txt`, `pyproject.toml`, or `setup.cfg` that can serve as the dependency manifest for `pip-audit`
- [ ] [XS] Confirm GitHub Actions runner type (e.g., `ubuntu-latest`) in the existing workflow file to ensure compatibility with `bandit` and `pip-audit` installation steps

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `feat/security-scanning-bandit-pip-audit`) from the default branch for all changes in this task
- [ ] [S] Add `bandit` and `pip-audit` as development/CI dependencies — pin versions explicitly in `requirements-dev.txt` (or equivalent `[dev]` extras in `pyproject.toml`) using the latest stable releases (e.g., `bandit>=1.7.9`, `pip-audit>=2.7.3`)
- [ ] [XS] Create a `bandit` configuration file `.bandit` (or `[tool.bandit]` section in `pyproject.toml`) specifying target directories (e.g., `targets: [src]`), any agreed skipped test IDs, and severity/confidence thresholds to prevent noise on first run
- [ ] [XS] Run `bandit` locally against the codebase and capture the baseline output to identify any pre-existing findings that must be triaged before CI gate is enforced

---

## Phase 2 — Core Upgrade

- [ ] [M] Add a `security` job to the existing CI workflow file in `.github/workflows/` (e.g., `ci.yml`) containing the following ordered steps: checkout, Python setup, dependency install, `bandit` scan, and `pip-audit` scan
- [ ] [S] Implement the `bandit` scan step in `.github/workflows/ci.yml` using `bandit -r <target_dir> -c .bandit --format json -o bandit-report.json` and configure the step to fail the job on medium-or-higher severity findings
- [ ] [S] Implement the `pip-audit` scan step in `.github/workflows/ci.yml` using `pip-audit --requirement requirements.txt --output pip-audit-report.json --format json` (adjust manifest path to match the actual dependency file identified in Prerequisites)
- [ ] [XS] Add `upload-artifact` steps in `.github/workflows/ci.yml` to persist `bandit-report.json` and `pip-audit-report.json` as workflow artifacts for review on every run
- [ ] [XS] Configure the `security` job in `.github/workflows/ci.yml` to run on `push` to the default branch and on all `pull_request` events targeting the default branch

---

## Phase 3 — Testing & Validation

- [ ] [S] Trigger the updated workflow on the feature branch and verify the `security` job executes both `bandit` and `pip-audit` steps without configuration errors
- [ ] [XS] Confirm `bandit-report.json` and `pip-audit-report.json` artifacts are correctly uploaded and accessible from the GitHub Actions run summary
- [ ] [XS] Introduce a deliberate test finding (e.g., a `subprocess.call` with `shell=True` in a throwaway test file) to verify the `bandit` step correctly fails the CI job, then revert the test file
- [ ] [XS] Verify `pip-audit` correctly parses the dependency manifest and exits non-zero when a known-vulnerable package version is present (use a pinned vulnerable version in a scratch branch, then revert)
- [ ] [XS] Confirm the `security` job does not block unrelated CI jobs (e.g., `test`, `lint`) by verifying job dependency configuration (`needs:`) in `.github/workflows/ci.yml`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Confirm the GitHub Actions runner (`ubuntu-latest`) has network access to PyPI to install `bandit` and `pip-audit` during the workflow; document any proxy or private registry configuration required in `.github/workflows/ci.yml`
- [ ] [XS] Add a `cache` step for pip in `.github/workflows/ci.yml` using `actions/cache` keyed on the hash of the security dependency file to reduce job runtime on repeated runs

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CONTRIBUTING.md` (or equivalent developer guide) to document that `bandit` and `pip-audit` are required CI gates and describe how to run them locally before pushing
- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) recording the addition of `bandit` and `pip-audit` security scanning to the CI pipeline
- [ ] [XS] Open a follow-up issue (or add a `TODO` comment in `.bandit` config) to schedule triage of any pre-existing `bandit` findings suppressed during initial rollout, with an agreed resolution deadline