# Plan: Introduce Structured Logging

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

Structured logging will be introduced incrementally using a strangler-fig approach, replacing existing unstructured log calls component by component rather than in a single big-bang rewrite. This minimises risk by allowing the new logging layer to coexist with existing logging until each component is fully migrated and validated.

**Justification:**
- Upgrade urgency is rated **medium**, indicating no immediate production crisis but meaningful tech debt to address.
- The strangler-fig pattern allows partial rollout, isolated testing, and low-risk rollback per component.
- Because the language, runtime, and build tool are currently unidentified (see TODOs below), a phased approach provides checkpoints to re-evaluate tooling choices as context is clarified.

> ⚠️ **NOTE:** The tech analysis did not supply language, runtime, build tool, framework, or specific dependency versions. All technology-specific recommendations below are marked **TODO** and must be resolved before implementation begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Discovery & Decision — identify current logging approach, select structured logging library, define log schema (fields: timestamp, level, service, trace_id, message, error, etc.) | Access to codebase and runtime details | TODO (derive from option once details provided) |
| 2 | Foundation — introduce structured logging library, create a shared logging initialisation/configuration module, define standard log fields and output format (JSON) | Phase 1 complete; dependency versions confirmed | TODO |
| 3 | Core Component Migration — replace unstructured log calls in core/critical-path components with structured equivalents | Phase 2 complete | TODO |
| 4 | Remaining Component Migration — migrate all remaining components; remove legacy logging configuration | Phase 3 validated in staging | TODO |
| 5 | Observability Integration & Validation — confirm log ingestion in log aggregation platform, validate queries, set CI lint/format gates | Phase 4 complete; log platform access | TODO |

> **Note:** Effort estimates are marked TODO because the upgrade option detail was not provided. Populate from the `moderate` option's person-days breakdown once available.

---

## Component Changes

> ⚠️ No code context, class names, or file paths were provided. The structure below represents the expected change pattern. Replace placeholders with actual names from the codebase.

### Logging Initialisation Module
- **What changes:** A new centralised logging setup module is created (e.g., `logger.{ext}`, `logging_config.{ext}`). All other modules import from this single source of truth.
- **Files affected:** TODO — new file to be created; path TBD based on project structure.
- **APIs modified:** N/A (new module).

### Application Entry Point
- **What changes:** Logger is initialised at startup with environment-aware configuration (log level from env var, JSON output in production, human-readable in development).
- **Files affected:** TODO — e.g., `main.{ext}`, `app.{ext}`, `server.{ext}`.
- **APIs modified:** TODO.

### Existing Log Call Sites
- **What changes:** All calls to unstructured logging (e.g., `print()`, `console.log()`, `logger.info("string")`) are replaced with structured calls that include contextual key-value fields (e.g., `logger.info("event description", {user_id: x, request_id: y})`).
- **Files affected:** TODO — full list to be produced during Phase 1 discovery (grep/AST scan for existing log calls).
- **APIs modified:** Logging call signatures change from positional string interpolation to structured key-value pairs.

### Error Handling Paths
- **What changes:** Exception/error log calls are updated to include structured error fields (e.g., `error.type`, `error.message`, `error.stack`).
- **Files affected:** TODO.
- **APIs modified:** TODO.

### Configuration / Environment
- **What changes:** Log level and output format become environment-variable-driven (e.g., `LOG_LEVEL`, `LOG_FORMAT`).
- **Files affected:** TODO — e.g., `.env.example`, `config.{ext}`, Helm values / Docker Compose env blocks.

---

## Dependency Upgrade Plan

> ⚠️ No dependency versions were supplied in the tech analysis. The table below shows the expected shape; all versions are TODO.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Structured logging library | TODO | TODO | TODO | To be selected in Phase 1 based on confirmed language/runtime (e.g., `winston`, `pino`, `structlog`, `zerolog`, `slog`, `logback` + `logstash-encoder`) |
| Existing logging library/framework (if any) | TODO | TODO (remove or retain as facade) | TODO | Assess whether to wrap or replace outright |
| Log serialisation dependency (if separate) | TODO | TODO | TODO | TODO |

---

## Infrastructure Changes

> ⚠️ No infrastructure context was provided. Items below are conditional on confirmation.

- **Log Aggregation Platform:** TODO — confirm whether a platform (e.g., ELK, Loki, Datadog, Splunk, CloudWatch) is in use. Structured JSON logs must match the expected ingest format/field mapping.
- **Docker Base Image:** TODO — no changes anticipated solely for structured logging, but confirm log driver settings (e.g., `json-file`, `fluentd`) in Docker Compose or container runtime config.
- **Kubernetes Manifests:** TODO — if deployed on Kubernetes, confirm that stdout/stderr JSON logs are correctly scraped by the log collector (e.g., Fluent Bit DaemonSet). No manifest changes expected unless log volume or sidecar configuration is required.
- **CI/CD Pipeline:** Add a lint/format gate in CI to enforce structured log call patterns (e.g., ban raw `print`/`console.log` via linter rule). TODO — specify pipeline tool (GitHub Actions, GitLab CI, Jenkins, etc.).
- **IaC:** TODO — if log retention policies or alerting rules are managed via IaC (Terraform, Pulumi), update to account for new structured field names.

---

## Rollback Strategy

Each phase is independently reversible.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Discard discovery artefacts; no code changes made — zero rollback cost. |
| **Phase 2** | Remove the new logging initialisation module and revert dependency additions in the package manifest. Re-run dependency install to restore prior state. |
| **Phase 3** | Revert commits for core component log call migrations (git revert or branch reset). The Phase 2 foundation module can remain in place without harm. |
| **Phase 4** | Revert commits for remaining component migrations. Legacy logging configuration files should be retained in version control (not deleted) until Phase 5 is confirmed stable. |
| **Phase 5** | If observability integration fails, revert log field mapping changes in the aggregation platform configuration. Application code changes from Phases 3–4 remain safe to keep as they emit valid JSON regardless of platform configuration. |

**General principle:** Do not delete legacy logging configuration files until Phase 5 is signed off. Keep them alongside new config under version control to enable fast revert.

---

## Testing Strategy

### Unit Tests
- **Goal:** Verify that the logging initialisation module produces correctly structured output (valid JSON, required fields present: `timestamp`, `level`, `message`, `service`).
- **Tool:** TODO — confirm unit test framework for the stack.
- **Coverage target:** 100% of the new logging initialisation module; all modified log call sites covered by at least one test asserting structured output shape.

### Integration Tests
- **Goal:** Verify that log output captured from running application components contains expected structured fields under realistic request flows.
- **Tool:** TODO — confirm integration test framework. Capture stdout/stderr in tests and assert JSON parseability and field presence.
- **Coverage target:** All critical-path components migrated in Phase 3 must have at least one integration test asserting structured log output.

### Regression Tests
- **Goal:** Confirm that introducing structured logging does not alter application behaviour (no functional regressions).
- **Tool:** Existing regression/end-to-end test suite (TODO — confirm tooling).
- **Gate:** Full existing regression suite must pass before merging each phase.

### Performance Tests
- **Goal:** Confirm that structured logging does not introduce unacceptable latency overhead (JSON serialisation cost).
- **Tool:** TODO — confirm load/benchmark test tooling.
- **Acceptance criteria:** p99 latency increase ≤ 5% compared to baseline; throughput degradation ≤ 2%.

### CI Gates
- Lint rule enforcing no raw unstructured log calls (TODO — configure for confirmed linter).
- JSON schema validation of sampled log output in CI smoke test.
- All phases require green CI before merge to main.

---

## Timeline

> ⚠️ Effort values are TODO pending confirmation of the `moderate` upgrade option's person-days breakdown and team size.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Discovery complete; library selected; log schema agreed | Phase 1 | TODO | TODO |
| Logging foundation module merged; dependency added | Phase 2 | TODO | TODO |
| Core components migrated and tested | Phase 3 | TODO | TODO |
| All components migrated; legacy logging removed | Phase 4 | TODO | TODO |
| Observability platform validated; CI gates active | Phase 5 | TODO | TODO |

---

## Open TODOs (Must Resolve Before Implementation)

| # | Item |
|---|------|
| 1 | Confirm language, runtime, and build tool so the correct structured logging library can be selected. |
| 2 | Provide `moderate` upgrade option person-days breakdown to populate effort estimates. |
| 3 | Identify existing logging library/approach in the codebase (grep for log call patterns). |
| 4 | Confirm log aggregation platform and expected JSON field schema. |
| 5 | Confirm CI/CD pipeline tooling for gate implementation. |
| 6 | Confirm infrastructure platform (Docker, Kubernetes, serverless, etc.) for log driver/collector configuration. |