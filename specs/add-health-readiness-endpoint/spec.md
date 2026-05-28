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
- No structured health-check response contract exists.
- Infrastructure probes (load balancer, orchestrator) have no dedicated target; they may be hitting an unrelated route or relying on TCP-level checks only.
- Specific classes, config keys, and routing registrations related to health checking: **TODO** — codebase context not provided; these must be identified during implementation planning.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route exists | `/health` route registered and handled | N |
| Health response contract | None | Structured response with at minimum a status field and HTTP status code | N |
| Readiness logic | None | Endpoint reflects service readiness state (e.g., dependencies reachable, app initialised) | N |
| Configuration | No health endpoint config | TODO — determine if port, path, or auth config is required | N |

---

## Compatibility & Breaking Changes

No breaking changes are introduced by this task. The `/health` endpoint is a net-new addition and does not modify any existing interfaces, APIs, or data models.

| Change | Impact | Migration Path |
|---|---|---|
| New route `/health` added | Additive only | No migration required for existing callers |
| TODO: If `/health` path conflicts with an existing route | Potential conflict | TODO — verify no existing route uses this path |

---

## Acceptance Criteria

1. **Given** the service is running and fully initialised, **when** an HTTP GET request is made to `/health`, **then** the response HTTP status code is `200`.
2. **Given** the service is running and fully initialised, **when** an HTTP GET request is made to `/health`, **then** the response body contains a field indicating a healthy/ready status (e.g., `"status": "ok"` or equivalent structured format).
3. **Given** the service is not yet ready (e.g., a required dependency is unreachable or initialisation is incomplete), **when** an HTTP GET request is made to `/health`, **then** the response HTTP status code is `503` (or a non-2xx code).
4. **Given** a request is made to `/health` using an HTTP method other than GET (e.g., POST), **when** the request is received, **then** the response HTTP status code is `405 Method Not Allowed`.
5. **Given** the service is running, **when** `/health` is called repeatedly under normal load, **then** the endpoint responds within **TODO** ms (latency threshold to be defined) and does not cause side effects or write operations.
6. **Given** a CI pipeline is running, **when** the test suite executes, **then** an automated test verifies the `/health` endpoint returns `200` with the expected response body for a healthy service instance.
7. **Given** the service is deployed in the target environment, **when** the infrastructure readiness probe is configured to call `/health`, **then** the probe reports the instance as ready only after the endpoint returns `200`.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and framework is the service built on? This determines how the route is registered and tested. | TODO | TODO |
| 2 | What dependencies (database, cache, downstream services) should be checked as part of readiness, versus liveness? | TODO | TODO |
| 3 | Should the `/health` endpoint require authentication, or must it be publicly accessible for infrastructure probes? | TODO | TODO |
| 4 | What is the required response body schema — plain JSON `{"status":"ok"}`, or a richer format including dependency statuses? | TODO | TODO |
| 5 | Is there a separate `/health/live` (liveness) endpoint also required, or only readiness? | TODO | TODO |
| 6 | What is the acceptable response latency threshold for the health endpoint under load? | TODO | TODO |
| 7 | Does the `/health` path conflict with any existing route in the service? | TODO | TODO |
| 8 | Should the endpoint be served on the same port as the main application, or a separate management/admin port? | TODO | TODO |