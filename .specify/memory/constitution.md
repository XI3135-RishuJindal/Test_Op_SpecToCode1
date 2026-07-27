## Project Identity

**Name:** Build/Test Entrypoints & Baseline Versions Inventory (Documentation)  
**Purpose:** Produce authoritative documentation that identifies how to build and test the system, and records the baseline runtime and framework versions currently in use.  
**High-level goal:** Reduce modernization uncertainty by capturing verified build/test entrypoints and current runtime/framework version baselines in a single, maintainable source of truth.

## Guiding Principles

1. **Prefer verified commands over inferred commands because the language/runtime/build tool are unknown.**  
2. **Prefer repository-sourced evidence (configs, lockfiles, CI logs) over human memory because the current tech stack details are unspecified.**  
3. **Prefer documenting “as-is” baselines over proposing upgrades because the task is inventory/documentation only.**  
4. **Prefer explicit “unknown/TODO” markers over guessing because the tech analysis provides no concrete versions or frameworks.**  
5. **Prefer a single canonical doc location over scattered notes because the output must serve as a source of truth for later specs/plans.**

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for Option ID `conservative`.  
- **Technology mandates (runtime versions, cloud provider, compliance):** N/A — not applicable to this task (no mandates provided; task is documentation).  
- **Budget or scope freezes:** Scope is limited to **inventory and documentation** of:
  - build entrypoints (commands/scripts/CI jobs)
  - test entrypoints (commands/scripts/CI jobs)
  - baseline runtime/framework versions  
  No upgrade implementation is in scope.

## Quality Standards

- **Evidence requirement:** Every documented build/test entrypoint must cite its source (e.g., file path like `package.json`, `Makefile`, `pom.xml`, `build.gradle`, `requirements.txt`, CI workflow file, or CI job output). Measurable bar: **100% of entries include at least one source reference**.  
- **Reproducibility bar:** Documented commands must be copy/paste runnable (including required environment variables and working directory) *or* explicitly marked **“requires TODO prerequisites”**. Measurable bar: **0 undocumented prerequisites** (must be listed or marked TODO).  
- **Version baseline bar:** Runtime/framework version statements must be backed by a file/config/source reference (e.g., `.tool-versions`, `Dockerfile`, CI image tag). Measurable bar: **100% of version claims include a source reference**.  
- **Review requirement:** At least **1 code review approval** from a maintainer familiar with CI/build before merging documentation changes.  
- **Documentation must-haves:** The inventory must include:
  - build entrypoints (local + CI if present)
  - test entrypoints (unit/integration/e2e if present; otherwise note “not found”)
  - baseline runtime version(s)
  - baseline framework version(s) (or “none found” / TODO)  
  Measurable bar: **all four headings present** even if populated with “unknown/TODO”.  
- **Deployment gates:** N/A — not applicable to this task (documentation-only).

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Limit scope to inventory and documentation of build/test entrypoints and baseline runtime/framework versions. | The modernization goal explicitly specifies documentation-only inventory; tech details are unknown and no upgrade execution is requested. | accepted |
| ADR-002 | Use explicit TODO markers for unknown language/runtime/build tool/framework/version details. | Tech analysis lists these as unknown; guessing would undermine the inventory’s reliability. | accepted |
| ADR-003 | Require source references for every documented command and version claim. | Ensures the inventory is verifiable and maintainable given unspecified stack and medium upgrade urgency. | accepted |