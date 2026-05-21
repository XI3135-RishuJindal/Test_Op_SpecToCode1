# PLAN: Add GitHub Actions CI Pipeline

## Overview

**Migration Strategy: Big-Bang (Greenfield Addition)**

This task introduces a net-new GitHub Actions CI pipeline into a repository that currently has no automated CI. Because no existing pipeline infrastructure is being replaced or modified, a big-bang delivery is appropriate — the entire pipeline is added in a single, self-contained pull request with no risk of breaking existing workflows.

The upgrade urgency is rated **medium**, and the effort estimate is moderate. The absence of a pre-existing CI system means there is no strangler-fig or parallel-run complexity; the primary risk is misconfiguration of individual job steps, which is mitigated by incremental job-level testing during implementation.

> **NOTE:** The repository's primary language, runtime, build tool, and framework are not specified in the provided tech analysis. All language-specific tooling choices below are marked **TODO** and must be resolved by the implementing engineer before work begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Repository audit — identify language, runtime, build tool, existing test commands, and secrets required | None | 0.5 person-days |
| 2 | Scaffold workflow file structure (`.github/workflows/`) and define trigger strategy | Phase 1 complete | 0.5 person-days |
| 3 | Implement linting job | Phase 2 complete | 0.5 person-days |
| 4 | Implement SAST job | Phase 2 complete | 0.5 person-days |
| 5 | Implement dependency scanning job | Phase 2 complete | 0.5 person-days |
| 6 | Implement test execution job | Phase 2 complete | 1 person-day |
| 7 | Wire jobs with `needs:` dependencies, add status badges, validate end-to-end on a feature branch | Phases 3–6 complete | 0.5 person-days |
| 8 | Documentation update (`README.md`, `CONTRIBUTING.md`) and team review | Phase 7 complete | 0.5 person-days |

**Total estimated effort: ~4.5 person-days** (consistent with a moderate-effort option)

---

## Component Changes

### `.github/workflows/ci.yml` *(new file)*
- Primary workflow file triggered on `push` to all branches and `pull_request` targeting `main` (or default branch).
- Defines the following jobs:
  - `lint` — runs the project linter (TODO: tool TBD per language)
  - `sast` — runs static application security testing (see Dependency Upgrade Plan)
  - `dependency-scan` — runs dependency vulnerability scanning
  - `test` — runs the project test suite
- All jobs run on `ubuntu-latest` unless the runtime requires a specific OS (TODO: confirm).
- Jobs `sast`, `dependency-scan`, and `test` declare `needs: [lint]` to fail fast on style errors before heavier jobs run.

### `.github/workflows/` *(new directory)*
- May be split into multiple focused workflow files if the repository grows (e.g., `security.yml` for SAST + dep-scan, `ci.yml` for lint + test). Single-file approach is recommended for initial delivery.

### `README.md` *(existing file — modified)*
- Add CI status badge referencing the new workflow.
- Add a "Local Development" section documenting how to run lint and tests locally to mirror CI.

### `CONTRIBUTING.md` *(new or existing file — modified)*
- Document the CI gate requirements: all jobs must pass before merge.
- Document how to reproduce each CI job locally.

### `.github/dependabot.yml` *(new file — optional but recommended)*
- Enable Dependabot for GitHub Actions action version pinning to complement the dependency scanning job.

---

## Dependency Upgrade Plan

> All version numbers are marked TODO because the tech analysis does not specify the language, runtime, or build tool. The table below lists the GitHub Actions actions that will be used; pin to the exact SHA or tag confirmed at implementation time.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `actions/checkout` | N/A (not present) | TODO: pin to latest stable tag (e.g., `v4`) | N/A | Required by all jobs |
| `actions/setup-<runtime>` | N/A (not present) | TODO: pin per runtime (e.g., `actions/setup-node@v4`, `actions/setup-python@v5`, `actions/setup-java@v4`) | N/A | TODO: select correct action after Phase 1 audit |
| SAST tool action | N/A (not present) | TODO: select per language — candidates: `github/codeql-action` (multi-language), `returntocorp/semgrep-action`, `SonarSource/sonarcloud-github-action` | N/A | CodeQL is free for public repos; confirm licensing for private repos |
| Dependency scanner action | N/A (not present) | TODO: select per ecosystem — candidates: `actions/dependency-review-action` (PR-scoped), `snyk/actions`, `aquasecurity/trivy-action` | N/A | `dependency-review-action` requires GitHub Advanced Security for private repos |
| Linter action/tool | N/A (not present) | TODO: select per language — candidates: `super-linter/super-linter`, language-native linter (ESLint, Flake8, Checkstyle, etc.) | N/A | Prefer language-native linter for precision over super-linter for large repos |
| `actions/upload-artifact` | N/A (not present) | TODO: pin to latest stable tag (e.g., `v4`) | N/A | Used to upload SAST and test reports |

---

## Infrastructure Changes

### GitHub Actions Runner
- All jobs target `ubuntu-latest` (GitHub-hosted runner). No self-hosted runner infrastructure is required unless the repository has network-restricted dependencies.
- TODO: Confirm whether the build requires access to a private package registry (e.g., private npm, PyPI, Maven). If so, runner network configuration or secrets for registry authentication must be added.

### GitHub Repository Settings
- **Branch protection rule** on `main` (or default branch): require all CI jobs to pass before merge. This must be configured manually in repository Settings → Branches after the workflow is merged.
- **Secrets**: TODO — identify any secrets required (e.g., `SNYK_TOKEN`, `SONAR_TOKEN`, registry credentials) and add them to repository or organization secrets before the workflow runs.
- **GitHub Advanced Security**: TODO — confirm whether the repository is public or private. CodeQL and `dependency-review-action` have licensing implications for private repositories.

### Docker / Kubernetes / IaC
N/A — not applicable to this task. The CI pipeline runs on GitHub-hosted runners; no container builds, Kubernetes manifests, or IaC changes are introduced by this task.

---

## Rollback Strategy

Because this task adds only new files and does not modify existing application code, rollback is low-risk at every phase.

| Phase | Rollback Action |
|-------|----------------|
| Phase 2–7 (workflow files added) | Delete or revert the `.github/workflows/ci.yml` file via a follow-up PR or by reverting the merge commit. The application codebase is unaffected. |
| Phase 7 (branch protection enabled) | Disable the branch protection rule in repository Settings → Branches. This is an independent, immediately reversible repository setting. |
| Phase 8 (README/CONTRIBUTING updated) | Revert the documentation changes via a follow-up PR. Remove the status badge from `README.md`. |
| Dependabot config added | Delete `.github/dependabot.yml` via a follow-up PR to stop automated PRs. |

**General principle:** No phase in this task modifies application source code, build scripts, or deployment configuration. Any rollback is a file deletion or revert with zero application risk.

---

## Testing Strategy

### Pipeline Self-Validation (during implementation)
- Each job must be tested on a feature branch before merging to `main`. Push commits to the feature branch and observe job results in the GitHub Actions UI.
- Use `act` (https://github.com/nektos/act) for local workflow execution during development to reduce iteration time.

### Test Pyramid for the CI Pipeline Jobs

| Layer | What is tested | Tool | Gate |
|-------|---------------|------|------|
| **Unit** | Application unit tests | TODO: language-native test runner (e.g., Jest, pytest, JUnit, go test) | All tests must pass; zero tolerance for test failures |
| **Lint** | Code style and formatting | TODO: language-native linter | Zero lint errors; warnings configurable per project standard |
| **SAST** | Static security vulnerabilities in source code | TODO: CodeQL / Semgrep / SonarCloud (see Dependency Upgrade Plan) | Block merge on HIGH/CRITICAL findings; MEDIUM findings generate annotations |
| **Dependency Scan** | Known CVEs in third-party dependencies | TODO: `dependency-review-action` / Snyk / Trivy | Block merge on HIGH/CRITICAL CVEs in direct dependencies |
| **Integration** | TODO: if integration tests exist, add a separate job | TODO | TODO: define pass/fail threshold |
| **Performance** | N/A for initial pipeline delivery | — | Not gated in initial implementation |

### Coverage Targets
- TODO: Define minimum code coverage threshold after Phase 1 audit reveals the existing test suite baseline. A common starting gate is 80% line coverage; do not set a target higher than the current baseline without a remediation plan.
- Coverage reports should be uploaded as workflow artifacts using `actions/upload-artifact` for review.

### CI Gates (merge blocking)
- All jobs in `ci.yml` must have a green status before a PR can be merged (enforced via branch protection rule — see Infrastructure Changes).
- SAST and dependency scan jobs must exit non-zero on HIGH/CRITICAL findings to block merge.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Language/runtime/build tool confirmed, secrets identified | Phase 1 | Day 1 | TODO |
| Workflow file scaffolded, triggers defined | Phase 2 | Day 1 | TODO |
| Lint job passing on feature branch | Phase 3 | Day 2 | TODO |
| SAST job passing on feature branch | Phase 4 | Day 2 | TODO |
| Dependency scan job passing on feature branch | Phase 5 | Day 3 | TODO |
| Test job passing on feature branch | Phase 6 | Day 3–4 | TODO |
| Full pipeline end-to-end green, badge added | Phase 7 | Day 4 | TODO |
| Docs updated, branch protection enabled, PR merged | Phase 8 | Day 5 | TODO |

**Total calendar time: ~5 working days** (assumes a single engineer; parallelizable across Phases 3–6 with two engineers to reduce to ~3 days).