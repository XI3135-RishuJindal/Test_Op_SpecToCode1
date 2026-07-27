## Project Identity

**Name:** Baseline Inventory — Runtime/Framework/Build Tooling Versions  
**Purpose:** Establish an authoritative snapshot of the current runtime, framework(s), and build tooling versions used by the system.  
**High-level goal:** Produce a baseline inventory of version information to enable future modernization planning while keeping scope limited to discovery and documentation.

## Guiding Principles

1. **Prefer verified evidence (repository config, lockfiles, CI logs) over assumptions because language/runtime/build tool are currently unknown.**
2. **Prefer read-only inspection over code or dependency changes because the task is baseline inventory only (no upgrade scope).**
3. **Prefer recording exact versions (including patch and distribution where possible) over loose ranges because the output must serve as a reliable baseline for future decisions.**
4. **Prefer documenting unknowns explicitly as TODO over guessing because the tech analysis contains missing fields and the constitution must not invent details.**

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for Option ID `conservative`.
- **Technology mandates:** N/A — not applicable to this task (no runtime/framework/build tool mandates provided; task is discovery only).
- **Budget or scope freezes:** Scope is frozen to **capturing and documenting current versions only**; **no upgrades, migrations, refactors, or dependency changes**.

## Quality Standards

- **Evidence-backed inventory:** Every recorded version entry must include a source reference (e.g., file path + snippet, command output, CI job log link/ID). Measurable bar: **100% of entries have a cited source**.
- **Reproducibility:** Inventory must be reproducible by another engineer following documented steps. Measurable bar: **at least one documented “how to verify” step per major category** (runtime, frameworks, build tooling).
- **Review:** Inventory document changes require **at least 1 reviewer approval** before merge.
- **Documentation:** Deliverable must include a single consolidated inventory artifact (e.g., `docs/baseline-inventory.md` or equivalent). Measurable bar: **one canonical file** containing the baseline.
- **Deployment gates:** N/A — not applicable to this task (no deployment changes expected).
- **Testing coverage:** N/A — not applicable to this task (no code changes required; if scripts are added, TODO define minimal checks).

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Limit scope to capturing current runtime, framework, and build tooling versions (baseline inventory only). | Task explicitly requires baseline inventory; tech details are unknown; avoid expanding into upgrades. | accepted |
| ADR-002 | Use Option ID `conservative` as the operating approach. | Provided upgrade option is `conservative` (details not provided). | proposed (TODO: confirm details) |
| ADR-003 | Record unknown fields as TODO rather than infer. | Tech analysis fields (language/runtime/build tool/frameworks) are unknown; constitution must not fabricate. | accepted |