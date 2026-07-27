## Project Identity

**Name:** CI SAST Baseline — CodeQL  
**Purpose:** Add basic Static Application Security Testing (SAST) to CI using GitHub CodeQL with baseline query suites.  
**High-level goal:** Ensure every CI run includes CodeQL analysis using baseline queries appropriate to the repository’s language(s), without expanding scope beyond initial setup.

## Guiding Principles

1. **Prefer default CodeQL query suites over custom queries because the task scope is “basic SAST with baseline queries,” and custom tuning would expand scope.**
2. **Prefer CI-integrated scanning over ad-hoc/manual runs because the goal is “in CI,” ensuring consistent execution on every change.**
3. **Prefer minimal, reversible workflow changes over broad CI refactors because language/build tool/runtime are unknown (TODO), and we must avoid risky assumptions.**
4. **Prefer failing on configuration errors over silently skipping analysis because a “configured” SAST pipeline must be reliably present.**
5. **Prefer incremental adoption (baseline coverage first) over attempting comprehensive security hardening because upgrade urgency is medium and the option is “conservative.”**

## Constraints

- **Timeline and effort ceiling:** TODO — upgrade option “conservative” provided with no person-day estimate; must be supplied before committing to a delivery schedule.
- **Technology mandates:**
  - **SAST tool:** GitHub CodeQL (CodeQL Action) in CI.
  - **Languages/build/runtime:** TODO — unknown; CodeQL language matrix must be derived from repository contents.
  - **CI platform:** TODO — not stated; assume nothing. If GitHub Actions is required, this must be explicitly confirmed.
- **Budget/scope freezes:**
  - Scope limited strictly to **basic SAST configuration** with **baseline query suites**. No custom queries, no broad CI redesign, no additional security tooling unless explicitly added later.

## Quality Standards

- **Workflow presence:** A CI workflow (or equivalent CI config) must run CodeQL analysis on:
  - Pull requests (minimum), and
  - Default branch pushes (minimum).
  *(If the project’s CI trigger model differs, document and align via TODO.)*
- **Query baseline:** Use CodeQL’s baseline query suite(s) for detected language(s); no custom query packs in this task.
- **Measurable outcome:** Each run must produce a CodeQL analysis result artifact/log output indicating analysis completed successfully (not skipped).
- **Failure behavior:** The pipeline must fail when CodeQL initialization or analysis fails (misconfiguration, missing permissions, etc.).
- **Code review bar:** All CI workflow changes require at least **1 reviewer approval** before merge.
- **Documentation must-haves:** A short repository note (e.g., in `SECURITY.md` or `README.md`) stating:
  - Where CodeQL runs in CI (events/branches),
  - Which query suite level is used (“baseline”),
  - How to view results (TODO — depends on GitHub Advanced Security / code scanning availability).

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use GitHub CodeQL for SAST with baseline query suites in CI | Task explicitly requires “basic SAST (CodeQL) in CI with baseline queries” | accepted |
| ADR-002 | Avoid custom queries/tuning in initial implementation | Keeps scope aligned to “basic” setup and conservative option | accepted |
| ADR-003 | Defer language/runtime/build-tool-specific configuration until repository inspection | Tech analysis lists language/runtime/build tool as unknown; assumptions would be risky | accepted |

N/A — not applicable to this task: Any production runtime upgrade decisions, infrastructure migrations, dependency modernization, performance tuning, or broader security program changes.