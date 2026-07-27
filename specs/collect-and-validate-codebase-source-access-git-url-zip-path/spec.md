## Summary
This spec defines the required capability to **collect and validate access to the codebase source** via one of three input types—**Git URL**, **ZIP archive**, or **local path**—and to produce a **verified, normalized source reference** that downstream modernization steps can rely on. Expected outcome: a repeatable validation step that confirms the source is accessible, complete enough to proceed, and unambiguously identifies what was validated.

## Motivation
- **Business driver:** Ensure the modernization effort starts from a verifiable, auditable source snapshot to reduce rework and prevent analyzing the wrong repository or incomplete artifacts.
- **Technical driver:** The tech analysis indicates **upgrade urgency: medium**; this task reduces schedule risk by catching access/credential/path issues early and establishing a stable input boundary for later phases.
- **Version/EOL/CVE/compliance specifics:** N/A — not applicable to this task (no versions, EOL dates, CVEs, or compliance requirements were provided in the tech analysis).

## Current State
N/A — not applicable to this task (no codebase interfaces, APIs, classes, config keys, or schemas were provided in the context).

## Proposed Changes
Introduce a single, explicit “Source Access Intake & Validation” capability that accepts one of the supported source types and produces a validated result record.

### Supported source inputs (what changes)
- **Git URL input**
  - Collect: repository URL and reference selector (branch/tag/commit) (**TODO: confirm whether ref is required or optional**), and authentication material if needed (**TODO: confirm supported auth types**).
  - Validate: repository is reachable and the requested ref exists (or default branch is resolvable if ref omitted—**TODO**).
- **ZIP archive input**
  - Collect: ZIP location and provenance metadata (**TODO: define required metadata fields if any**).
  - Validate: ZIP is readable, is a valid archive, and contains a plausible source tree (minimum criteria defined below).
- **Local path input**
  - Collect: path identifier and any access context needed (**TODO**).
  - Validate: path exists, is readable, and contains a plausible source tree (minimum criteria defined below).

### Validation outputs (what is added)
A normalized “Validated Source Reference” containing at minimum:
- **Source type** (git/zip/path)
- **Resolved identity**
  - For Git: resolved commit SHA (**TODO: confirm availability/requirement**)
  - For ZIP: deterministic content identifier (**TODO: define method**) and original filename
  - For path: canonicalized path and deterministic content identifier (**TODO**)
- **Validation status** (pass/fail) and **structured failure reasons**
- **Timestamp** of validation

### Removed
N/A — not applicable to this task (no existing mechanism was provided to remove/replace).

### Component change table

| Component | Before | After | Breaking? (Y/N) |
|---|---|---:|:---:|
| Source acquisition | Ad hoc / unspecified | Standardized intake supporting Git URL, ZIP, or path | N |
| Source validation | Unspecified | Explicit validation step with pass/fail and reasons | N |
| Source identity / traceability | Unspecified | Normalized validated source reference produced | N |

## Compatibility & Breaking Changes
N/A — not applicable to this task (no existing callers, APIs, or contracts were provided; no breaking changes can be asserted from context).

## Acceptance Criteria
1. **Given** a reachable Git repository URL and valid credentials (if required), **when** the source intake is executed with that Git URL, **then** validation passes and a validated source reference is produced that includes the source type `git` and a resolved immutable identifier (**TODO: specify required identifier fields, e.g., commit SHA**).

2. **Given** an unreachable Git repository URL or invalid credentials, **when** the source intake is executed with that Git URL, **then** validation fails with a structured failure reason indicating reachability/authentication failure.

3. **Given** a ZIP input that is a readable, valid ZIP archive, **when** the source intake is executed with that ZIP, **then** validation passes and a validated source reference is produced that includes the source type `zip` and a deterministic content identifier (**TODO: define identifier requirement**).

4. **Given** a ZIP input that is not a valid ZIP archive or is unreadable, **when** the source intake is executed with that ZIP, **then** validation fails with a structured failure reason indicating invalid archive/unreadable artifact.

5. **Given** a local path that exists and is readable, **when** the source intake is executed with that path, **then** validation passes and a validated source reference is produced that includes the source type `path` and a canonicalized path value.

6. **Given** a local path that does not exist or is not readable, **when** the source intake is executed with that path, **then** validation fails with a structured failure reason indicating missing/unreadable path.

7. **Given** any supported source input type, **when** validation fails, **then** the process returns a non-success status that can be checked by CI and includes at least one machine-readable failure reason (not only free-form text).

8. **Given** any supported source input type that passes validation, **when** the validated source reference is generated, **then** it includes enough information to re-fetch or re-identify the same source snapshot deterministically (**TODO: define determinism requirements per input type**).

## Open Questions

| # | Question | Owner (or TODO) | Due Date (or TODO) |
|---:|---|---|---|
| 1 | What authentication methods must be supported for Git URL access (SSH keys, HTTPS token, etc.)? | TODO | TODO |
| 2 | Is a Git ref (branch/tag/commit) required, and what is the default behavior if omitted? | TODO | TODO |
| 3 | What minimum criteria define a “plausible source tree” for ZIP/path validation (e.g., presence of specific files)? | TODO | TODO |
| 4 | What deterministic identifier is required for ZIP and path inputs (hash algorithm/strategy)? | TODO | TODO |
| 5 | Where and how should validated source references be recorded for traceability (system of record, retention)? | TODO | TODO |
| 6 | What is the expected maximum source size and any limits for ZIP/path intake? | TODO | TODO |
| 7 | Are there any privacy/compliance constraints on storing credentials or source artifacts during validation? | TODO | TODO |