# Spec: Add /health Readiness Endpoint

## Summary

This spec covers the addition of a `/health` HTTP readiness endpoint to the service. The endpoint will provide a standardised mechanism for infrastructure components (load balancers, container orchestrators, monitoring systems) to determine whether the service is ready to accept traffic. The expected outcome is a lightweight, reliable endpoint that returns a structured response reflecting the current readiness state of the application.

---

## Motivation

- **Operational need:** Without a dedicated readiness endpoint, infrastructure tooling (e.g., Kubernetes readiness probes, load balancer health checks) has no reliable way to determine whether the service is ready to handle requests. This creates risk of traffic being routed to instances that are not yet initialised or are in a degraded state.
- **Upgrade urgency:** Medium — the absence of this endpoint is a gap in operational observability and deployment safety, but does not represent an immediate outage risk.
- **Compliance / best practice:** Readiness endpoints are a standard requirement for services deployed in containerised or cloud-native environments and are expected by most modern deployment platforms.
- **Tech debt:** The lack of a health endpoint is an operational debt item that increases deployment risk and complicates incident response.

> **Note:** Specific framework, runtime, and language details were not provided in the tech analysis. Version-specific references are marked as TODO below.

---

## Current State

- There is currently **no `/health` endpoint** exposed by the service.
- No readiness or liveness probe contract exists for infrastructure consumers.
- TODO: Identify any existing monitoring or ping endpoints that may partially overlap with this functionality.
- TODO: Identify the current HTTP routing layer, middleware stack, and any existing response envelope formats used by the service.
- TODO: Identify existing application startup or dependency-check logic that should inform readiness state.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route defined | `GET /health` route registered and handled | N |
| Response contract | N/A | Returns structured JSON body with readiness status and HTTP status code | N |
| Dependency checks | TODO — unknown if any exist | TODO — determine whether downstream dependency checks (DB, cache, etc.) are included in readiness response | TODO |
| Infrastructure config | No health probe target defined | `/health` designated as the readiness probe endpoint | N |

**What is added:**
- A `GET /health` endpoint that returns an HTTP `200 OK` when the service is ready to accept traffic.
- A structured JSON response body indicating overall readiness status (at minimum `{ "status": "ok" }`).
- An HTTP `503 Service Unavailable` response when the service is not ready (e.g., during startup or when a critical dependency is unavailable).

**What is removed:**
- Nothing is removed.

**What changes:**
- Infrastructure probe configuration (Kubernetes readiness probe, load balancer health check target, etc.) should be updated to point to `/health`.

---

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New `GET /health` route added | Additive only — no existing callers affected | No migration required |
| TODO: If an existing ad-hoc ping/health route exists at a different path | Potential duplication or conflict | TODO — determine whether the existing route should be deprecated or aliased |
| Infrastructure probe reconfiguration | Deployment configuration must be updated to reference `/health` | Update readiness probe target in deployment manifests / load balancer config |

---

## Acceptance Criteria

1. **Given** the service has started successfully and all critical dependencies are reachable, **when** a `GET /health` request is made, **then** the response status code is `200 OK` and the response body is valid JSON containing a field indicating a ready/healthy status (e.g., `"status": "ok"`).

2. **Given** the service is not yet ready (e.g., mid-initialisation or a critical dependency is unavailable), **when** a `GET /health` request is made, **then** the response status code is `503 Service Unavailable` and the response body is valid JSON indicating the not-ready state.

3. **Given** a `GET /health` request is made, **when** the endpoint responds, **then** the `Content-Type` response header is `application/json`.

4. **Given** a `POST`, `PUT`, `DELETE`, or other non-GET HTTP method is used against `/health`, **when** the request is received, **then** the response status code is `405 Method Not Allowed`.

5. **Given** the service is running normally, **when** a `GET /health` request is made, **then** the response time is under 500 ms under normal load conditions (verifiable via a CI performance/smoke test).

6. **Given** a Kubernetes (or equivalent) readiness probe is configured to target `GET /health`, **when** the service pod starts, **then** the pod transitions to the `Ready` state only after `/health` returns `200 OK`.

7. **Given** the `/health` endpoint is called, **when** the response is returned, **then** no authentication or authorisation is required to access the endpoint (it must be publicly reachable by infrastructure probes).

> TODO: Add acceptance criteria for individual dependency checks if it is decided that downstream dependency health is included in the readiness response.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and framework is the service built on? This determines the implementation approach and any framework-specific conventions for health endpoints. | TODO | TODO |
| 2 | Should the `/health` endpoint perform active checks against downstream dependencies (database, cache, external APIs), or should it reflect only the local process readiness? | TODO | TODO |
| 3 | Is there an existing endpoint (e.g., `/ping`, `/status`) that overlaps with this functionality? If so, should it be deprecated? | TODO | TODO |
| 4 | What is the required response schema? Should it include additional fields such as `version`, `uptime`, or per-dependency status beyond a top-level `status` field? | TODO | TODO |
| 5 | Should a separate `/health/live` liveness endpoint also be introduced, or is a single `/health` readiness endpoint sufficient for current needs? | TODO | TODO |
| 6 | Are there security or network policy requirements that would restrict access to `/health` (e.g., internal-only routing)? | TODO | TODO |
| 7 | Which deployment platform and probe mechanism will consume this endpoint (Kubernetes, ECS, ALB, etc.)? This affects timeout and interval configuration recommendations. | TODO | TODO |