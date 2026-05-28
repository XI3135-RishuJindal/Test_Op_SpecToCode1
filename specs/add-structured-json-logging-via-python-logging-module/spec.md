# Spec: Add Structured JSON Logging via Python Logging Module

## Summary

This spec covers the addition of structured JSON logging to the application using Python's built-in `logging` module. The expected outcome is that all application log output is emitted as machine-readable JSON objects, replacing any existing unstructured or plain-text log formatting. This enables downstream log aggregation, search, and alerting tooling to parse log fields reliably without fragile regex-based extraction.

## Motivation

- **Operational observability:** Plain-text logs cannot be reliably queried or aggregated by log management platforms (e.g., Datadog, Splunk, CloudWatch Logs Insights, Loki). Structured JSON logging is a prerequisite for field-level filtering and alerting.
- **Tech debt reduction:** Unstructured logging is identified as existing tech debt in the modernization analysis.
- **Upgrade urgency:** Rated **medium** — no immediate production outage risk, but the absence of structured logging increases mean time to diagnose incidents.
- **Consistency:** Standardising on Python's `logging` module ensures a single, well-understood logging interface across the codebase rather than ad-hoc `print` statements or multiple third-party logging libraries.

> **Note:** Specific CVEs, EOL dates, and framework versions are not applicable to this task. No runtime or build-tool version constraints were provided in the tech analysis.

## Current State

The current logging implementation details are not fully specified in the provided context. The following describes the assumed baseline; items marked TODO require confirmation during discovery.

- **Log format:** TODO — confirm whether logs are currently plain-text, semi-structured, or already partially JSON.
- **Log emission points:** TODO — identify all call sites using `print()`, `logging.basicConfig()`, custom handlers, or third-party logging libraries.
- **Existing handlers:** TODO — document any `StreamHandler`, `FileHandler`, or external sink configurations currently in place.
- **Log levels in use:** TODO — confirm which levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) are actively used.
- **Configuration mechanism:** TODO — confirm whether logging is configured via code, a `logging.ini` / `dictConfig` file, or environment variables.
- **Contextual fields:** TODO — identify any request IDs, user IDs, trace IDs, or other contextual metadata currently threaded through log messages as free text.

## Proposed Changes

For each affected component, the changes are described below.

| Component | Before | After | Breaking? |
|---|---|---|---|
| Log formatter | Plain-text or unstructured string formatter | JSON formatter producing a structured object per log record | N — log consumers must be updated, but application behaviour is unchanged |
| Logger configuration | `basicConfig` or ad-hoc setup (TODO — confirm) | Centralised `dictConfig`-based configuration with JSON formatter attached | N |
| Log record fields | Unstructured message string only | Structured fields: `timestamp`, `level`, `logger`, `message`, plus optional contextual fields | N |
| Contextual metadata | Embedded inline in message string (TODO — confirm) | Passed as structured key-value pairs via `extra` dict or `LoggerAdapter` | N |
| Third-party logging calls (if any) | TODO | Routed through standard `logging` module | TODO — depends on discovery |
| `print()` statements used for logging (if any) | Direct stdout output | Replaced with appropriate `logging` calls | N |

### What is added
- A JSON log formatter (using Python's `logging` module formatter interface and a JSON serialisation library available in the standard library or already in the dependency tree).
- A centralised logging configuration entry point applied at application startup.
- A `LoggerAdapter` or equivalent mechanism for attaching per-request or per-context structured fields without modifying every call site.

### What is removed
- Unstructured plain-text format strings from the formatter configuration.
- Any `print()` statements used for operational logging purposes.
- TODO — any redundant third-party logging libraries that are superseded by this change.

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Log output format changes from plain text to JSON | Any downstream consumer parsing plain-text logs (e.g., log shippers, alerting rules, dashboards) will break | Update log shipper / parser configuration to expect JSON; update alert queries to use field-based selectors |
| Contextual data previously embedded in message strings is now in discrete fields | Regex-based log queries against the `message` field will not match extracted fields | Rewrite queries to reference the new structured field names |
| TODO — removal of third-party logging library (if applicable) | Callers importing that library directly will break | TODO — migration path depends on discovery of affected call sites |

## Acceptance Criteria

1. **Given** the application is running, **when** any log statement at any level (`DEBUG` through `CRITICAL`) is emitted, **then** each log line written to stdout/stderr is a single, valid JSON object parseable without error by a standard JSON parser.

2. **Given** a log record is emitted, **when** the JSON output is inspected, **then** it contains at minimum the fields `timestamp` (ISO 8601 format), `level` (string), `logger` (string), and `message` (string).

3. **Given** contextual metadata (e.g., request ID) is attached to a logger via the designated context mechanism, **when** a log statement is emitted within that context, **then** the contextual key-value pairs appear as top-level fields in the JSON output alongside `timestamp`, `level`, `logger`, and `message`.

4. **Given** an unhandled exception is raised, **when** the exception is logged, **then** the JSON log record includes a structured `exception` field containing the exception type, message, and traceback — not as a raw multi-line string that breaks JSON parsing.

5. **Given** the application starts up, **when** the logging configuration is initialised, **then** no plain-text log lines are emitted to stdout or stderr at any point during normal operation.

6. **Given** the existing test suite runs in CI, **when** log output is captured during tests, **then** all captured log lines are valid JSON and no test relies on matching plain-text log format strings.

7. **Given** the log level is set to `WARNING` via environment variable or configuration, **when** a `DEBUG` or `INFO` statement is executed, **then** no output is produced, confirming the standard `logging` level-filtering behaviour is preserved.

8. **Given** multiple concurrent requests or threads are active, **when** log records are emitted simultaneously, **then** each JSON object appears on its own complete line with no interleaving of records from different threads.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current log formatting mechanism — `basicConfig`, `dictConfig`, `logging.ini`, or ad-hoc? | TODO | TODO |
| 2 | Are there any `print()` statements used for operational logging that must be migrated? | TODO | TODO |
| 3 | Are any third-party logging libraries (e.g., `structlog`, `loguru`) currently in use that would be replaced or need to coexist? | TODO | TODO |
| 4 | What JSON serialisation library is available and approved for use (standard library `json`, `orjson`, `ujson`)? | TODO | TODO |
| 5 | Which contextual fields (request ID, trace ID, user ID, etc.) must be included as structured fields in every log record? | TODO | TODO |
| 6 | What is the target log destination — stdout only, file, or both — and does the JSON format requirement apply to all destinations? | TODO | TODO |
| 7 | Do existing log aggregation pipelines or dashboards need to be updated as part of this change, and who owns that work? | TODO | TODO |
| 8 | Is there a required JSON schema or field naming convention mandated by the organisation's observability platform? | TODO | TODO |