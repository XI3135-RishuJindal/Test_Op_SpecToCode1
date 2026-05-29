# PLAN: Add CI/CD Pipeline with Test, Lint, and SAST Stages

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental Pipeline Rollout**

Since the existing codebase has no CI/CD pipeline, this effort introduces one from scratch using an incremental (strangler-fig-style) approach: stages are added one at a time and gated behind branch protection rules rather than activated all at once. This minimises disruption to the current development workflow while progressively hardening the pipeline.

**Justification:**
- Upgrade urgency is **medium** — no production outage risk, but technical debt accumulates without automated quality gates.
- The tech stack (language, runtime, build tool) is **not fully identified** in the provided context. The plan therefore uses placeholder values (`<TOOL>`) wherever stack-specific tooling must be confirmed before implementation.
- A big-bang activation of all three stages simultaneously (test + lint + SAST) risks blocking the team if any stage produces false positives or misconfigured failures on day one. Incremental activation allows each stage to be tuned before it becomes a hard gate.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Repository audit & pipeline scaffolding — confirm language/runtime, select CI platform, create pipeline config skeleton | Access to repo, CI platform decision | TODO (derive from confirmed option person-days) |
| 2 | Lint stage — integrate linter, define ruleset, add pipeline job, set as non-blocking initially | Phase 1 complete | TODO |
| 3 | Test stage — integrate test runner, configure coverage reporting, add pipeline job, set coverage gate | Phase 1 complete, test suite exists or is created | TODO |
| 4 | SAST stage — integrate SAST tool, baseline scan, triage findings, add pipeline job as non-blocking | Phase 1 complete | TODO |
| 5 | Harden gates — flip all three stages to blocking on `main`/`trunk`, enable branch protection rules, document pipeline | Phases 2–4 tuned and stable | TODO |

> **NOTE:** Effort values are marked TODO because the upgrade option did not supply person-day estimates and the runtime/build tool is unknown. Populate these once Phase 1 audit is complete.

---

## Component Changes

### CI/CD Pipeline Configuration File

- **What changes:** A new pipeline configuration file is created at the repository root (or `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc. — **TODO: confirm CI platform**).
- **Files affected:**
  - `TODO: <pipeline-config-file>` — primary pipeline definition (e.g., `.github/workflows/ci.yml` for GitHub Actions)
  - `TODO: <linter-config-file>` — linter ruleset config (e.g., `.eslintrc`, `.flake8`, `.rubocop.yml`)
  - `TODO: <sast-config-file>` — SAST tool config (e.g., `.semgrep.yml`, `sonar-project.properties`)
  - `TODO: <coverage-config-file>` — coverage thresholds (e.g., `pytest.ini`, `jest.config.js`, `.nycrc`)

### Lint Stage

- **What changes:** A dedicated lint job is added to the pipeline. The linter is configured with a project-specific ruleset. Initially runs in warn-only mode; promoted to blocking in Phase 5.
- **APIs/commands modified:** `TODO: <lint-command>` (e.g., `npm run lint`, `flake8 .`, `rubocop`)
- **Files affected:** `TODO: <linter-config-file>`

### Test Stage

- **What changes:** A dedicated test job is added to the pipeline. The test runner executes the full test suite and generates a coverage report. A minimum coverage threshold is enforced as a gate.
- **APIs/commands modified:** `TODO: <test-command>` (e.g., `pytest`, `npm test`, `go test ./...`)
- **Files affected:** `TODO: <test-runner-config-file>`

### SAST Stage

- **What changes:** A dedicated SAST job is added to the pipeline. The tool scans source code for known vulnerability patterns. An initial baseline is established to suppress pre-existing findings; only new findings block the pipeline.
- **APIs/commands modified:** `TODO: <sast-command>` (e.g., `semgrep --config=auto`, `trivy fs .`, `bandit -r .`)
- **Files affected:** `TODO: <sast-config-file>`, `TODO: <sast-baseline-file>`

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| CI platform runner/agent | TODO | TODO | TODO | Confirm platform (GitHub Actions, GitLab CI, Jenkins, etc.) |
| Linter | TODO | TODO | TODO | Select tool matching confirmed language |
| Test runner | TODO | TODO | TODO | Select tool matching confirmed language/framework |
| Coverage reporter | TODO | TODO | TODO | Must integrate with CI platform for PR annotations |
| SAST tool | TODO | TODO | TODO | Prefer open-source baseline (Semgrep, Bandit, etc.) |

> **NOTE:** All version numbers are marked TODO because the tech analysis did not identify the language, runtime, or build tool. These must be resolved during Phase 1 before any tooling is pinned.

---

## Infrastructure Changes

- **CI Platform:** TODO — confirm whether GitHub Actions, GitLab CI/CD, Jenkins, CircleCI, or other is in use or to be adopted.
- **Secrets/Credentials:** TODO — SAST tools may require API tokens (e.g., SonarCloud token, Snyk token). Confirm secret storage mechanism (GitHub Secrets, Vault, etc.).
- **Docker base image:** TODO — if pipeline jobs run in containers, a base image must be selected and pinned. Not derivable from current context.
- **Kubernetes manifests:** N/A — not applicable to this task (pipeline runs in CI, not in-cluster).
- **IaC updates:** TODO — if the CI platform itself is provisioned via IaC (e.g., Terraform for self-hosted runners), those resources must be identified.
- **Branch protection rules:** Must be configured on `main`/`trunk` to require all three pipeline stages to pass before merge. This is a repository settings change, not a code change.
- **Artifact/report storage:** TODO — coverage reports and SAST results should be stored as pipeline artifacts for auditability. Confirm artifact retention policy.

---

## Rollback Strategy

Each phase is independently reversible because pipeline stages are additive and gated.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** (Scaffolding) | Delete the pipeline config file and revert the commit. No branch protection rules are active yet; no impact to developers. |
| **Phase 2** (Lint) | Remove or comment out the lint job from the pipeline config. If branch protection was not yet enabled for this stage, no PRs are blocked. |
| **Phase 3** (Test) | Remove or comment out the test job from the pipeline config. Revert any coverage threshold config changes. |
| **Phase 4** (SAST) | Remove or comment out the SAST job from the pipeline config. Delete the SAST baseline file if created. No security findings are surfaced to developers. |
| **Phase 5** (Harden gates) | Disable branch protection rules for the affected stages via repository settings. Pipeline jobs continue to run but no longer block merges. This restores the pre-Phase-5 state without removing any pipeline code. |

> **Key principle:** Stages are never removed from the pipeline config during rollback unless the entire phase is being abandoned. Prefer disabling the gate (non-blocking) over deleting the job, to preserve observability.

---

## Testing Strategy

The pipeline itself must be tested before it gates production work.

### Unit
- **What:** Validate individual pipeline job scripts and linter/SAST config files in isolation.
- **Tool:** TODO (depends on CI platform — e.g., `act` for local GitHub Actions testing, `gitlab-runner exec` for GitLab).
- **Target:** All pipeline job scripts execute without syntax errors on a clean checkout.

### Integration
- **What:** Run the full pipeline on a feature branch with known-good code (all stages should pass) and known-bad code (lint errors, failing tests, SAST findings — each stage should fail independently).
- **Tool:** CI platform's own pipeline execution on a test branch.
- **Gate:** All three stages must correctly pass/fail on the respective test inputs before Phase 5 hardening.

### Regression
- **What:** Ensure the pipeline does not produce false positives on the existing codebase after baseline suppression is applied.
- **Tool:** Run pipeline on `main`/`trunk` HEAD before enabling branch protection.
- **Gate:** Zero unexpected blocking failures on the current codebase.

### Performance
- **What:** Measure total pipeline wall-clock time. Target: pipeline completes within a developer-acceptable window.
- **Tool:** CI platform's built-in job timing metrics.
- **Target:** TODO — establish baseline in Phase 1; set a budget (e.g., < 10 minutes total) appropriate to the team's workflow.

### CI Gates (Phase 5 enforcement)
- Lint stage: **blocking** on all PRs targeting `main`/`trunk`.
- Test stage: **blocking** on all PRs targeting `main`/`trunk`; coverage must meet threshold (TODO: set threshold in Phase 3).
- SAST stage: **blocking** on new findings only (baseline suppresses pre-existing issues).

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Repo audit complete, CI platform confirmed, stack identified | Phase 1 | TODO | TODO |
| Pipeline skeleton merged to `main` | Phase 1 | TODO | TODO |
| Lint stage live (non-blocking) | Phase 2 | TODO | TODO |
| Test stage live (non-blocking), coverage reporting active | Phase 3 | TODO | TODO |
| SAST stage live (non-blocking), baseline established | Phase 4 | TODO | TODO |
| All stages hardened as blocking gates, branch protection enabled | Phase 5 | TODO | TODO |
| Pipeline documentation published | Phase 5 | TODO | TODO |

> **NOTE:** All dates and owners are marked TODO. Populate after Phase 1 audit confirms the stack and the team assigns ownership. Effort estimates from the upgrade option were not provided; derive them from Phase 1 findings.