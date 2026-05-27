# CONSTITUTION
## Micrometer + Prometheus Metrics Integration

---

## Project Identity

**Name:** Micrometer–Prometheus Metrics Integration

**Purpose:** Instrument the application with Micrometer and expose metrics in Prometheus-compatible format, enabling observability through a standardised metrics pipeline.

**High-Level Goal:** Deliver a working, production-ready metrics endpoint (`/actuator/prometheus` or equivalent scrape endpoint) that Prometheus can consume, with core application metrics captured via Micrometer's vendor-neutral API.

---

## Guiding Principles

1. **Prefer Micrometer's vendor-neutral API over direct Prometheus client calls** because it decouples instrumentation code from the export backend, allowing future registry changes without re-instrumentation.
2. **Prefer additive, non-breaking changes over refactoring existing code** because the upgrade urgency is medium and scope must remain contained to the metrics integration task.
3. **Prefer explicit metric naming conventions over auto-generated names** because Prometheus query correctness depends on stable, predictable metric names across deployments.
4. **Prefer configuration-driven registry setup over hard-coded values** because scrape intervals, histogram buckets, and tag cardinality must be tunable without code changes.
5. **Prefer a single, secured scrape endpoint over multiple ad-hoc metric surfaces** because exposing raw metrics without access control is a security risk in production environments.

---

## Constraints

- **Timeline / Effort:** Effort ceiling follows the "moderate" option — treat as a bounded, focused integration task. No large-scale refactoring is in scope.
- **Scope Freeze:** Work is limited to: adding Micrometer core + Prometheus registry dependencies, configuring the scrape endpoint, and instrumenting key application touchpoints. Feature development outside metrics is out of scope.
- **Runtime / Language:** TODO — runtime and language are unconfirmed. Dependency choices (e.g., `micrometer-registry-prometheus` for JVM, `prometheus_client` bridge for others) must be confirmed once the stack is identified.
- **Build Tool:** TODO — dependency declarations must match the confirmed build tool (Maven, Gradle, npm, etc.).
- **Compliance:** TODO — confirm whether metrics data is subject to data-privacy constraints (e.g., no PII in metric tags).
- **Prometheus Version Compatibility:** The Prometheus exposition format version (OpenMetrics vs. classic) must match the target Prometheus server version. Confirm before finalising the registry configuration.

---

## Quality Standards

- **Test Coverage:** Every custom `MeterBinder` or instrumentation class must have unit tests asserting that expected meters are registered and record values. Coverage floor: 80% on new instrumentation code.
- **Endpoint Verification:** A smoke/integration test must assert that the scrape endpoint returns HTTP 200 with `Content-Type: text/plain; version=0.0.4` (or OpenMetrics equivalent) before any deployment gate passes.
- **Code Review:** All instrumentation changes require at least one reviewer familiar with Prometheus data model (label cardinality, naming conventions).
- **Documentation:** A `METRICS.md` file must be delivered listing every custom metric: name, type, unit, description, and labels. Auto-collected JVM/runtime metrics must be noted as "default — see Micrometer docs."
- **Deployment Gate:** The scrape endpoint must be reachable and return at least one metric in the target environment before the integration is considered complete. No merge to the main branch without this gate passing in CI.
- **Cardinality Guard:** No metric label may accept unbounded values (e.g., user IDs, request URLs). This must be reviewed explicitly during code review.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use Micrometer as the instrumentation facade | Vendor-neutral API; aligns with the stated integration goal; avoids lock-in to Prometheus client directly | Accepted |
| ADR-002 | Expose a dedicated `/metrics` (or framework-equivalent) scrape endpoint | Prometheus pull model requires a stable HTTP endpoint; separating it from application APIs is standard practice | Accepted |
| ADR-003 | Scope limited to metrics integration only | Upgrade option is "moderate"; no runtime upgrades or framework migrations are bundled into this task | Accepted |
| ADR-004 | Specific dependency versions TBD | Runtime and build tool are unknown; versions must be pinned once stack is confirmed | Proposed |
| ADR-005 | Scrape endpoint authentication mechanism TBD | Security requirement exists but implementation depends on the application's existing auth framework | Proposed |