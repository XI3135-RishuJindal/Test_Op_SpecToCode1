## Project Identity

**Name:** CVE Patch/Minor Dependency Upgrade Modernization  
**Purpose:** Apply patch/minor dependency upgrades that require code changes to remediate **critical/high** CVEs.  
**High-level goal:** Reduce security risk by upgrading vulnerable dependencies within patch/minor version bounds while preserving existing behavior and delivery cadence.

---

## Guiding Principles

1. **Prefer patch/minor upgrades over major upgrades because the stated goal is CVE remediation without expanding scope.**
2. **Prefer remediating critical/high CVEs over addressing medium/low issues because the task explicitly targets critical/high severity.**
3. **Prefer code changes that preserve existing public behavior over refactors because this is a security maintenance activity, not a redesign.**
4. **Prefer smallest viable change sets over broad dependency refreshes because upgrade urgency is medium and the option is “conservative.”**
5. **Prefer reproducible upgrades (lockfiles/pinned versions) over floating ranges because security fixes must be auditable and repeatable.** *(TODO — confirm whether the ecosystem uses lockfiles and how versions are currently pinned.)*
6. **Prefer automated verification (tests + basic build checks) over manual validation because dependency upgrades can introduce regressions even within minor versions.** *(TODO — confirm what test/build system exists.)*

---

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for option **conservative**.
- **Technology mandates:**
  - Language/runtime/build tool: **TODO — unknown** (must not assume).
  - Runtime version changes: **Not in scope unless required** to apply patch/minor dependency fixes. *(TODO — confirm if any CVE fix requires runtime bump.)*
  - Cloud/provider/compliance requirements: **TODO — not provided**.
- **Budget/scope freezes:**
  - **Scope is limited to patch/minor dependency upgrades needed to remediate critical/high CVEs, including required code changes.**
  - **No feature work, architecture changes, or major-version dependency upgrades** unless explicitly required and approved (would require updating this Constitution).

---

## Quality Standards

- **Security verification**
  - All identified **critical/high CVEs** in targeted dependencies must be **remediated** (upgrade, removal, or mitigations) and evidenced via a scan report **before merge**. *(TODO — define scanner/tooling once known.)*
- **Build/CI gate**
  - A clean **build** and **test execution** must pass on CI for every change set. *(TODO — define build/test commands once known.)*
- **Testing bar**
  - **No reduction in existing automated test coverage** (if coverage measurement exists). *(TODO — confirm coverage tooling; if none, N/A.)*
- **Code review**
  - Minimum **1 approving reviewer** for each PR touching dependency versions and/or remediation code changes.
  - PR must include: list of upgraded packages, CVE references, and notes on behavior changes (if any).
- **Documentation**
  - Maintain a short **upgrade note** in repo (e.g., changelog entry or SECURITY/UPGRADE note) enumerating: CVEs addressed, packages/versions changed, and any required operational steps. *(TODO — confirm documentation conventions.)*
- **Deployment gates**
  - N/A — not applicable to this task (deployment process/environment not provided).

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Limit remediation to **patch/minor dependency upgrades** (with necessary code changes) targeting **critical/high CVEs**. | Matches the modernization goal and avoids scope expansion. | accepted |
| ADR-002 | Use a **conservative** upgrade approach. | Upgrade option selected is “conservative” (details not provided). | accepted |
| ADR-003 | Do **not** assume or change language/runtime/build tool absent explicit data. | Tech analysis lists these as unknown; avoid inventing constraints. | accepted |
| ADR-004 | Require CI build/tests and scan evidence as merge criteria. | Dependency upgrades risk regressions; CVE remediation must be verifiable. | proposed *(TODO — confirm current CI/scanner availability)* |