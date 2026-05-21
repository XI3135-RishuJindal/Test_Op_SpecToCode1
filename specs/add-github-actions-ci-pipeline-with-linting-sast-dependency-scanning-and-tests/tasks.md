# Tasks: Add GitHub Actions CI Pipeline with Linting, SAST, Dependency Scanning, and Tests

> **Note:** Language, runtime, and build tool are unspecified in the tech analysis. Tasks below are written at the workflow/configuration level and must be refined once the repository's language stack is confirmed. Placeholder values (e.g., `<language>`, `<package-manager>`) are marked explicitly for substitution — no fictional framework tasks have been added.

---

## Prerequisites

- [ ] [XS] Confirm repository language, runtime, and build tool by inspecting root-level files (e.g., `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Gemfile`) and document findings in a `STACK.md` note or PR description
- [ ] [XS] Verify repository has a `.github/` directory or confirm write access to create one under the default branch
- [ ] [XS] Confirm GitHub Actions is enabled for the repository under **Settings → Actions → General**
- [ ] [XS] Identify and document the default branch name (e.g., `main`, `master`) to use as the CI trigger target
- [ ] [XS] Confirm repository has at least one existing test entry point (e.g., test directory, test script in build manifest) so the test job has a concrete command to run
- [ ] [XS] Identify whether any secrets (e.g., `GITHUB_TOKEN`, third-party SAST tokens) need to be registered under **Settings → Secrets and variables → Actions** before workflows execute

---

## Phase 1 — Preparation

- [ ] [XS] Create feature branch `ci/add-github-actions-pipeline` from the default branch
- [ ] [XS] Create directory structure `.github/workflows/` in the repository root if it does not already exist
- [ ] [S] Document the baseline test pass/fail state by running the existing test suite locally and recording results in the PR description (provides regression comparison for Phase 3)
- [ ] [XS] Add `.github/workflows/.gitkeep` placeholder commit to establish the workflows directory on the branch before adding individual workflow files

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `.github/workflows/lint.yml` defining a linting job that triggers on `push` and `pull_request` to the default branch, using the appropriate linter for the confirmed language stack (e.g., `eslint` for JS/TS, `flake8`/`ruff` for Python, `golangci-lint` for Go, `checkstyle` for Java)
- [ ] [S] Create `.github/workflows/test.yml` defining a test job that triggers on `push` and `pull_request`, checks out the repository, sets up the confirmed runtime/build tool, installs dependencies, and executes the existing test command (e.g., `npm test`, `pytest`, `go test ./...`, `mvn test`)
- [ ] [S] Create `.github/workflows/sast.yml` defining a SAST job using **CodeQL** (`github/codeql-action`) — configure the `language` matrix key to match the confirmed language, trigger on `push`, `pull_request`, and `schedule` (weekly), and set `security-events: write` permission
- [ ] [S] Create `.github/workflows/dependency-scan.yml` defining a dependency scanning job using **Dependabot** configuration (`.github/dependabot.yml`) for automated PR-based alerts, and optionally a workflow step using `actions/dependency-review-action` to block PRs that introduce known-vulnerable dependencies
- [ ] [XS] Add `.github/dependabot.yml` configuring Dependabot for the confirmed package ecosystem (e.g., `npm`, `pip`, `gomod`, `maven`), targeting the default branch with a weekly update schedule
- [ ] [XS] Set `permissions` blocks explicitly in each workflow file (`contents: read`, `security-events: write` where required) to follow least-privilege best practice

---

## Phase 3 — Testing & Validation

- [ ] [S] Open a draft PR from `ci/add-github-actions-pipeline` to the default branch and verify all four workflow runs (lint, test, SAST, dependency scan) are triggered and appear in the **Actions** tab
- [ ] [XS] Confirm the lint job exits `0` (or produces expected output) against the current codebase; document any pre-existing lint failures in the PR description without fixing them in this PR
- [ ] [XS] Confirm the test job executes the correct test command and matches the baseline pass/fail state recorded in Phase 1
- [ ] [XS] Confirm the CodeQL SAST job completes and uploads results to the **Security → Code scanning** tab without workflow errors
- [ ] [XS] Confirm the dependency review job runs on the PR and produces no blocking errors for the existing dependency set
- [ ] [XS] Verify Dependabot is active under **Insights → Dependency graph → Dependabot** after `.github/dependabot.yml` is merged

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add branch protection rule on the default branch under **Settings → Branches** requiring the `lint`, `test`, and `sast` status checks to pass before merge
- [ ] [XS] Set the `dependency-review` workflow check as a required status check on pull requests targeting the default branch
- [ ] [XS] Confirm `GITHUB_TOKEN` automatic permissions are scoped correctly for the repository (read for most jobs, write only for `security-events` in the SAST job) under **Settings → Actions → General → Workflow permissions**

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `## CI` section to `README.md` (or create `README.md` if absent) describing the four workflow files, their triggers, and how to run linting and tests locally
- [ ] [S] Add `CONTRIBUTING.md` (or update if present) with instructions for: running the linter locally, running tests locally, and understanding CI gate failures — referencing the specific workflow files in `.github/workflows/`
- [ ] [XS] Update `CHANGELOG.md` (or create one) with an entry recording the addition of the GitHub Actions CI pipeline, the four job types, and the date of introduction
- [ ] [XS] Remove the draft status from the PR, request review, and confirm all required status checks are green before merging to the default branch
- [ ] [XS] After merge, monitor the **Actions** tab for one full week to confirm scheduled CodeQL and Dependabot runs execute without errors

---

> **Substitution checklist before starting Phase 2:**
> - [ ] Replace `<language>` in `sast.yml` CodeQL matrix with the confirmed language value (e.g., `javascript`, `python`, `go`, `java`)
> - [ ] Replace the linter tool in `lint.yml` with the stack-appropriate tool
> - [ ] Replace the test command in `test.yml` with the actual test invocation
> - [ ] Replace the `package-ecosystem` value in `dependabot.yml` with the confirmed package manager