# TASKS: Add CI/CD Pipeline with Test, Lint, and SAST Stages

> **Note:** The tech analysis did not specify a language, runtime, or build tool. The tasks below are written for the most common general case (a source repository with no existing CI/CD configuration). **Before work begins, the assignee must confirm the language/runtime and substitute the correct tool names in each task.** Placeholder tokens are marked with `<angle-brackets>`.

---

## Prerequisites

- [ ] [XS] Confirm the primary language, runtime version, and build tool used in the repository and record findings in a `CI_SETUP_NOTES.md` file at the repo root
- [ ] [XS] Verify that the CI/CD platform account (GitHub Actions / GitLab CI / etc.) has the necessary permissions to create pipelines and store secrets for the target repository
- [ ] [XS] Confirm that a SAST tool license or free-tier account (e.g., GitHub Advanced Security, Semgrep, Snyk) is available and that API tokens/secrets can be stored in the repository's secret store
- [ ] [XS] Confirm that branch protection rules can be updated to enforce pipeline status checks on the default branch

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch `ci/add-pipeline` from the default branch for all pipeline work
- [ ] [S] Audit existing test scripts and lint configurations in the repository root (e.g., `package.json` scripts, `Makefile`, `pyproject.toml`, `.eslintrc`, `setup.cfg`) and document which commands are already runnable locally in `CI_SETUP_NOTES.md`
- [ ] [XS] Add or verify a `.gitignore` entry for any CI cache directories (e.g., `.cache/`, `node_modules/`, `__pycache__/`) to prevent accidental commits
- [ ] [XS] Create the CI configuration directory (e.g., `.github/workflows/` for GitHub Actions or `.gitlab-ci.yml` stub) so subsequent tasks have a clear target location

---

## Phase 2 — Core Upgrade

- [ ] [M] Create the primary pipeline configuration file (e.g., `.github/workflows/ci.yml`) defining three top-level jobs: `test`, `lint`, and `sast`, with a trigger on `push` and `pull_request` to all branches
- [ ] [S] Implement the `test` job in `.github/workflows/ci.yml`: configure the correct `<runtime>` version matrix, install dependencies using `<build-tool>` (e.g., `npm ci`, `pip install -r requirements.txt`, `mvn dependency:resolve`), and run the existing test command (e.g., `npm test`, `pytest`, `mvn test`)
- [ ] [S] Implement the `lint` job in `.github/workflows/ci.yml`: install the linter (e.g., ESLint, Flake8, Checkstyle), run it against the source tree, and configure it to fail the job on any lint error using the project's existing lint config file (e.g., `.eslintrc.json`, `.flake8`, `checkstyle.xml`)
- [ ] [S] Implement the `sast` job in `.github/workflows/ci.yml`: integrate the chosen SAST tool (e.g., `github/codeql-action/analyze`, `semgrep/semgrep-action`, or `snyk/actions/<language>`), configure it to scan the source tree, and upload results as a job artifact or to the Security tab
- [ ] [XS] Add a `permissions` block to `.github/workflows/ci.yml` scoping each job to the minimum required GitHub token permissions (e.g., `contents: read`, `security-events: write` for SAST)
- [ ] [XS] Store any required API tokens (e.g., `SNYK_TOKEN`, `SEMGREP_APP_TOKEN`) as encrypted secrets in the repository settings and reference them via `${{ secrets.<TOKEN_NAME> }}` in `.github/workflows/ci.yml`
- [ ] [XS] Add a `cache` step to the `test` and `lint` jobs in `.github/workflows/ci.yml` for the package manager's dependency cache (e.g., `actions/cache` keyed on the lock file hash) to reduce pipeline runtime

---

## Phase 3 — Testing & Validation

- [ ] [S] Trigger the pipeline manually on the `ci/add-pipeline` branch and verify all three jobs (`test`, `lint`, `sast`) complete without errors; capture a screenshot or log excerpt in the PR description
- [ ] [XS] Introduce a deliberate lint violation in a scratch file, confirm the `lint` job fails, then revert the change to validate the lint gate is enforced
- [ ] [XS] Introduce a known-vulnerable dependency or test pattern (if safe to do so in a branch), confirm the `sast` job flags it, then revert to validate the SAST gate is enforced
- [ ] [XS] Verify that test results and SAST reports are accessible as job artifacts or in the Security tab after a successful pipeline run

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Enable branch protection on the default branch in repository settings, requiring all three pipeline jobs (`test`, `lint`, `sast`) to pass before a pull request can be merged
- [ ] [XS] Add a pipeline status badge for the `ci.yml` workflow to `README.md` so build status is visible on the repository homepage

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Write a `docs/ci-pipeline.md` runbook documenting: how to run each stage locally, how to update the SAST tool token, how to modify the runtime version matrix, and how to interpret SAST findings
- [ ] [XS] Add a `CHANGELOG.md` entry (or update the existing one) recording the addition of the CI/CD pipeline, the three stages, and the tools chosen
- [ ] [XS] Open the pull request from `ci/add-pipeline` to the default branch, request review from at least one team member, and confirm all three pipeline jobs pass on the PR before merging

---

> **Reminder:** Replace all `<angle-bracket>` placeholders with the confirmed language, runtime, and tooling values identified in the Prerequisites phase before assigning tasks to an AI coding agent.