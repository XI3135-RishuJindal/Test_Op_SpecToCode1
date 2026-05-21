# Spec: Introduce GitHub Actions CI Pipeline with Ruff, Bandit, pip-audit, and pytest

## Summary

This spec covers the introduction of a GitHub Actions continuous integration (CI) pipeline for the repository. The pipeline will automate code-quality enforcement and security scanning on every pull request and push to the main branch, executing four tools in sequence: ruff (linting/formatting), Bandit (static security analysis), pip-audit (dependency vulnerability scanning), and pytest (test suite execution). The expected outcome is a reproducible, automated quality gate that blocks merges when any check fails.

## Motivation

- **No existing CI gate:** The repository currently has no automated quality or security checks, meaning regressions, style drift, and vulnerable dependencies can be merged undetected.
- **Security posture:** Without pip-audit and Bandit running on every change, known CVEs in dependencies and common Python security anti-patterns go undetected until a manual review or incident.
- **Code consistency:** The absence of an enforced linter means contributors apply inconsistent style, increasing review overhead and technical debt over time.
- **Upgrade urgency:** Rated **medium** — no active incident, but the gap represents meaningful risk accumulation with each merged PR.
- **Compliance readiness:** Automated SAST (Bandit) and SCA (pip-audit) checks are commonly required by SOC 2, ISO 27001, and similar frameworks; introducing them now reduces future compliance remediation effort.

## Current State

- There are **no existing GitHub Actions workflow files** in the repository.
- There is **no enforced linting, formatting, or security scanning** step in any merge or review process.
- Test execution (pytest) is presumed to be a manual, developer-local step only — no evidence of automated test runs on CI.
- Dependency vulnerability scanning (pip-audit) and static security analysis (Bandit) are not present in any automated or documented manual process.
- Specific configuration files for ruff, Bandit, or pip-audit (e.g., `pyproject.toml` sections, `.bandit`, `pip-audit` config) are: **TODO — confirm whether any pre-existing tool configuration exists in the repository.**
- The existing test suite location, coverage level, and any pytest configuration (`pytest.ini`, `pyproject.toml` `[tool.pytest.ini_options]`) are: **TODO — confirm structure and entry point.**

## Proposed Changes

The following components are introduced or modified to establish the CI pipeline.

| Component | Before | After | Breaking? |
|---|---|---|---|
| GitHub Actions workflow | None | New workflow triggered on `push` and `pull_request` to main branch | N |
| Ruff (linting & formatting check) | Not present | Runs as a CI job; fails pipeline on lint or format violations | N |
| Bandit (SAST) | Not present | Runs as a CI job; fails pipeline on medium-or-higher severity findings (threshold TODO) | N |
| pip-audit (SCA) | Not present | Runs as a CI job; fails pipeline on any known vulnerable dependency | N |
| pytest (test execution) | Manual/local only | Runs as a CI job; fails pipeline on any test failure or error | N |
| Branch protection rules | Not configured | TODO — recommend enabling "Require status checks to pass" for the new workflow jobs | N |

**What is added:**
- A GitHub Actions workflow definition containing at minimum one job per tool (or a single job with sequential steps — sequencing strategy is an implementation detail for plan.md).
- Any minimal tool configuration required to make each tool runnable in a clean CI environment (e.g., ruff and Bandit severity thresholds).

**What is removed:**
- Nothing is removed from the existing codebase as part of this change.

## Compatibility & Breaking Changes

Because this change introduces new infrastructure rather than modifying existing code, there are no breaking changes to runtime behaviour, APIs, or data models.

| Change | Impact | Migration Path |
|---|---|---|
| CI pipeline fails on existing lint violations | PRs with pre-existing ruff violations will be blocked | Existing violations must be resolved (or ruff rules scoped) before the workflow is enabled on protected branches |
| CI pipeline fails on existing Bandit findings | PRs with pre-existing SAST findings will be blocked | Existing findings must be triaged; accepted risks should be marked with inline suppressions or a Bandit baseline file |
| CI pipeline fails on existing vulnerable dependencies | PRs will be blocked if current `requirements` contain known CVEs | Vulnerable packages must be updated or pip-audit ignore list established with documented justification |
| CI pipeline fails on existing test failures | PRs will be blocked if the test suite is currently broken | Test suite must be in a passing state before branch protection is enforced |

## Acceptance Criteria

1. **Given** a pull request is opened against the main branch, **when** the GitHub Actions workflow is triggered, **then** all four jobs (ruff, Bandit, pip-audit, pytest) execute and their pass/fail status is reported as individual check statuses on the PR.

2. **Given** a source file containing a ruff lint violation is committed, **when** the CI pipeline runs, **then** the ruff job exits with a non-zero status and the overall workflow run is marked as failed.

3. **Given** all source files conform to ruff rules, **when** the CI pipeline runs, **then** the ruff job exits with status zero.

4. **Given** a source file containing a Bandit finding at or above the configured severity threshold is committed, **when** the CI pipeline runs, **then** the Bandit job exits with a non-zero status and the workflow run is marked as failed.

5. **Given** no Bandit findings exist at or above the configured threshold, **when** the CI pipeline runs, **then** the Bandit job exits with status zero.

6. **Given** a dependency with a known CVE is present in the project's dependency list, **when** the CI pipeline runs, **then** the pip-audit job exits with a non-zero status and the workflow run is marked as failed.

7. **Given** no dependencies with known CVEs are present, **when** the CI pipeline runs, **then** the pip-audit job exits with status zero.

8. **Given** one or more pytest tests fail or error, **when** the CI pipeline runs, **then** the pytest job exits with a non-zero status and the workflow run is marked as failed.

9. **Given** all pytest tests pass, **when** the CI pipeline runs, **then** the pytest job exits with status zero.

10. **Given** a push is made directly to the main branch (not via PR), **when** the event occurs, **then** the CI workflow is triggered and all four jobs execute.

11. **Given** the CI pipeline completes successfully on a clean codebase, **when** the workflow run is inspected in the GitHub Actions UI, **then** all four jobs are shown with a green (success) status and total wall-clock time is recorded for baseline comparison.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What Python version(s) must the CI matrix target? | TODO | TODO |
| 2 | What is the Bandit severity/confidence threshold for failing the build (e.g., medium+, high only)? | TODO | TODO |
| 3 | Does the repository use `requirements.txt`, `pyproject.toml`, `Pipfile`, or another dependency format that pip-audit must be pointed at? | TODO | TODO |
| 4 | Are there pre-existing ruff, Bandit, or pytest configuration sections in `pyproject.toml` or separate config files that the workflow must respect? | TODO | TODO |
| 5 | Should branch protection rules be enabled as part of this task, or is that a separate work item? | TODO | TODO |
| 6 | Should the workflow run on all branches (for every PR) or only PRs targeting main/master? | TODO | TODO |
| 7 | Is there a requirement to publish test results or coverage reports as CI artifacts or PR comments? | TODO | TODO |
| 8 | Are there self-hosted runners or specific GitHub-hosted runner OS/version requirements (e.g., `ubuntu-latest` vs a pinned version)? | TODO | TODO |
| 9 | Should pip-audit findings against dependencies with no available fix be treated as blocking or advisory? | TODO | TODO |