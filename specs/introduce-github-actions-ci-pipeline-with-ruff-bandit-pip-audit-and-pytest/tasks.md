# Tasks: Introduce GitHub Actions CI Pipeline (ruff, Bandit, pip-audit, pytest)

## Prerequisites

- [ ] [XS] Confirm repository has a `main` (or `master`) branch with write access and GitHub Actions enabled in repository settings
- [ ] [XS] Confirm Python source files and a `requirements.txt` or `pyproject.toml` exist in the repository root (required for all four tools to operate)
- [ ] [XS] Verify GitHub repository has no existing `.github/workflows/` directory that would conflict with the new pipeline file

---

## Phase 1 — Preparation

- [ ] [S] Audit existing dependencies in `requirements.txt` or `pyproject.toml` and record a baseline list of known `pip-audit` vulnerabilities so pre-existing issues are not treated as regressions
- [ ] [S] Run `ruff check .` locally against the current codebase and capture the full output as a baseline lint report (save as `docs/ci-baseline-ruff.txt`) so initial violations are documented before enforcement begins
- [ ] [S] Run `bandit -r . -f txt` locally against the current codebase and capture output as `docs/ci-baseline-bandit.txt` to distinguish pre-existing findings from new ones
- [ ] [XS] Create feature branch `ci/github-actions-pipeline` from `main` for all pipeline work

---

## Phase 2 — Core Upgrade

- [ ] [XS] Create directory `.github/workflows/` in the repository root if it does not already exist
- [ ] [M] Create `.github/workflows/ci.yml` defining a workflow named `CI` triggered on `push` and `pull_request` to `main`, with a single job `lint-test` running on `ubuntu-latest`
- [ ] [S] Add a `Set up Python` step in `.github/workflows/ci.yml` using `actions/setup-python@v5` pinned to a specific Python version (match the version used in local development)
- [ ] [S] Add a `Install dependencies` step in `.github/workflows/ci.yml` that runs `pip install --upgrade pip`, installs project dependencies from `requirements.txt` or `pyproject.toml`, and installs `ruff bandit pip-audit pytest` as CI tooling
- [ ] [S] Add a `Lint — ruff` step in `.github/workflows/ci.yml` running `ruff check .` and configure `ruff` settings (select, ignore, line-length) in `pyproject.toml` under `[tool.ruff]` or in a new `ruff.toml` at the repository root
- [ ] [S] Add a `Security scan — Bandit` step in `.github/workflows/ci.yml` running `bandit -r . -ll -f txt` (medium-severity threshold) and document the chosen severity flags in a comment within the workflow step
- [ ] [S] Add a `Dependency audit — pip-audit` step in `.github/workflows/ci.yml` running `pip-audit` against the installed environment; if pre-existing vulnerabilities were found in Phase 1, add a `--ignore-vuln` flag or a `.pip-audit-ignore` file to suppress only those known issues
- [ ] [S] Add a `Test — pytest` step in `.github/workflows/ci.yml` running `pytest --tb=short -q` and ensure the step fails the job on any test failure (default behaviour)
- [ ] [XS] Pin all `uses:` action references in `.github/workflows/ci.yml` to full SHA digests or explicit version tags (e.g. `actions/checkout@v4`, `actions/setup-python@v5`) to prevent supply-chain drift

---

## Phase 3 — Testing & Validation

- [ ] [S] Push the feature branch and confirm the Actions workflow triggers automatically; verify all four steps (`ruff`, `bandit`, `pip-audit`, `pytest`) appear in the GitHub Actions run log
- [ ] [XS] Confirm `ruff check .` step exits `0` (or review and fix any violations not present in the baseline report captured in Phase 1)
- [ ] [XS] Confirm `bandit` step exits `0` (or triage any findings not present in the baseline report and either fix or add targeted `# nosec` annotations with justification comments)
- [ ] [XS] Confirm `pip-audit` step exits `0` (or verify all remaining findings are covered by the ignore list established in Phase 2)
- [ ] [XS] Confirm `pytest` step exits `0` and that the test count matches the locally observed count

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a branch protection rule on `main` in GitHub repository settings requiring the `lint-test` job in `.github/workflows/ci.yml` to pass before merging pull requests
- [ ] [XS] Add a `ci` status badge to `README.md` using the GitHub Actions badge URL pointing to `.github/workflows/ci.yml` on `main`

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CONTRIBUTING.md` (or create it) to document how to run `ruff`, `bandit`, `pip-audit`, and `pytest` locally before pushing, including the exact commands used in the CI steps
- [ ] [XS] Add a `CHANGELOG.md` entry (or append to the existing one) recording the introduction of the GitHub Actions CI pipeline, the four tools added, and the effective date
- [ ] [XS] Open and merge the feature branch `ci/github-actions-pipeline` via pull request, confirming the new pipeline itself passes on the merge commit to `main`