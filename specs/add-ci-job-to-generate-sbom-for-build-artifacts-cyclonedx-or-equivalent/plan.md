## Overview

**Migration strategy:** feature-flag gated (CI-only, additive)

Because the tech stack (language/runtime/build tool) and CI system are **unknown**, the safest approach is to add an **additive CI job** that can run in a **non-blocking / informational mode** first, then be promoted to a required gate once validated. This minimizes risk while meeting the medium urgency.

**Risk / effort justification:** The upgrade option is **conservative** (details not provided), and no person-day estimate is provided. Given unknowns, we will implement the smallest viable CI addition with a controlled rollout (non-blocking → blocking).

## Phases

> Effort must derive from the upgrade option’s person-days estimate, but **no estimate is provided**. Therefore, effort is marked as **TODO**.

| Phase | Description | Dependencies | Estimated Effort |
|---|---|---|---|
| 1 | Discover CI system + build artifact boundaries; choose SBOM format/tooling approach | Access to repo CI config; build output locations | TODO (upgrade option person-days not provided) |
| 2 | Implement SBOM generation job (non-blocking) + publish SBOM as CI artifact | Phase 1 | TODO (upgrade option person-days not provided) |
| 3 | Wire SBOM to release/build outputs; enforce naming/versioning; optionally sign | Phase 2 | TODO (upgrade option person-days not provided) |
| 4 | Promote job to required (blocking) gate once stable | Phase 3 | TODO (upgrade option person-days not provided) |

## Component Changes

N/A — not applicable to this task (no application code changes required; this is CI-focused).  
**TODO:** Once CI system is identified, list exact files (e.g., `.github/workflows/*.yml`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`) and keys modified.

## Dependency Upgrade Plan

N/A — not applicable to this task

- No dependency versions were provided in the tech analysis summary.
- SBOM tooling choice and versioning are **unknown** until the build tool/ecosystem is identified.

**TODO:** After identifying build tool, select one:
- **CycloneDX** generator for the ecosystem (e.g., Maven/Gradle/npm/pip/dotnet/go) or an equivalent SBOM generator
- Record exact current/target versions (if any) from repo lockfiles and tool versions used in CI

## Infrastructure Changes

N/A — not applicable to this task

- No Docker/Kubernetes/IaC context is provided.
- **TODO:** If CI runs in container images, we may need to add a container image that includes the SBOM tool, or install it during the job.

## Rollback Strategy

Rollback is strictly limited to CI configuration and is independently reversible per phase.

### Phase 1 rollback
1. Revert any exploratory CI config commits (e.g., temporary debug steps).
2. Remove any temporary CI variables created for discovery.

### Phase 2 rollback
1. Remove/disable the SBOM generation job from CI configuration.
2. Remove SBOM artifact upload step(s).
3. Ensure pipeline returns to prior behavior (no new required checks).

### Phase 3 rollback
1. Revert changes that attach SBOM to release/build outputs.
2. Remove any SBOM naming/versioning enforcement steps.
3. If signing was added, remove signing step and any related secrets from CI.

### Phase 4 rollback
1. Change the SBOM job back to non-blocking (allow-failure / informational).
2. Remove branch protection / required status check enforcement (if applicable in the CI/VCS settings).
3. Confirm merges/builds proceed as before.

## Testing Strategy

N/A — not applicable to this task (no product code changes)

CI validation for this task will be done via pipeline checks:

- **Unit:** N/A
- **Integration:** Validate SBOM job can parse dependency graph and completes successfully on main branch.
- **Regression:** Ensure existing build/test jobs are unaffected (no changes to build outputs or ordering unless explicitly required).
- **Performance:** Ensure SBOM generation time remains within acceptable CI duration. **TODO:** define threshold once baseline is measured.

**Concrete CI gates (TODO until CI/tooling known):**
- Gate 1 (initial): SBOM job runs and uploads an artifact; failures do **not** fail pipeline.
- Gate 2 (after stabilization): SBOM job becomes required for merges/releases.
- Verify artifact presence and non-empty output (e.g., `sbom.json` / `sbom.xml`) via a lightweight validation step.

## Timeline

> Must derive from upgrade option effort estimate; none is provided. Timeline cannot be computed without it.

| Milestone | Phase | Estimated Completion | Owner (or TODO) |
|---|---|---|---|
| CI system + build tool identified; SBOM approach selected | 1 | TODO (requires person-days estimate) | TODO |
| SBOM job implemented and publishing artifacts (non-blocking) | 2 | TODO (requires person-days estimate) | TODO |
| SBOM attached to build/release artifacts with consistent naming/versioning | 3 | TODO (requires person-days estimate) | TODO |
| SBOM job promoted to required gate | 4 | TODO (requires person-days estimate) | TODO |