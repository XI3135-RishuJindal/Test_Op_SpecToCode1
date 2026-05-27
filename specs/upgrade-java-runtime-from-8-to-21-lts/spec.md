# Spec: Upgrade Java Runtime from 8 to 21 (LTS)

## Summary

This spec covers the upgrade of the Java runtime from version 8 to version 21 (LTS). The goal is to move the application off an end-of-life Java release onto a supported long-term support release, restoring access to security patches, modern language features, and improved runtime performance. The expected outcome is a fully operational application running on Java 21 with all existing functionality preserved and CI/CD pipelines validated against the new runtime.

---

## Motivation

- **End-of-Life status:** Oracle Java 8 public updates ended in March 2022 (non-commercial). OpenJDK 8 community support is in extended/diminishing maintenance. Running on an EOL runtime creates unpatched security exposure.
- **Security risk:** Java 8 no longer receives routine CVE patches from most vendors, leaving the runtime surface unaddressed for newly disclosed vulnerabilities.
- **Upgrade urgency:** Medium — the application is not in immediate crisis, but continued operation on Java 8 increases risk over time and blocks adoption of modern libraries and frameworks that have dropped Java 8 support.
- **Java 21 LTS benefits:** Java 21 is the current LTS release with Oracle Premier Support through September 2031. It includes significant performance improvements (e.g., virtual threads via Project Loom, improved GC), security hardening, and language enhancements accumulated across Java 9–21.
- **Ecosystem compatibility:** Many third-party libraries and frameworks have deprecated or removed Java 8 support. Staying on Java 8 increasingly constrains dependency upgrade paths.

---

## Current State

> **Note:** The provided tech analysis does not specify the build tool, framework, or codebase details. The items below represent the known baseline; specifics are marked TODO.

| Attribute | Current Value |
|---|---|
| Java version | 8 |
| Build tool | TODO — not identified in tech analysis |
| Application framework(s) | TODO — not identified in tech analysis |
| CI/CD runtime target | TODO — not identified in tech analysis |
| Deployment runtime (JRE/JDK) | TODO — not identified in tech analysis |
| Key APIs in use | TODO — not identified in tech analysis |

**Known Java 8 behaviours relevant to this upgrade:**

- The application is compiled and run targeting Java 8 bytecode (`--source 8 / --target 8` or equivalent).
- The application may use APIs removed or encapsulated between Java 9 and Java 21 (e.g., `sun.*` internal APIs, `javax.*` packages moved to `jakarta.*`, deprecated reflection access).
- The strong encapsulation of JDK internals introduced in Java 9 and enforced by default from Java 16+ may affect runtime behaviour.
- The module system (JPMS) introduced in Java 9 may require classpath/module-path adjustments.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Java runtime version | Java 8 | Java 21 (LTS) | Y |
| Bytecode target level | Java 8 (`class` version 52) | Java 21 (`class` version 65) | Y — binaries are not backward compatible to Java 8 JREs |
| Build tool JDK requirement | JDK 8 | JDK 21 | Y |
| CI/CD pipeline JDK | JDK 8 | JDK 21 | Y |
| Deployment environment JRE/JDK | JRE/JDK 8 | JRE/JDK 21 | Y |
| Removed/encapsulated JDK internal API usage | Permitted via `--illegal-access` (Java 9–15) or open by default (Java 8) | Strongly encapsulated; access denied by default | Y — requires code or dependency changes |
| Deprecated API usage (Java 9–21 removals) | May be in use | Must be replaced with supported alternatives | Y — compile or runtime errors if not addressed |
| Build tool configuration (version/plugin compatibility) | TODO | TODO — must be validated for Java 21 compatibility | TODO |
| Framework dependencies | TODO | TODO — must be validated/upgraded for Java 21 support | TODO |
| Third-party library versions | TODO | TODO — libraries dropping Java 8 support may need upgrading | TODO |

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Strong encapsulation of JDK internals (e.g., `sun.*`, `com.sun.*` APIs) | Runtime `InaccessibleObjectException` or compile errors | Replace usages with supported public APIs; or, for third-party libraries, upgrade to versions that have removed internal API dependencies |
| Removal of `java.xml.bind` (JAXB), `java.activation`, `java.corba`, `java.transaction` modules (removed in Java 11) | `ClassNotFoundException` / `NoClassDefFoundError` at runtime | Add the corresponding standalone dependencies explicitly (e.g., `jakarta.xml.bind-api` + implementation) |
| Removal of `javax.annotation` from default classpath (Java 9+) | Compile/runtime errors for `@PostConstruct`, `@PreDestroy`, etc. | Add `jakarta.annotation-api` as an explicit dependency |
| `SecurityManager` deprecated (Java 17) and removed (Java 24 — not yet, but flagged) | Warnings in Java 17–21; removal in a future release | Audit and remove or replace `SecurityManager` usage now to avoid future breakage |
| Reflection access restrictions (JPMS strong encapsulation) | Libraries using deep reflection may fail | Upgrade affected libraries to JPMS-aware versions; avoid `--add-opens` as a permanent fix |
| `Thread.stop()`, `Thread.suspend()`, `Thread.resume()` removed (Java 20) | Runtime `UnsupportedOperationException` | Replace with cooperative cancellation patterns (e.g., `interrupt()`) |
| `finalize()` method deprecation (for removal) | Warnings; eventual removal in future LTS | Replace with `Cleaner` API or `try-with-resources` |
| Build tool / plugin compatibility with Java 21 | Build failures if plugins target Java 8 toolchains only | TODO — specific plugins not identified; audit required |
| Framework compatibility with Java 21 | TODO | TODO — framework not identified; compatibility matrix must be checked |
| Third-party library compatibility | TODO | TODO — dependency list not provided; full audit required |
| GC behaviour changes (default GC changed from Parallel GC in Java 8 to G1GC in Java 9+) | Potential change in memory/throughput characteristics | Benchmark and tune GC settings post-upgrade; G1GC is generally preferable but may require heap tuning |

---

## Acceptance Criteria

1. **Given** the project build configuration targets Java 21, **when** a full build is executed, **then** the build completes without errors or warnings related to illegal reflective access, removed APIs, or incompatible bytecode targets.

2. **Given** the application is packaged and deployed on a Java 21 JRE/JDK, **when** the application starts, **then** it reaches a healthy/ready state with no `InaccessibleObjectException`, `NoClassDefFoundError`, or `ClassNotFoundException` errors in the startup logs.

3. **Given** the full automated test suite (unit, integration), **when** executed against the Java 21 runtime, **then** all tests that passed on Java 8 continue to pass with no regressions introduced by the runtime upgrade.

4. **Given** the CI/CD pipeline is configured to use JDK 21, **when** a pull request or main-branch build is triggered, **then** the pipeline completes successfully end-to-end (build, test, package).

5. **Given** the application is running on Java 21, **when** the application processes its standard workload, **then** no `java.lang.reflect.InaccessibleObjectException` or strong-encapsulation-related errors appear in application logs.

6. **Given** any previously used `sun.*` or `com.sun.*` internal API references, **when** the codebase is compiled against JDK 21, **then** zero compilation errors or warnings referencing internal APIs are present.

7. **Given** the deployment environment, **when** the Java version is queried at runtime, **then** the reported version is Java 21.

8. **Given** the application's external interfaces (APIs, message formats, data outputs — TODO: specify), **when** exercised on Java 21, **then** all outputs are byte-for-byte or semantically equivalent to those produced on Java 8 (no behavioural regressions).

9. **Given** no `--illegal-access` JVM flags are present in startup configuration, **when** the application runs on Java 21, **then** the application operates correctly (Java 21 does not support `--illegal-access`; its presence must be removed).

10. **Given** the upgraded application, **when** a static analysis scan is run for deprecated-for-removal APIs (Java 9–21 deprecation list), **then** zero usages of APIs scheduled for removal in Java 25 or earlier are present.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the build tool and version (Maven, Gradle, Ant, other)? This determines plugin compatibility requirements. | TODO | TODO |
| 2 | What application framework(s) are in use (Spring Boot, Jakarta EE, Quarkus, other)? Framework-specific migration steps depend on this. | TODO | TODO |
| 3 | What is the full list of third-party dependencies and their current versions? A dependency audit is required to identify Java 21 incompatibilities. | TODO | TODO |
| 4 | What JDK distribution will be standardised on for Java 21 (Eclipse Temurin, Oracle JDK, Amazon Corretto, Microsoft Build of OpenJDK, other)? | TODO | TODO |
| 5 | Are there any uses of `sun.*` / `com.sun.*` internal APIs in the application source code? | TODO | TODO |
| 6 | Is `SecurityManager` used anywhere in the application or its configuration? | TODO | TODO |
| 7 | What are the deployment targets (containers, VMs, PaaS)? Base images or platform runtimes may need to be updated independently. | TODO | TODO |
| 8 | Are there any native libraries (JNI) or agents (Java agents, JVMTI) in use that may not be compatible with Java 21? | TODO | TODO |
| 9 | Is there a performance baseline established on Java 8 against which Java 21 runtime behaviour should be benchmarked? | TODO | TODO |
| 10 | Are there any compliance or certification requirements (e.g., FIPS) that constrain the choice of JDK distribution or configuration? | TODO | TODO |