# TASKS: Baseline Unit and Integration Test Safety Net

> **Goal:** Establish a regression safety net by writing baseline unit and integration tests before any modernization work begins.
> **Upgrade Option:** Moderate
> **Note:** Language, runtime, build tool, and framework details were not provided in the tech analysis. Tasks below are written to be adapted to the discovered stack during Prerequisites. Size estimates assume a typical medium-complexity service; adjust after stack discovery.

---

## Prerequisites

- [ ] [XS] Identify and document the project language, runtime version, and build tool by inspecting the repository root (e.g., `package.json`, `pom.xml`, `build.gradle`, `pyproject.toml`, `*.csproj`, `go.mod`) and record findings in `docs/tech-stack.md`
- [ ] [XS] Identify the existing test framework(s) in use (e.g., JUnit, pytest, Jest, RSpec, Go test) by scanning the dependency manifest and any existing test directories, and record in `docs/tech-stack.md`
- [ ] [XS] Confirm test runner can be executed locally and in CI by running the existing test suite (even if empty) and capturing the exit code and output
- [ ] [XS] Confirm code coverage tooling is available or installable (e.g., JaCoCo, coverage.py, Istanbul/nyc, SimpleCov) and record the chosen tool in `docs/tech-stack.md`
- [ ] [XS] Ensure all engineers and CI agents have read access to the repository and write access to a dedicated branch

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated branch `baseline-tests` from the current default branch to isolate all test-writing work
- [ ] [S] Audit the codebase for all public-facing modules, classes, and functions by scanning source directories and produce an inventory in `docs/test-coverage-inventory.md`, noting which have zero existing tests
- [ ] [S] Audit existing test files (if any) to catalogue current coverage gaps, recording results in `docs/test-coverage-inventory.md` alongside the module inventory
- [ ] [XS] Configure code coverage reporting in the build tool config file (e.g., `pom.xml`, `build.gradle`, `pyproject.toml`, `package.json`) to generate a coverage report on every test run
- [ ] [XS] Capture the current baseline coverage percentage by running the test suite with coverage enabled and saving the report output to `docs/baseline-coverage-report.txt` (commit this file as the regression reference)
- [ ] [XS] Define minimum coverage thresholds (line and branch) in `docs/test-coverage-inventory.md` to be enforced after baseline tests are written — do not enforce yet

---

## Phase 2 — Core Upgrade

> N/A — not applicable to this task. This task is exclusively about writing tests; no dependency upgrades are performed.

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for the highest-risk or most-called pure functions/methods identified in `docs/test-coverage-inventory.md`, targeting happy-path and known edge cases, in the appropriate test source directory
- [ ] [M] Write unit tests for all remaining untested public functions/methods from `docs/test-coverage-inventory.md`, covering at least one positive and one negative case each
- [ ] [L] Write integration tests for each major integration boundary (e.g., database access layer, external HTTP clients, message queue consumers/producers) identified in `docs/test-coverage-inventory.md`, using test doubles (mocks/stubs/fakes) or a local test environment as appropriate
- [ ] [M] Write integration tests for the primary application entry points (e.g., HTTP handlers, CLI commands, event handlers) covering the main success and failure flows identified in `docs/test-coverage-inventory.md`
- [ ] [S] Run the full test suite with coverage enabled, compare the new coverage report against `docs/baseline-coverage-report.txt`, and update `docs/baseline-coverage-report.txt` with the post-baseline numbers
- [ ] [XS] Verify all newly written tests pass consistently by running the suite three times locally and confirming zero flaky failures
- [ ] [XS] Enforce the minimum coverage thresholds defined in `docs/test-coverage-inventory.md` in the build tool config file so the build fails if coverage drops below the baseline

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add or update the CI pipeline configuration (e.g., `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`) to run the full test suite with coverage on every pull request targeting the default branch
- [ ] [XS] Configure the CI pipeline to publish the coverage report as a build artifact and, if the CI platform supports it, post a coverage summary comment on each pull request
- [ ] [XS] Add a CI gate that fails the pipeline if coverage drops below the threshold configured in Phase 3, referencing the build tool config file

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` with instructions for running the test suite and generating the coverage report locally
- [ ] [S] Write `docs/testing-runbook.md` documenting: test directory structure, naming conventions, how to add new tests, how to interpret coverage reports, and how to update the baseline
- [ ] [XS] Open a pull request from `baseline-tests` to the default branch, including the coverage report diff and a summary of modules now covered, for team review before merging
- [ ] [XS] After merge, confirm the CI pipeline passes on the default branch and the coverage artifact is published successfully
- [ ] [XS] Add a note to `docs/test-coverage-inventory.md` marking the baseline as established, with the merge date and final coverage percentage, to serve as the regression reference for all future modernization work

---

> **Reminder:** Because the tech stack was not specified in the analysis, the file paths and tool names above are illustrative. The first two Prerequisites tasks must be completed before any Phase 1 work begins, and their findings should be used to make all subsequent task references concrete.