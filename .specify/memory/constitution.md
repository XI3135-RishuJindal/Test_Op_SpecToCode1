## Project Identity

**Name:** SBOM CI Job Modernization  
**Purpose:** Add a CI job that generates a Software Bill of Materials (SBOM) for build artifacts using CycloneDX or an equivalent standard.  
**High-level goal:** Produce an SBOM as part of CI so build outputs have an auditable dependency inventory.

## Guiding Principles

1. **Prefer generating SBOMs in CI over manual generation because repeatability and auditability depend on automation.**
2. **Prefer a standardized SBOM format (CycloneDX or equivalent) over custom inventories because downstream security/compliance tooling expects common schemas.**
3. **Prefer attaching/publishing SBOMs alongside build artifacts over storing them ad hoc because consumers need a reliable way to locate the SBOM for a given build.**
4. **Prefer minimal, task-scoped CI changes over broader pipeline refactors because the modernization goal is limited to adding SBOM generation.**

## Constraints

- **Timeline and effort ceiling:** TODO — person-days estimate not provided for Option ID `conservative`.
- **Technology mandates:**  
  - Language: TODO — unknown  
  - Runtime: TODO — unknown  
  - Build tool: TODO — unknown  
  - CI system: TODO — unknown (GitHub Actions assumed by “GitHub Spec Kit” context, but not explicitly specified)
- **Budget or scope freezes:** Scope is frozen to “add CI job to generate SBOM for build artifacts (CycloneDX or equivalent)”; no additional modernization work.

## Quality Standards

- **CI integration bar:** The SBOM job must run automatically in CI on every build that produces artifacts. (Trigger specifics: TODO — depends on existing pipeline.)
- **Artifact handling bar:** The generated SBOM must be persisted as a CI artifact and/or published alongside build artifacts for the same build run. (Exact mechanism: TODO — depends on current artifact storage/release process.)
- **Format bar:** Output must be CycloneDX (or an equivalent industry-standard SBOM format). Chosen format and version must be documented in-repo. (Exact choice/version: TODO.)
- **Determinism bar:** Re-running the SBOM job on the same commit/build inputs should produce functionally equivalent SBOM output (allowing for timestamps/metadata if unavoidable). Any nondeterministic fields must be documented.
- **Failure policy bar:** SBOM generation failure must fail the CI workflow for protected branches/releases. (Branch policy specifics: TODO.)
- **Review bar:** Changes to CI configuration and SBOM tooling configuration require at least 1 code review approval.
- **Documentation bar:** Repository documentation must include:
  - Where the SBOM is generated in CI
  - Where it is published/stored
  - How to regenerate locally (if feasible)  
  (Exact doc location: TODO — e.g., `README.md` or `docs/`.)

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Add a CI job to generate an SBOM for build artifacts. | Modernization goal explicitly requires SBOM generation integrated into CI. | accepted |
| ADR-002 | Use CycloneDX or an equivalent standard SBOM format. | Task requires CycloneDX or equivalent; standard formats maximize interoperability. | accepted |
| ADR-003 | Use “conservative” upgrade option. | Upgrade option provided is `conservative` (details not provided). | accepted (details TODO) |