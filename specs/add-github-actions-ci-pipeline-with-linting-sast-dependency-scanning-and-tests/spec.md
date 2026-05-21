# Spec: Add GitHub Actions CI Pipeline

## Summary

This spec covers the introduction of a GitHub Actions CI pipeline to the repository. The pipeline will automate linting, static application security testing (SAST), dependency vulnerability scanning, and test execution on every pull request and push to the default branch. The expected outcome is a repeatable, automated quality gate that surfaces code style violations, security issues, vulnerable dependencies, and test failures before changes are merged.

## Motivation

The repository currently has no automated CI pipeline. This creates the following risks and inefficiencies:

- **No automated quality gate:** Code style and correctness issues are caught only through manual review, increasing review burden and inconsistency.
- **Security exposure:** Without SAST and dependency scanning, vulnerable code patterns and known-CVE dependencies can be merged undetected.
- **Compliance risk:** Many organisational and regulatory standards (e.g., SOC 2, ISO 27001) require evidence of automated security scanning in the software delivery process.
- **Upgrade urgency:** Rated **medium** — the absence of CI is an ongoing risk that compounds with each unreviewed merge, but does not represent an immediate production outage.

No specific EOL dates or CVEs are referenced in the provided tech analysis; urgency is driven by the absence of baseline DevSecOps controls.

## Current State

- **CI system:** None. There is no existing pipeline configuration in the repository.
- **Linting:** TODO — no existing linter configuration files or enforced style rules have been identified in the provided context.
- **Testing:** TODO — no existing test runner configuration, test directory structure, or test framework has been identified in the provided context.
- **SAST tooling:** None configured.
- **Dependency scanning:** None configured.
- **Language / Runtime / Build tool:** Not determined from the provided tech analysis (listed as "unknown"). These must be confirmed before tool selection can be finalised (see Open Questions).

Because the language, runtime, and build tool are unknown, specific tool names (e.g., ESLint, Bandit, pip-audit, Trivy) are intentionally left as TODO in this spec and will be resolved in plan.md once the stack is confirmed.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| CI pipeline | None | GitHub Actions workflow triggered on pull requests and pushes to the default branch | N |
| Linting job | None | Automated linter execution; non-zero exit fails the pipeline | N |
| SAST job | None | Automated static analysis security scan; findings above configured severity threshold fail the pipeline | N |
| Dependency scanning job | None | Automated scan of declared dependencies against known vulnerability databases; critical/high findings fail the pipeline | N |
| Test job | None | Automated test suite execution; any test failure fails the pipeline | N |
| Branch protection | TODO — current state unknown | Default branch requires all pipeline jobs to pass before merge is permitted | N |

## Compatibility & Breaking Changes

This change introduces new infrastructure only; it does not modify application source code, APIs, data models, or runtime behaviour. There are no breaking changes to existing callers or consumers.

The one operational impact is that **pull requests will be blocked from merging if any pipeline job fails**, once branch protection rules are enabled. Contributors must resolve lint, security, and test failures before merge. This is an intentional gate, not an unintended regression.

| Change | Impact | Migration Path |
|---|---|---|
| Branch protection requiring CI to pass | Existing open PRs may be blocked if they contain pre-existing lint or test failures | Pre-existing failures must be remediated or explicitly suppressed with documented justification before the protection rule is activated |
| SAST severity threshold | Findings at or above the configured threshold block merge | TODO — threshold level (e.g., high, critical) to be agreed by security owner before rollout |
| Dependency scan severity threshold | Same as above | TODO — threshold level to be agreed by security owner before rollout |

## Acceptance Criteria

1. **Given** a pull request is opened against the default branch, **when** the PR is created or updated, **then** the GitHub Actions pipeline is automatically triggered within 5 minutes.

2. **Given** the pipeline is triggered, **when** all jobs complete successfully, **then** each job (lint, SAST, dependency scan, tests) reports a green status check visible on the pull request.

3. **Given** a source file containing a linting violation is introduced in a pull request, **when** the lint job runs, **then** the lint job exits with a non-zero code and the pipeline run is marked as failed.

4. **Given** a source file containing a code pattern flagged by the configured SAST tool at or above the agreed severity threshold is introduced in a pull request, **when** the SAST job runs, **then** the SAST job exits with a non-zero code and the pipeline run is marked as failed.

5. **Given** a dependency with a known vulnerability at or above the agreed severity threshold is declared in the project's dependency manifest, **when** the dependency scanning job runs, **then** the dependency scanning job exits with a non-zero code and the pipeline run is marked as failed.

6. **Given** a commit that causes one or more tests to fail is introduced in a pull request, **when** the test job runs, **then** the test job exits with a non-zero code and the pipeline run is marked as failed.

7. **Given** all four jobs (lint, SAST, dependency scan, tests) pass, **when** a reviewer attempts to merge the pull request, **then** the merge is permitted by branch protection rules.

8. **Given** any one of the four jobs fails, **when** a reviewer attempts to merge the pull request, **then** the merge is blocked by branch protection rules until the failure is resolved.

9. **Given** the pipeline runs on a clean commit with no violations or failures, **when** all jobs complete, **then** total pipeline wall-clock time does not exceed TODO minutes (threshold to be set after baseline measurement).

10. **Given** the dependency scanning job runs, **when** it completes, **then** a machine-readable report of findings (e.g., SARIF or JSON) is uploaded as a GitHub Actions artifact or to GitHub's Security tab, making results auditable.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the primary language, runtime, and build tool for this repository? This is required to select appropriate linting, SAST, and dependency scanning tools. | TODO | TODO |
| 2 | What severity threshold (e.g., critical only, high and above) should cause SAST findings to fail the pipeline? | Security owner (TODO) | TODO |
| 3 | What severity threshold should cause dependency scan findings to fail the pipeline? | Security owner (TODO) | TODO |
| 4 | Are there existing linter configuration files or coding style standards that the lint job must enforce, or does a standard needs to be adopted as part of this work? | TODO | TODO |
| 5 | What is the current state of branch protection on the default branch? Are there existing required status checks that must be preserved? | TODO | TODO |
| 6 | Should SAST results be published to GitHub Advanced Security (Code Scanning) via SARIF upload, or to a third-party security platform? | Security owner (TODO) | TODO |
| 7 | Are there any self-hosted runner requirements (e.g., air-gapped environment, specific hardware), or will GitHub-hosted runners be used? | Infrastructure owner (TODO) | TODO |
| 8 | What is the acceptable maximum pipeline duration (wall-clock time) for the team? This informs job parallelisation decisions in plan.md. | Engineering lead (TODO) | TODO |
| 9 | Should the pipeline run on all branches or only on pull requests targeting the default branch? | Engineering lead (TODO) | TODO |