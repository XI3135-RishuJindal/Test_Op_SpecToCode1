# Spec: Add Structured JSON Logging

## Summary

This spec covers the addition of structured JSON logging to replace or augment the existing logging implementation. The expected outcome is that all application log output is emitted as machine-readable JSON objects, enabling downstream log aggregation, search, and alerting tooling to parse log fields without relying on fragile regex-based text parsing.

## Motivation

- **Operational observability:** Unstructured text logs cannot be reliably queried or aggregated by log management platforms (e.g., Elasticsearch, Splunk, Datadog, CloudWatch Logs Insights). Structured JSON logging is a prerequisite for field-level filtering and alerting.
- **Upgrade urgency:** Medium — current unstructured logging is a source of ongoing operational tech debt, increasing mean time to diagnose incidents.
- **Consistency:** Without a defined log schema, different parts of the application emit logs in inconsistent formats, making cross-service correlation difficult.
- **Compliance readiness:** Structured logs with defined fields (timestamp, severity, correlation ID, etc.) are commonly required for audit trail and compliance reporting.

> **Note:** Specific framework versions, CVEs, and runtime details were not provided in the tech analysis. Version-specific references are marked TODO below.

## Current State

- **Logging format:** TODO — confirm whether current logs are plain text, a mix of formats, or partially structured.
- **Logging library/framework:** TODO — identify the specific logging library in use (e.g., log4j, Winston, Python logging, slog, etc.) and its current version.
- **Log destinations:** TODO — confirm current log sinks (stdout, file, syslog, external service).
- **Existing log call sites:** TODO — enumerate the modules, classes, or packages that currently emit log statements.
- **Log levels in use:** TODO — confirm which severity levels are actively used (e.g., DEBUG, INFO, WARN, ERROR, FATAL).
- **Contextual fields:** TODO — document any fields currently attached to log entries (e.g., request ID, user ID, service name).

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Log output format | Unstructured plain text (TODO: confirm exact format) | JSON object per log line | Y — any consumer parsing raw text must be updated |
| Log schema | None defined | Defined JSON schema with required fields (see below) | Y — new field contract |
| Logging library configuration | TODO: current config | Configured to emit JSON | N (internal change) |
| Log level field | Embedded in text string | Dedicated `level` key in JSON object | Y |
| Timestamp field | TODO: confirm current format | ISO 8601 timestamp in dedicated `timestamp` key | Y |
| Contextual/correlation fields | TODO: confirm current state | Structured keys (e.g., `correlation_id`, `service`, `environment`) | N (additive) |
| Human-readable console output (dev mode) | TODO | TODO — decide whether to retain pretty-print in development | TODO |

**Minimum required JSON log schema fields:**

| Field | Type | Description |
|---|---|---|
| `timestamp` | string (ISO 8601) | Time the log entry was created |
| `level` | string | Severity level (DEBUG, INFO, WARN, ERROR, FATAL) |
| `message` | string | Human-readable log message |
| `service` | string | Name of the emitting service |
| `correlation_id` | string | Request or trace correlation identifier |
| `environment` | string | Runtime environment (e.g., production, staging) |

> Additional fields are permitted; the above are the minimum required set.

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Log output is now JSON instead of plain text | Any log shipper, parser, or alert rule that matches on raw text format will break | Update log shipper/parser configuration to parse JSON fields; update alert rules to use field-based queries |
| `level` is now a discrete JSON key, not embedded in message text | Text-based log level filters will stop matching | Update filters to query the `level` JSON field |
| `timestamp` format may change | Downstream time-based queries may break if format changes | TODO — confirm current timestamp format and define migration for existing dashboards/queries |
| Log line structure changes | Any tooling that splits log lines by position or delimiter will break | TODO — audit all log consumers and update parsing logic |
| Development console output format | Developers relying on human-readable output may find JSON harder to read locally | TODO — decide whether to provide a dev-mode pretty-printer toggle |

## Acceptance Criteria

1. **Given** the application is running, **when** any log statement is emitted at any severity level, **then** the output is a single-line valid JSON object parseable by a standard JSON parser.

2. **Given** a log entry is emitted, **when** the JSON object is inspected, **then** it contains at minimum the fields: `timestamp`, `level`, `message`, `service`, `environment`, and `correlation_id`.

3. **Given** a log entry is emitted, **when** the `timestamp` field is inspected, **then** its value conforms to ISO 8601 format.

4. **Given** a log entry is emitted at each supported severity level (DEBUG, INFO, WARN, ERROR, FATAL), **when** the `level` field is inspected, **then** it contains the exact string representation of that severity level.

5. **Given** an inbound request carries a correlation/trace identifier, **when** a log entry is emitted during that request's handling, **then** the `correlation_id` field in the JSON log entry matches the inbound identifier.

6. **Given** an exception or error is logged, **when** the JSON log entry is inspected, **then** the error message and stack trace (if applicable) are captured in defined, consistent JSON fields rather than concatenated into the `message` string.

7. **Given** the application emits logs under concurrent load, **when** log output is inspected, **then** each line is a complete, individually valid JSON object with no interleaved or truncated output.

8. **Given** a CI pipeline run, **when** the log output of the test suite is parsed by a JSON parser, **then** zero parse errors are reported across all emitted log lines.

9. **Given** the structured logging change is deployed, **when** existing log-based alerts and dashboards are reviewed, **then** all alerts have been updated to use field-based queries and confirmed operational (no silent failures). *(TODO: define specific alert inventory as acceptance gate.)*

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current logging library and version in use? | TODO | TODO |
| 2 | What is the current log output format (exact structure)? | TODO | TODO |
| 3 | What log sinks/consumers exist that will be affected by the format change? | TODO | TODO |
| 4 | Should a human-readable (pretty-print) mode be retained for local development? | TODO | TODO |
| 5 | What is the full inventory of required JSON schema fields beyond the minimum set? | TODO | TODO |
| 6 | Are there any compliance or audit requirements that mandate specific field names or formats? | TODO | TODO |
| 7 | How should multi-line content (e.g., stack traces) be handled — escaped within a single JSON field or split across lines? | TODO | TODO |
| 8 | What is the rollout strategy — big-bang replacement or gradual migration per module? | TODO | TODO |
| 9 | Who owns the update of downstream log consumers (dashboards, alerts, shippers)? | TODO | TODO |