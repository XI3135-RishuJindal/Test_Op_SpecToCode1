# PLAN: Structured JSON Logging with Logback and logstash-logback-encoder

---

## Overview

**Migration Strategy: Feature-Flag Gated / Big-Bang (per environment)**

The logging configuration change is applied as a big-bang switch within each environment, gated by environment-specific Logback configuration profiles. Because logging is a cross-cutting concern with no business logic impact, the risk of a coordinated cutover is low. The strangler-fig pattern is not applicable here — logging backends are not incrementally replaceable at the statement level.

**Justification:**
- Structured JSON logging is a configuration-layer change (Logback XML + dependency addition); no application source code changes are required in the typical case.
- Rollback is immediate: revert the Logback configuration file and remove the encoder dependency.
- Risk score is **medium** (per tech analysis); the effort is modest and self-contained.
- Each environment (local dev, CI, staging, production) can adopt the JSON appender independently by activating the appropriate Logback configuration file or Spring profile, providing a natural progressive rollout without requiring a formal strangler-fig decomposition.

> **NOTE:** Because the tech analysis did not supply runtime, build tool, or framework specifics, several sections below are marked **TODO** where environment-specific details are required.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Dependency Addition | Add `logstash-logback-encoder` to the build descriptor; verify transitive Logback version compatibility | None | TODO person-days (derive from moderate option once supplied) |
| 2 — Logback Configuration | Author `logback-spring.xml` (or `logback.xml`) with a `LogstashEncoder`-backed `ConsoleAppender` and/or `RollingFileAppender`; define environment profiles | Phase 1 complete | TODO |
| 3 — Custom Fields & MDC | Define standard MDC keys (e.g., `traceId`, `spanId`, `userId`, `requestId`); add any `customFields` or `providers` to the encoder config | Phase 2 complete | TODO |
| 4 — Validation & CI Gate | Run log-output assertions in integration tests; confirm JSON schema in CI; update log-parsing rules in downstream tooling (e.g., Logstash pipeline, CloudWatch, Datadog) | Phase 3 complete | TODO |
| 5 — Production Cutover | Deploy to staging → validate → promote to production; decommission legacy plain-text appender | Phase 4 green | TODO |

---

## Component Changes

### 1. Build Descriptor

**TODO:** Build tool not identified in tech analysis. Apply the relevant snippet below.

**Maven (`pom.xml`):**
```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>TODO — see Dependency Upgrade Plan</version>
</dependency>
```

**Gradle (`build.gradle` / `build.gradle.kts`):**
```kotlin
implementation("net.logstash.logback:logstash-logback-encoder:TODO")
```

- **Files affected:** `pom.xml` **or** `build.gradle` / `build.gradle.kts`
- **APIs modified:** None — dependency addition only.

---

### 2. Logback Configuration File

**Target file:** `src/main/resources/logback-spring.xml` (preferred when Spring Boot is present) **or** `src/main/resources/logback.xml`.

**Structural change:** Replace or supplement the existing `PatternLayoutEncoder` with `LogstashEncoder`.

**Reference configuration:**
```xml
<configuration>

  <!-- Human-readable appender for local development -->
  <springProfile name="!production,!staging">
    <appender name="CONSOLE_PLAIN" class="ch.qos.logback.core.ConsoleAppender">
      <encoder>
        <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
      </encoder>
    </appender>
    <root level="INFO">
      <appender-ref ref="CONSOLE_PLAIN"/>
    </root>
  </springProfile>

  <!-- Structured JSON appender for staging and production -->
  <springProfile name="staging,production">
    <appender name="CONSOLE_JSON" class="ch.qos.logback.core.ConsoleAppender">
      <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <!-- Rename default fields to match your log platform schema -->
        <fieldNames>
          <timestamp>timestamp</timestamp>
          <message>message</message>
          <logger>logger</logger>
          <thread>thread</thread>
          <level>level</level>
          <levelValue>[ignore]</levelValue>
        </fieldNames>
        <!-- Static custom fields -->
        <customFields>{"service":"TODO_SERVICE_NAME","env":"${ENVIRONMENT:-unknown}"}</customFields>
        <!-- Include MDC fields automatically -->
        <includeMdcKeyName>traceId</includeMdcKeyName>
        <includeMdcKeyName>spanId</includeMdcKeyName>
        <includeMdcKeyName>requestId</includeMdcKeyName>
        <includeMdcKeyName>userId</includeMdcKeyName>
      </encoder>
    </appender>
    <root level="INFO">
      <appender-ref ref="CONSOLE_JSON"/>
    </root>
  </springProfile>

</configuration>
```

- **Files affected:** `src/main/resources/logback-spring.xml` (create or modify), `src/main/resources/logback.xml` (remove or retain as fallback — **TODO:** confirm which file is currently active).
- **APIs modified:** None at the Java/Kotlin source level unless MDC population is added (see Phase 3).

---

### 3. MDC Population (Phase 3)

If request-scoped fields (`traceId`, `requestId`, etc.) are not already placed into `org.slf4j.MDC`, a servlet filter or interceptor must be added or modified.

- **TODO:** Identify existing filter/interceptor class names from codebase (not provided in context).
- **Pattern:**
```java
MDC.put("requestId", UUID.randomUUID().toString());
try {
    chain.doFilter(request, response);
} finally {
    MDC.clear();
}
```
- **Files affected:** TODO — existing request filter class.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `net.logstash.logback:logstash-logback-encoder` | Not present (new addition) | TODO — tech analysis did not specify; check [Maven Central](https://central.sonatype.com/artifact/net.logstash.logback/logstash-logback-encoder) for latest stable | N/A (new dep) | Requires Logback ≥ 1.2.x; verify transitive version does not conflict with existing Logback on classpath |
| `ch.qos.logback:logback-classic` | TODO — not provided in tech analysis | TODO — must be compatible with chosen `logstash-logback-encoder` version | TODO | If managed transitively by Spring Boot BOM, confirm BOM-managed version satisfies encoder's minimum requirement |
| `ch.qos.logback:logback-core` | TODO | TODO | TODO | Same as above |
| `org.slf4j:slf4j-api` | TODO | TODO | TODO | `logstash-logback-encoder` ≥ 7.x requires SLF4J 2.x; verify alignment with existing SLF4J version |

> **⚠️ All version numbers are marked TODO** because the tech analysis explicitly states versions are unknown. Do **not** substitute training-data guesses — resolve against the project's actual dependency tree (`mvn dependency:tree` or `gradle dependencies`).

---

## Infrastructure Changes

**Log Shipper / Aggregation Platform:**
- TODO — If a log shipper (Filebeat, Fluentd, Logstash agent) is deployed as a sidecar or DaemonSet, update its input codec from `plain` to `json` once the JSON appender is active in production.
- TODO — If logs are shipped to an external platform (Datadog, Splunk, CloudWatch Logs Insights, Elastic), update index mappings or parsing rules to reflect the new JSON field schema.

**Docker:**
- TODO — Base image not specified. No base image change is required for this task; Logback configuration is application-layer only.

**Kubernetes:**
- TODO — If `stdout` log collection is configured via a Kubernetes logging agent, update the agent's parser configuration to `json` format after cutover.

**CI/CD Pipeline:**
- Add a CI step (Phase 4) that asserts log output is valid JSON when the `staging` or `production` profile is active. See Testing Strategy for tooling details.
- TODO — CI platform not identified (GitHub Actions, Jenkins, GitLab CI, etc.).

**IaC:**
- TODO — Not mentioned in context.

---

## Rollback Strategy

Each phase is independently reversible.

### Phase 1 Rollback — Dependency Addition
1. Remove the `logstash-logback-encoder` dependency from `pom.xml` or `build.gradle`.
2. Run `mvn dependency:tree` / `gradle dependencies` to confirm removal.
3. Rebuild and redeploy.

### Phase 2 Rollback — Logback Configuration
1. Revert `logback-spring.xml` (or `logback.xml`) to the previous committed version via `git revert` or `git checkout <file>`.
2. Rebuild the artifact (configuration is bundled in the JAR/WAR).
3. Redeploy the previous artifact or the reverted build.
4. Confirm plain-text log output is restored in the target environment.

### Phase 3 Rollback — MDC Population
1. Revert the filter/interceptor class changes via `git revert`.
2. Rebuild and redeploy.
3. MDC fields will no longer appear in logs; no functional regression.

### Phase 4 Rollback — CI Gate
1. Remove or disable the JSON log assertion step from the CI pipeline configuration.
2. This does not affect running services.

### Phase 5 Rollback — Production Cutover
1. Activate the non-JSON Logback profile (e.g., set Spring profile back to a non-`production` value, or swap the active `logback.xml`).
2. Redeploy the previous artifact if a rollback build is required.
3. Notify the log aggregation team to revert parser/codec configuration to plain-text mode.
4. Verify log ingestion is restored in the aggregation platform.

---

## Testing Strategy

### Unit Tests
- **Goal:** Verify that log statements produce valid JSON when the JSON encoder is active.
- **Tool:** JUnit 5 + `ch.qos.logback:logback-classic` test utilities (`ListAppender<ILoggingEvent>`).
- **Approach:** Instantiate a `LogstashEncoder` in a test, encode a synthetic `ILoggingEvent`, and assert the output parses as valid JSON with expected fields (`message`, `level`, `timestamp`, `logger`).
- **Coverage target:** All custom MDC fields and `customFields` entries must appear in at least one test assertion.

```java
// Pseudocode sketch
LogstashEncoder encoder = new LogstashEncoder();
encoder.start();
byte[] encoded = encoder.encode(mockLoggingEvent);
JsonNode node = objectMapper.readTree(encoded);
assertThat(node.get("message").asText()).isEqualTo("expected message");
assertThat(node.get("traceId").asText()).isEqualTo("abc-123");
```

### Integration Tests
- **Goal:** Confirm that the running application emits JSON logs on `stdout`/`stderr` when the `staging` profile is active.
- **Tool:** TODO (depends on test framework — Spring Boot Test, Testcontainers, etc.).
- **Approach:** Capture `System.out` during an HTTP request cycle; assert the captured string is valid JSON and contains `requestId` from MDC.
- **CI gate:** Integration test suite must pass before Phase 5 (production cutover) is permitted.

### Regression Tests
- **Goal:** Confirm no log statements are silently dropped or malformed after the encoder change.
- **Approach:** Compare log event counts between the old plain-text run and the new JSON run for a representative workload (e.g., a smoke test suite).
- **Tool:** TODO — depends on log aggregation platform query capability.

### Performance Tests
- **Goal:** Confirm that JSON serialization overhead does not materially increase request latency or GC pressure.
- **Tool:** TODO (JMH microbenchmark for encoder throughput; load test tool such as Gatling or k6 for end-to-end latency).
- **Acceptance criterion:** p99 latency increase < 5% compared to baseline with plain-text encoder under equivalent load.
- **CI gate:** Performance regression check is advisory (non-blocking) in CI; blocking gate applied in staging load test before production promotion.

### CI Gates Summary

| Gate | Phase | Blocking? |
|------|-------|-----------|
| Unit tests pass | Phase 2 | Yes |
| JSON schema assertion (valid JSON output) | Phase 4 | Yes |
| Integration tests pass | Phase 4 | Yes |
| Performance regression < 5% p99 | Phase 5 (staging) | Yes |

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Dependency added and build verified | Phase 1 | TODO — derive from moderate effort estimate once person-days are supplied | TODO |
| `logback-spring.xml` authored and reviewed | Phase 2 | TODO | TODO |
| MDC population implemented and reviewed | Phase 3 | TODO | TODO |
| CI JSON assertion gate green | Phase 4 | TODO | TODO |
| Staging validation complete | Phase 5 | TODO | TODO |
| Production cutover complete | Phase 5 | TODO | TODO |

> **Note:** All timeline estimates are marked **TODO** because the upgrade option's person-days estimate was not provided (`moderate — details not provided`). Populate this table once the effort estimate is confirmed with the team.