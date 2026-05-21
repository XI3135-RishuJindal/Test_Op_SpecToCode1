# TASKS: Set up CI Pipeline with Build and Test Stages

> **Note:** Tech analysis did not specify language, runtime, or build tool. Tasks below are scoped to what is determinable from the goal. Assignee must resolve unknowns in Phase 1 before proceeding to later phases. Tasks marked with ⚠️ require Phase 1 findings to be completed first.

---

## Prerequisites

- [ ] [XS] Confirm repository hosting platform (GitHub, GitLab, Bitbucket, etc.) and verify CI/CD feature is enabled for the target repository
- [ ] [XS] Confirm team members requiring write access to the repository have it, and that a service account or bot token is available for CI runner authentication
- [ ] [XS] Verify that branch protection rules can be configured on the main/default branch to enforce CI gates

---

## Phase 1 — Preparation

- [ ] [S] Audit the repository root to identify the language, runtime, build tool, and existing test framework — document findings in `docs/tech-stack.md` (create if absent)
- [ ] [S] Identify all build commands (e.g., `make build`, `npm run build`, `./gradlew build`) and test commands (e.g., `npm test`, `pytest`, `./gradlew test`) by inspecting the root-level build manifest (e.g., `package.json`, `Makefile`, `build.gradle`, `pom.xml`, `pyproject.toml`) and record them in `docs/tech-stack.md`
- [ ] [XS] Create a dedicated feature branch `ci/setup-build-test-pipeline` from the default branch for all CI configuration work
- [ ] [XS] Capture the current test suite baseline (pass/fail counts, coverage if available) by running the test command locally and recording output in `docs/ci-baseline.md` (create if absent)
- [ ] [XS] Confirm which CI platform will be used (e.g., GitHub Actions, GitLab CI, CircleCI) based on repository hosting, and document the decision in `docs/tech-stack.md`

---

## Phase 2 — Core Upgrade

> ⚠️ Complete Phase 1 before starting. Replace placeholder filenames below with actuals identified in Phase 1.

- [ ] [S] Create the CI configuration file for the chosen platform (e.g., `.github/workflows/ci.yml` for GitHub Actions, `.gitlab-ci.yml` for GitLab CI) with a skeleton defining `build` and `test` stages and triggering on push and pull request events to the default branch
- [ ] [S] Add the `build` stage job to the CI configuration file: specify the correct runner image matching the identified runtime, install dependencies using the identified build tool command, and run the identified build command
- [ ] [S] Add the `test` stage job to the CI configuration file: depend on the `build` stage, run the identified test command, and configure the job to fail the pipeline on any test failure
- [ ] [XS] Add a `.gitignore` entry (or confirm existing entry) to exclude local build artifacts and CI cache directories from version control in `.gitignore`
- [ ] [XS] Configure dependency caching in the CI configuration file for the identified package manager (e.g., `actions/cache` for npm/pip/maven) to reduce pipeline run time

---

## Phase 3 — Testing & Validation

- [ ] [S] Trigger the CI pipeline manually on the feature branch `ci/setup-build-test-pipeline` and verify the `build` stage completes successfully with zero errors
- [ ] [S] Verify the `test` stage executes all tests identified in the baseline captured in `docs/ci-baseline.md` and that pass/fail counts match the baseline
- [ ] [XS] Intentionally introduce a failing test locally, push to the feature branch, and confirm the CI pipeline correctly reports a failed `test` stage — then revert the change
- [ ] [XS] Confirm pipeline run time is reasonable (document actual duration in `docs/ci-baseline.md`) and that dependency caching is functioning by comparing a cached vs. uncached run

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Configure branch protection on the default branch to require the CI pipeline (`build` and `test` stages) to pass before pull requests can be merged — document the setting location in `docs/ci-baseline.md`
- [ ] [XS] Verify that the CI configuration file does not embed secrets in plain text and that any required credentials are stored in the platform's secrets/environment variable store (e.g., GitHub Actions Secrets, GitLab CI Variables)

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` to add a CI status badge pointing to the new pipeline and a brief section describing how to run the build and test commands locally
- [ ] [XS] Add a `CONTRIBUTING.md` entry (create if absent) documenting the CI gate requirement: all PRs must pass the `build` and `test` stages before merge
- [ ] [XS] Open a pull request from `ci/setup-build-test-pipeline` to the default branch, confirm the pipeline runs automatically on the PR, and request review from at least one team member
- [ ] [XS] After merge, monitor the first two post-merge pipeline runs on the default branch and record any flakiness or failures in `docs/ci-baseline.md`

---

**Open Questions (must resolve in Phase 1 before proceeding):**

| # | Question | Owner |
|---|----------|-------|
| 1 | What is the language and runtime? | Assignee |
| 2 | What is the build tool and build command? | Assignee |
| 3 | What is the test framework and test command? | Assignee |
| 4 | Which CI platform will be used? | Assignee |