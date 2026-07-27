## Project Identity

**Name:** CI Secret Scanning with Gitleaks — Actionable Reporting  
**Purpose:** Add automated secret scanning to the CI pipeline using **gitleaks**, producing **actionable, developer-friendly reports** for detected secrets.  
**High-level goal:** Reduce secret leakage risk by detecting credentials/tokens in code changes early and consistently during CI runs.

## Guiding Principles

1. **Prefer automated CI enforcement over manual checks because secret leakage risk is continuous and manual review is unreliable.**
2. **Prefer actionable, developer-oriented findings over raw scanner output because the goal is remediation, not just detection.**
3. **Prefer minimal, conservative CI changes over broad pipeline refactors because the selected upgrade option is “conservative” (details not provided).**
4. **Prefer repository-scoped configuration over organization-wide policy changes because scope is limited to this task and broader governance is unspecified (TODO).**
5. **Prefer fail-fast on confirmed secrets over permissive warnings because the objective is to prevent secret introduction (severity thresholds/config are TODO).**

## Constraints

- **Timeline / effort ceiling:** TODO — person-days estimate not provided in the upgrade option.
- **Technology mandates:**
  - **CI platform:** TODO — not specified (e.g., GitHub Actions, GitLab CI, Jenkins).
  - **Gitleaks usage:** Must use **gitleaks** for secret scanning (per task).
  - **Language/runtime/build tool:** N/A — not applicable to this task (unknown and not required to configure gitleaks).
- **Budget / scope freezes:** Constrain work strictly to **CI secret scanning configuration and reporting**. No broader modernization, refactoring, or runtime upgrades. (Option: conservative; details not provided.)

## Quality Standards

- **CI integration bar:** Gitleaks must run automatically on every **pull request** and on the default branch **after merge** (exact triggers TODO depending on CI platform).
- **Actionable reporting bar:** Each finding must include, at minimum:
  - file path
  - line number (or nearest available location)
  - rule ID / description
  - commit/PR reference (when available)
- **Fail condition bar:** The CI job must **fail** when findings exceed the agreed threshold (threshold policy TODO: e.g., any finding vs. only high-confidence rules).
- **Baselining / legacy handling:** If the repository contains existing secrets, implement a **baseline/allowlist mechanism** so CI blocks *new* exposures while tracking existing ones (exact method TODO: gitleaks baseline file vs. ignore rules).
- **Code review bar:** All CI/config changes require **at least 1 approving review** from a repo maintainer before merge.
- **Documentation bar:** Add a short repository doc (e.g., `SECURITY.md` note or `docs/ci-secret-scanning.md`) covering:
  - how gitleaks runs in CI
  - how developers reproduce locally (command example)
  - how to handle false positives / approved allowlisting process
- **Deployment gates:** N/A — not applicable to this task (no production deployment; CI configuration only).  
- **Test coverage floor:** N/A — not applicable to this task (no application code changes implied; validation is via CI job behavior).

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use **gitleaks** for CI secret scanning | Task explicitly requires configuring gitleaks | accepted |
| ADR-002 | Apply a **conservative** implementation approach | Upgrade option selected is “conservative” (details not provided) | accepted |
| ADR-003 | Language/runtime/build-tool changes are **out of scope** | Tech analysis marks them unknown and not needed for CI-only secret scanning | accepted |

**TODOs (unresolved due to missing inputs):** CI provider and pipeline structure; effort ceiling/person-days; exact failure thresholds; reporting target format (SARIF vs. text) and where reports are surfaced; baseline strategy specifics; branch/PR trigger details.