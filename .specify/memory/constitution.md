# CONSTITUTION — CI/CD Pipeline Modernization

## Project Identity

**Name:** CI/CD Pipeline Implementation
**Purpose:** Introduce an automated CI/CD pipeline to the project, enforcing test, lint, and SAST (Static Application Security Testing) stages on every code change.
**High-Level Goal:** Establish a repeatable, automated quality gate that catches functional regressions, style violations, and security vulnerabilities before code reaches production — replacing any current manual or ad-hoc process.

---

## Guiding Principles

1. **Prefer automated enforcement over documentation-only standards** because the current state has no pipeline, meaning quality checks are inconsistently applied and depend on individual discipline.
2. **Prefer failing fast (lint → test → SAST order) over running all stages in parallel** because surfacing cheap errors (lint) before expensive ones (SAST) reduces wasted compute and shortens feedback loops.
3. **Prefer pipeline-as-code (committed configuration) over UI-configured pipelines** because version-controlled pipeline definitions are auditable, reproducible, and reviewable like any other change.
4. **Prefer blocking merges on stage failure over advisory-only results** because non-blocking gates are routinely bypassed under delivery pressure, defeating the purpose of the pipeline.
5. **Prefer minimal external service dependencies over feature-rich integrations** because the language/runtime/build tool are currently unknown (see Constraints), so the pipeline must remain adaptable as the stack is confirmed.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option selected; scope is limited to pipeline scaffolding — test, lint, and SAST stages only. No refactoring of application code is in scope. |
| **Language / Runtime** | TODO — language, runtime, and build tool are unconfirmed. Pipeline tooling choices (test runner, linter, SAST scanner) must be finalised once the stack is identified before implementation begins. |
| **SAST tooling** | Must use a tool with a free/OSS tier or one already licensed by the organisation. TODO — confirm approved SAST scanner. |
| **CI platform** | TODO — target CI platform (GitHub Actions, GitLab CI, Jenkins, etc.) not specified. Must be decided before pipeline configuration is authored. |
| **Scope freeze** | Pipeline covers CI only (pull-request and main-branch triggers). CD (deployment automation) is explicitly out of scope for this option. |
| **No application changes** | This task does not authorise changes to application source code, dependencies, or infrastructure beyond pipeline configuration files. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test stage** | Pipeline must execute the project's existing test suite; stage fails if any test fails or if no tests are found/configured. |
| **Lint stage** | Zero lint errors permitted for a passing build; warnings may be reported but do not block merge until threshold is agreed (TODO). |
| **SAST stage** | Pipeline must produce a machine-readable report (e.g. SARIF); any finding rated **High** or **Critical** blocks merge. Medium and below are reported only until a remediation policy is established (TODO). |
| **Pipeline config review** | All changes to pipeline configuration files require at least one peer code-review approval before merge. |
| **Documentation** | A `CI.md` (or equivalent) must be committed alongside the pipeline config, documenting: stage purposes, how to run checks locally, and how to interpret SAST results. |
| **Coverage floor** | TODO — minimum test-coverage percentage cannot be set until language and existing test suite are known. Must be defined before pipeline goes live. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Implement pipeline in three discrete, sequential stages: lint → test → SAST | Fail-fast ordering minimises CI cost; separation makes stage failures unambiguous | Accepted |
| ADR-002 | Pipeline configuration stored as code in the repository root | Ensures auditability and parity between branches; aligns with pipeline-as-code principle | Accepted |
| ADR-003 | CD (deployment) stages are out of scope | Upgrade option is scoped to quality gates only; deployment automation introduces risk and effort beyond the moderate ceiling | Accepted |
| ADR-004 | Specific CI platform, test runner, linter, and SAST scanner deferred | Language and runtime are unknown at constitution time; tooling must be confirmed before spec.md is authored | Proposed |