# Tasks: Introduce GitHub Actions CI Pipeline

> **Scope:** Add a GitHub Actions CI pipeline with lint, SAST, dependency scan, and test stages.
> **Upgrade Option:** moderate
> **Urgency:** medium

---

## Prerequisites

- [ ] [XS] Confirm repository is hosted on GitHub and Actions is enabled for the repository in **Settings → Actions → General**
- [ ] [XS] Confirm at least one team member has repository **Admin** or **Write** access to create branch protection rules and manage Actions secrets
- [ ] [XS] Audit existing CI configuration files (e.g., `.travis.yml`, `Jenkinsfile`, `circle.yml`, `.gitlab-ci.yml`) in the repository root to identify any pipeline logic that must be preserved or migrated
- [ ] [XS] Identify and document the repository's primary language, runtime, and build tool by inspecting root-level files (e.g., `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Gemfile`) before pipeline authoring begins — record findings in a `docs/ci-discovery.md` scratch note

---

## Phase 1 — Preparation

- [ ] [XS] Create a long-lived feature branch `ci/github-actions-pipeline` from the default branch for all pipeline work
- [ ] [XS] Create the directory structure `.github/workflows/` in the repository root if it does not already exist
- [ ] [S] Capture the current test suite baseline (pass/fail counts, coverage percentage) by running tests locally and recording results in `docs/ci-discovery.md` for later regression comparison
- [ ] [XS] Identify all secrets required by the pipeline (e.g., `GITHUB_TOKEN`, any third-party SAST or scan tokens) and register them in **Settings → Secrets and variables → Actions** before workflow files reference them
- [ ] [XS] Confirm the default branch name (`main` or `master`) and target PR trigger branches in the repository settings so workflow `on:` triggers are set correctly

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `.github/workflows/ci.yml` with top-level `on:` triggers for `push` to the default branch and `pull_request` targeting the default branch, and define the four jobs: `lint`, `sast`, `dependency-scan`, and `test`
- [ ] [S] Implement the `lint` job in `.github/workflows/ci.yml`: select an appropriate linter for the detected language (e.g., `eslint`, `flake8`, `golangci-lint`, `checkstyle`), pin the linter version, and configure it to fail the job on any lint error
- [ ] [S] Implement the `sast` job in `.github/workflows/ci.yml` using **CodeQL** (`github/codeql-action/analyze`) with the language matrix set to the detected language; configure the job to upload SARIF results to the GitHub Security tab
- [ ] [S] Implement the `dependency-scan` job in `.github/workflows/ci.yml` using **Dependabot** alerts (enable via `.github/dependabot.yml`) and/or a scanning action (e.g., `actions/dependency-review-action` for PRs) to block merges when high-severity vulnerabilities are detected
- [ ] [XS] Create `.github/dependabot.yml` configuring automated dependency version updates for the detected package ecosystem and setting `schedule.interval` to `weekly`
- [ ] [S] Implement the `test` job in `.github/workflows/ci.yml`: install dependencies using the detected build tool, run the full test suite, and upload test results or coverage reports as job artifacts using `actions/upload-artifact`
- [ ] [XS] Pin all third-party Actions to specific SHA commits (not floating tags) in `.github/workflows/ci.yml` to prevent supply-chain risk (e.g., `actions/checkout@<SHA>`)
- [ ] [XS] Add a `permissions:` block at the workflow or job level in `.github/workflows/ci.yml` granting only the minimum required permissions (e.g., `contents: read`, `security-events: write` for CodeQL)

---

## Phase 3 — Testing & Validation

- [ ] [S] Trigger the pipeline manually via `workflow_dispatch` or by pushing a test commit to `ci/github-actions-pipeline` and verify all four jobs (`lint`, `sast`, `dependency-scan`, `test`) complete without errors
- [ ] [XS] Confirm CodeQL SARIF results appear in **Security → Code scanning alerts** in the GitHub repository UI
- [ ] [XS] Confirm dependency scan results surface in **Security → Dependabot alerts** or as a PR check comment, as appropriate
- [ ] [XS] Compare the `test` job pass/fail counts and coverage output against the baseline recorded in `docs/ci-discovery.md` and confirm no regressions
- [ ] [XS] Intentionally introduce a lint error, a known vulnerable dependency version, and a failing test in a draft PR to verify each respective job correctly fails and blocks the PR

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Configure branch protection rules on the default branch in **Settings → Branches**: require status checks for `lint`, `sast`, `dependency-scan`, and `test` to pass before merging; require PRs; disallow force-pushes
- [ ] [XS] Set `dependency-review` action in `.github/workflows/ci.yml` to run only on `pull_request` events and configure `fail-on-severity: high` in the action's `with:` block
- [ ] [XS] Add a workflow concurrency group in `.github/workflows/ci.yml` using `concurrency:` to cancel in-progress runs on the same branch when a new push arrives, preventing redundant runs

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Write `docs/ci-pipeline.md` documenting each job's purpose, the tools used, how to interpret failures, and how to update pinned Action SHAs
- [ ] [XS] Add a CI status badge for the `ci.yml` workflow to `README.md` using the GitHub-generated badge URL
- [ ] [XS] Update `CONTRIBUTING.md` (or create it) to document that all PRs must pass the four CI checks before review, and explain how to run lint and tests locally
- [ ] [XS] Merge `ci/github-actions-pipeline` to the default branch via a PR and confirm all four status checks pass on the merge commit
- [ ] [XS] Monitor the **Actions** tab and **Security** tab for the first two weeks post-merge to confirm no false positives or runaway job costs, and record any tuning actions in `docs/ci-pipeline.md`

---

> **Note:** Task sizes and specific tool choices (linter, test runner) are estimated based on a single-language, moderate-complexity repository. Re-size tasks after the language/runtime discovery step in Phase 1 confirms the actual stack.