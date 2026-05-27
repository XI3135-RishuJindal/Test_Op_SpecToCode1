# SPEC: Configure Structured JSON Logging with Logback and logstash-logback-encoder

---

## Summary

This spec covers the configuration of structured JSON logging for the application by integrating Logback as the logging framework with the `logstash-logback-encoder` library as the JSON encoder. The expected outcome is that all application log output is emitted as machine-readable, structured JSON objects — replacing any existing plain-text or unstructured log format — enabling downstream log aggregation, search, and alerting tooling (e.g., ELK stack, Splunk, Datadog) to parse log events without custom regex patterns.

---

## Motivation

- **Operational observability:** Plain-text log formats are not reliably parseable by log aggregation platforms, leading to degraded search, alerting, and tracing capabilities in production environments.
- **Structured context propagation:** Unstructured logs cannot carry consistent machine-readable fields (e.g., correlation IDs, trace IDs, user context) across service boundaries, increasing mean time to diagnose (MTTD) incidents.
- **Industry standard alignment:** JSON-structured logging is the de facto standard for containerised and cloud-native deployments; the current format creates operational tech debt.
- **Upgrade urgency:** Rated **medium** — no active CVE or hard EOL deadline is blocking, but the absence of structured logging is a recognised tech debt item that increases operational risk over time.
- **Specific version targets:** TODO — exact versions of `logstash-logback-encoder` and Logback to be confirmed from the project's dependency resolution (see Open Questions).

---

## Current State

The current logging configuration and behaviour are not fully specified in the provided context. The following represents the assumed baseline that this change targets:

- **Log format:** TODO — confirm whether current output is plain-text pattern layout (e.g., `%d{ISO8601} %-5level [%thread] %logger{36} - %msg%n`) or another format.
- **Logging framework:** TODO — confirm Logback is already on the classpath (e.g., via `spring-boot-starter-logging` or explicit dependency) or must be added.
- **Configuration file:** TODO — confirm whether a `logback.xml`, `logback-spring.xml`, or programmatic configuration currently exists.
- **Appenders in use:** TODO — identify existing appenders (console, file, syslog, etc.) that must be migrated or replaced.
- **MDC usage:** TODO — identify any existing Mapped Diagnostic Context (MDC) keys that must be preserved as JSON fields in the new format.
- **Log levels:** TODO — document current root and per-package log level configuration that must be carried forward unchanged.

---

## Proposed Changes

### Overview

The change introduces `logstash-logback-encoder` as the JSON serialisation layer for Logback, replacing the existing pattern-based encoder on all appenders. No changes to application logging call sites (e.g., `Logger.info(...)`) are required.

### Component Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Log encoder / layout | Plain-text `PatternLayout` or equivalent | `LogstashEncoder` (JSON) from `logstash-logback-encoder` | Y — log format changes; any consumer parsing plain-text logs will break |
| Logback configuration file | Existing pattern-based appender config | Updated appender(s) using `LogstashEncoder` | Y — configuration file is replaced/modified |
| Console appender | Outputs human-readable text | Outputs JSON objects, one per line | Y — human readability reduced in local dev (see mitigation below) |
| File appender (if present) | Plain-text log file | JSON log file | Y — existing log file parsers/scripts must be updated |
| `logstash-logback-encoder` dependency | Not present | Added at TODO version | N — additive dependency |
| MDC fields | Embedded in text pattern or absent | Automatically serialised as top-level JSON fields | N — behaviour is additive/improved |
| Logback version | TODO — confirm current version | TODO — confirm target version compatible with chosen encoder version | TODO — confirm if version bump is required |

### What Is Added

- Dependency on `logstash-logback-encoder` at TODO version.
- Logback configuration declaring one or more appenders using `LogstashEncoder` or `LoggingEventCompositeJsonEncoder`.
- Standard JSON fields in every log event: `@timestamp`, `@version`, `level`, `logger_name`, `thread_name`, `message`, `stack_trace` (on exceptions).
- All existing MDC keys surfaced as top-level JSON fields.

### What Is Removed

- Pattern-based encoder strings from appender configuration.
- Any custom log formatting utilities that exist solely to structure plain-text output (TODO — confirm existence).

### What Is Unchanged

- Logger names, log levels, and appender targets (console, file, etc.) — only the encoding changes.
- Application source code logging call sites.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path for Callers |
|---|---|---|
| Log output format changes from plain-text to JSON | Any script, monitoring rule, or log shipper that parses plain-text patterns will fail | Update log shipper configuration (e.g., Filebeat, Fluentd) to parse JSON; update any grep/awk scripts that parse log files |
| Console output is no longer human-readable by default | Developer experience degraded in local environments | TODO — decide whether to provide a separate `logback-spring.xml` profile that uses plain-text for `local`/`dev` Spring profiles, or recommend a JSON-pretty-print CLI tool |
| Log file format changes (if file appender exists) | Existing archived log files remain in old format; new files are JSON | Document the format boundary (timestamp of cutover); update any log analysis tooling |
| Field names change (e.g., `level` vs `LEVEL`, timestamp format) | Dashboards or alerts keyed on old field names will break | TODO — audit existing Kibana/Splunk/Datadog dashboards and update field references to match `logstash-logback-encoder` default schema |
| Exception stack traces serialised as JSON string field | Stack trace parsers expecting multi-line plain-text will not match | Update any alerting rules that match on multi-line stack trace patterns |

---

## Acceptance Criteria

1. **Given** the application is started, **when** any log statement is emitted at any level, **then** each log line written to the console appender is a single, valid JSON object parseable without error by a standard JSON parser.

2. **Given** a log event is emitted, **when** the JSON output is inspected, **then** it contains at minimum the fields: `@timestamp` (ISO-8601 format), `level`, `logger_name`, `thread_name`, and `message`.

3. **Given** an exception is logged via `logger.error("msg", exception)`, **when** the JSON output is inspected, **then** the output contains a `stack_trace` field (or equivalent) with the full exception stack trace as a string value within the JSON object — not as additional plain-text lines outside the JSON structure.

4. **Given** an MDC key-value pair is set before a log statement is emitted, **when** the JSON output is inspected, **then** the MDC key appears as a top-level field in the JSON object with the correct value.

5. **Given** the application is running, **when** log output is piped to a log aggregation tool configured for JSON ingestion (e.g., Filebeat with JSON codec), **then** each log event is indexed as a structured document with no parsing errors.

6. **Given** the existing log levels and logger name configuration, **when** the application starts with the new Logback configuration, **then** the effective log levels for all named loggers are identical to those in the pre-migration configuration, verified by emitting a test log at each configured level and confirming presence or absence in output.

7. **Given** a CI pipeline build, **when** the build and test suite execute, **then** no `ClassNotFoundException`, `NoSuchMethodError`, or dependency conflict errors related to Logback or `logstash-logback-encoder` are present in build output.

8. **Given** the application runs under load, **when** log volume is high, **then** log output contains no interleaved partial JSON objects (i.e., each line is a complete, self-contained JSON object), confirming thread-safe encoding.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current Logback version on the classpath? This determines whether a Logback version upgrade is needed to satisfy `logstash-logback-encoder` compatibility requirements. | TODO | TODO |
| 2 | What is the target version of `logstash-logback-encoder` to be adopted? (Latest stable as of writing is 7.x, but must be confirmed against runtime Java version and Logback version.) | TODO | TODO |
| 3 | What is the runtime environment (JVM version, container base image)? Required to confirm encoder version compatibility. | TODO | TODO |
| 4 | What is the build tool (Maven, Gradle)? Required to specify dependency declaration format in plan.md. | TODO | TODO |
| 5 | Does a `logback.xml` or `logback-spring.xml` already exist, or is logging configured programmatically or via framework auto-configuration? | TODO | TODO |
| 6 | Are there existing MDC keys in use that must be explicitly mapped or renamed in the JSON output? | TODO | TODO |
| 7 | Should a human-readable (plain-text) log profile be maintained for local development environments? If so, what is the mechanism (Spring profile, environment variable, separate config file)? | TODO | TODO |
| 8 | Are there existing log aggregation dashboards (Kibana, Splunk, Datadog, etc.) whose field mappings will break and must be updated as part of this change? | TODO | TODO |
| 9 | Is there a file appender in use, and if so, are log rotation and archival settings required to be preserved? | TODO | TODO |
| 10 | Are there any compliance or audit logging requirements that mandate specific fields or field formats in the JSON output? | TODO | TODO |