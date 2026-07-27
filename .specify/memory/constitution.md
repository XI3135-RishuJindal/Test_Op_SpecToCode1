## Project Identity

**Name:** Dependency Risk Backlog Constitution  
**Purpose:** Establish the source-of-truth rules for producing a prioritized upgrade backlog based on **CVE exposure** and **outdated dependency** analysis.  
**High-level goal:** Deliver a **prioritized, evidence-backed list of dependency upgrades** (security + staleness), aligned to the project’s **medium urgency** and unknown stack details (to be discovered).

---

## Guiding Principles

1. **Prefer evidence-backed prioritization over opinion-based ordering because the task is explicitly “CVE and outdated dependency analysis.”**
2. **Prefer identifying unknowns early over assuming stack details because language/runtime/build tool are unknown in the tech analysis summary.**
3. **Prefer conservative, low-disruption recommendations over aggressive upgrades because the selected upgrade option is “conservative.”**
4. **Prefer reproducible scanning outputs over one-off manual notes because the backlog must be defensible and re-runnable as dependencies change.**
5. **Prefer security fixes (known CVEs) over cosmetic version freshness because CVE remediation is a primary driver of the requested backlog.**
6. **Prefer clearly scoped backlog items over broad modernization initiatives because the modernization goal is limited to producing an upgrade backlog.**

---

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for Option ID `conservative`.
- **Technology mandates (runtime versions, cloud provider, compliance requirements):** N/A — not provided; language/runtime/build tool are unknown.
- **Budget or scope freezes visible in the upgrade option:**  
  - **Scope is frozen to:** producing a prioritized upgrade backlog (CVE + outdated dependency analysis).  
  - **Out of scope:** implementing upgrades, refactoring, runtime migration, build/deploy pipeline changes. (No authorization stated in task.)
- **Upgrade urgency:** Medium (must be reflected in prioritization framing and recommended sequencing).

---

## Quality Standards

- **Input discovery completeness:** 100% of detected dependency manifests/lockfiles in the repository must be enumerated in the analysis output (or explicitly marked **TODO/blocked** with reason).
- **CVE triage requirements:** For each prioritized security-related backlog item, include:
  - dependency name, current version (if discoverable), recommended version range/target (if discoverable),
  - CVE identifier(s) or advisory link(s),
  - severity rating (as provided by the scanner/advisory source),
  - affected transitive vs direct classification (if detectable).
- **Outdated dependency triage requirements:** For each non-CVE backlog item, include:
  - current vs latest (or latest compatible) version (if discoverable),
  - rationale for priority (e.g., major-version gap, end-of-life signal if present, high churn risk),
  - confidence level if metadata is incomplete.
- **Prioritization format:** Backlog must be ranked using a consistent rubric that, at minimum, separates:
  - **P0:** exploitable/critical-high severity CVEs (per source data),
  - **P1:** medium severity CVEs and high-risk staleness,
  - **P2:** low severity CVEs and routine currency upgrades,
  - with explicit “unknown/needs verification” labels where data is missing.
- **Reproducibility:** Outputs must include the exact commands/tools/versions used to generate findings (or **TODO** if not yet known).
- **Review gate:** At least 1 reviewer must validate:
  - that no stack assumptions were made (unknowns marked TODO),
  - that prioritization rubric is applied consistently across items.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Scope limited to producing a prioritized upgrade backlog based on CVE and outdated dependency analysis. | Stated modernization goal explicitly restricts deliverable to backlog/analysis, not implementation. | accepted |
| ADR-002 | Use “conservative” upgrade posture for recommendations. | Upgrade Option selected is `conservative` (details not provided), implying lower-risk guidance. | accepted |
| ADR-003 | Do not assume language/runtime/build tooling; treat as discovery items. | Tech analysis summary lists language/runtime/build tool as unknown. | accepted |
| ADR-004 | Treat effort ceiling and schedule as unknown pending option details. | Upgrade option lacks person-day estimate and timeline specifics. | proposed (TODO) |