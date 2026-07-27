## Overview

**Migration strategy:** feature-flag gated (CI-only, non-invasive rollout)

**Justification (risk/effort):** The provided upgrade option is **Option ID: conservative (details not provided)**, and no risk score or person-day estimate is included. Given **medium urgency** and the fact that secret scanning can initially be noisy, we will gate enforcement in CI:
1) start in **report-only** mode (non-blocking), then  
2) optionally switch to **blocking** once false positives are addressed.

**TODO:** Confirm the upgrade option’s **risk score** and **person-days** estimate so this plan can align phase effort and timeline to the required source.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|---|---|---:|---:|
| 1 | Add gitleaks CI job in report-only mode; publish actionable artifacts/log annotations | CI system (TODO: identify GitHub Actions/GitLab/Jenkins/etc.) | TODO — upgrade option person-days not provided |
| 2 | Tune rules/allowlist; reduce false positives; establish baseline | Phase 1 | TODO — upgrade option person-days not provided |
| 3 | Enforce blocking on new findings (optional gate); document developer workflow | Phase 2 | TODO — upgrade option person-days not provided |

---

## Component Changes

### CI Pipeline Configuration
**Structural change:** introduce a new CI step/job for secret scanning using **gitleaks**, producing an artifact report and (if supported) inline annotations.

- **Files affected:**  
  - TODO — CI is not specified in context. Add/update the relevant pipeline file once identified, e.g.:
    - `.github/workflows/<workflow>.yml` (GitHub Actions) **or**
    - `.gitlab-ci.yml` (GitLab CI) **or**
    - `Jenkinsfile` (Jenkins) **or**
    - other CI config (TODO)

- **APIs modified:** N/A — no application/runtime APIs are involved in this task.

### Repository Configuration (gitleaks)
**Structural change:** add repository-level gitleaks configuration to define rules and allowlists.

- **Files affected:**
  - `gitleaks.toml` (or `.gitleaks.toml`) — TODO: confirm preferred filename/location
  - `.gitleaksignore` — optional allowlist for known non-secret test data (only if needed)

**Notes on actionable reporting:**
- Configure the CI job to produce at least:
  - a human-readable log output for immediate triage
  - a machine-readable report artifact (e.g., JSON/SARIF) for review and retention
- **TODO:** Confirm which report formats are supported/desired by the chosen CI provider (e.g., SARIF upload is native to GitHub Advanced Security; otherwise store as artifact).

---

## Dependency Upgrade Plan

N/A — not applicable to this task (no dependency versions were provided in the tech analysis, and this task is CI tooling-focused).

**TODO:** If gitleaks must be pinned (e.g., container tag or binary version), capture:
- current version (if any)
- target version  
from approved internal standards/source of truth. This plan cannot invent versions.

---

## Infrastructure Changes

N/A — not applicable to this task.

**TODO:** If CI runners use Docker images, we may need one of:
- a gitleaks container image reference, or
- install step in the runner image  
But no Docker/Kubernetes/IaC context is provided, so this remains unspecified.

---

## Rollback Strategy

### Phase 1 rollback (report-only CI job)
1. Revert the commit that adds the gitleaks CI job configuration (TODO: CI file path).
2. Remove any newly added gitleaks config files (`gitleaks.toml`, `.gitleaksignore`) if they are not used elsewhere.
3. Verify CI pipeline returns to prior green state without the gitleaks job.

### Phase 2 rollback (tuning/baseline)
1. Revert changes to `gitleaks.toml` / `.gitleaksignore` that introduced allowlists or rule modifications.
2. Keep Phase 1 job in report-only mode to continue visibility while tuning is redone.

### Phase 3 rollback (blocking enforcement)
1. Change the CI job back to non-blocking behavior:
   - set `continue-on-error: true` (GitHub Actions) **or**
   - `allow_failure: true` (GitLab) **or**
   - equivalent in the CI system (TODO)
2. Re-run pipeline to confirm gitleaks findings do not fail the build while still producing a report.

Each rollback step is independently reversible by re-applying the reverted commit.

---

## Testing Strategy

N/A — not applicable to this task (no application code changes).

**CI gates for this task (tooling validation):**
- Validate the gitleaks job runs on:
  - pull requests / merge requests
  - default branch pushes
- Validate reporting outputs:
  - report artifact is uploaded and accessible
  - logs include file path + line number + rule ID (as supported by gitleaks output)

**TODO:** Specify concrete tools and thresholds once CI provider is known:
- CI log annotation mechanism (e.g., GitHub Checks annotations)
- artifact retention policy
- whether SARIF is required and how it is consumed

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner (or TODO) |
|---|---|---|---|
| CI gitleaks report-only job merged | 1 | TODO — cannot derive without person-days estimate | TODO |
| Rules tuned; baseline established | 2 | TODO — cannot derive without person-days estimate | TODO |
| Blocking enforcement enabled (optional) | 3 | TODO — cannot derive without person-days estimate | TODO |

**TODO:** Provide the upgrade option’s person-day estimate (and any delivery constraints) so the timeline and phase effort can be populated per requirement.