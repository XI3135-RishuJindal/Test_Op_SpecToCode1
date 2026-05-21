# Plan: GitHub Actions CI Pipeline Setup

## Overview

**Migration Strategy: Big-Bang (Greenfield CI Introduction)**

Since no existing CI/CD pipeline is referenced in the provided context, this is a net-new implementation rather than a migration. A big-bang approach is appropriate: the entire pipeline is introduced in a single pull request, becomes active immediately upon merge, and there is no legacy system to strangle or run in parallel.

**Justification:**
- Upgrade urgency is **medium** — there is no production breakage risk from the absence of CI, but the gap represents meaningful tech debt.
- Effort is low-to-moderate (greenfield configuration, no code refactoring required).
- A feature-flag or strangler-fig strategy would add unnecessary complexity for what is fundamentally a new configuration file addition.

> ⚠️ **NOTE:** The tech analysis did not identify the language, runtime, or build tool. All language/runtime-specific steps below are marked **TODO** and must be filled in once the stack is confirmed.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Repository audit & pipeline design — confirm language, runtime, build tool, test framework, and SAST tool selection | Access to repository source | 0.5 person-days |
| 2 | Scaffold GitHub Actions workflow file(s) — directory structure, trigger configuration, job skeleton | Phase 1 complete | 0.5 person-days |
| 3 | Implement Build step — checkout, dependency install, compile/build | Phase 2 complete; TODO: build tool confirmed | 0.5 person-days |
| 4 | Implement Test step — unit and integration test execution, coverage reporting | Phase 3 complete; TODO: test framework confirmed | 0.5 person-days |
| 5 | Implement SAST step — static analysis tool integration, threshold enforcement | Phase 2 complete; TODO: SAST tool selected | 0.5 person-days |
| 6 | Validation, branch protection rules, and documentation | Phases 3–5 complete | 0.5 person-days |

**Total estimated effort: ~3 person-days** (derived from moderate option; adjust per Phase 1 findings)

---

## Component Changes

### `.github/workflows/ci.yml` *(new file)*
- **What changes:** Created from scratch. This is the primary deliverable.
- **Structure:**
  - `on:` triggers — `push` to `main`/`master`, `pull_request` to `main`/`master`
  - `jobs.build:` — checkout, dependency install, compile
  - `jobs.test:` — test execution, coverage artifact upload
  - `jobs.sast:` — static analysis scan, results upload to GitHub Security tab (SARIF format)
- **Key config keys:**
  - `on.push.branches`, `on.pull_request.branches`
  - `jobs.<job>.runs-on` — TODO: confirm runner OS (`ubuntu-latest` assumed)
  - `jobs.<job>.steps[].uses` — specific Action versions TBD per stack
  - `jobs.test.steps[].run` — TODO: test command
  - `jobs.sast.steps[].uses` — TODO: SAST action

### `.github/workflows/` *(directory)*
- **What changes:** Directory created if not already present.
- Consider splitting into separate workflow files if build+test and SAST have different trigger requirements (e.g., SAST only on PR).

### Branch Protection Rules *(GitHub repository settings — not a file)*
- Require status checks to pass before merging:
  - `build` job
  - `test` job
  - `sast` job
- Require branches to be up to date before merging.

### TODO: Build configuration files
- Specific files (e.g., `Makefile`, `pom.xml`, `package.json`, `pyproject.toml`, `go.mod`) depend on confirmed stack from Phase 1.

---

## Dependency Upgrade Plan

> The tech analysis did not identify the language, runtime, build tool, or current dependency versions. The table below covers GitHub Actions dependencies only.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `actions/checkout` | N/A (new) | TODO: confirm latest (v4 as of last analysis) | N/A | Use `with: fetch-depth: 0` if SAST tool requires full history |
| `actions/upload-artifact` | N/A (new) | TODO: confirm latest (v4 as of last analysis) | N/A | Used for test coverage and SAST report artifacts |
| `actions/cache` | N/A (new) | TODO: confirm latest (v4 as of last analysis) | N/A | Cache dependency directories to speed up builds |
| SAST Action (e.g., CodeQL, Semgrep, Snyk) | N/A (new) | TODO: select and pin version | N/A | TODO: select tool based on confirmed language |
| Language setup action (e.g., `actions/setup-node`, `actions/setup-python`, `actions/setup-java`) | N/A (new) | TODO: confirm based on stack | N/A | TODO: pin to specific version |

> ⚠️ All version numbers marked TODO must be sourced from the confirmed tech analysis — do not use training-data guesses.

---

## Infrastructure Changes

### GitHub Actions Runner
- **Runner OS:** TODO — `ubuntu-latest` is the default assumption; confirm if a self-hosted runner or specific OS version is required.
- **Runner permissions:** The workflow will require `GITHUB_TOKEN` with the following permissions:
  ```yaml
  permissions:
    contents: read
    security-events: write   # Required for SARIF upload to GitHub Security tab
    actions: read
  ```

### GitHub Repository Settings
- Enable **GitHub Advanced Security** (required for CodeQL SARIF upload) — TODO: confirm if repository is on a plan that includes this feature.
- Configure **branch protection rules** on `main`/`master` to require CI status checks (see Component Changes).

### Secrets / Environment Variables
- TODO: Identify if SAST tool (e.g., Snyk, SonarCloud) requires an API token stored as a GitHub Actions secret (`Settings > Secrets and variables > Actions`).
- TODO: Identify if package registry authentication is required for dependency installation.

### Docker / Kubernetes / IaC
N/A — not applicable to this task. The CI pipeline runs on GitHub-hosted runners; no container builds, Kubernetes manifests, or IaC changes are required by this task.

---

## Rollback Strategy

Each phase is independently reversible because all changes are additive (new files, new settings).

| Phase | Rollback Action |
|-------|----------------|
| **Phase 2–5** (workflow file merged) | Delete or rename `.github/workflows/ci.yml` (or revert the merge commit). The pipeline will immediately stop triggering. No application code is affected. |
| **Phase 6** (branch protection enabled) | Navigate to `Settings > Branches > Branch protection rules`, remove or disable the required status checks. This restores the ability to merge PRs without CI passing. |
| **Any phase** (pre-merge) | Close the PR without merging. No changes take effect until the workflow file lands on the default branch. |

> Because this is a greenfield addition with no changes to application source code, rollback at any phase carries zero risk of application regression.

---

## Testing Strategy

The CI pipeline itself must be validated before it is considered production-ready.

### Pipeline Validation (Meta-Testing)

| Layer | Approach | Tools | Gate |
|-------|----------|-------|------|
| **Syntax validation** | Lint the workflow YAML before merge | [`actionlint`](https://github.com/rhysd/actionlint) — run locally or as a pre-commit hook | Must pass with zero errors |
| **Dry-run / act** | Execute the workflow locally against the repository | [`act`](https://github.com/nektos/act) | All jobs exit 0 on a representative branch |
| **PR-based smoke test** | Open a test PR to trigger the new workflow end-to-end | GitHub Actions UI | All three jobs (build, test, sast) show green |
| **Failure-path test** | Introduce a deliberate test failure in a branch to confirm the `test` job blocks merge | GitHub Actions UI + branch protection | PR correctly blocked |
| **SAST gate test** | Introduce a known-bad code pattern to confirm SAST job detects and reports it | GitHub Actions UI | SAST job fails or posts annotation as expected |

### Application-Level Testing (within the pipeline)

| Layer | Description | Tools | Coverage Target |
|-------|-------------|-------|----------------|
| **Unit tests** | TODO: specify test command and framework once stack is confirmed | TODO | TODO: define coverage threshold (recommend ≥ 80% line coverage as a starting baseline) |
| **Integration tests** | TODO: specify if integration tests exist and how they are invoked | TODO | TODO |
| **SAST** | Static analysis for security vulnerabilities | TODO: select tool (CodeQL, Semgrep, or Snyk recommended) | Zero high/critical findings to pass gate |

### CI Gates (enforced on every PR)
1. Workflow syntax valid (`actionlint`).
2. Build job exits 0.
3. Test job exits 0 AND coverage meets threshold (TODO: define threshold).
4. SAST job exits 0 OR posts results without exceeding severity threshold.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Stack confirmed (language, runtime, build tool, test framework) | Phase 1 | Day 1 | TODO |
| Workflow file skeleton merged to feature branch | Phase 2 | Day 1 | TODO |
| Build step implemented and passing | Phase 3 | Day 2 | TODO |
| Test step implemented with coverage reporting | Phase 4 | Day 2 | TODO |
| SAST step implemented and uploading results | Phase 5 | Day 3 | TODO |
| Branch protection enabled; pipeline documented; PR merged to `main` | Phase 6 | Day 3 | TODO |

**Total calendar time: ~3 days** (assumes single engineer, no blockers on stack confirmation in Phase 1)

> ⚠️ Timeline is contingent on Phase 1 completing on Day 1. If stack confirmation is delayed, all subsequent phases shift accordingly.