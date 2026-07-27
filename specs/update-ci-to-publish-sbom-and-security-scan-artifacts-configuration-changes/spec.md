## Summary
This spec covers updating the project’s CI configuration to publish Software Bill of Materials (SBOM) and security scan artifacts as build outputs, so they are consistently generated, retained, and accessible for audit and downstream consumption. The expected outcome is that every CI run (per defined triggers) produces and uploads SBOM and security scan artifacts without changing application/runtime code.

## Motivation
- **Security posture improvement (urgency: medium):** The tech analysis rates the upgrade urgency as **medium**, and this effort directly supports security hygiene by making SBOMs and scan reports available as first-class CI outputs.
- **Compliance/audit readiness:** Publishing SBOM and security scan artifacts enables traceability and evidence collection for internal audits and external compliance requirements.
- **Operational consistency:** Standardized artifact publishing reduces ad-hoc/manual security reporting and improves repeatability across branches/releases.

*EOL dates, CVEs, performance issues:* **N/A — not applicable to this task** (not provided in tech analysis; task scope is CI artifact publication only).

## Current State
- CI currently does **not** publish SBOM artifacts. (**TODO:** confirm whether SBOM generation exists but is not uploaded, or is absent entirely.)
- CI currently does **not** publish security scan artifacts. (**TODO:** identify which scanners, if any, are currently executed and what outputs they produce.)
- Language/runtime/build tool are **unknown** per tech analysis and are not required for artifact publication spec at this level.

Interfaces, APIs, data models, and key behaviors affected:
- **CI pipeline artifact interface:** The CI system’s mechanism for declaring build outputs/artifacts that can be downloaded after a run.
- **CI run triggers and retention behavior:** Which branches/tags/PRs produce artifacts and how long artifacts are retained. (**TODO:** document current triggers and retention defaults.)

## Proposed Changes
### Scope
Configuration-only CI changes to ensure SBOM and security scan outputs are uploaded as artifacts for relevant CI runs.

### Component change summary

| Component | Before | After | Breaking? (Y/N) |
|---|---|---:|:---:|
| CI pipeline artifact publishing | SBOM artifacts not published (**TODO:** confirm) | SBOM artifacts are published for applicable CI runs | N |
| CI pipeline artifact publishing | Security scan artifacts not published (**TODO:** confirm) | Security scan artifacts are published for applicable CI runs | N |
| CI reporting/outputs | No standardized naming/structure for security evidence (**TODO:** confirm) | Standardized artifact naming and predictable structure for SBOM + scan outputs (**TODO:** define naming convention) | N |

### What is added
- CI configuration that uploads:
  - **SBOM artifact(s)** (format and tool output **TODO**).
  - **Security scan artifact(s)** (scanner(s), formats **TODO**).
- Artifact metadata expectations:
  - Consistent artifact names (e.g., include workflow/job identifier and target environment) (**TODO**).
  - Retention period defined or explicitly accepted as CI default (**TODO**).

### What is removed
- N/A — not applicable to this task (no removals required by scope).

## Compatibility & Breaking Changes
No breaking changes are expected because the changes are limited to CI configuration and add artifacts rather than changing runtime behavior.

| Breaking Change | Impacted Callers/Users | Migration Path |
|---|---|---|
| N/A | N/A | N/A |

## Acceptance Criteria
1. **Given** a CI run is triggered under the project’s standard CI conditions (**TODO:** enumerate triggers: PR, main branch, tag, release), **when** the pipeline completes successfully, **then** an SBOM artifact is uploaded and is downloadable from the CI run results.
2. **Given** a CI run is triggered under the project’s standard CI conditions (**TODO:** enumerate triggers), **when** the pipeline completes successfully, **then** a security scan artifact is uploaded and is downloadable from the CI run results.
3. **Given** an SBOM artifact is uploaded, **when** the artifact is inspected, **then** it contains at least one SBOM document file in the expected format (**TODO:** define expected format(s), e.g., SPDX/CycloneDX) and is non-empty.
4. **Given** a security scan artifact is uploaded, **when** the artifact is inspected, **then** it contains at least one scan report file in the expected format (**TODO:** define expected report format(s), e.g., SARIF/JSON) and is non-empty.
5. **Given** artifact naming rules are defined (**TODO**), **when** a CI run publishes artifacts, **then** artifact names match the defined convention and do not collide within a single run.
6. **Given** artifact retention requirements are defined (**TODO**), **when** artifacts are uploaded, **then** their retention period matches the defined requirement or the CI system’s retention default is explicitly documented and approved (**TODO: choose**).

## Open Questions

| # | Question | Owner (or TODO) | Due Date (or TODO) |
|---:|---|---|---|
| 1 | Which CI platform/workflow system is in use (e.g., GitHub Actions, GitLab CI, etc.) and what is the current artifact upload mechanism? | TODO | TODO |
| 2 | What SBOM standard and output format are required (e.g., SPDX, CycloneDX), and is there an existing SBOM generator already used? | TODO | TODO |
| 3 | Which security scanners are in scope (dependency, SAST, container, IaC, secrets), and which output formats are required (e.g., SARIF)? | TODO | TODO |
| 4 | Which CI triggers must publish artifacts (PRs, default branch, tags/releases), and should behavior differ by trigger? | TODO | TODO |
| 5 | What artifact naming convention and directory/structure expectations should be enforced for downstream automation? | TODO | TODO |
| 6 | What artifact retention period is required for compliance/audit needs? | TODO | TODO |
| 7 | Should the CI run fail based on scan findings severity/thresholds, or is this task strictly artifact publication with no gating? | TODO | TODO |