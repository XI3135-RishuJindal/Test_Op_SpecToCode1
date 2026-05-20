# CONSTITUTION
## Security Tooling CI Integration — Bandit & pip-audit

---

## Project Identity

**Name:** Security Tooling CI Integration  
**Purpose:** Integrate Bandit (static application security testing for Python) and pip-audit (dependency vulnerability scanning) into the project's GitHub Actions CI pipeline.  
**High-Level Goal:** Establish automated, repeatable security checks that run on every relevant CI trigger, surfacing code-level security issues and known vulnerable dependencies before code is merged.

---

## Guiding Principles

1. **Prefer failing the CI pipeline on detected issues over silent reporting**, because unblocked merges with known vulnerabilities defeat the purpose of automated security scanning.
2. **Prefer pinned, versioned tool invocations over unpinned `latest`** because non-deterministic tool versions produce inconsistent results across runs and make regressions hard to attribute.
3. **Prefer dedicated, scoped CI jobs for each tool over combining them into a single step** because isolated jobs produce clearer failure signals and allow independent re-runs.
4. **Prefer storing scan results as CI artifacts over discarding them** because audit trails are required to demonstrate due diligence and support incident response.
5. **Prefer configuring tool-specific ignore/allowlist files committed to the repository over ad-hoc inline suppressions** because repository-tracked exceptions are reviewable and auditable.

---

## Constraints

- **Timeline & Effort:** Moderate effort ceiling (exact person-days not provided — TODO: confirm with project lead). Scope is limited strictly to CI pipeline integration; no remediation of findings is in scope for this task.
- **Technology Mandates:**
  - Target language is Python (implied by Bandit and pip-audit tooling). TODO: confirm exact Python runtime version in use.
  - CI platform is GitHub Actions exclusively.
  - Bandit and pip-audit are the mandated tools; no substitutions without a new ADR.
- **Scope Freeze:** This task does not include fixing vulnerabilities found by the tools, upgrading dependencies, or modifying application source code.
- **Budget:** TODO — no explicit budget ceiling provided.

---

## Quality Standards

- **Pipeline coverage:** Both Bandit and pip-audit jobs must execute on every pull request targeting the default branch and on every push to the default branch. No exceptions without an ADR.
- **Bandit configuration:** A `bandit.yaml` (or equivalent config file) must exist in the repository root and be referenced explicitly in the workflow; zero undocumented inline skips permitted.
- **pip-audit configuration:** The workflow must target the project's dependency manifest (e.g., `requirements.txt`, `pyproject.toml`); the exact file path must be explicit, not inferred.
- **Artifact retention:** Scan output (SARIF, JSON, or plain text) must be uploaded as a GitHub Actions artifact with a minimum retention of 30 days.
- **Code review:** All changes to workflow files (`.github/workflows/`) require at least one peer review approval before merge.
- **Documentation:** A `SECURITY_SCANNING.md` (or equivalent section in `CONTRIBUTING.md`) must document how to run both tools locally, how to interpret results, and the process for adding justified suppressions.
- **Deployment gate:** The CI pipeline must be configured as a required status check on the default branch; merges are blocked if either security job fails.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use Bandit for Python SAST | Bandit is the mandated tool per the modernization task; it is the de facto standard for Python static security analysis. | Accepted |
| ADR-002 | Use pip-audit for dependency vulnerability scanning | pip-audit is the mandated tool per the modernization task; it queries PyPI Advisory Database and OSV for known CVEs. | Accepted |
| ADR-003 | GitHub Actions as the sole CI platform | Mandated by the task description; no alternative CI platforms are in scope. | Accepted |
| ADR-004 | Scope limited to integration only, not remediation | Remediating findings is a separate workstream; conflating the two would expand effort beyond the moderate ceiling. | Accepted |
| ADR-005 | TODO: Decide on SARIF vs. JSON output format | SARIF enables native GitHub Code Scanning integration; JSON is simpler. Decision pending confirmation of GitHub Advanced Security availability on this repository. | Proposed |