## Project Identity

**Name:** Source Access Collection & Validation  
**Purpose:** Securely collect and validate access to the codebase source via one of: Git URL, ZIP archive, or local filesystem path.  
**High-level goal:** Confirm the team can reliably obtain the complete source code and that it is usable for subsequent analysis/work (e.g., consistent retrieval, integrity checks, basic structure validation).

---

## Guiding Principles

1. **Prefer validating access early over assuming availability because language/runtime/build details are unknown and downstream work depends on verified source retrieval.**
2. **Prefer least-privilege access over broad credentials because the task involves handling repository/archives and may involve sensitive code.**
3. **Prefer immutable, checksum-verified artifacts over ad-hoc transfers because integrity must be confirmable when accepting ZIPs or local copies.**
4. **Prefer reproducible retrieval instructions over one-off manual steps because access must be repeatable by the project team and auditors.**
5. **Prefer documenting unknowns as TODO over guessing because the tech analysis indicates unknown language/runtime/build tool and the upgrade option details are not provided.**

---

## Constraints

- **Timeline and effort ceiling:** TODO — upgrade option “conservative” person-days estimate not provided.
- **Technology mandates:** N/A — not applicable to this task (language/runtime/build tool/cloud/compliance requirements are unknown and not required to collect source access).
- **Budget or scope freezes:** Limited strictly to **collecting and validating source access (Git URL / ZIP / path)**. No modernization, upgrades, refactors, dependency changes, or runtime/build alterations.

---

## Quality Standards

- **Access validation criteria (must pass):**
  - Provide **exactly one** primary source access method (Git URL *or* ZIP *or* path), plus a fallback method if available (optional).
  - For **Git URL**: ability to clone successfully using documented authentication method; repository contains expected top-level structure (e.g., non-empty, not a partial export).
  - For **ZIP**: archive opens without errors; extraction yields a non-empty tree; include **SHA-256 checksum** recorded in documentation.
  - For **Local path**: path is accessible to the executing environment; tree is readable; include a **tree listing** summary (top-level directories/files) recorded in documentation.
- **Security handling bar (must meet):**
  - Credentials/tokens must **not** be committed to the repo or placed in plaintext in project docs; reference secure storage mechanism as TODO if not defined.
- **Review requirement:**
  - All collected access details and validation evidence must be reviewed by **at least one** other team member before being marked complete.
- **Documentation must-haves (minimum):**
  - A single “Source Access Record” (location TBD) containing: method used, access instructions, authentication approach (high level), checksum (if ZIP), date validated, validator name/handle, and any access caveats.
- **Deployment gates:** N/A — not applicable to this task.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Scope is limited to collecting and validating source access via Git URL, ZIP, or filesystem path. | Explicit task and modernization goal specify only source access collection/validation; tech stack is unknown. | accepted |
| ADR-002 | Record unknown technical details (language/runtime/build tool) as TODO rather than infer them. | Tech analysis summary lists these as unknown; guessing would create incorrect constraints. | accepted |
| ADR-003 | “Conservative” upgrade option details (including person-days) are treated as TODO until provided. | Option ID is given but details are not provided; cannot derive timeline/effort constraints. | accepted |