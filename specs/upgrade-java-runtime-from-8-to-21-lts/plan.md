# PLAN: Upgrade Java Runtime from 8 to 21 (LTS)

## Overview

**Migration Strategy: Phased Strangler-Fig**

The upgrade from Java 8 to Java 21 spans three major LTS versions (8 → 11 → 17 → 21) and carries meaningful compatibility risk due to the removal of APIs, module system enforcement (JPMS introduced in Java 9), and behavioral changes in GC, security, and reflection. A big-bang cutover is not appropriate given this span.

A strangler-fig / phased approach is selected:
- Each phase targets a stable LTS boundary (8→11, 11→17, 17→21), allowing incremental validation.
- The build toolchain is updated ahead of runtime to catch compile-time incompatibilities early.
- Feature-flag gating of the final production cutover provides a rollback escape hatch.

**Risk Justification:** The upgrade option is rated `moderate`. The absence of a known framework inventory and build tool in the tech analysis introduces additional unknowns that warrant conservative, phase-gated progression rather than a single cutover. Effort is derived from the `moderate` option baseline.

> **TODO:** Confirm actual risk score and person-days estimate once full tech analysis (build tool, frameworks, dependency tree) is available.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 0 — Discovery & Baseline | Audit codebase for Java 8-specific APIs, deprecated/removed APIs, illegal reflective access, and third-party library compatibility. Establish test coverage baseline. | Access to full source tree and dependency manifest | TODO person-days (see note) |
| 1 — Toolchain & Build Upgrade | Update build tool configuration to target Java 11 source/target compatibility. Resolve compile-time errors. Update CI pipeline to use JDK 11. | Phase 0 complete | TODO person-days |
| 2 — Runtime Validation on Java 11 | Run full test suite under JDK 11. Fix runtime failures (removed APIs, JPMS split packages, `sun.*` usage). Validate in staging. | Phase 1 complete | TODO person-days |
| 3 — Advance to Java 17 | Update build and CI to JDK 17. Address sealed classes conflicts, `SecurityManager` deprecation, stronger encapsulation (`--illegal-access` removed). | Phase 2 signed off | TODO person-days |
| 4 — Advance to Java 21 (Target) | Update build and CI to JDK 21. Address pattern matching, record conflicts, finalized JPMS enforcement. Enable virtual threads if applicable. | Phase 3 signed off | TODO person-days |
| 5 — Production Cutover & Hardening | Deploy Java 21 runtime to production behind feature flag / canary. Monitor GC, startup, and performance metrics. Remove flag and decommission Java 8 infrastructure. | Phase 4 signed off; infra updated | TODO person-days |

> **TODO:** Populate person-days per phase once the `moderate` option's total estimate is confirmed and a source-line/module count is available.

---

## Component Changes

> **TODO:** Specific class, method, and file names cannot be identified — no code context was provided. The entries below describe the structural change categories that apply universally to a Java 8 → 21 migration. Update with concrete file paths once the codebase is accessible.

### Build Configuration
- **Files affected:** `pom.xml` (Maven) **or** `build.gradle` / `build.gradle.kts` (Gradle) — **TODO: confirm build tool**
- **Changes:**
  - Update `maven.compiler.source` / `maven.compiler.target` **or** `sourceCompatibility` / `targetCompatibility` from `1.8` to `21`.
  - Update `java.version` property references.
  - Add `--add-opens` / `--add-exports` JVM flags as a temporary bridge where JPMS encapsulation breaks existing code (to be removed progressively).

### Reflection & Internal API Usage
- **Files affected:** TODO — any class using `sun.*`, `com.sun.*`, or `jdk.internal.*` packages.
- **Changes:** Replace with supported public API equivalents (e.g., `sun.misc.BASE64Encoder` → `java.util.Base64`).

### Security Manager
- **Files affected:** TODO — any class calling `System.setSecurityManager()` or implementing `SecurityManager`.
- **Changes:** `SecurityManager` is deprecated for removal in Java 17 and removed in Java 21. Replace with application-level security controls.

### Serialization
- **Files affected:** TODO — any class implementing `Serializable` with custom `readObject`/`writeObject`.
- **Changes:** Audit for `serialVersionUID` consistency; test deserialization across JVM versions.

### Removed / Changed APIs
- `javax.*` → `jakarta.*` migration: **TODO** — only applicable if Jakarta EE frameworks are present (not confirmed).
- `Thread.stop()`, `Thread.suspend()`, `Thread.resume()`: removed — **TODO** audit usage.
- `finalize()` overrides: deprecated for removal — replace with `Cleaner` or try-with-resources.

### JVM Launch Flags
- **Files affected:** startup scripts, Dockerfile `ENTRYPOINT`, Kubernetes `args`, CI test runner configs — **TODO: confirm locations**.
- **Changes:** Remove `-XX:+UseConcMarkSweepGC` (removed in Java 14). Evaluate G1GC (default) or ZGC for Java 21.

---

## Dependency Upgrade Plan

> **TODO:** No dependency versions were provided in the tech analysis. The table below lists the dependency categories that commonly require updates during a Java 8 → 21 migration. Populate version columns once a `pom.xml` / `build.gradle` / BOM is available.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| JDK / JRE | 8 | 21 (LTS) | JPMS, removed APIs, stronger encapsulation | Core upgrade target |
| Build tool (Maven/Gradle) | TODO | TODO | TODO | Must support Java 21 toolchain; TODO confirm tool |
| Byte-manipulation libs (ASM, Javassist, ByteBuddy) | TODO | TODO | Must support Java 21 class file version (65.0) | High-risk; often pulled in transitively |
| Reflection-heavy frameworks (Spring, Hibernate, etc.) | TODO | TODO | TODO | TODO — framework inventory not provided |
| JAXB / JAX-WS | TODO | TODO | Removed from JDK in Java 11 | Must be added as explicit dependencies |
| Testing framework (JUnit, TestNG) | TODO | TODO | TODO | TODO |
| Logging framework | TODO | TODO | TODO | TODO |
| Application server / servlet container | TODO | TODO | TODO | TODO |

> **All version numbers marked TODO must be sourced from the actual dependency manifest — no version numbers have been invented here.**

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. Apply the following change categories once infrastructure files are located.

- **Docker base image:** Replace `FROM openjdk:8-*` (or equivalent) with `FROM eclipse-temurin:21-jre-jammy` (or organization-approved Java 21 base image). TODO — confirm image registry and policy.
- **Kubernetes manifests:** Update any `java.version` environment variables or JVM flag arguments in `Deployment` / `StatefulSet` specs. TODO — confirm manifest locations.
- **CI/CD pipeline:** Update JDK installation step to JDK 21 (e.g., `actions/setup-java@v4` with `java-version: '21'`, or equivalent for the CI platform in use). TODO — confirm CI platform (GitHub Actions, Jenkins, GitLab CI, etc.).
- **IaC (Terraform/Ansible/etc.):** TODO — not mentioned in context.
- **JVM flags in startup scripts:** TODO — confirm locations of any shell scripts or systemd units that pass JVM arguments.

---

## Rollback Strategy

Each phase is independently reversible by reverting the build/runtime configuration to the previous JDK version. No data-format changes are introduced by the runtime upgrade itself.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1 — Toolchain** | 1. Revert `pom.xml` / `build.gradle` compiler source/target to `1.8`. 2. Restore CI JDK installation to JDK 8. 3. Re-run build to confirm green. |
| **Phase 2 — Runtime Java 11** | 1. Redeploy staging with JDK 8 Docker image / runtime. 2. Revert any `--add-opens` flags added for Java 11. 3. Validate test suite passes under JDK 8. |
| **Phase 3 — Runtime Java 17** | 1. Redeploy staging with JDK 11 image. 2. Revert compiler target to `11`. 3. Re-run Phase 2 validation suite. |
| **Phase 4 — Runtime Java 21** | 1. Redeploy staging with JDK 17 image. 2. Revert compiler target to `17`. 3. Re-run Phase 3 validation suite. |
| **Phase 5 — Production Cutover** | 1. Shift canary / feature-flag traffic back to Java 17 (or prior stable) deployment. 2. Redeploy production with previous JDK image. 3. Confirm monitoring metrics return to baseline. 4. File incident report and schedule remediation before re-attempting cutover. |

---

## Testing Strategy

### Test Pyramid

| Layer | Scope | Tools | Coverage Target | CI Gate |
|-------|-------|-------|----------------|---------|
| **Unit** | Individual classes and methods | TODO (JUnit 5 recommended; confirm existing framework) | ≥ 80% line coverage (establish baseline in Phase 0) | Fail build on regression below baseline |
| **Integration** | Component interactions, DB, messaging | TODO (confirm: Testcontainers, Spring Test, etc.) | Key integration paths covered | Fail build on any failure |
| **Regression** | Full functional suite re-run under each new JDK | Existing test suite executed against JDK 11, 17, 21 sequentially | 100% of pre-existing passing tests must pass | Phase gate: no advancement without green suite |
| **Performance** | Startup time, throughput, GC pause times | TODO (JMH, Gatling, or existing perf suite) | No regression > 10% vs Java 8 baseline | Required before Phase 5 production cutover |

### Additional Testing Notes
- **Phase 0:** Run `jdeprscan --release 21` against compiled JARs to enumerate deprecated/removed API usage before writing any code.
- **Phase 0:** Run `jdeps --multi-release 21` to identify split-package and JPMS issues.
- **Each phase gate:** The full regression suite must pass under the target JDK before the next phase begins.
- **TODO:** Confirm existing test framework versions are compatible with Java 21 before Phase 1.

---

## Timeline

> **TODO:** Total person-days for the `moderate` option were not provided. The milestone sequence below is correct; populate durations once the estimate is confirmed and team size is known.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Discovery complete; compatibility report produced | Phase 0 | TODO | TODO |
| Build compiles cleanly under JDK 11 | Phase 1 | TODO | TODO |
| Full test suite green under JDK 11 in staging | Phase 2 | TODO | TODO |
| Full test suite green under JDK 17 in staging | Phase 3 | TODO | TODO |
| Full test suite green under JDK 21 in staging | Phase 4 | TODO | TODO |
| Performance baseline validated on Java 21 | Phase 4 | TODO | TODO |
| Production cutover to Java 21 complete | Phase 5 | TODO | TODO |
| Java 8 infrastructure decommissioned | Phase 5 | TODO | TODO |

---

*Document status: DRAFT — multiple TODO items require resolution from codebase access, confirmed tech analysis, and infrastructure inventory before this plan can be finalized.*