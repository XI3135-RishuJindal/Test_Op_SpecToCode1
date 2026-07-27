## Overview

**Migration strategy:** feature-flag gated (non-blocking → blocking)

**Justification:** The upgrade option is **conservative** (details not provided), and the **risk/effort are not quantified** in the provided context. For CI security scanning, a gated rollout reduces risk of disrupting delivery by:
- Starting in **report-only** mode (CodeQL runs but does not fail builds).
- Moving to **enforced** mode once findings/noise are understood.

**TODO:** Provide the conservative option’s **risk score** and **person-days estimate** so rollout gates and phase sizing can be tied to it.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|---|---|---|---|
| 1 | Add CodeQL workflow in CI (default query suite, reporting only) | GitHub Actions enabled (TODO confirm), repository permissions for code scanning | TODO — requires person-days from upgrade option |
| 2 | Tune baseline (suppress noise, adjust query packs/config, document triage) | Phase 1, security/code owners available for triage | TODO — requires person-days from upgrade option |
| 3 | Enforce gates (fail on high severity or new findings, PR checks required) | Phase 2, agreed policy on severity/threshold | TODO — requires person-days from upgrade option |

---

## Component Changes

### CI / GitHub Actions
**Structural change:** Add a CodeQL scanning workflow file.

- **Files added/modified:**
  - `/.github/workflows/codeql.yml` (new) — CodeQL initialization, build (autobuild or explicit), and analysis steps.
  - (Optional) `/.github/codeql/codeql-config.yml` (new) — if custom query suites, paths, or packs are needed.

**APIs modified:** N/A (CI configuration only).

**Notes / TODOs (due to unknown stack):**
- **Language** is unknown; CodeQL needs one of the supported languages specified. Use CodeQL’s language autodetection initially, then pin explicitly once confirmed.
- **Build tool/runtime** unknown; decide between:
  - `github/codeql-action/autobuild` (preferred first pass), or
  - explicit build commands (TODO once build tool is known).

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

*(CodeQL uses GitHub Actions; action versions are configuration, not runtime dependencies. No dependency versions were provided in the tech analysis, so none can be specified here.)*

---

## Infrastructure Changes

N/A — not applicable to this task.

**TODO (only if applicable in this repo):**
- If CI is not GitHub Actions (e.g., Jenkins/CircleCI), identify the CI system and map CodeQL execution accordingly.
- If containerized builds are required, determine Docker base image requirements for CodeQL runs.

---

## Rollback Strategy

### Phase 1 rollback
1. Revert commit adding `/.github/workflows/codeql.yml`.
2. (If added) remove `/.github/codeql/codeql-config.yml`.
3. Verify CI returns to prior green state and no “Code scanning” runs are triggered.

### Phase 2 rollback
1. Revert changes to CodeQL config (e.g., restore previous `codeql-config.yml`).
2. Remove any added suppressions/filters that caused missed detections (revert to baseline query suite).
3. Confirm CodeQL results return to pre-tuning behavior.

### Phase 3 rollback
1. Remove required status checks for CodeQL in branch protection (TODO: exact repo settings path/automation unknown).
2. Update workflow to “report-only” (do not fail job) if enforcement was implemented at workflow level.
3. Confirm merges are unblocked and CodeQL still publishes results.

---

## Testing Strategy

**Test pyramid focus for this task:** CI gates and security scan signal quality (not application functional tests).

- **Unit tests:** N/A — CodeQL setup does not add unit-testable code.
- **Integration tests (CI validation):**
  - Ensure the workflow runs on:
    - `pull_request`
    - `push` to default branch
    - (optional) scheduled run for drift detection (TODO confirm desired cadence)
  - CI gate: workflow must complete successfully (in report-only mode for Phase 1).
- **Regression (signal/noise control):**
  - Establish a baseline triage process:
    - Confirm findings are visible in GitHub “Code scanning alerts”.
    - Track false positives and decide whether to adjust query suite or suppress specific paths.
  - Coverage target: N/A — CodeQL coverage is not measured like unit test coverage; instead track **alert volume** and **time-to-triage** (TODO define acceptable thresholds).
- **Performance:**
  - CI gate: CodeQL job time budget (TODO set threshold once first runs are observed).
  - If time is excessive: narrow scope via config (paths) or switch from autobuild to explicit build steps.

**Concrete tools (from context):**
- GitHub CodeQL Action (workflow-based).  
**TODO:** confirm CI platform is GitHub Actions; otherwise replace with appropriate CI integration.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner (or TODO) |
|---|---|---|---|
| CodeQL workflow added, runs in report-only mode | 1 | TODO — needs upgrade option person-days | TODO |
| Baseline tuned and documented triage process in place | 2 | TODO — needs upgrade option person-days | TODO |
| Enforcement enabled (policy-based gating) | 3 | TODO — needs upgrade option person-days | TODO |

**TODO:** Provide the conservative option’s **person-days estimate** so completion estimates can be derived as required.