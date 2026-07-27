## Overview

**Migration strategy:** feature-flag gated (CI-only)

This change is limited to CI configuration and artifact publishing; it can be introduced behind conditional steps (e.g., default-off env var) and then enabled per-branch or per-workflow to reduce risk.

**Justification (risk/effort):** TODO — upgrade option “conservative” risk score and person-days estimate were not provided in the input. Strategy is chosen to minimize blast radius given unknown stack/runtime/build tooling.

## Phases

> Effort must derive from the upgrade option’s person-days estimate, but that estimate is not provided. All effort values are **TODO**.

| Phase | Description | Dependencies | Estimated Effort |
|---|---|---|---|
| 1 | Discover current CI system + artifact publishing mechanism; decide SBOM format and security scan outputs to publish | Access to CI config repo/settings (TODO) | TODO (person-days) |
| 2 | Implement SBOM generation step(s) and upload as CI artifacts | Phase 1 | TODO (person-days) |
| 3 | Implement security scan step(s) and upload results as CI artifacts | Phase 1 | TODO (person-days) |
| 4 | Add CI gates/retention/metadata and document usage | Phases 2–3 | TODO (person-days) |
| 5 | Rollout (enable on default branch), monitor, and adjust | Phase 4 | TODO (person-days) |

## Component Changes

N/A — not applicable to this task (no application/runtime code changes were requested or provided in context).

## Dependency Upgrade Plan

N/A — not applicable to this task.

(Dependency versions and targets were not provided in the tech analysis; additionally this task is CI configuration-only.)

## Infrastructure Changes

### CI/CD pipeline changes (applicable)

**TODO — CI platform is not specified.** Apply the following changes in the repository’s CI configuration (examples depend on platform):

1. **Add SBOM generation job/step**
   - Output: `sbom.*` (format TBD: SPDX JSON, CycloneDX JSON/XML)  
   - Store as build artifact and/or attach to the build summary.
   - Include build metadata in artifact name (commit SHA, workflow run number).

2. **Add security scan job/step**
   - Output: machine-readable results (e.g., `sarif`, `json`) and optional human-readable summary (`txt`/`md`).
   - Publish as CI artifacts.

3. **Artifact publishing**
   - Configure artifact retention policy (days) — **TODO key name varies by CI system**.
   - Ensure artifacts are uploaded even on failure (scan job failures should still publish results).

4. **Branch/PR behavior**
   - Run on PRs and default branch; optionally restrict “full” scans to default branch/nightly.
   - Feature flag via env var, e.g., `PUBLISH_SBOM=true`, `PUBLISH_SECURITY_ARTIFACTS=true` (names TBD).

5. **Permissions / tokens**
   - If publishing to a registry or external system is desired: **TODO** (not requested; do not add without confirmation).
   - If uploading SARIF to a code scanning UI is desired: **TODO** (not requested; clarify target).

### Docker / Kubernetes / IaC

N/A — not applicable to this task (no Docker/K8s/IaC context provided; CI artifact publishing does not require infra changes by default).

## Rollback Strategy

> Each rollback is actionable and independently reversible; scoped to CI configuration only.

### Phase 1 (Discovery)
- No rollback needed (no changes).

### Phase 2 (SBOM generation + artifact upload)
- Revert the CI configuration commit(s) that:
  - add the SBOM generation step/job
  - add the SBOM artifact upload step/job
- Alternatively, disable via feature flag (if implemented): set `PUBLISH_SBOM=false` (exact mechanism **TODO**).

### Phase 3 (Security scan + artifact upload)
- Revert the CI configuration commit(s) that:
  - add the security scan step/job
  - add the scan results artifact upload step/job
- Alternatively, disable via feature flag: `PUBLISH_SECURITY_ARTIFACTS=false` (**TODO**).

### Phase 4 (Gates/retention/metadata)
- Remove/rollback enforcement (e.g., “fail build on high findings”) by reverting those CI config changes while keeping artifact publishing intact.
- Restore previous artifact retention settings by reverting CI config.

### Phase 5 (Rollout)
- If rollout causes CI instability:
  - Disable on default branch by adjusting workflow triggers (platform-specific **TODO**) or toggling feature flags off.
  - Keep changes available on a non-blocking/manual workflow until stabilized.

## Testing Strategy

CI configuration changes should be validated primarily through workflow execution and artifact verification.

### Unit
N/A — not applicable to this task (no application code changes).

### Integration
- Add/execute a CI run on a test branch that:
  - generates SBOM artifact successfully
  - generates security scan artifact successfully
  - uploads both artifacts
- Validate:
  - artifacts exist for successful runs and failed scan runs (if configured to upload “always”)
  - artifact names include commit/run metadata (if implemented)
  - artifacts are in expected formats (SPDX/CycloneDX; SARIF/JSON) — **TODO formats not specified**

### Regression
- Confirm existing pipeline jobs (build/test) still run unchanged and duration impact is acceptable.
- Ensure scan/SBOM steps don’t alter build outputs (read-only behavior).

### Performance
- Track CI duration before/after enabling steps.
- If scan time is excessive, adjust:
  - run scope (PR vs nightly)
  - caching (tool-specific, **TODO**)
  - parallelization (CI-specific, **TODO**)

### Concrete tools / CI gates
- Tools: **TODO — unknown language/build tool/CI platform; cannot name specific generators/scanners from provided context.**
- Gates:
  - “Artifact presence” gate: workflow must upload SBOM + scan outputs (non-empty files).
  - Optional “fail on severity threshold” gate: **TODO**, only if required (not specified).

## Timeline

> Must derive from the upgrade option’s person-days estimate; not provided. Dates/owners are TODO.

| Milestone | Phase | Estimated Completion | Owner (or TODO) |
|---|---|---|---|
| CI discovery complete; decision on SBOM + scan formats | 1 | TODO | TODO |
| SBOM artifacts publishing live (non-blocking) | 2 | TODO | TODO |
| Security scan artifacts publishing live (non-blocking) | 3 | TODO | TODO |
| CI gates/retention/metadata finalized | 4 | TODO | TODO |
| Enabled on default branch + monitored | 5 | TODO | TODO |