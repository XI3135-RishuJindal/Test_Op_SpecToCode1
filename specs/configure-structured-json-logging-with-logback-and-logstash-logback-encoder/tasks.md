# TASKS: Configure Structured JSON Logging with Logback and logstash-logback-encoder

## Prerequisites

- [ ] [XS] Confirm Java runtime version and build tool (Maven `pom.xml` or Gradle `build.gradle` / `build.gradle.kts`) are present in the repository root
- [ ] [XS] Verify Logback is already on the classpath (either via `ch.qos.logback:logback-classic` direct dependency or transitively through a framework such as Spring Boot's `spring-boot-starter-logging`)
- [ ] [XS] Confirm write access to the repository and ability to open pull requests against the main branch
- [ ] [XS] Ensure a local environment can run the application and execute existing tests to establish a pre-migration baseline

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feature/structured-json-logging` from the current default branch
- [ ] [S] Audit existing logging configuration — locate all active Logback config files (`logback.xml`, `logback-spring.xml`, `logback-test.xml`) across `src/main/resources` and `src/test/resources` and document current appenders, encoders, and log patterns
- [ ] [XS] Record the current `logstash-logback-encoder` version available on Maven Central (latest stable, e.g. `7.4`) and the current `logback-classic` version in use, and note them in a comment at the top of the dependency block
- [ ] [XS] Capture a pre-migration sample log output (plain-text format) to a file `docs/logging-baseline.txt` for regression comparison in Phase 3

---

## Phase 2 — Core Upgrade

- [ ] [S] Add `net.logstash.logback:logstash-logback-encoder` dependency at the confirmed version in the build file (`pom.xml` `<dependencies>` block **or** `build.gradle` / `build.gradle.kts` `dependencies {}` block), scoped to `runtime` (Maven: `<scope>runtime</scope>`; Gradle: `runtimeClasspath`)
- [ ] [M] Replace the existing `<encoder>` (or `<layout>`) element in the primary appender inside `src/main/resources/logback.xml` (or `logback-spring.xml`) with `<encoder class="net.logstash.logback.encoder.LogstashEncoder">`, removing the legacy `<pattern>` child element
- [ ] [S] Configure `LogstashEncoder` with required custom fields inside `logback.xml` / `logback-spring.xml`: add `<customFields>{"service":"<app-name>","env":"${ENV:-local}"}</customFields>` and set `<includeCallerData>false</includeCallerData>` to control performance
- [ ] [S] Add a `<throwableConverter>` using `net.logstash.logback.stacktrace.ShortenedThrowableConverter` inside the `LogstashEncoder` block in `logback.xml` / `logback-spring.xml` to produce structured stack traces with `<maxDepthPerCause>` and `<rootCauseFirst>true</rootCauseFirst>`
- [ ] [S] Update `src/test/resources/logback-test.xml` (if present) to retain a human-readable `PatternLayoutEncoder` for local test output while keeping the production config JSON-only — ensure the test config references a separate `ConsoleAppender` with a plain `<pattern>`
- [ ] [XS] Remove or comment out any now-redundant `<pattern>` or `<layout>` elements left in `logback.xml` / `logback-spring.xml` after the encoder swap to prevent duplicate configuration warnings at startup

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full existing test suite locally and confirm zero new test failures introduced by the logging config change; record results in a comment on the PR
- [ ] [S] Start the application locally, trigger at least one log statement at each level (TRACE/DEBUG/INFO/WARN/ERROR), capture output to `docs/logging-sample-json.txt`, and manually verify each line is valid JSON containing `@timestamp`, `level`, `message`, `logger_name`, and the custom `service` field
- [ ] [XS] Validate that exception log entries contain a structured `stack_trace` field (not a raw multi-line string) by deliberately triggering a logged exception and inspecting the JSON output
- [ ] [XS] Confirm no plain-text log lines appear in the production appender output by grepping the sample output: `grep -v '^{' docs/logging-sample-json.txt` should return no lines

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g. `.github/workflows/build.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`) to ensure the build step resolves the new `logstash-logback-encoder` artifact from the configured artifact repository (Maven Central or internal Nexus/Artifactory mirror)
- [ ] [XS] If a Docker image is used, verify the base image's filesystem has no volume mount or log-shipper config that expects plain-text log format; update any `CMD`/`ENTRYPOINT` log-path references in `Dockerfile` if the log destination changes

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CHANGELOG.md` with an entry under the current version describing the switch to structured JSON logging via `logstash-logback-encoder`, listing the new dependency version and any removed configuration keys
- [ ] [S] Update or create a `docs/logging.md` runbook section documenting: the JSON field schema, how to add MDC fields, how to override log level per package via environment variable, and how to revert to plain-text locally using `logback-test.xml`
- [ ] [XS] Open the pull request for `feature/structured-json-logging`, link the baseline file `docs/logging-baseline.txt` and sample `docs/logging-sample-json.txt` in the PR description for reviewer comparison
- [ ] [XS] After merge, monitor the first deployment's log output in the target environment to confirm the log aggregation pipeline (e.g. Logstash, Fluentd, CloudWatch) correctly parses the JSON fields without errors