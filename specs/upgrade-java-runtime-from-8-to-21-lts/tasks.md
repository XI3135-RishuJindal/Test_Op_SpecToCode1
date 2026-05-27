# Tasks: Upgrade Java Runtime from 8 to 21 (LTS)

> **Scope:** Java runtime upgrade from version 8 to 21 (LTS).
> **Note:** Build tool, frameworks, and specific file paths were not provided in the tech analysis. Tasks below use the most common Java project conventions (Maven `pom.xml` / Gradle `build.gradle`). Adjust file references to match your actual project structure before assigning work.

---

## Prerequisites

- [ ] [XS] Confirm local developer JDK 21 installation (e.g., Eclipse Temurin 21 LTS) is available on all developer machines before branch work begins
- [ ] [XS] Confirm CI runner images support JDK 21 — verify runner OS and available Java versions in CI platform settings
- [ ] [XS] Confirm repository write access and branch protection rules allow the upgrade branch to be created and merged via PR

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated upgrade branch (e.g., `upgrade/java-8-to-21`) from the main branch and confirm it builds cleanly on Java 8 before any changes are made
- [ ] [S] Capture the full test suite baseline on Java 8 — record pass/fail counts, skipped tests, and any pre-existing failures in a `docs/java-upgrade-baseline.md` file so regressions can be identified objectively
- [ ] [M] Run a dependency compatibility audit against Java 21 — use `mvn dependency:tree` or `gradle dependencies` and cross-reference each dependency version against its Java 21 compatibility matrix; document findings in `docs/java-upgrade-baseline.md`
- [ ] [S] Identify all uses of removed or deprecated Java 8–17 APIs in the codebase — run `javac --release 21` (or equivalent) with `-Xlint:deprecation` and `-Xlint:removal` flags and capture the full compiler output for use in Phase 2
- [ ] [XS] Add a CI gate on the upgrade branch that fails the build if the Java version is not 21, preventing accidental merges under the wrong runtime

---

## Phase 2 — Core Upgrade

- [ ] [S] Update the Java source and target compiler version to 21 in the build configuration file (`pom.xml` `<maven.compiler.source>` / `<maven.compiler.target>` properties, or `build.gradle` `sourceCompatibility` / `targetCompatibility` settings)
- [ ] [S] Replace any explicit `--add-opens` or `--add-exports` JVM flags used to work around strong encapsulation in Java 9–17 — audit `JAVA_TOOL_OPTIONS`, startup scripts, and `surefire`/`test` JVM args; remove flags that are no longer needed or replace with proper API usage
- [ ] [M] Resolve all removed-API compilation errors identified in Phase 1 — common removals between Java 8 and 21 include `sun.misc.BASE64Encoder/Decoder` (replace with `java.util.Base64`), `javax.*` packages moved to `jakarta.*` (if applicable), and deprecated `Thread.stop()`/`Thread.destroy()` calls
- [ ] [M] Resolve all strong-encapsulation runtime warnings and errors — replace reflective access to JDK internals flagged during the Phase 1 audit with supported public APIs
- [ ] [S] Update any code using `Runtime.exec()` or `ProcessBuilder` patterns that relied on Java 8 behavior changes documented in the compiler output from Phase 1
- [ ] [XS] Update the `release` or `toolchain` version in the build configuration to target Java 21 (e.g., `maven-toolchains-plugin` `<jdk><version>21</version></jdk>`, or Gradle toolchains `languageVersion = JavaLanguageVersion.of(21)`)

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full unit and integration test suite under JDK 21 and compare results against the baseline captured in `docs/java-upgrade-baseline.md` — investigate and resolve any new failures
- [ ] [S] Execute any existing performance or load tests under JDK 21 and compare throughput/latency metrics against the Java 8 baseline — document results in `docs/java-upgrade-baseline.md`
- [ ] [XS] Verify that no test is silently skipped due to JDK version guards (e.g., `assumeTrue(javaVersion < 9)` style conditions) that would mask regressions on Java 21
- [ ] [S] Perform a manual smoke test of the application's critical paths on Java 21 in a local or dev environment and confirm expected behavior

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or equivalent) to use a JDK 21 build image — replace any `java-version: 8` or `openjdk:8` references with `java-version: 21` / `eclipse-temurin:21`
- [ ] [S] Update any `Dockerfile` or container base images that reference `openjdk:8`, `adoptopenjdk:8`, or equivalent — replace with `eclipse-temurin:21-jre` (or `-jdk` as appropriate) and verify the image builds and the application starts correctly
- [ ] [XS] Update any JVM startup flags in deployment configuration files (e.g., environment variable files, Helm values, systemd unit files) to remove Java 8–specific flags (e.g., `-XX:+UseConcMarkSweepGC`, which was removed in Java 14) and add Java 21–appropriate equivalents if needed

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry documenting the Java 8 → 21 upgrade, listing any removed APIs replaced, dependency version changes, and JVM flag changes
- [ ] [S] Review and update the project `README` and any developer setup guides that reference Java 8 installation or `JAVA_HOME` configuration — replace with Java 21 instructions
- [ ] [XS] Update any `CONTRIBUTING.md` or onboarding documentation that specifies the required Java version for local development
- [ ] [S] Coordinate a staged rollout — deploy to a non-production environment first, monitor application logs and JVM metrics (GC pause times, heap usage, thread counts) for at least one full business cycle before promoting to production
- [ ] [XS] Set up or confirm post-deployment monitoring alerts for JVM-level anomalies (unexpected GC behavior, `ClassNotFoundException`, `InaccessibleObjectException`) in the production observability tooling after rollout