# Spec: Add /health Readiness Endpoint

## Summary

This spec covers the addition of a `/health` HTTP readiness endpoint to the service. The endpoint will provide a standardised mechanism for infrastructure components (load balancers, container orchestrators, monitoring systems) to determine whether the service is ready to accept traffic. The expected outcome is a lightweight, reliable endpoint that returns a structured response reflecting the current readiness state of the application.

## Motivation

- **Operational need:** Without a dedicated readiness endpoint, infrastructure tooling (e.g., Kubernetes readiness probes, load balancer health checks) has no reliable way to determine whether the service is ready to handle requests. This creates risk of traffic being routed to instances that are not yet initialised or are in a degraded state.
- **Upgrade urgency:** Medium — the absence of this endpoint is a gap in operational readiness and observability, but does not represent an immediate outage risk.
- **Compliance / reliability:** Many deployment platforms require a health or readiness endpoint as a prerequisite for automated rollout, scaling, and self-healing behaviour.
- **Tech debt:** The lack of a health endpoint is an identified tech debt item that limits the service's operability in modern deployment environments.

## Current State

- There is no existing `/health` or equivalent readiness endpoint in the service.
- No current interface, API route, or handler exists for health or readiness checks.
- Infrastructure probes (if any) are currently either absent, relying on TCP checks, or using an unstructured workaround.
- Specific classes, config keys, and schema elements affected: **TODO** — codebase language, runtime, and framework details were not provided in the tech analysis.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route exists | `/health` GET route added | N |
| Health response contract | None | Structured response body with at minimum a `status` field and HTTP status code | N |
| Dependency checks | None | TODO — whether downstream dependencies (DB, cache, etc.) are checked as part of readiness is unresolved | N |
| Configuration | No health endpoint config | TODO — configurable timeout or dependency check list may be needed | N |

**What is added:**
- A `GET /health` endpoint returning an appropriate HTTP status code (e.g., `200 OK` when ready, `503 Service Unavailable` when not ready).
- A structured JSON response body containing at minimum a `status` field (e.g., `"status": "ok"` or `"status": "unavailable"`).

**What is removed:**
- Nothing is removed.

**What changes:**
- The service's HTTP routing layer is updated to register the new route.

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New `GET /health` route added | Additive only — no existing routes are modified | No migration required for existing callers |
| Response contract for `/health` | New contract; no prior contract existed | Callers should expect `200` with `{"status": "ok"}` on success and `503` on not-ready |
| Dependency check behaviour | TODO — if downstream checks are included, a failing dependency will cause `503` | TODO — document which dependencies are checked and their failure behaviour |

## Acceptance Criteria

1. **Given** the service is running and fully initialised, **when** a `GET /health` request is made, **then** the response HTTP status code is `200`.
2. **Given** the service is running and fully initialised, **when** a `GET /health` request is made, **then** the response body is valid JSON containing at minimum a `status` field with a value indicating readiness (e.g., `"ok"`).
3. **Given** the service is in a not-ready state (e.g., still initialising or a required dependency is unavailable — TODO: confirm scope), **when** a `GET /health` request is made, **then** the response HTTP status code is `503`.
4. **Given** a `GET /health` request is made, **when** the endpoint is called, **then** the response is returned within 500 milliseconds under normal operating conditions.
5. **Given** a `POST`, `PUT`, `DELETE`, or other non-GET HTTP method is used against `/health`, **when** the request is made, **then** the response HTTP status code is `405 Method Not Allowed`.
6. **Given** the service is deployed in a container orchestration environment, **when** a readiness probe is configured to call `GET /health`, **then** the probe succeeds (receives `200`) once the service is ready and fails (receives `503` or connection refused) before the service is ready.
7. **Given** the `/health` endpoint is called, **when** the response is returned, **then** no authentication or authorisation is required to access the endpoint (it must be publicly accessible to infrastructure probes).

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and framework is the service built on? This determines the implementation approach for routing and response handling. | TODO | TODO |
| 2 | Should the `/health` endpoint perform shallow checks only (process is alive) or deep checks (verify connectivity to downstream dependencies such as databases, caches, or external APIs)? | TODO | TODO |
| 3 | If deep dependency checks are included, which specific dependencies should be checked as part of readiness? | TODO | TODO |
| 4 | Should there be a separate `/health/live` (liveness) endpoint distinct from `/health` (readiness), or is a single endpoint sufficient? | TODO | TODO |
| 5 | What is the expected response body schema beyond the `status` field? Should it include version, uptime, or dependency sub-statuses? | TODO | TODO |
| 6 | Are there security or network policy requirements that would restrict access to the `/health` endpoint (e.g., internal-only access)? | TODO | TODO |
| 7 | Should the endpoint be excluded from access logs or metrics collection to avoid noise? | TODO | TODO |