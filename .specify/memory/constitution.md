# CONSTITUTION
## GitHub Actions CI Pipeline Setup

---

## Project Identity

**Name:** GitHub Actions CI Pipeline  
**Purpose:** Establish a repeatable, automated CI pipeline for the repository using GitHub Actions, covering build, test, and Static Application Security Testing (SAST) steps.  
**High-Level Goal:** Deliver a working, maintainable CI pipeline that enforces code quality and security checks on every pull request and push to the main branch, reducing manual verification overhead and surfacing defects early.

---

## Guiding Principles

1. **Prefer fail-fast pipeline ordering (build → test → SAST) over parallel-first execution** because catching compilation/build errors before running expensive test or security scans conserves runner minutes and provides faster developer feedback.
2. **Prefer reusable, composable workflow steps over monolithic scripts** because the language/runtime is currently unknown (TODO), making modular steps easier to swap when the stack is confirmed.
3. **Prefer pinned Action versions (SHA or exact tag) over floating `@latest` references** because unpinned actions introduce supply-chain risk, which is a direct SAST/security concern for the pipeline itself.
4. **Prefer SAST as a blocking gate over advisory-only reporting** because the upgrade urgency is medium and unreviewed security findings should not reach the main branch unacknowledged.
5. **Prefer secrets managed via GitHub Encrypted Secrets over hardcoded values** because CI pipelines are a common vector for credential exposure.

---

## Constraints

- **Timeline/Effort:** Upgrade option is rated *moderate*; no explicit person-days figure was provided — **TODO: confirm effort ceiling with project lead before sprint planning.**
- **Technology Mandates:**
  - CI platform: **GitHub Actions** (non-negotiable per task scope).
  - Language, runtime, and build tool are **unknown** — **TODO: identify and document before writing workflow YAML.**
  - SAST tooling must integrate natively with GitHub Actions (e.g., CodeQL, Semgrep, or equivalent); tool selection is **TODO** pending language confirmation.
- **Scope Freeze:** This pipeline covers **build, test, and SAST only**. CD, deployment, release, or infrastructure provisioning steps are explicitly out of scope.
- **Budget:** No budget constraints specified — **TODO: confirm if GitHub-hosted runners are approved or if self-hosted runners are required.**

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Pipeline green rate | All three stages (build, test, SAST) must pass before a PR is mergeable (branch protection rule enforced). |
| SAST coverage | SAST step must scan 100% of changed files on every PR; zero high-severity findings may be silently bypassed. |
| Workflow lint | Workflow YAML must pass `actionlint` with zero errors before merge. |
| Secret hygiene | Zero plaintext secrets in workflow files; verified by automated secret-scanning (GitHub native or equivalent). |
| Documentation | Each job in the workflow must include an inline `name:` field and a corresponding entry in `docs/ci.md` explaining its purpose and configuration options. |
| Review requirement | All changes to `.github/workflows/` require at least one peer code-review approval from a team member with CI/security context. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use GitHub Actions as the sole CI platform | Explicitly mandated by the task; no alternative platforms evaluated. | Accepted |
| ADR-002 | Pipeline stage order: build → test → SAST | Fail-fast principle; build failures make test/SAST results meaningless. | Accepted |
| ADR-003 | SAST is a blocking (required) check, not advisory | Medium upgrade urgency warrants enforced security gates, not optional warnings. | Accepted |
| ADR-004 | Pin all third-party Actions to exact versions or commit SHAs | Mitigates supply-chain attack risk inherent in CI tooling. | Accepted |
| ADR-005 | SAST tool selection deferred | Language/runtime unknown; tool must be chosen once stack is identified. | Proposed — TODO |
| ADR-006 | Self-hosted vs. GitHub-hosted runners deferred | No budget or infrastructure constraints provided in the upgrade option. | Proposed — TODO |