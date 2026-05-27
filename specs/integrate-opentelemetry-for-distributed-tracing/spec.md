# Spec: Integrate OpenTelemetry for Distributed Tracing

## Summary

This spec covers the integration of OpenTelemetry (OTel) into the existing system to provide distributed tracing capabilities across service boundaries. The expected outcome is that all in-scope services emit standardized trace data (spans, trace context propagation) to a configured OTel-compatible backend, enabling end-to-end visibility into request flows without replacing or disrupting existing logging or metrics pipelines.

## Motivation

- **Observability gap:** The system currently lacks distributed tracing, making it difficult to diagnose latency issues, identify bottlenecks, and correlate failures across service boundaries.
- **Upgrade urgency:** Medium — the absence of tracing is an operational risk that grows as the system scales, but there is no immediate EOL or CVE driver.
- **Standardization:** OpenTelemetry is the CNCF-graduated, vendor-neutral standard for telemetry instrumentation, reducing future lock-in to any single APM vendor.
- **Tech debt:** Instrumentation is currently absent or ad hoc. Establishing OTel as the tracing standard now prevents fragmented, incompatible instrumentation from accumulating further.

> **Note:** Specific runtime, language, and framework versions are not available in the provided tech analysis. Version-specific motivation details are marked TODO below.

## Current State

- **Tracing:** No distributed tracing instrumentation exists in the codebase.
- **Existing telemetry:** TODO — confirm whether any existing logging or metrics libraries are in use that may share context (e.g., correlation IDs in logs).
- **Service boundaries:** TODO — enumerate the specific services/components in scope for this integration.
- **Inbound/outbound protocols:** TODO — identify transport protocols in use (HTTP, gRPC, message queues, etc.) that require trace context propagation.
- **Configuration:** TODO — identify existing configuration mechanisms (environment variables, config files, secrets management) that will be used to supply OTel endpoint and sampling settings.
- **Interfaces/APIs affected:** TODO — list specific classes, middleware hooks, or request-handling entry points where instrumentation will attach.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Tracing instrumentation | None | OpenTelemetry SDK integrated; spans created for in-scope operations | N |
| Trace context propagation | None | W3C TraceContext headers propagated on all inter-service calls | N (additive headers) |
| OTel exporter configuration | None | Exporter endpoint, protocol, and sampling rate configurable via environment/config | N |
| Existing logging pipeline | Unlinked from traces | Trace ID and span ID injected into log records where feasible | N |
| Service entry points (HTTP/gRPC/etc.) | No instrumentation | Auto- or manual instrumentation applied at request boundaries | N |
| OTel Collector / backend | Not present | OTel-compatible receiver configured to accept exported trace data | N |

> **Note:** Specific component names, class names, and config keys are TODO pending codebase and runtime details.

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Addition of W3C TraceContext headers on outbound requests | Downstream services that strictly reject unknown headers may fail | TODO — audit downstream consumers; headers should be ignored by compliant HTTP stacks |
| New required configuration keys for OTel endpoint | Services will not export traces if keys are absent | Provide safe defaults (e.g., no-op exporter) so services start successfully without configuration; document required keys |
| Log record format change (trace/span ID injection) | Log parsing rules or dashboards keyed on exact log format may break | TODO — identify and update any log parsing rules or alerting queries that depend on current log format |
| SDK dependency added to build | Build and dependency graphs change | TODO — confirm no version conflicts with existing dependencies once runtime is identified |

## Acceptance Criteria

1. **Given** a service is deployed with a valid OTel exporter endpoint configured, **when** an inbound request is processed, **then** a root span is created and exported to the configured backend within 30 seconds of request completion.

2. **Given** two in-scope services communicate over HTTP (or the identified transport), **when** Service A calls Service B, **then** Service B's span has a `parent_span_id` matching Service A's span, confirming trace context propagation.

3. **Given** a request traverses all in-scope services, **when** the trace is queried in the OTel backend, **then** a single complete trace tree is visible with no broken parent-child links.

4. **Given** the OTel exporter endpoint is not configured, **when** a service starts, **then** the service starts successfully and processes requests normally (no-op/null exporter active; no startup errors).

5. **Given** the OTel exporter endpoint is unreachable, **when** a service processes requests, **then** trace export failures are logged at WARN level and do not affect request latency by more than TODO ms (define SLA).

6. **Given** trace and span IDs are injected into log records, **when** a log entry is retrieved for a known request, **then** the log entry contains a `trace_id` field matching the trace visible in the OTel backend.

7. **Given** the integration is deployed, **when** the CI pipeline runs, **then** all existing unit and integration tests pass with no regressions.

8. **Given** a sampling rate is configured, **when** load is applied at a defined request rate, **then** the observed export rate matches the configured sampling ratio within a ±5% tolerance.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and framework are in use? This determines which OTel SDK and auto-instrumentation libraries apply. | TODO | TODO |
| 2 | Which services/components are in scope for this initial integration? | TODO | TODO |
| 3 | What OTel-compatible backend will receive traces (e.g., Jaeger, Tempo, Datadog, cloud-native)? Is an OTel Collector required as an intermediary? | TODO | TODO |
| 4 | What transport protocols are used for inter-service communication (HTTP/1.1, HTTP/2, gRPC, Kafka, etc.)? | TODO | TODO |
| 5 | Is auto-instrumentation sufficient, or are manual span annotations required for business-critical operations? | TODO | TODO |
| 6 | What is the acceptable performance overhead budget for tracing instrumentation (CPU, memory, latency)? | TODO | TODO |
| 7 | What sampling strategy is required (head-based, tail-based, always-on for dev, probabilistic for prod)? | TODO | TODO |
| 8 | Are there compliance or data-residency constraints on what data may appear in span attributes (e.g., no PII in trace payloads)? | TODO | TODO |
| 9 | Does the existing logging pipeline support structured log enrichment with trace/span IDs? | TODO | TODO |
| 10 | What is the rollout strategy — all services simultaneously or phased by service? | TODO | TODO |