# Spec: Integrate Micrometer with Prometheus Metrics Export

## Summary

This spec covers the integration of Micrometer as the application metrics facade with Prometheus as the metrics export backend. The expected outcome is that the application emits standardised, scrapeable metrics at a dedicated HTTP endpoint, enabling Prometheus to collect and store time-series data for observability, alerting, and dashboarding purposes. No changes to existing business logic are in scope; only instrumentation and metrics-pipeline plumbing are addressed.

---

## Motivation

- **Observability gap:** The application currently has no standardised, machine-readable metrics export. This limits the ability to monitor latency, error rates, resource utilisation, and throughput in production.
- **Operational risk:** Without metrics, incident detection relies on logs alone, increasing mean time to detect (MTTD) for production issues.
- **Ecosystem alignment:** Prometheus is the de-facto standard for metrics collection in cloud-native environments. Micrometer provides a vendor-neutral instrumentation API, reducing future lock-in if the metrics backend changes.
- **Upgrade urgency:** Medium — the application is functional but lacks production-grade observability, creating growing operational and compliance risk as the system scales.
- **Tech debt:** Absence of a metrics layer is a recognised gap; this integration addresses it directly.

> **Note:** Specific CVEs, EOL dates, and framework version numbers were not provided in the tech analysis. See [Open Questions](#open-questions) for items requiring confirmation before implementation begins.

---

## Current State

- **Metrics instrumentation:** None — the application does not currently expose a metrics endpoint or use a metrics facade.
- **Monitoring integration:** TODO — confirm whether any ad-hoc logging-based metrics or APM agents are in use.
- **HTTP endpoints:** TODO — confirm existing endpoint inventory so the new `/actuator/prometheus` (or equivalent) endpoint does not conflict.
- **Build configuration:** TODO — confirm build tool and dependency management approach (e.g., Maven, Gradle, npm, etc.) to specify correct dependency additions.
- **Runtime/framework:** TODO — confirm runtime and framework (e.g., Spring Boot, Quarkus, Micronaut, Node.js) as this determines the Micrometer integration path.
- **Security/auth model:** TODO — confirm whether HTTP endpoints require authentication, which affects how the metrics endpoint is exposed.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Metrics facade | None | Micrometer core API | N |
| Metrics export | None | Micrometer Prometheus registry | N |
| Metrics HTTP endpoint | Does not exist | Dedicated scrape endpoint (e.g., `/actuator/prometheus` or `/metrics`) | N |
| Application build config | No Micrometer dependencies | Micrometer core + Micrometer Prometheus registry dependencies added | N |
| Runtime configuration | No metrics config | Metrics endpoint enabled; scrape path, port, and access controls configured | N |
| JVM / runtime metrics | Not collected | Standard JVM/runtime metrics auto-registered via Micrometer binders (TODO: confirm binders applicable to runtime) | N |
| Custom application metrics | Not instrumented | Key application operations instrumented with Counters, Timers, and Gauges via Micrometer API | N |

---

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New HTTP endpoint added | Minimal — additive change; no existing endpoint is modified | Ensure network/firewall rules permit Prometheus scraper to reach the new endpoint |
| Micrometer dependency added | Minimal — no existing code removed | TODO — confirm no classpath conflicts with existing logging or APM libraries |
| Metric naming conventions | Micrometer uses dot-notation internally; Prometheus registry converts to underscore-separated names | Consumers of any existing ad-hoc metrics must update queries to use new canonical names — TODO: confirm if any existing dashboards or alerts exist |
| Endpoint access control | If the metrics endpoint is unauthenticated, it may expose internal data | Restrict endpoint access to Prometheus scraper IP range or require a bearer token — TODO: confirm security requirements |

---

## Acceptance Criteria

1. **Given** the application is running, **when** an HTTP GET request is made to the metrics scrape endpoint, **then** the response returns HTTP 200 with `Content-Type: text/plain; version=0.0.4` (Prometheus text exposition format).

2. **Given** the application is running, **when** the metrics endpoint is scraped, **then** the response body contains at least the standard JVM/runtime metrics (e.g., memory usage, thread counts) in valid Prometheus exposition format.

3. **Given** the application is running and has processed at least one request, **when** the metrics endpoint is scraped, **then** HTTP request count and latency metrics for that request are present in the response.

4. **Given** a Prometheus instance is configured to scrape the application endpoint, **when** Prometheus performs a scrape, **then** the target appears as `UP` in the Prometheus targets UI with no parse errors.

5. **Given** the application is under load, **when** the metrics endpoint is scraped repeatedly, **then** counter values are monotonically non-decreasing and timer histograms reflect observed latency distributions.

6. **Given** the metrics endpoint is deployed to a production-like environment, **when** an unauthenticated request is made from an unauthorised source, **then** the endpoint returns HTTP 401 or HTTP 403 (TODO: confirm security requirement; criterion to be finalised once access control policy is decided).

7. **Given** the application starts up, **when** the metrics endpoint is scraped before any traffic is processed, **then** the endpoint returns a valid (possibly empty-metric) Prometheus response without error, confirming the registry initialises correctly on startup.

8. **Given** the CI pipeline runs, **when** the build executes, **then** all existing tests pass with no regressions introduced by the addition of Micrometer dependencies.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the application runtime and framework (e.g., Spring Boot, Quarkus, Micronaut, plain JVM, Node.js)? This determines the correct Micrometer integration module and auto-configuration approach. | TODO | TODO |
| 2 | What is the build tool and dependency management approach (Maven, Gradle, other)? Required to specify exact dependency additions. | TODO | TODO |
| 3 | What specific versions of Micrometer core and the Micrometer Prometheus registry should be used? (Tech analysis did not supply version numbers.) | TODO | TODO |
| 4 | Is there an existing APM agent or ad-hoc metrics mechanism in place that could conflict with Micrometer? | TODO | TODO |
| 5 | What is the required access control policy for the metrics endpoint (unauthenticated, IP allowlist, bearer token)? | TODO | TODO |
| 6 | Are there existing Prometheus dashboards or alerting rules that depend on metric names from any current instrumentation? If so, a naming migration plan is needed. | TODO | TODO |
| 7 | Which application-specific operations (beyond JVM defaults) must be instrumented in this iteration (e.g., database calls, queue processing, external HTTP calls)? | TODO | TODO |
| 8 | What port and path should the scrape endpoint be exposed on? Must not conflict with existing endpoints. | TODO | TODO |
| 9 | Is there a Prometheus instance already deployed and available to validate end-to-end scraping, or does that infrastructure need to be provisioned as part of this work? | TODO | TODO |