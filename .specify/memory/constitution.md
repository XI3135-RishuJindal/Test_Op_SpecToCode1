# CONSTITUTION
## GitHub Actions CI Pipeline with Bandit SAST and Safety CVE Scanning

---

## Project Identity

**Name:** CI Security Pipeline Modernization
**Purpose:** Introduce an automated GitHub Actions CI pipeline that enforces static application security testing (SAST) via Bandit and dependency vulnerability scanning via Safety CVE checks on every code change.
**High-Level Goal:** Eliminate manual or absent security scanning by embedding Bandit and Safety into the GitHub Actions workflow, ensuring no code reaches the main branch without passing both security gates.

---

## Guiding Principles

1. **Prefer automated security gates over manual review for vulnerability detection** because the current state has no documented SAST or CVE scanning, creating medium-urgency upgrade risk from undetected code flaws and vulnerable dependencies.
2. **Prefer failing the pipeline fast on critical findings over silently passing** because unblocked merges with known vulnerabilities defeat the purpose of introducing scanning tooling.
3. **Prefer minimal, focused workflow scope over broad CI expansion** because the upgrade option is moderate in effort and the task is narrowly scoped to Bandit and Safety — no other CI concerns are in scope.
4. **Prefer pinned tool versions over floating versions** because unpinned Bandit and Safety versions introduce non-deterministic scan results and potential supply-chain risk in the pipeline itself.
5. **Prefer pipeline-as-code (YAML in `.github/workflows/`) over external CI configuration** because GitHub Actions is the mandated platform and all pipeline logic must be version-controlled alongside the application code.

---

## Constraints

- **Timeline/Effort:** Moderate effort ceiling (exact person-days not specified in option — TODO: confirm effort estimate with project lead before work begins).
- **Technology Mandates:**
  - CI platform: GitHub Actions only.
  - SAST tool: Bandit only (no substitution).
  - CVE scanning tool: Safety only (no substitution).
  - Target language: TODO — runtime and language version are unspecified in the tech analysis; pipeline configuration must be updated once confirmed.
  - Build tool: TODO — unknown; workflow steps must accommodate the actual build tool once identified.
- **Scope Freeze:** This pipeline introduction covers Bandit and Safety scanning exclusively. No other CI stages (e.g., linting, test execution, deployment) are in scope unless explicitly added via a separate task.
- **Branch Protection:** Pipeline must be wired to pull request and push events on the main branch at minimum. Exact branch strategy is TODO pending repository conventions.

---

## Quality Standards

- **Scan Coverage:** Bandit must scan 100% of Python source files in the repository (recursive scan); no directory exclusions without documented justification in the workflow file as a comment.
- **CVE Threshold:** Safety scan must check all entries in `requirements.txt` (or equivalent dependency manifest — TODO: confirm file name). Pipeline must exit non-zero on any known CVE of severity medium or above.
- **Workflow Validity:** The GitHub Actions YAML must pass `actionlint` validation before merge (enforced in the same or a companion workflow).
- **Pinned Versions:** Bandit and Safety must be installed at explicitly pinned versions (e.g., `bandit==X.Y.Z`) recorded in a `requirements-ci.txt` or equivalent file committed to the repository.
- **Code Review:** All changes to `.github/workflows/` files require at least one peer review approval before merge.
- **Documentation:** The repository `README` or a `docs/ci-security.md` file must document how to run Bandit and Safety locally, matching the pipeline invocation exactly.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use GitHub Actions as the CI platform | Task explicitly mandates GitHub Actions; no alternative platform evaluated. | Accepted |
| ADR-002 | Use Bandit for SAST | Explicitly required by the modernization task; addresses absence of static security analysis. | Accepted |
| ADR-003 | Use Safety for CVE scanning | Explicitly required by the modernization task; addresses absence of dependency vulnerability detection. | Accepted |
| ADR-004 | Pin Bandit and Safety to explicit versions | Prevents non-deterministic results and supply-chain risk in the pipeline itself. | Accepted |
| ADR-005 | Scope pipeline to security scanning only | Upgrade option is moderate; expanding scope risks exceeding effort ceiling and violates task boundaries. | Accepted |
| ADR-006 | Language/runtime version selection | TODO — language and runtime are unknown per tech analysis; must be resolved before pipeline YAML is finalised. | Proposed |