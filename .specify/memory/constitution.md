# CONSTITUTION — GitHub Actions CI Pipeline Introduction

> **Project source of truth.** All specs, plans, and tasks must conform to this document.

---

## Project Identity

**Name:** GitHub Actions CI Pipeline — Modernization Initiative

**Purpose:** Introduce a GitHub Actions–based continuous integration pipeline to enforce code quality, security, and correctness gates on every code change.

**High-Level Goal:** Deliver a working CI pipeline with four ordered stages — lint, SAST (static application security testing), dependency scanning, and automated tests — integrated into the repository's pull-request and main-branch workflows.

---

## Guiding Principles

1. **Prefer automated enforcement over manual review for quality gates** because the current absence of a CI pipeline means lint, security, and test checks are inconsistently applied, creating medium-urgency tech debt.
2. **Prefer fail-fast stage ordering (lint → SAST → dependency scan → test) over parallel-only execution** because catching cheap errors early (lint) avoids wasting compute on expensive stages (test).
3. **Prefer reusable, composable workflow steps over monolithic scripts** because maintainability of the pipeline itself is a first-class concern when the language/runtime stack is not yet locked down.
4. **Prefer pinned Action versions (SHA or exact tag) over floating `@latest` references** because unpinned actions are a known supply-chain attack vector that SAST and dependency scanning are designed to catch.
5. **Prefer explicit secrets management via GitHub Encrypted Secrets over hardcoded credentials** because CI pipelines are a common credential-leakage surface.
6. **Prefer documented TODO markers over invented decisions** because the language, runtime, and build tool are currently unknown; tooling choices for each stage must be confirmed before implementation begins.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option selected; specific person-days not provided — TODO: confirm effort budget before sprint planning. |
| **Scope freeze** | Pipeline covers exactly four stages: lint, SAST, dependency scan, test. No deployment, release, or environment-promotion stages in this initiative. |
| **Platform mandate** | CI must run exclusively on GitHub Actions (not Jenkins, CircleCI, or other providers). |
| **Trigger mandate** | Pipeline must execute on `pull_request` and `push` to the default branch at minimum. |
| **Language/runtime** | TODO: unknown — tooling selection for each stage is blocked until stack is identified. |
| **Build tool** | TODO: unknown — stage scripts cannot be finalised until confirmed. |
| **Budget** | TODO: GitHub Actions compute costs (self-hosted vs. GitHub-hosted runners) not specified. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Pipeline green rate** | All four stages must pass before a PR is eligible to merge (branch protection rule required). |
| **Lint coverage** | Lint stage must check 100% of source files in the repository, with zero warnings-as-errors bypassed. |
| **SAST findings** | No new High or Critical severity findings introduced by a PR may be merged without a documented exception. |
| **Dependency scan** | No known Critical CVE dependencies may be merged; High CVEs require a tracked issue before merge. |
| **Test execution** | All existing tests must be executed in the test stage; zero test regressions permitted on the default branch. |
| **Workflow file review** | All changes to `.github/workflows/` require at least one peer code-review approval. |
| **Pipeline documentation** | A `docs/ci.md` file describing each stage, its tooling, and how to run checks locally must ship with the pipeline. |
| **Action pinning** | 100% of third-party Actions must be pinned to a full-length commit SHA or verified release tag. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use GitHub Actions as the sole CI platform | Task mandate; no alternative platform evaluation required. | Accepted |
| ADR-002 | Enforce four-stage pipeline: lint → SAST → dependency scan → test | Directly specified in the modernization goal; order chosen for fail-fast efficiency. | Accepted |
| ADR-003 | Require branch protection rules to enforce pipeline passage | Without enforcement, pipeline gates are advisory only and provide no real quality guarantee. | Accepted |
| ADR-004 | Pin all third-party Actions to exact SHA | Supply-chain risk mitigation; consistent with SAST goals of the pipeline itself. | Accepted |
| ADR-005 | Defer tooling selection per stage until language/runtime confirmed | Language and build tool are unknown; inventing tooling choices would create rework. | Accepted |
| ADR-006 | Scope limited to CI only (no CD/release stages) | Upgrade option is moderate scope; deployment automation is out of scope for this initiative. | Accepted |