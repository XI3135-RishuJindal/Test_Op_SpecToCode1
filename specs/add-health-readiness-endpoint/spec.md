# Spec: Add /health Readiness Endpoint

## Summary

This spec covers the addition of a `/health` HTTP readiness endpoint to the service. The endpoint will provide a standardised mechanism for infrastructure components (load balancers, container orchestrators, monitoring systems) to determine whether the service is ready to accept traffic. The expected outcome is a lightweight, reliable endpoint that returns a structured response reflecting the current readiness state of the application.

---

## Motivation

- **Operational need:** Without a dedicated readiness endpoint, infrastructure tooling (e.g., Kubernetes readiness probes, load balancer health checks) has no reliable way to determine whether the service is ready to handle requests. This creates risk of traffic being routed to instances that are not yet initialised or are in a degraded state.
- **Upgrade urgency:** Medium — the absence of this endpoint is a gap in operational observability and deployment safety, but does not represent an immediate outage risk.
- **Compliance / best practice:** Readiness endpoints are a standard requirement for services deployed in containerised or cloud-native environments and are expected by most modern deployment pipelines.
- **Tech debt:** The lack of a health endpoint is a known operational gap that increases the risk of failed deployments going undetected and complicates zero-downtime rollout strategies.

---

## Current State

- There is currently no `/health` or equivalent readiness endpoint exposed by the service.
- No health-check route, handler, or controller exists.
- Infrastructure probes (load balancer, orchestrator) have no dedicated target; they may be hitting an unrelated route or relying on TCP-level checks only.
- Specific classes, config keys, and schema elements affected: **TODO** — codebase context was not provided; these must be identified during implementation planning.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route exists | `/health` GET route registered and handled | N |
| Health handler / controller | Does not exist | New handler returns readiness status and HTTP status code | N |
| Response contract | N/A | Structured response body indicating readiness state (at minimum: status field) | N |
| Configuration | No health endpoint config | TODO — determine if port, path, or auth config is required | N |
| Infrastructure probe config | TCP-level or absent | Points to `GET /health` | N |

**What is added:**
- A `GET /health` endpoint accessible over HTTP.
- A response body with at minimum a machine-readable status indicator (e.g., `{ "status": "ok" }` or equivalent).
- Appropriate HTTP status codes: `200` when ready, a non-2xx code (e.g., `503`) when not ready.

**What is removed:**
- Nothing is removed.

**What changes:**
- Infrastructure probe configuration updated to target the new endpoint.

---

## Compatibility & Breaking Changes

No breaking changes are introduced. The `/health` route is a net-new addition and does not modify any existing routes, data models, or interfaces.

| Change | Impact | Migration Path |
|---|---|---|
| New `/health` route registered | Additive only | No action required by existing callers |
| Infrastructure probe reconfiguration | Operational change | TODO — confirm existing probe config location and update target to `GET /health` |

---

## Acceptance Criteria

1. **Given** the service is running and fully initialised, **when** a `GET /health` request is made, **then** the response HTTP status code is `200`.
2. **Given** the service is running and fully initialised, **when** a `GET /health` request is made, **then** the response body contains a machine-readable field indicating a ready/healthy state (e.g., a `status` field with a positive value).
3. **Given** the service is not ready (e.g., a required dependency is unavailable or initialisation is incomplete), **when** a `GET /health` request is made, **then** the response HTTP status code is `503` (or another non-2xx code).
4. **Given** a `GET /health` request is made, **when** the endpoint responds, **then** the `Content-Type` header indicates a structured format (e.g., `application/json`).
5. **Given** the service is running, **when** a `GET /health` request is made, **then** the response is returned within 500 milliseconds under normal operating conditions.
6. **Given** an infrastructure readiness probe is configured to target `GET /health`, **when** the service starts successfully, **then** the probe transitions to a healthy/passing state without manual intervention.
7. **Given** the CI pipeline runs, **when** the test suite executes, **then** an automated test verifies that `GET /health` returns `200` for a running service instance.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and framework is the service built on? This determines the implementation approach for routing and handlers. | TODO | TODO |
| 2 | Should the `/health` endpoint perform deep checks (e.g., database connectivity, downstream dependency reachability) or return a shallow/static response only? | TODO | TODO |
| 3 | Is the endpoint required to be unauthenticated (typical for infrastructure probes), or does it need to sit behind existing auth middleware? | TODO | TODO |
| 4 | Should a separate `/ready` (readiness) and `/live` (liveness) endpoint be provided, or is a single `/health` endpoint sufficient? | TODO | TODO |
| 5 | What is the exact response schema contract expected by the infrastructure tooling (Kubernetes, load balancer, etc.)? | TODO | TODO |
| 6 | Should the endpoint be served on the same port as the main application or a separate management/admin port? | TODO | TODO |
| 7 | Are there existing logging or metrics conventions that the health endpoint should conform to (e.g., should health check requests be excluded from access logs)? | TODO | TODO |