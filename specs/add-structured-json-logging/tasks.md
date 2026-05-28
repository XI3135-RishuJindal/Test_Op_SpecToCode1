# Tasks: Add Structured JSON Logging

> **Goal:** Introduce structured JSON logging across the application to replace or augment existing unstructured log output.
> **Upgrade Option:** Moderate
> **Urgency:** Medium

---

## Prerequisites

- [ ] [XS] Confirm the application's language, runtime, and build tool by inspecting the repository root (e.g., `package.json`, `pom.xml`, `go.mod`, `requirements.txt`, `Gemfile`) before any work begins
- [ ] [XS] Identify the existing logging library/framework in use (e.g., `console.log`, `log4j`, `logrus`, `logging`, `Serilog`) by searching import statements and configuration files in the codebase
- [ ] [XS] Verify that the target deployment environment (local, CI, staging, production) can consume JSON log output (e.g., log aggregator such as Datadog, ELK, CloudWatch accepts JSON)
- [ ] [XS] Confirm write access to the repository and that a feature branch can be created from the default branch

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feat/structured-json-logging` from the default branch
- [ ] [S] Capture a baseline sample of current log output (format, fields, log levels) by running the application locally and saving representative log lines to `docs/logging-baseline.txt`
- [ ] [S] Audit all existing log call sites in the codebase — document which files emit logs, what fields are present, and which are missing structured context (e.g., `requestId`, `userId`, `traceId`) in `docs/logging-audit.md`
- [ ] [XS] Identify and document the chosen JSON logging library appropriate to the confirmed runtime (e.g., `pino` for Node.js, `loguru`/`structlog` for Python, `logrus`/`zap` for Go, `log4j2` JSON layout for Java) in `docs/logging-audit.md`
- [ ] [XS] Add a CI lint/format gate (if not already present) to prevent plain `console.log` / `print` / unstructured log calls from being merged, configured in the CI pipeline config file

---

## Phase 2 — Core Upgrade

- [ ] [M] Install and configure the selected JSON logging library as the sole logging provider, replacing the existing logger initialisation in the application entry point (e.g., `src/index.*`, `main.*`, `app.*`)
- [ ] [M] Define a standard log schema (fields: `timestamp`, `level`, `message`, `service`, `environment`, `requestId`, `traceId`, `error`) and implement a shared logger factory/wrapper module in `src/lib/logger.*` (or language-equivalent path)
- [ ] [M] Replace all unstructured log call sites identified in the audit with calls to the new structured logger, passing context fields, across all application source files
- [ ] [S] Add request-scoped context middleware (e.g., `requestId`, `traceId` injection) to the HTTP layer or equivalent entry point so every log line within a request carries correlation identifiers
- [ ] [S] Ensure error log entries serialize the full error object (message, stack, code) as structured fields rather than string interpolation, updating error-handling modules identified in the audit
- [ ] [XS] Set log level via an environment variable (e.g., `LOG_LEVEL`) with a documented default of `info`, configuring this in the application config/env loading module

---

## Phase 3 — Testing & Validation

- [ ] [S] Write unit tests for the shared logger factory/wrapper in `src/lib/logger.*` verifying that output is valid JSON and contains all required schema fields
- [ ] [S] Write integration tests (or update existing ones) to assert that HTTP request logs include `requestId` and `traceId` fields in the response log entries
- [ ] [XS] Manually run the application locally and pipe output through a JSON validator (e.g., `| jq .`) to confirm all log lines are valid JSON with no plain-text leakage
- [ ] [XS] Compare captured log output against `docs/logging-baseline.txt` to confirm no log call sites were silently dropped during migration
- [ ] [XS] Verify that `LOG_LEVEL=debug` surfaces debug logs and `LOG_LEVEL=error` suppresses info/debug logs, confirming environment-variable-driven level control works correctly

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration file to set `LOG_LEVEL=info` (or `debug` for test runs) as an environment variable in the test and build job definitions
- [ ] [XS] Confirm that the log aggregation sink (e.g., Datadog agent config, Fluentd/Logstash pipeline, CloudWatch log group) is configured to parse JSON rather than plain text — document any required config changes in `docs/logging-audit.md`
- [ ] [XS] Update any Docker `CMD`/`ENTRYPOINT` or process supervisor config to avoid wrapping the application in a shell that buffers stdout, ensuring JSON log lines are flushed immediately

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `## Logging` section to `README.md` (or `docs/logging.md`) documenting the log schema, available fields, how to set `LOG_LEVEL`, and how to read logs locally with `jq`
- [ ] [XS] Update `CHANGELOG.md` with an entry under the current version describing the addition of structured JSON logging and any breaking changes to log format
- [ ] [XS] Review and update any runbook or on-call guide that references log query patterns to reflect the new JSON field names (e.g., replace grep-based queries with `jq` or log aggregator field filters)
- [ ] [S] Deploy to staging, monitor the log aggregator dashboard for 24 hours to confirm JSON ingestion, field parsing, and alerting rules based on log fields are functioning correctly
- [ ] [XS] After successful staging validation, merge to the default branch and deploy to production; set a monitoring reminder to review log volume and error rates 48 hours post-deployment