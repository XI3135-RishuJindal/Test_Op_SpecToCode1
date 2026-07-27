## Project Identity

**Name:** Source Access Validation (SAV)  
**Purpose:** Obtain and validate access to the existing codebase source via one of the allowed delivery methods (GitHub URL, ZIP archive, or filesystem path).  
**High-level goal:** Confirm the team can reliably retrieve the complete source code and establish a verified, repeatable access method suitable for subsequent modernization work.

## Guiding Principles

1. **Prefer verified access over assumed access because language/runtime/build details are unknown and cannot be derived without the source.**
2. **Prefer minimal, reversible steps over invasive changes because the task is limited to obtaining and validating access only.**
3. **Prefer repeatable retrieval (documented steps and checks) over one-off transfers because future specs and plans must be based on a stable source-of-truth.**
4. **Prefer integrity checks (e.g., checksums, commit SHAs) over trust-based validation because the access method may be GitHub/ZIP/path and must be provably complete.**
5. **Prefer least-privilege access over broad permissions because the task requires access validation, not administrative control.**

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for Option ID `conservative`.
- **Technology mandates (runtime versions, cloud provider, compliance requirements):** N/A — not applicable to this task (unknown and not required to validate source access).
- **Budget or scope freezes visible in the upgrade option:** Scope freeze: **only** obtain and validate codebase source access (GitHub URL/ZIP/path). No modernization/refactoring/build changes.

## Quality Standards

- **Access validation evidence:** Provide at least one verifiable proof of retrieval:
  - For GitHub: repository URL + commit SHA(s) retrieved, and confirmation that default branch is accessible.
  - For ZIP: checksum (e.g., SHA-256) recorded and successful extraction verified.
  - For filesystem path: canonical path recorded and read access verified.
- **Completeness check:** Confirm the retrieved source contains:
  - A top-level directory structure (not an empty scaffold), and
  - At least one build/entry indicator if present (e.g., `README`, `package.json`, `pom.xml`, `build.gradle`, `Makefile`, `requirements.txt`, etc.).  
  If none exist, record as **TODO/unknown** rather than guessing.
- **Reproducibility:** Document the exact retrieval steps so another engineer can repeat them without additional context (commands/URLs/credentials mechanism described at a high level).
- **Security bar:** No secrets (tokens, passwords, private keys) may be stored in the repo or in project documents; credential handling must be via secure channels (exact mechanism: TODO).
- **Review gate:** Access method and validation evidence must be reviewed/acknowledged by at least **one** other team member before declaring the task complete.
- **Testing coverage floor:** N/A — not applicable to this task.
- **Deployment gates:** N/A — not applicable to this task.

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Limit scope to obtaining and validating source access via GitHub URL, ZIP, or filesystem path. | User-stated modernization goal and task definition explicitly constrain scope. | accepted |
| ADR-002 | Treat all technology characteristics (language/runtime/build tool/frameworks) as unknown until source is retrieved. | Tech analysis states unknowns; inferring would be speculative. | accepted |
| ADR-003 | Use Upgrade Option ID `conservative` as the selected approach placeholder, with details marked TODO. | Option identified but details not provided; cannot derive constraints/effort. | proposed |