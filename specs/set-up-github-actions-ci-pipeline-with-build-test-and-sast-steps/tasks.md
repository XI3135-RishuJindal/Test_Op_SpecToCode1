# TASKS: Set up GitHub Actions CI Pipeline with Build, Test, and SAST Steps

> **Note:** The tech analysis did not specify a language, runtime, or build tool. Tasks below are scoped to the GitHub Actions pipeline infrastructure itself. File paths and tool names should be updated once the stack is confirmed.

---

## Prerequisites

- [ ] [XS] Confirm repository has a `main` (or equivalent default) branch with push/PR access for the engineer performing setup
- [ ] [XS] Verify GitHub Actions is enabled for the repository under **Settings → Actions → General**
- [ ] [XS] Confirm repository admin access is available to create repository secrets (e.g., for SAST tokens if required)
- [ ] [XS] Identify and document the project's build command, test command, and package manager before workflow authoring begins (record in a scratch note or PR description)

---

## Phase 1 — Preparation

- [ ] [XS] Create feature branch `ci/github-actions-setup` from the default branch in the repository
- [ ] [XS] Create the workflow directory `.github/workflows/` in the repository root if it does not already exist
- [ ] [S] Audit existing CI configuration files (e.g., `Makefile`, `Jenkinsfile`, `.travis.yml`, `circle.yml`) in the repository root and document the current build, test, and lint commands to be replicated in GitHub Actions
- [ ] [XS] Identify the correct GitHub Actions runner OS (e.g., `ubuntu-latest`) based on the project's runtime requirements and record the decision in the PR description

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `.github/workflows/ci.yml` with a `push` and `pull_request` trigger targeting the default branch, defining the top-level workflow name `CI`
- [ ] [S] Add a `build` job to `.github/workflows/ci.yml` that checks out the repository using `actions/checkout@v4` and executes the project's build command on `ubuntu-latest`
- [ ] [S] Add a `test` job to `.github/workflows/ci.yml` that depends on the `build` job (`needs: build`), checks out the repository, and executes the project's test command, including upload of test results using `actions/upload-artifact@v4`
- [ ] [S] Add a `sast` job to `.github/workflows/ci.yml` using the GitHub-native CodeQL action (`github/codeql-action/init@v3`, `github/codeql-action/analyze@v3`) configured to auto-detect language, running on `pull_request` events
- [ ] [XS] Configure the `sast` job in `.github/workflows/ci.yml` to use `continue-on-error: false` so SAST failures block PR merges
- [ ] [XS] Add a `permissions` block to `.github/workflows/ci.yml` scoped to minimum required permissions (`contents: read`, `security-events: write`) for the CodeQL SAST job

---

## Phase 3 — Testing & Validation

- [ ] [S] Open a draft pull request from `ci/github-actions-setup` to the default branch and verify all three jobs (`build`, `test`, `sast`) appear and execute in the **Actions** tab
- [ ] [XS] Confirm the `test` job passes and that test result artifacts are visible under the workflow run summary in GitHub Actions
- [ ] [XS] Confirm the `sast` job completes and that CodeQL results appear under **Security → Code scanning alerts** in the repository
- [ ] [XS] Intentionally introduce a trivial syntax error in a source file on the branch, push, and verify the `build` or `test` job fails and blocks the PR — then revert

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a branch protection rule on the default branch under **Settings → Branches** requiring the `build`, `test`, and `sast` status checks to pass before merging
- [ ] [XS] Set `on.pull_request.branches` in `.github/workflows/ci.yml` to explicitly list the default branch (e.g., `main`) to prevent unintended triggers on unrelated branches
- [ ] [XS] Add a workflow concurrency group in `.github/workflows/ci.yml` (`concurrency: group: ${{ github.ref }}`, `cancel-in-progress: true`) to cancel redundant runs on rapid pushes

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Add a `## CI Pipeline` section to `README.md` (or create it if absent) documenting the three jobs, their triggers, and how to interpret a failed SAST alert
- [ ] [XS] Add a `CODEOWNERS` file (or update the existing one) in the repository root to require review from a designated owner for any future changes to `.github/workflows/`
- [ ] [XS] Merge `ci/github-actions-setup` to the default branch via a reviewed PR and confirm all status checks pass on the merge commit in the **Actions** tab
- [ ] [XS] Verify the branch protection rule is enforced by confirming the **Merge** button is disabled on a test PR with a failing check

---

**Open items before work starts:**
- Stack (language, runtime, build tool) must be confirmed to fill in the build and test commands in Phase 2 tasks.
- If a third-party SAST tool (e.g., Snyk, Semgrep) is preferred over CodeQL, the `sast` job tasks in Phase 2 and the secret setup in Prerequisites will need to be updated accordingly.