# TASKS: Configure Structured Logging Output

> **Modernization Goal:** Configure structured logging output
> **Option:** Moderate
> **Upgrade Urgency:** Medium

---

## Prerequisites

- [ ] [XS] Confirm the target log format (JSON, logfmt, etc.) with the team and document the decision in a shared design note or ADO/GitHub issue before any code changes begin
- [ ] [XS] Identify the existing logging library/framework in use (e.g., by searching the codebase for import statements, config files, or lock files) and record the exact name and version
- [ ] [XS] Verify that all engineers and CI runners have read/write access to the logging configuration files and any secrets or environment variables required for log sinks
- [ ] [XS] Confirm that a log aggregation or observability destination (e.g., stdout consumer, log shipper) is available and ready to receive structured output before rollout

---

## Phase 1 — Preparation

- [ ] [S] Audit all existing log call sites in the codebase to catalogue current log levels, message formats, and any unstructured string interpolation patterns that will need to be migrated
- [ ] [S] Capture a baseline sample of current log output (format, fields, volume) from a running environment and store it as a reference artifact in the repository (e.g., `docs/logging/baseline-sample.log`)
- [ ] [XS] Create a dedicated feature branch (e.g., `feat/structured-logging`) from the main branch for all changes in this task
- [ ] [XS] Define the required structured log fields (e.g., `timestamp`, `level`, `message`, `service`, `trace_id`, `request_id`) in a logging standards document at `docs/logging/structured-logging-spec.md`
- [ ] [XS] Configure a CI gate that fails the build if any new log call site introduces unstructured string concatenation into log messages (lint rule or custom script)

---

## Phase 2 — Core Upgrade

- [ ] [M] Update the logging configuration file (identified in Prerequisites) to enable structured (JSON or logfmt) output format, setting the formatter/encoder, log level, and output target (stdout)
- [ ] [M] Refactor all existing log call sites identified in Phase 1 to use structured key-value fields instead of interpolated strings, ensuring required fields from the spec are present on every log entry
- [ ] [S] Add a logging initialisation/bootstrap module (e.g., `logger.init()` or equivalent) that reads log level and format from environment variables (e.g., `LOG_LEVEL`, `LOG_FORMAT`) so configuration is environment-driven
- [ ] [S] Ensure that error log entries include a structured `error` field (with message and, where available, stack trace) rather than embedding error details in the log message string
- [ ] [XS] Remove or replace any legacy logging configuration (e.g., old formatter config, plaintext pattern strings) that conflicts with the new structured output settings

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for the logging initialisation module verifying that output is valid JSON (or chosen format), required fields are present, and log level filtering works correctly
- [ ] [S] Write integration or smoke tests that start the application, emit at least one log entry per level (DEBUG, INFO, WARN, ERROR), and assert that each entry parses as valid structured output
- [ ] [S] Compare structured log output against the baseline sample captured in Phase 1 to confirm no log lines are silently dropped and all previously logged events are still represented
- [ ] [XS] Validate that sensitive fields (e.g., passwords, tokens, PII) are not present in structured log output by reviewing sampled log entries and adding redaction where needed

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration to assert that the application emits valid structured log output during test runs (e.g., pipe stdout through a JSON validator step)
- [ ] [XS] Update any Docker or container run configurations to ensure the application writes logs to stdout/stderr (not to a file) so the container runtime can capture structured output
- [ ] [XS] Update environment variable definitions in CI/CD pipeline config (e.g., `.env.example`, pipeline YAML) to include `LOG_LEVEL` and `LOG_FORMAT` with documented default values

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `docs/logging/structured-logging-spec.md` with final field definitions, example log entries, and guidance for developers on how to add new log call sites correctly
- [ ] [XS] Add a `CHANGELOG` entry describing the switch to structured logging output, the log format chosen, and any breaking changes to log field names or structure
- [ ] [XS] Review and update any runbooks or operational playbooks that reference log parsing, alerting queries, or log-based dashboards to reflect the new structured field names
- [ ] [S] Perform a staged rollout to a non-production environment first, monitor log output in the aggregation destination for at least one full business day, and confirm no missing or malformed entries before promoting to production
- [ ] [XS] Set up or update observability alerts (e.g., alert on `level=error` field) in the log aggregation tool to use the new structured field names post-migration