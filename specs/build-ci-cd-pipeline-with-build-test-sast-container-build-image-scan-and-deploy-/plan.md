# PLAN: CI/CD Pipeline Implementation

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental Stage Rollout**

Since this task introduces a net-new CI/CD pipeline rather than migrating existing infrastructure, a **staged incremental rollout** is the appropriate strategy. Each pipeline stage (build → test → SAST → container build → image scan → deploy) is introduced and validated independently before the next stage is activated. This approach minimizes disruption to any existing ad-hoc build or deployment processes and allows each stage to be verified in isolation before the full pipeline is enforced as a merge gate.

**Justification:**
- Upgrade urgency is **medium** — no emergency forcing a big-bang cutover.
- Language/runtime/build tool are currently **unknown** (see TODOs below), meaning some stages require discovery before implementation.
- Incremental rollout allows the team to validate tooling choices at each stage without blocking development work.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Discovery & scaffolding — identify language, runtime, build tool; select CI platform; create pipeline skeleton | Access to repository and existing build scripts | 2 person-days |
| 2 | Build & Test stages — implement compile/build step and automated test execution | Phase 1 complete; test suite exists or is created | 2 person-days |
| 3 | SAST stage — integrate static analysis security testing tool into pipeline | Phase 2 complete; SAST tool selected and licensed | 1 person-day |
| 4 | Container build stage — write or validate `Dockerfile`; integrate container image build step | Phase 2 complete; container registry access provisioned | 1 person-day |
| 5 | Image scan stage — integrate container image vulnerability scanner | Phase 4 complete; scanner tool selected | 1 person-day |
| 6 | Deploy stage — implement environment promotion (e.g., staging → production) with approval gates | Phases 2–5 complete; target environment access provisioned | 2 person-days |
| 7 | Hardening & documentation — enforce pipeline as merge gate, set failure thresholds, document runbook | All prior phases complete | 1 person-day |

**Total estimated effort: ~10 person-days** (derived from moderate upgrade option)

---

## Component Changes

### CI/CD Pipeline Definition File

- **What changes:** A pipeline definition file is created from scratch as the central artifact of this effort.
- **Files affected:**
  - TODO: Exact filename depends on CI platform selected (e.g., `.github/workflows/pipeline.yml` for GitHub Actions, `.gitlab-ci.yml` for GitLab CI, `Jenkinsfile` for Jenkins, `azure-pipelines.yml` for Azure DevOps).
- **Structure:** The file will define the following named stages/jobs:
  1. `build` — compiles or packages the application
  2. `test` — executes unit and integration tests, publishes results
  3. `sast` — runs static analysis, publishes findings, optionally fails on high/critical severity
  4. `container-build` — builds the Docker image, tags with commit SHA and branch
  5. `image-scan` — scans the built image for CVEs, fails on configurable severity threshold
  6. `deploy` — deploys to target environment(s) with optional manual approval gate

### Dockerfile

- **What changes:** A `Dockerfile` must exist and be validated (or created) to support the container build stage.
- **Files affected:** `Dockerfile` at repository root (TODO: confirm location)
- **Key concerns:** Multi-stage build recommended to minimize final image size and attack surface; base image must be pinned to a specific digest or version tag.

### Environment / Secrets Configuration

- **What changes:** Secrets (registry credentials, deployment tokens, SAST license keys) must be registered in the CI platform's secret store.
- **Files affected:** CI platform secret/variable configuration (not stored in repository).
- **Config keys to define:**
  - `REGISTRY_URL` — container registry endpoint
  - `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` (or equivalent OIDC/workload identity)
  - `DEPLOY_TOKEN` or equivalent — credential for deployment target
  - `SAST_TOKEN` — if commercial SAST tool requires license key (TODO: confirm tool)

### Branch Protection / Merge Gate Rules

- **What changes:** Repository branch protection rules updated to require pipeline passage before merge to default branch.
- **Files affected:** Repository settings (GitHub branch protection, GitLab protected branches, etc.) — TODO: confirm platform.

---

## Dependency Upgrade Plan

> **Note:** Language, runtime, and build tool are listed as **unknown** in the tech analysis. The table below lists the pipeline tooling dependencies that must be selected and pinned. Versions marked TODO must be confirmed during Phase 1 discovery.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| CI Platform (e.g., GitHub Actions, GitLab CI) | TODO — unknown/none | TODO | N/A — net new | Select platform in Phase 1; pin runner versions |
| SAST Tool (e.g., Semgrep, Bandit, SonarQube, Checkmarx) | TODO — unknown/none | TODO | N/A — net new | Select based on language identified in Phase 1 |
| Container Image Scanner (e.g., Trivy, Grype, Snyk) | TODO — unknown/none | TODO | N/A — net new | Prefer open-source (Trivy/Grype) unless enterprise scanner already licensed |
| Docker / container build tool | TODO | TODO | N/A | Confirm Docker daemon availability on CI runner; consider Buildah/Kaniko for rootless builds |
| Container Registry (e.g., ECR, GCR, GHCR, Docker Hub) | TODO — unknown/none | TODO | N/A — net new | Provision in Phase 1; configure OIDC auth where possible |

---

## Infrastructure Changes

### CI Runner / Agent

- TODO: Confirm whether self-hosted runners or cloud-hosted runners will be used.
- TODO: If self-hosted, confirm runner OS, available resources, and Docker daemon access.
- Runners must have network access to: source repository, container registry, SAST tool endpoint, and deployment target.

### Container Registry

- TODO: Registry platform not specified. Must be provisioned before Phase 4.
- Image naming convention to establish: `<registry>/<org>/<app>:<git-sha>` and `:<branch>-latest`.

### Deployment Target

- TODO: Target environment (Kubernetes, VM, PaaS, serverless) not specified in context.
- If Kubernetes: `kubectl` or Helm must be available on the deploy runner; kubeconfig must be injected via secret.
- If cloud PaaS: platform CLI must be installed on runner.

### Dockerfile / Base Image

- TODO: Base image not yet determined (depends on language/runtime discovered in Phase 1).
- Base image must be pinned to a specific version tag (not `latest`).
- Multi-stage build strongly recommended.

### IaC

- TODO: No IaC context provided. If registry or runner infrastructure requires provisioning, IaC templates (Terraform, Pulumi, CloudFormation) should be created — scope TBD after Phase 1.

---

## Rollback Strategy

Each phase produces an independently reversible artifact.

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 — Scaffolding | Delete or disable the pipeline definition file; no production impact. |
| Phase 2 — Build & Test | Remove or comment out `build` and `test` jobs from pipeline file; revert to manual build process. |
| Phase 3 — SAST | Disable SAST job in pipeline config or set `allow_failure: true` to make it non-blocking; revoke SAST tool credentials. |
| Phase 4 — Container Build | Disable `container-build` job; revert to prior image build process (if any). Registry images pushed during testing can be deleted manually. |
| Phase 5 — Image Scan | Set image scan job to `allow_failure: true` or remove it; does not affect deployed artifacts. |
| Phase 6 — Deploy | Disable `deploy` job; revert to prior manual deployment process. If a bad deployment occurs, re-run pipeline against previous known-good commit SHA or execute manual rollback procedure on target environment (TODO: define per environment). |
| Phase 7 — Merge Gate | Remove branch protection rule requiring pipeline passage; pipeline continues to run but is no longer a hard gate. |

**General principle:** The pipeline definition file is version-controlled; any phase can be rolled back via `git revert` of the relevant commit.

---

## Testing Strategy

### Pipeline Self-Testing

The pipeline itself must be validated at each phase before being enforced as a merge gate.

| Layer | What is Tested | Tools | Gate |
|-------|---------------|-------|------|
| **Unit** | Application unit tests (language-specific) | TODO — depends on runtime identified in Phase 1 | Must pass; fail pipeline on any test failure |
| **Integration** | Application integration tests (if present) | TODO — depends on runtime | Must pass; fail pipeline on any test failure |
| **SAST / Security** | Static code analysis for vulnerabilities | TODO — tool selected in Phase 3 | Fail pipeline on `HIGH` or `CRITICAL` findings (configurable threshold) |
| **Image Vulnerability Scan** | CVE scan of built container image | TODO — tool selected in Phase 5 (e.g., Trivy, Grype) | Fail pipeline on `HIGH` or `CRITICAL` CVEs (configurable threshold) |
| **Pipeline Lint / Validation** | Syntax and logic validation of pipeline definition file | CI platform native linter (e.g., `actionlint` for GitHub Actions, `gitlab-ci-lint` for GitLab) | Run on every PR; fail on syntax errors |
| **Smoke / Regression** | Post-deploy smoke test confirming application is reachable and healthy | TODO — depends on deployment target; curl/wget health check endpoint as minimum | Run after deploy stage; fail and trigger rollback on failure |

### Coverage Targets

- TODO: Specific coverage percentage targets cannot be set until language and existing test suite are known. Recommend establishing a baseline in Phase 2 and enforcing a minimum threshold (e.g., 80% line coverage) from Phase 7 onward.

### CI Gates (Summary)

- All stages must pass before merge to default branch (enforced from Phase 7).
- SAST and image scan severity thresholds must be explicitly configured — do not leave as "warn only" in production.
- Test results and scan reports must be published as pipeline artifacts for audit purposes.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Language, runtime, build tool confirmed; CI platform selected; pipeline skeleton committed | Phase 1 | End of Week 1 | TODO |
| Build and test stages live and passing on all PRs | Phase 2 | End of Week 1 | TODO |
| SAST stage integrated and non-blocking (warn mode) | Phase 3 | Mid Week 2 | TODO |
| Container build stage live; images pushed to registry on main branch | Phase 4 | Mid Week 2 | TODO |
| Image scan stage integrated and non-blocking (warn mode) | Phase 5 | End of Week 2 | TODO |
| Deploy stage live for staging environment; production deploy with approval gate | Phase 6 | End of Week 3 | TODO |
| Pipeline enforced as merge gate; SAST and scan thresholds set to blocking; runbook published | Phase 7 | End of Week 3 | TODO |

> **Note:** Timeline assumes ~10 person-days of effort distributed across approximately 3 calendar weeks with one engineer. Adjust based on actual team availability and Phase 1 discovery findings.