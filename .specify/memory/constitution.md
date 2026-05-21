# CONSTITUTION
## Project: Add ASP.NET Core Health-Check Endpoint

---

## Project Identity

**Name:** ASP.NET Core Health-Check Endpoint Addition
**Purpose:** Introduce a standardised `/health` (or equivalent) HTTP endpoint to the existing ASP.NET Core application so that infrastructure tooling (load balancers, container orchestrators, monitoring systems) can programmatically verify service liveness and readiness.
**High-Level Goal:** Deliver a production-ready health-check endpoint with minimal disruption to the existing codebase, following ASP.NET Core's built-in `Microsoft.Extensions.Diagnostics.HealthChecks` infrastructure.

---

## Guiding Principles

1. **Prefer the built-in `IHealthChecksBuilder` API over custom middleware** because reinventing health-check plumbing increases maintenance surface and diverges from the ASP.NET Core ecosystem standard.
2. **Prefer additive changes over modifications to existing startup/middleware pipeline** because the upgrade urgency is medium and risk of regression must be kept low.
3. **Prefer explicit liveness and readiness separation over a single combined endpoint** because container orchestrators (Kubernetes, etc.) treat the two signals differently; conflating them causes incorrect restart or traffic-routing behaviour.
4. **Prefer thin, dependency-free health checks at initial delivery over deep dependency probing** because scope is constrained to a moderate effort option — deep checks (DB, cache, downstream APIs) can be added incrementally once the scaffold is in place.
5. **Prefer configuration-driven endpoint paths over hard-coded strings** because deployment environments may require different URL conventions without a code change.

---

## Constraints

| Category | Constraint |
|---|---|
| **Effort ceiling** | Moderate option — treat as a small, focused change (TODO: confirm exact person-days once option details are provided). No architectural refactoring is in scope. |
| **Runtime / framework** | Must use `Microsoft.Extensions.Diagnostics.HealthChecks` (ships in-box with ASP.NET Core 2.2+). TODO: confirm exact runtime version in use; minimum target is ASP.NET Core 2.2. |
| **Scope freeze** | Only health-check scaffolding is in scope. No changes to business logic, data models, authentication flows, or unrelated middleware. |
| **Breaking changes** | Zero breaking changes to existing API surface or middleware order are permitted. |
| **Technology mandates** | TODO: confirm cloud provider / orchestrator requirements (e.g., Azure App Service health probes vs. Kubernetes probes) that may dictate exact response schema. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test coverage** | At minimum, one integration test per exposed health endpoint asserting HTTP 200 (healthy) and, where applicable, HTTP 503 (unhealthy) responses. |
| **Code review** | All changes require at least one peer-review approval before merge; reviewer must verify middleware registration order is correct. |
| **Documentation** | A concise README section (or inline XML doc) must describe: endpoint URL(s), expected response codes, and how to add a new check. |
| **Deployment gate** | CI pipeline must execute health-check integration tests and return green before any merge to the main branch. |
| **Response contract** | Healthy response must return `HTTP 200`; degraded/unhealthy must return `HTTP 503`. Response body format must be consistent (JSON recommended; TODO: confirm if a specific schema is mandated by the monitoring platform). |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use `Microsoft.Extensions.Diagnostics.HealthChecks` as the implementation mechanism | It is the idiomatic, in-box ASP.NET Core solution; avoids third-party dependencies for a standard concern. | Accepted |
| ADR-002 | Expose separate `/health/live` and `/health/ready` endpoints rather than a single `/health` | Aligns with orchestrator best practices; liveness and readiness have distinct semantics. | Proposed — confirm with ops team |
| ADR-003 | Defer deep dependency health checks (DB, external services) to a follow-on task | Keeps this change within the moderate effort ceiling and reduces risk of introducing new failure modes at launch. | Accepted |
| ADR-004 | Runtime version and cloud provider TBD | Tech analysis lists runtime as unknown; version-specific registration API (`MapHealthChecks` vs. `UseHealthChecks`) depends on this. | TODO |