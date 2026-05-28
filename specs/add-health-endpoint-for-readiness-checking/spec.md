# Spec: Add /health Endpoint for Readiness Checking

## Summary

This spec covers the addition of a `/health` HTTP endpoint to the service for the purpose of readiness checking. The endpoint will allow orchestration platforms, load balancers, and monitoring systems to programmatically determine whether the service is ready to accept traffic. The expected outcome is a standardised, lightweight endpoint that returns the current health and readiness status of the service.

---

## Motivation

- **Operational readiness:** Without a dedicated health endpoint, orchestration platforms (e.g., Kubernetes, ECS) cannot reliably determine whether the service is ready to receive traffic, leading to potential routing of requests to unready instances.
- **Monitoring gaps:** The absence of a machine-readable health check forces operators to rely on indirect signals (e.g., log scraping, port checks), increasing mean time to detection for service degradation.
- **Upgrade urgency:** Rated **medium** — the service is functional but lacks a standard readiness signal, which is a gap in operational maturity and a prerequisite for safe automated deployments and rolling restarts.
- **Compliance / best practice:** Health endpoints are a baseline requirement for services operating in containerised or cloud-native environments and are expected by most modern deployment pipelines.

---

## Current State

- There is **no existing `/health` endpoint** or equivalent readiness/liveness route in the service.
- No current mechanism exists for orchestrators or load balancers to query service readiness programmatically.
- Specific frameworks, runtime, and build tooling are not confirmed in the provided context (see Open Questions).
- No existing health-check configuration keys, middleware, or data models are present to reference.

---

## Proposed Changes

The following changes are required to introduce the `/health` endpoint:

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route exists | `/health` route registered, responds to `GET` requests | N |
| Health response contract | None | Returns HTTP `200` with a structured readiness payload when healthy | N |
| Unhealthy response contract | None | Returns HTTP `503` with a structured payload when not ready | N |
| Health check logic | None | Evaluates service readiness (at minimum: process is alive and accepting connections) | N |
| Dependency checks | None | TODO — scope of dependency checks (e.g., database, cache) to be confirmed | N/A |

---

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New `GET /health` route added | Additive only — no existing routes are modified or removed | No migration required for existing callers |
| Response payload schema introduced | New contract; no prior consumers | Consumers should be built against the new schema from the outset |
| TODO: If auth/middleware is applied globally | Could inadvertently require authentication on `/health` | TODO — confirm whether `/health` must be excluded from authentication middleware |

---

## Acceptance Criteria

1. **Given** the service is running and ready to accept traffic, **when** a `GET` request is made to `/health`, **then** the response status code is `200`.

2. **Given** the service is running and ready to accept traffic, **when** a `GET` request is made to `/health`, **then** the response body contains a machine-readable payload indicating a healthy/ready status (e.g., a status field with a defined value such as `"ok"` or `"ready"`).

3. **Given** the service is in an unready or degraded state, **when** a `GET` request is made to `/health`, **then** the response status code is `503`.

4. **Given** the service is in an unready or degraded state, **when** a `GET` request is made to `/health`, **then** the response body contains a machine-readable payload indicating the unhealthy/not-ready status.

5. **Given** a `GET` request is made to `/health`, **when** the service is healthy, **then** the response is returned within an acceptable latency threshold (TODO — define threshold, suggested ≤ 200 ms under normal load).

6. **Given** a request is made to `/health` using any HTTP method other than `GET` (e.g., `POST`, `PUT`), **when** the request is received, **then** the response status code is `405 Method Not Allowed`.

7. **Given** the `/health` endpoint is deployed, **when** a CI health-check test suite is executed against the running service, **then** all acceptance criteria above pass without manual intervention.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the confirmed runtime, language, and framework for this service? This affects how the route is registered and tested. | TODO | TODO |
| 2 | Should `/health` also serve as a liveness check, or should liveness and readiness be separate endpoints (e.g., `/health/live` and `/health/ready`)? | TODO | TODO |
| 3 | What dependencies (database, cache, external APIs) should be checked as part of the readiness evaluation, if any? | TODO | TODO |
| 4 | Should the `/health` endpoint be excluded from authentication/authorisation middleware? | TODO | TODO |
| 5 | Is there a required response payload schema (e.g., mandated by the platform or an internal standard)? | TODO | TODO |
| 6 | What is the acceptable response latency threshold for the health endpoint under normal load? | TODO | TODO |
| 7 | Should the endpoint be accessible externally, or restricted to internal/cluster traffic only? | TODO | TODO |