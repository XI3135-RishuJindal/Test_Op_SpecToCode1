## Project Identity

**Name:** SCA Baseline: SBOM + Dependency Vulnerability Report  
**Purpose:** Establish a software composition analysis (SCA) baseline by generating a Software Bill of Materials (SBOM) and a dependency vulnerability report for the existing codebase.  
**High-level goal:** Produce repeatable artifacts (SBOM and vulnerability report) that capture current dependency inventory and known vulnerabilities, without changing application behavior or upgrading dependencies.

## Guiding Principles

1. **Prefer producing an accurate snapshot over attempting remediation because the stated goal is a baseline report, not dependency upgrades or fixes.**
2. **Prefer tool-agnostic outputs (standard SBOM formats) over proprietary-only formats because the language/build tool are unknown and outputs must remain usable across ecosystems.**
3. **Prefer non-invasive analysis over build/runtime changes because runtime/build tool are unknown and scope is limited to reporting.**
4. **Prefer deterministic, repeatable generation over ad-hoc/manual runs because the baseline must be comparable over time.**
5. **Prefer clearly labeled unknowns and limitations over inferred metadata because the tech analysis omits language/runtime/build details and guessing would corrupt the baseline.**

## Constraints

- **Timeline and effort ceiling:** **TODO — not provided.** (Upgrade Option: *conservative* with no person-day estimate.)
- **Technology mandates:**  
  - Language: **TODO — unknown**  
  - Runtime: **TODO — unknown**  
  - Build tool: **TODO — unknown**  
  - Cloud provider: **N/A — not applicable to this task** (not referenced; reporting task only)  
  - Compliance requirements: **TODO — not provided**
- **Budget/scope freezes:**  
  - **Scope is strictly limited to generating SBOM and a dependency vulnerability report (SCA baseline).**  
  - **No dependency upgrades, refactors, runtime changes, or platform migrations** as part of this task (baseline only).

## Quality Standards

- **Artifacts produced (measurable):**
  - Generate **at least one SBOM** in a **standard format**: **SPDX (JSON) and/or CycloneDX (JSON/XML)**. *(Exact format selection: TODO — depends on ecosystem/tooling.)*
  - Generate **at least one dependency vulnerability report** covering **direct and transitive dependencies** where discoverable by the ecosystem tooling.
- **Reproducibility:**
  - Provide **documented, runnable commands** (or a script) to regenerate both artifacts on demand.
  - Artifact generation must be **deterministic for a given commit** (same inputs → same outputs), to the extent supported by chosen tools.
- **Documentation must-haves:**
  - A short **README section** (or doc) stating:
    - tool(s) used and version(s) (**TODO** until selected),
    - invocation commands,
    - output locations,
    - known gaps/limitations (e.g., “language/build tool unsupported”, “private registry resolution not available”).
- **Review and gates:**
  - **At least 1 peer review approval** for any changes introducing the tooling/scripts/docs.
  - CI/CD deployment gates: **N/A — not applicable to this task** (no deployment changes required).
- **Testing coverage floor:**
  - **N/A — not applicable to this task** (report generation only; no functional code change required).  
    If scripts are added, they must at minimum have **a basic smoke check** (e.g., command exits non-zero on failure).

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Limit scope to generating SBOM and dependency vulnerability report only (no remediation). | Modernization goal explicitly states “Generate SBOM and dependency vulnerability report (SCA baseline)”; no upgrade/remediation targets provided. | accepted |
| ADR-002 | Do not assume language/runtime/build tool; treat as TODO until discovered. | Tech analysis lists language/runtime/build tool as unknown; guessing would produce inaccurate baseline artifacts. | accepted |
| ADR-003 | Prefer standard SBOM formats (SPDX and/or CycloneDX) over proprietary formats. | Ensures portability and usefulness despite unknown ecosystem/tooling. | proposed (pending tool selection) |
| ADR-004 | Use “conservative” upgrade option approach. | Only upgrade option provided is “conservative” (details not provided). | accepted (details TODO) |