# PLAN: Integrate OpenTelemetry for Distributed Tracing

> **Status:** Draft
> **Spec reference:** spec.md — Integrate OpenTelemetry for distributed tracing
> **Option selected:** Moderate

---

## Overview

**Strategy: Feature-Flag Gated / Strangler-Fig**

Because the runtime, language, and build toolchain are not yet confirmed (see TODOs throughout), a **feature-flag gated** rollout is the safest approach. Instrumentation is introduced incrementally — one service or layer at a time — behind a runtime toggle. This allows:

- Production traffic to flow through uninstrumented paths until each component is validated.
- Immediate disable of tracing export if the collector pipeline causes latency regression.
- Parallel operation of any existing logging/metrics infrastructure while OpenTelemetry is stabilised.

A big-bang approach is explicitly avoided given the medium upgrade urgency and the number of architectural unknowns present in the provided context. The moderate effort estimate implies a multi-phase delivery rather than a single cutover.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Discovery & Baseline | Confirm runtime/language/build tool; audit existing observability; define trace context propagation standard (W3C TraceContext); select OpenTelemetry SDK version | None | TODO — derive from confirmed tech stack |
| 2 — SDK & Collector Setup | Add OpenTelemetry SDK and auto-instrumentation libraries as dependencies; deploy/configure OpenTelemetry Collector (or agent sidecar); validate connectivity to backend (Jaeger/Tempo/OTLP endpoint) | Phase 1 complete; collector infrastructure available | TODO |
| 3 — Core Instrumentation | Instrument inbound request handlers, outbound HTTP/RPC clients, and database calls; propagate `traceparent` headers; emit spans with standard semantic conventions | Phase 2 complete | TODO |
| 4 — Custom Spans & Attributes | Add business-relevant custom spans, events, and attributes to critical code paths identified in Phase 1 | Phase 3 complete | TODO |
| 5 — Validation & Cutover | Load/performance testing; confirm no latency regression; enable tracing in production; remove feature flags; update runbooks | Phase 4 complete; performance baseline from Phase 1 | TODO |

> **Note:** Effort values are marked TODO because the upgrade option did not supply person-day figures and the runtime/language are unknown. Estimates must be populated once Phase 1 discovery is complete.

---

## Component Changes

> **Note:** No source files, class names, or method signatures were provided in the code context. The entries below describe the *structural pattern* of changes required. File and class names must be filled in after Phase 1 discovery.

### Entry-Point / Request Handler Layer
- **What changes:** Add OpenTelemetry middleware or filter to extract incoming `traceparent`/`tracestate` headers and start a root span per request.
- **Files affected:** TODO — main application entry point, HTTP router/middleware chain.
- **APIs modified:** TODO — middleware registration API specific to the framework in use.

### Outbound HTTP / RPC Clients
- **What changes:** Wrap or replace HTTP client instances with OTel-instrumented equivalents; inject `traceparent` header on all outbound calls.
- **Files affected:** TODO — HTTP client factory/wrapper classes.
- **APIs modified:** TODO.

### Database / Cache Access Layer
- **What changes:** Instrument database drivers or ORM calls to emit `db.*` semantic-convention spans.
- **Files affected:** TODO — repository classes, data-access objects, connection pool configuration.
- **APIs modified:** TODO.

### Application Bootstrap / Dependency Injection
- **What changes:** Register `TracerProvider`, `SpanExporter` (OTLP/gRPC or OTLP/HTTP), and `Propagator` (W3C TraceContext + Baggage) at startup; bind lifecycle to application shutdown hook for clean flush.
- **Files affected:** TODO — application bootstrap/main file, DI container configuration.
- **Config keys added:**
  - `OTEL_SERVICE_NAME`
  - `OTEL_EXPORTER_OTLP_ENDPOINT`
  - `OTEL_EXPORTER_OTLP_HEADERS` (if auth required)
  - `OTEL_TRACES_SAMPLER` + `OTEL_TRACES_SAMPLER_ARG`
  - Feature-flag key: `TRACING_ENABLED` (boolean, default `false` until Phase 5)

### Feature-Flag Control Point
- **What changes:** A single conditional at `TracerProvider` initialisation reads `TRACING_ENABLED`; when `false`, a no-op `TracerProvider` is registered so all instrumentation calls are zero-cost.
- **Files affected:** TODO — bootstrap file identified above.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| OpenTelemetry SDK (core) | Not present | TODO — confirm from tech analysis once runtime known | N/A (new dependency) | Select stable 1.x release for the confirmed language |
| OpenTelemetry Auto-Instrumentation | Not present | TODO | N/A | Framework-specific; confirm after Phase 1 |
| OTLP Exporter | Not present | TODO | N/A | Choose gRPC or HTTP/protobuf based on collector config |
| OpenTelemetry Collector | Not present | TODO | N/A | Deploy as sidecar or standalone agent; see Infrastructure Changes |
| Existing logging library | TODO (current) | No change planned | N/A | Correlate trace IDs into log output via OTel log bridge if supported |

> **All version numbers are marked TODO** because the tech analysis did not supply confirmed versions or the current language/runtime. Versions must be pinned to the latest stable OpenTelemetry release for the confirmed runtime during Phase 1 and recorded here before Phase 2 begins.

---

## Infrastructure Changes

### OpenTelemetry Collector
- TODO — Determine whether the Collector runs as a sidecar container, a DaemonSet, or a standalone service. This depends on the deployment platform (Kubernetes, VM, serverless) which is not specified in the provided context.
- TODO — Define the Collector pipeline: receivers (`otlp`), processors (`batch`, `memory_limiter`), exporters (Jaeger / Grafana Tempo / vendor OTLP endpoint).
- TODO — Provide Collector configuration file (`otel-collector-config.yaml`).

### Docker / Container Images
- TODO — If services are containerised, confirm base images. No changes to base images are expected solely for OTel SDK integration (SDK is a library dependency). Collector requires its own image (`otel/opentelemetry-collector-contrib:TODO_VERSION`).

### Kubernetes Manifests
- TODO — If running on Kubernetes: add `OTEL_*` environment variables to Deployment manifests via ConfigMap or Secret; optionally add collector sidecar container spec.

### CI/CD Pipeline
- TODO — Add a pipeline step in Phase 2 to validate that the OTLP exporter can reach the collector in the test environment (smoke test: emit a single span, assert it appears in the backend).
- TODO — Add `TRACING_ENABLED=false` to CI environment by default; set `TRACING_ENABLED=true` only in integration/staging pipeline stages.

### IaC
- TODO — No IaC context was provided. If infrastructure is managed via Terraform/Pulumi/etc., add resources for the Collector service and any managed tracing backend.

---

## Rollback Strategy

### Phase 2 Rollback (SDK & Collector)
1. Set `TRACING_ENABLED=false` in environment configuration — no-op provider activates immediately; zero application code changes required.
2. Remove or stop the OpenTelemetry Collector deployment. Application continues to function; spans are simply dropped.
3. Revert dependency additions in the package manifest and redeploy. No data-layer or API changes have been made at this phase.

### Phase 3 Rollback (Core Instrumentation)
1. Set `TRACING_ENABLED=false` — instrumentation calls become no-ops without code removal.
2. If a latency regression is confirmed even with the no-op provider, revert the instrumentation commits via git revert and redeploy.
3. Collector can remain running; it will receive no traffic.

### Phase 4 Rollback (Custom Spans)
1. Set `TRACING_ENABLED=false`.
2. Custom span code is additive and non-functional (no side effects); rollback is the feature flag alone unless a specific span is causing errors, in which case revert the relevant commit.

### Phase 5 Rollback (Production Cutover)
1. Set `TRACING_ENABLED=false` in production environment variables — takes effect on next process restart or config reload (no redeployment required if config is externalised).
2. If feature flags have been removed, maintain a tagged git release from before flag removal to enable rapid revert.
3. Document rollback SLA: target < 15 minutes from detection to tracing disabled in production.

---

## Testing Strategy

> Tool names below are placeholders appropriate for a generic stack. Confirm and replace with project-specific tools after Phase 1.

### Unit Tests
- **Scope:** Verify that `TracerProvider` initialisation respects the `TRACING_ENABLED` flag; assert no-op provider is registered when flag is `false`.
- **Tools:** TODO — unit test framework for confirmed language.
- **Coverage target:** 80 % line coverage on all new OTel bootstrap and wrapper code.
- **CI gate:** Fail build if coverage drops below target.

### Integration Tests
- **Scope:** Spin up an in-process OTLP receiver (or use the OTel SDK's in-memory exporter); exercise instrumented request paths; assert that spans are emitted with correct `service.name`, `http.method`, `http.status_code`, and `db.*` attributes per OpenTelemetry semantic conventions.
- **Tools:** TODO — integration test framework; OTel in-memory/fake exporter.
- **CI gate:** All span-assertion tests must pass in the staging pipeline before Phase 5 cutover.

### Regression Tests
- **Scope:** Full existing test suite must pass without modification — instrumentation must be transparent to business logic.
- **Tools:** TODO — existing test suite.
- **CI gate:** Zero new test failures introduced by OTel changes.

### Performance / Load Tests
- **Scope:** Compare p50/p95/p99 latency and CPU/memory usage with `TRACING_ENABLED=false` vs `true` under representative load. Acceptable overhead budget: < 2 % p99 latency increase.
- **Tools:** TODO — load testing tool (e.g., k6, Gatling, Locust — confirm with team).
- **CI gate:** Performance test runs in staging (Phase 5); block cutover if overhead exceeds budget.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Runtime/language/build tool confirmed; observability audit complete | Phase 1 — Discovery | TODO | TODO |
| Dependency versions pinned; Collector deployed to dev environment | Phase 2 — SDK & Collector Setup | TODO | TODO |
| Core instrumentation merged to main; integration tests passing | Phase 3 — Core Instrumentation | TODO | TODO |
| Custom spans implemented; staging validation complete | Phase 4 — Custom Spans | TODO | TODO |
| Performance baseline met; feature flag removed; production cutover | Phase 5 — Validation & Cutover | TODO | TODO |

> **All dates are TODO.** The upgrade option did not provide person-day estimates, and the runtime is unknown. Dates must be set during Phase 1 once scope is fully understood and team capacity is confirmed.

---

*Document owner: TODO | Last updated: see git history*