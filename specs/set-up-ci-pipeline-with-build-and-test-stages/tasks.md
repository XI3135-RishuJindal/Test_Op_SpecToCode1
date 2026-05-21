# TASKS: Set up CI Pipeline with Build and Test Stages

> **Note:** The tech analysis provided does not specify a language, runtime, build tool, or framework. The tasks below are scoped to what can be determined from the task description alone. **Before work begins, the assigned engineer or AI agent must confirm the language, runtime, and build toolchain and update this document accordingly.** Tasks that depend on those specifics are marked with `⚠️ confirm stack first`.

---

## Prerequisites

- [ ] [XS] Confirm the repository's primary language, runtime version, and build tool by inspecting the repository root (e.g., `package.json`, `pom.xml`, `pyproject.toml`, `go.mod`, `Makefile`) and record findings in a `STACK.md` or inline comment before any other task is started
- [ ] [XS] Verify that the target CI platform (GitHub Actions, GitLab CI, CircleCI, etc.) is accessible and that repository-level CI configuration permissions are granted to the working account
- [ ] [XS] Confirm that secrets or environment variables required for the build (e.g., package registry tokens, environment-specific keys) are available in the CI platform's secret store before pipeline tasks begin

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `ci/build-and-test-pipeline`) from the default branch in the repository for all CI configuration changes
- [ ] [S] ⚠️ Audit existing test suite in the repository root and test directories to confirm tests can be executed locally with a single command (e.g., `npm test`, `mvn test`, `pytest`, `go test ./...`) and document the exact command in a `CONTRIBUTING.md` or `README.md` section
- [ ] [XS] Record the current baseline test results (pass count, fail count, duration) by running the test command locally and saving output to `ci/baseline-test-results.txt` on the feature branch for later regression comparison

---

## Phase 2 — Core Upgrade

- [ ] [M] ⚠️ Create the CI platform configuration file (e.g., `.github/workflows/ci.yml` for GitHub Actions, `.gitlab-ci.yml` for GitLab CI, `.circleci/config.yml` for CircleCI) with a `build` stage that checks out the repository, installs dependencies, and compiles/builds the project using the confirmed build tool command
- [ ] [M] ⚠️ Add a `test` stage to the CI configuration file that depends on the `build` stage, executes the confirmed test command, and fails the pipeline on any test failure
- [ ] [S] ⚠️ Configure the CI pipeline trigger rules in the CI configuration file to run on `push` to the default branch and on all pull requests targeting the default branch
- [ ] [XS] Add a pipeline status badge to `README.md` pointing to the new CI workflow so build status is visible on the repository landing page

---

## Phase 3 — Testing & Validation

- [ ] [S] Push the feature branch and verify the CI pipeline triggers automatically, completes the `build` stage successfully, and completes the `test` stage successfully in the CI platform UI
- [ ] [XS] Introduce a deliberate failing test in a throwaway commit on the feature branch, confirm the CI pipeline reports a failure on the `test` stage, then revert the commit to confirm the pipeline returns to green
- [ ] [XS] Compare CI test results (pass count, duration) against the baseline recorded in `ci/baseline-test-results.txt` and confirm no regressions have been introduced by the pipeline configuration itself

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] ⚠️ Pin the CI runner image or action versions (e.g., `actions/checkout@v4`, `actions/setup-node@v4`) to explicit version tags in the CI configuration file to prevent uncontrolled upstream changes from breaking the pipeline
- [ ] [XS] ⚠️ Add dependency caching configuration (e.g., `actions/cache` for npm/Maven/pip/Go module cache) to the CI configuration file to reduce build times on repeated runs

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `## CI Pipeline` section to `README.md` or `CONTRIBUTING.md` documenting the pipeline stages, how to interpret results, and how to run the same build and test commands locally
- [ ] [XS] Open a pull request from `ci/build-and-test-pipeline` to the default branch, confirm the new CI pipeline runs and passes on the PR itself as a live validation of the setup, then merge after review
- [ ] [XS] Delete the `ci/baseline-test-results.txt` file or move it to `.github/` documentation if it should be retained, and confirm no temporary files were merged to the default branch unintentionally

---

**⚠️ Blocking dependency:** Tasks in Phase 2 and beyond cannot be completed with full specificity until the stack confirmation task in Prerequisites is resolved. An AI coding agent picking up Phase 2 tasks must read the output of the Prerequisites confirmation step before generating any CI configuration file content.