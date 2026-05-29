# Tasks: Introduce Structured Logging

> **Scope:** Introduce structured logging across the codebase.
> **Upgrade Option:** Moderate
> **Urgency:** Medium
>
> ⚠️ *Note: Language, runtime, build tool, and framework details were not provided in the tech analysis. Tasks below are written at the logical level. Assignees must substitute specific filenames, class names, and config keys once the codebase is inspected. No tasks have been invented for absent components.*

---

## Prerequisites

- [ ] [XS] Confirm target structured logging library and output format (e.g., JSON) by reviewing existing logging dependencies in the build manifest (e.g., `package.json`, `pom.xml`, `requirements.txt`, `go.mod`)
- [ ] [XS] Verify that the local development environment can run the existing test suite to establish a passing baseline before any changes are made
- [ ] [XS] Confirm log aggregation sink (e.g., stdout-only, file, external service) with the infrastructure owner so output format requirements are known before implementation begins
- [ ] [XS] Ensure all contributors have write access to the feature branch and that the CI pipeline is observable

---

## Phase 1 — Preparation

- [ ] [S] Audit all existing logging call sites in the codebase — identify every file that imports or calls the current logger — and produce a list of files requiring migration
- [ ] [S] Capture the current log output format as a baseline by running the application locally or in a staging environment and saving representative log samples to `docs/logging-baseline-samples.txt`
- [ ] [XS] Create a dedicated feature branch (e.g., `feat/structured-logging`) from the main branch for all work in this task
- [ ] [XS] Add a CI lint/format gate (if not already present) to the pipeline config to prevent unstructured `print`/`console.log`/raw-string log statements from being merged after migration

---

## Phase 2 — Core Upgrade

- [ ] [M] Add the chosen structured logging library as a dependency in the build manifest and lock file, pinning to the specific version agreed in Prerequisites
- [ ] [M] Create a centralized logger configuration module (e.g., `src/logger.{ext}` or `internal/logger/logger.{ext}`) that initialises the structured logger with the agreed output format (JSON), log level sourced from an environment variable, and service-name field
- [ ] [M] Replace all existing logging call sites identified in Phase 1 — Part 1 with calls to the new centralized logger, converting free-text messages to structured key-value pairs (e.g., `event`, `user_id`, `error`) in each affected file
- [ ] [S] Add standard context fields (e.g., `request_id`, `trace_id`, `service`, `environment`) to the logger middleware or request-handling layer so they are injected automatically on every log entry
- [ ] [S] Replace all error-logging call sites to include a structured `error` field containing the error message and, where available, stack trace — rather than interpolating error strings into the message
- [ ] [XS] Remove or replace any remaining raw `print`, `console.log`, `fmt.Println`, or equivalent unstructured output statements found during the audit in Phase 1

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for the centralized logger configuration module in the project's test directory, asserting that output is valid JSON and that required fields (`level`, `timestamp`, `message`, `service`) are always present
- [ ] [S] Run the full existing test suite and confirm it passes with zero regressions after the logging migration
- [ ] [S] Perform a manual smoke test of the running application, capture log output, and verify it matches the agreed structured format — compare against the baseline samples saved in `docs/logging-baseline-samples.txt`
- [ ] [XS] Confirm that log level filtering works correctly by setting the log-level environment variable to `warn` and verifying that `debug`/`info` entries are suppressed in output

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration to set the log-level environment variable (e.g., `LOG_LEVEL=info`) for all test and build jobs so structured logging is active during CI runs
- [ ] [XS] Confirm that the deployment environment (container, VM, or serverless config) passes the `LOG_LEVEL` and `SERVICE_NAME` environment variables to the application — update the relevant config file or IaC definition if they are absent

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Add a `## Logging` section to `README.md` (or the relevant developer guide) documenting: the chosen library, required environment variables, log field schema, and how to add structured fields in new code
- [ ] [XS] Add an entry to `CHANGELOG.md` describing the introduction of structured JSON logging and listing the environment variables introduced
- [ ] [XS] Update any existing runbook or operations guide to note that log output is now JSON and to provide a sample query for the log aggregation sink (e.g., a `jq` filter or Kibana/Loki query pattern)
- [ ] [XS] Monitor log volume and error rates in the staging environment for one full business day after deployment to confirm no log entries are lost or malformed before promoting to production