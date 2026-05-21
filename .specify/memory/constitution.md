# CONSTITUTION — GitHub Actions CI Pipeline

> Source of truth for all specs, plans, and tasks in this modernization effort.

---

## Project Identity

**Name:** GitHub Actions CI Pipeline Implementation
**Purpose:** Establish an automated continuous integration pipeline using GitHub Actions to enforce code quality, security posture, and test coverage on every code change.
**High-Level Goal:** Introduce linting, Static Application Security Testing (SAST), dependency vulnerability scanning, and automated test execution as mandatory gates in the development workflow. The pipeline must run reliably on pull requests and main-branch pushes with no manual intervention.

---

## Guiding Principles

1. **Prefer automated enforcement over documentation-only standards** because the current state has no CI pipeline, meaning quality and security checks are not consistently applied.
2. **Prefer fail-fast pipeline ordering (lint → SAST → dependency scan → tests) over parallel-only execution** because catching cheap errors early (linting) avoids wasting compute on expensive steps (tests).
3. **Prefer pinned Action versions (`uses: action@sha`) over floating tags** because unpinned third-party Actions introduce supply-chain risk, which is directly relevant to the security mandate of this task.
4. **Prefer pipeline-as-code in the repository over external CI configuration** because GitHub Actions YAML in `.github/workflows/` keeps CI config versioned alongside the code it governs.
5. **Prefer blocking PR merges on pipeline failure over advisory-only results** because non-blocking checks are routinely ignored and defeat the purpose of automated gates.

---

## Constraints

- **Timeline / Effort:** Moderate effort ceiling (exact person-days not specified in the upgrade option — TODO: confirm with project lead before planning sprint).
- **Technology Mandates:**
  - CI platform is **GitHub Actions** — no other CI system is in scope.
  - Language, runtime, and build tool are currently **unknown** — tooling choices for linter, SAST scanner, and test runner must be confirmed during discovery and recorded in the Decision Log before implementation begins (see TODO items below).
- **Scope Freeze:** This effort covers pipeline configuration only. Fixing pre-existing lint errors, security findings, or failing tests surfaced by the new pipeline is **out of scope** unless explicitly re-scoped.
- **TODO:** Identify language/runtime to select appropriate linter (e.g., ESLint, Flake8, golangci-lint).
- **TODO:** Identify dependency manifest format to select appropriate scanner (e.g., Dependabot, Trivy, Snyk, OWASP Dependency-Check).
- **TODO:** Confirm SAST tooling (e.g., CodeQL, Semgrep, Bandit) based on language.
- **TODO:** Confirm test runner and coverage tooling.

---

## Quality Standards

- **Pipeline reliability:** The CI workflow must pass on a clean repository checkout with zero flaky failures before the feature is considered done.
- **Coverage gate:** TODO — define minimum test-coverage threshold once language and test framework are identified; a numeric floor (e.g., ≥ 80%) must be set and enforced as a pipeline step, not left as advisory.
- **Code review:** All workflow YAML changes require at least **one peer review** and approval before merge; no self-merges.
- **Documentation:** A `docs/ci.md` (or equivalent) must be committed alongside the workflow files, describing each job, its purpose, required secrets/permissions, and how to run checks locally.
- **Deployment gate:** Branch protection rules on `main` must be configured to require the CI workflow to pass before merge is permitted — this is a hard acceptance criterion, not optional.
- **Secret hygiene:** No credentials, tokens, or API keys may appear in workflow YAML; all secrets must use `${{ secrets.* }}` references.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use GitHub Actions as the sole CI platform | Task explicitly mandates GitHub Actions; no alternative platforms are in scope | Accepted |
| ADR-002 | Pipeline jobs ordered: lint → SAST → dependency scan → tests | Fail-fast principle; cheaper checks gate more expensive ones | Accepted |
| ADR-003 | Pin all third-party Actions to full commit SHA | Mitigates supply-chain / dependency risk, consistent with security mandate of this task | Accepted |
| ADR-004 | Enforce pipeline as a required status check on `main` | Non-blocking CI provides no meaningful quality gate | Accepted |
| ADR-005 | Linter, SAST tool, and test runner selection | Deferred — language/runtime unknown at constitution time | Proposed (TODO) |