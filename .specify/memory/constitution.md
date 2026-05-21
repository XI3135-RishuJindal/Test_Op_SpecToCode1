# CONSTITUTION — GitHub Actions CI Pipeline

## Project Identity

**Name:** GitHub Actions CI Pipeline Introduction
**Purpose:** Establish an automated continuous integration pipeline for the repository using GitHub Actions, enforcing code quality, security scanning, dependency auditing, and test execution on every code change.
**High-Level Goal:** Deliver a working CI pipeline that runs `ruff` (linting/formatting), `Bandit` (static security analysis), `pip-audit` (dependency vulnerability scanning), and `pytest` (test suite) — blocking merges on failure.

---

## Guiding Principles

1. **Prefer blocking CI gates over advisory warnings** because unenforced checks provide no reliability guarantee and the upgrade urgency is medium, indicating accumulated risk that must be actively contained.
2. **Prefer a single composable workflow file over multiple fragmented workflows** because maintainability overhead must be minimised given the moderate effort ceiling.
3. **Prefer fail-fast job ordering (lint → security → audit → test) over parallel-only execution** because cheap static checks (ruff, Bandit) should short-circuit before expensive test runs, conserving CI minutes.
4. **Prefer pinned Action versions (SHA or exact tag) over floating `@latest` references** because unpinned actions introduce silent supply-chain risk — directly addressed by the pip-audit inclusion in scope.
5. **Prefer explicit Python version matrix declaration over implicit runner defaults** because the runtime is currently unknown (see Constraints), and the pipeline must remain portable once the runtime is confirmed.

---

## Constraints

| Category | Constraint |
|---|---|
| **Effort ceiling** | Moderate option — implementation must be completable in a small, bounded spike; no architectural refactoring of the application is in scope. |
| **Scope freeze** | Pipeline configuration only. No changes to application source code, dependencies, or test suite structure unless strictly required to make the pipeline pass. |
| **Runtime version** | TODO — Python runtime version is unknown; pipeline must parameterise the version and default must be confirmed before merge. |
| **Tooling mandates** | Exactly these four tools must be present: `ruff`, `Bandit`, `pip-audit`, `pytest`. No substitutions. |
| **Platform** | GitHub Actions only. No other CI platforms (Jenkins, CircleCI, etc.) are in scope. |
| **Branch protection** | The pipeline must be wired to pull-request and push-to-default-branch triggers at minimum. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Ruff** | Zero lint errors permitted; pipeline step exits non-zero on any violation. |
| **Bandit** | Zero high-severity findings permitted (`-ll` flag or equivalent); medium findings must be reported but may be baselined with documented justification. |
| **pip-audit** | Zero known critical/high CVEs in dependencies; pipeline step exits non-zero on any unfixed vulnerability. |
| **pytest** | All existing tests must pass; pipeline exits non-zero on any test failure or collection error. |
| **Workflow file review** | Every change to `.github/workflows/` requires at least one peer code-review approval before merge. |
| **Documentation** | A `CI.md` (or equivalent section in `README.md`) must document each job, its purpose, and how to run checks locally — present before the pipeline is marked complete. |
| **Pipeline runtime** | Total wall-clock time for the full pipeline must not exceed 10 minutes on a standard `ubuntu-latest` runner (TODO: revise once runtime is confirmed). |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use GitHub Actions as the sole CI platform | Task scope explicitly mandates GitHub Actions; no alternative platforms are in scope. | Accepted |
| ADR-002 | Include all four tools (ruff, Bandit, pip-audit, pytest) as required steps | Explicitly listed in the modernization goal; none may be omitted or deferred. | Accepted |
| ADR-003 | Pin all third-party GitHub Actions to a specific version or SHA | Aligns with pip-audit's inclusion as a supply-chain safeguard; prevents silent action drift. | Accepted |
| ADR-004 | Python runtime version to be confirmed before pipeline merge | Runtime is listed as unknown in tech analysis; a TODO placeholder must be resolved during implementation. | Proposed |
| ADR-005 | Treat pipeline failures as merge-blocking | Medium upgrade urgency indicates existing risk; advisory-only CI would not reduce that risk. | Accepted |