# CONSTITUTION
## Java 8 → 21 LTS Runtime Upgrade

---

## Project Identity

**Name:** Java Runtime Upgrade — 8 to 21 LTS

**Purpose:** Migrate the application's Java runtime from version 8 to Java 21 (LTS) to eliminate end-of-life runtime risk, restore access to long-term vendor support, and position the codebase for modern language and platform features.

**High-Level Goal:** Deliver a production-running application on Java 21 LTS with no functional regressions, within the effort envelope of the selected upgrade option.

---

## Guiding Principles

1. **Prefer incremental compatibility fixes over rewrites** because the build tool, framework stack, and dependency inventory are not yet fully known — minimising change surface reduces risk of introducing regressions.
2. **Prefer Java 21 LTS over any intermediate version** because only LTS releases carry the long-term vendor support that justifies the migration cost and resolves the EOL risk of Java 8.
3. **Prefer automated test validation over manual verification** because the full scope of runtime behaviour changes across 13 major Java versions (9–21) cannot be reliably caught by inspection alone.
4. **Prefer explicit dependency version pinning over open ranges** because Java 9+ module system and classpath changes frequently break libraries that compiled cleanly on Java 8.
5. **Prefer resolving `--illegal-access` and removed-API warnings as errors** over suppressing them, because suppression defers breakage to runtime and masks real incompatibilities introduced by the Java 9+ strong encapsulation model.
6. **Prefer documenting every TODO and unknown before writing code** because the tech analysis reveals the build tool, framework, and dependency tree are currently unconfirmed — proceeding without this inventory increases rework risk.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate upgrade option — exact person-days TODO (not provided); scope must not expand beyond runtime upgrade and direct compatibility fixes |
| **Target runtime** | Java 21 LTS — no other target version is acceptable |
| **Source compatibility** | Existing source language level must be confirmed before raising `--source`/`--release` flags; raising source level is out of scope unless required for compilation |
| **Build tool** | TODO — must be confirmed (Maven/Gradle/other) before any build-script changes are made |
| **Scope freeze** | New features, refactors, and framework upgrades are out of scope unless they are a hard prerequisite for Java 21 compatibility |
| **Compliance/security** | No new external runtime dependencies may be introduced without a security review |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Regression test pass rate** | 100% of pre-existing automated tests must pass on Java 21 before merge |
| **Test coverage floor** | TODO — existing coverage baseline must be measured and must not decrease after the upgrade |
| **Build reproducibility** | CI pipeline must produce a clean build on Java 21 with zero `WARNING: Illegal reflective access` or equivalent strong-encapsulation warnings |
| **Code review** | Every PR touching build configuration or dependency versions requires at least one reviewer with Java 9+ migration experience |
| **Deployment gate** | Application must start and pass smoke tests on Java 21 in a staging environment before any production promotion |
| **Documentation** | A migration notes document must record every dependency version bump, JVM flag change, and removed-API fix made during the upgrade |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Target Java 21 LTS as the sole destination version | LTS designation ensures long-term support; skipping intermediate versions reduces total migration effort | Accepted |
| ADR-002 | Treat the upgrade as runtime-only until build tool and framework are confirmed | Tech analysis lists build tool and frameworks as unknown; premature changes risk compounding unknowns | Accepted |
| ADR-003 | Block scope expansion beyond Java 21 compatibility fixes | Moderate effort ceiling requires strict scope control; feature work belongs in a separate initiative | Accepted |
| ADR-004 | TODO — Decision on build tool migration strategy (Maven toolchain vs. Gradle JVM toolchain) | Pending confirmation of current build tool | Proposed |
| ADR-005 | TODO — Decision on handling of `sun.*` / `com.sun.*` internal API usages | Requires dependency and source scan to determine extent of exposure | Proposed |