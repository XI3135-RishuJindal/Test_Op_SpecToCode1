## Summary
This spec defines the changes required to add a Continuous Integration (CI) job that generates a Software Bill of Materials (SBOM) for build artifacts using CycloneDX (or an equivalent SBOM format/tool), producing an SBOM output as part of the CI pipeline.

## Motivation
- **Supply chain security / artifact transparency:** Generating an SBOM for build artifacts improves visibility into included components and supports downstream security review and compliance workflows.
- **Modernization goal alignment:** The stated goal is to add an SBOM-generating CI job.
- **Urgency:** Upgrade urgency is **medium** (per provided tech analysis summary).
- **EOL/CVEs/compliance drivers:** N/A — not applicable to this task (no EOL dates, CVEs, or compliance requirements were provided in the tech analysis).

## Current State
N/A — not applicable to this task.

*(The provided context does not specify the current CI system, build tool, artifact types, existing pipeline stages, or existing security scanning steps. No specific classes, config keys, or schema elements were provided.)*

## Proposed Changes
Add a CI job that, for each build producing artifacts, generates an SBOM representing the contents/dependencies associated with those build artifacts and publishes the SBOM as a CI output (e.g., stored artifact or equivalent CI output mechanism).

**Component Change Table**

| Component | Before | After | Breaking? (Y/N) |
|---|---|---:|---:|
| CI pipeline | No SBOM generation job defined (TODO — confirm) | New CI job generates SBOM for build artifacts (CycloneDX or equivalent) and publishes SBOM output | N |

## Compatibility & Breaking Changes
N/A — not applicable to this task.

*(This change adds a CI job and does not modify runtime behavior or public APIs based on provided context. Any potential downstream expectations—e.g., consumers relying on a fixed set of CI artifacts—are unknown and must be confirmed.)*

## Acceptance Criteria
1. **Given** a CI run is triggered for a change that produces build artifacts, **when** the pipeline completes, **then** an SBOM is generated and is available as a retrievable CI output associated with that run.
2. **Given** the CI pipeline executes the SBOM job, **when** the SBOM is produced, **then** the SBOM output format is CycloneDX **or** another explicitly approved equivalent format (TODO — define which formats are acceptable).
3. **Given** a successful build, **when** the SBOM job finishes, **then** the SBOM generation step reports success in CI (pass/fail status is visible in the CI job results).
4. **Given** SBOM generation fails for any reason, **when** the CI pipeline runs, **then** the CI job is marked failed and the failure is visible in CI logs/results (ensuring the failure is detectable and does not silently pass).

## Open Questions
| # | Question | Owner (or TODO) | Due Date (or TODO) |
|---:|---|---|---|
| 1 | Which CI system is in use (e.g., GitHub Actions, GitLab CI, etc.) and what is the required integration mechanism for publishing the SBOM output? | TODO | TODO |
| 2 | What build artifacts are in scope for SBOM generation (packages, containers, binaries, archives, etc.)? | TODO | TODO |
| 3 | What is the approved SBOM format/tooling choice: CycloneDX specifically, or which “equivalent” formats/tools are acceptable? | TODO | TODO |
| 4 | Where must SBOMs be stored/published (CI artifacts only, release attachments, artifact repository metadata, etc.)? | TODO | TODO |
| 5 | Should SBOM generation run on every commit, only on merges to main, only for releases, or some combination? | TODO | TODO |
| 6 | Are there requirements for SBOM contents (e.g., include transitive dependencies, include build-time dependencies, include license fields)? | TODO | TODO |
| 7 | Are there any downstream consumers (security tooling, compliance checks, deployment gates) that require a specific SBOM filename, naming convention, or location? | TODO | TODO |