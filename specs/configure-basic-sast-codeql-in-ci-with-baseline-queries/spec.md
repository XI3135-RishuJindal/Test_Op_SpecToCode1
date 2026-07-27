## Summary
This spec covers adding basic Static Application Security Testing (SAST) using GitHub CodeQL to the CI pipeline with baseline (default) queries, with the expected outcome that CI routinely performs CodeQL analysis and reports findings in a consistent, repeatable way without expanding scope into broader security tooling or remediation work.

## Motivation
- **Business driver:** Establish a minimum-security baseline by enabling automated SAST checks as part of CI.
- **Technical driver:** Add standardized CodeQL scanning with baseline queries to surface common vulnerability patterns early in development.
- **Upgrade urgency:** **medium** (per provided tech analysis).
- **EOL dates, CVEs, performance issues, compliance requirements:** **N/A — not applicable to this task** (not provided in the tech analysis).

## Current State
- CI security scanning: **TODO — unknown whether any SAST currently exists** (not provided).
- CodeQL configuration: **Not present / TODO — to be confirmed** (not provided).
- Languages/runtimes/build tooling: **unknown** (per tech analysis), so existing CodeQL language coverage is **TODO**.
- Existing interfaces/APIs/data models/classes/config keys/schema elements impacted: **N/A — not applicable to this task** (no code context provided, and CodeQL setup is CI-focused).

## Proposed Changes
Enable GitHub CodeQL analysis in CI with baseline (default) query suites appropriate for the repository’s language(s), and publish results in the standard GitHub security/code scanning surface.

| Component | Before | After | Breaking? (Y/N) |
|---|---|---:|:---:|
| CI pipeline (security stage) | No CodeQL SAST (TODO — confirm) | CodeQL SAST runs in CI with baseline queries | N |
| Security reporting | No CodeQL code scanning alerts (TODO — confirm) | CodeQL results available as code scanning findings in GitHub | N |
| Repository configuration | No CodeQL configuration (TODO — confirm) | Repository has a declared CodeQL configuration aligned to baseline queries | N |
| Language coverage | Unknown | CodeQL enabled for detected/selected language(s) | N |

## Compatibility & Breaking Changes
No intended breaking changes to runtime behavior or public APIs.

| Breaking change | Impacted callers/users | Migration path |
|---|---|---|
| N/A | N/A | N/A |

## Acceptance Criteria
1. **Given** a pull request is opened against the default branch, **when** CI runs, **then** a CodeQL analysis job executes as part of the workflow and completes with a recorded success/failure status visible in the PR checks.
2. **Given** CodeQL analysis completes in CI, **when** results are uploaded, **then** the repository’s code scanning (security) view shows a new analysis run associated with the commit that triggered CI.
3. **Given** the repository language(s) are determined (currently **TODO**), **when** CodeQL is configured for baseline queries, **then** the CodeQL run indicates analysis was performed for those language(s) (verifiable via the analysis run metadata in GitHub).
4. **Given** CodeQL is configured with baseline (default) query suites, **when** CI runs on the default branch, **then** the executed query set corresponds to the baseline suite for the configured language(s) (verifiable via CodeQL run metadata/log summary in GitHub).
5. **Given** CodeQL identifies at least one finding (if present), **when** the analysis is published, **then** findings appear as code scanning alerts tied to the correct repository and commit (verifiable via GitHub Security/Code scanning UI).

## Open Questions
| # | Question | Owner (or TODO) | Due Date (or TODO) |
|---:|---|---|---|
| 1 | What programming language(s) should CodeQL be configured to analyze? (Tech analysis lists language as unknown.) | TODO | TODO |
| 2 | What CI system is currently in use (e.g., GitHub Actions or another provider), and where should CodeQL run? | TODO | TODO |
| 3 | Is there an existing CI workflow structure or required gating policy (e.g., fail PR on CodeQL findings vs. report-only)? | TODO | TODO |
| 4 | Should CodeQL run on PRs only, default branch only, or both? | TODO | TODO |
| 5 | Are there repository-specific exclusions needed (generated code, vendor code), and what is the policy for exclusions? | TODO | TODO |
| 6 | Are there any performance/time budget constraints for CI that CodeQL must meet? | TODO | TODO |
| 7 | Should the configuration include only baseline/default queries, or also include any organization-mandated query packs? (Task says baseline; confirm no additional requirements.) | TODO | TODO |