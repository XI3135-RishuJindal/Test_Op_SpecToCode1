# Spec: Add /health and /ready HTTP Endpoints

## Summary

This spec covers the addition of two new HTTP endpoints — `/health` and `/ready` — to the existing service. The `/health` endpoint will indicate whether the service process is alive, and the `/ready` endpoint will indicate whether the service is ready to accept traffic. The expected outcome is that infrastructure tooling (load balancers, container orchestrators, monitoring systems) can reliably probe the service's liveness and readiness without relying on ad-hoc checks.

## Motivation

- **Operational gap:** The service currently exposes no standard health or readiness signal, making it incompatible with container orchestration platforms (e.g., Kubernetes liveness/readiness probes) and load balancer health checks that expect HTTP-based responses.
- **Reliability risk:** Without a readiness gate, traffic can be routed to instances that are still initialising or degraded, causing user-facing errors.
- **Upgrade urgency:** Medium — the absence of these endpoints is a known operational gap that increases deployment risk and complicates incident response.
- **Tech debt:** Lack of standardised health signalling forces operators to use fragile workarounds (e.g., TCP checks, process monitors) that do not reflect application-level state.

> **Note:** Specific framework versions, runtime versions, and CVE references are not available in the provided context. See Open Questions.

## Current State

- The service exposes no `/health` or `/ready` HTTP endpoints.
- No liveness or readiness contract exists for infrastructure consumers (load balancers, orchestrators, monitoring agents).
- TODO: Identify existing HTTP router/framework and any middleware stack that new routes must be registered within.
- TODO: Identify any existing startup lifecycle hooks or dependency initialisation sequences that readiness logic should consult.
- TODO: Identify current deployment configuration (e.g., Kubernetes manifests, Docker Compose, systemd) to understand where probe configuration must be updated.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing layer | No `/health` route | `GET /health` route registered, returns liveness status | N |
| HTTP routing layer | No `/ready` route | `GET /ready` route registered, returns readiness status | N |
| Response contract | N/A | `/health` returns `200 OK` when process is alive | N |
| Response contract | N/A | `/ready` returns `200 OK` when all dependencies are reachable and initialisation is complete; `503 Service Unavailable` otherwise | N |
| Response body | N/A | Both endpoints return a structured response body (at minimum a `status` field) | N |
| Deployment / probe config | No probes configured | Liveness and readiness probes point to new endpoints | N |

**Endpoint behaviour summary:**

- **`GET /health`** — Liveness check. Confirms the process is running and the HTTP server is responsive. Does not check downstream dependencies. Returns `200 OK` unconditionally while the process is up.
- **`GET /ready`** — Readiness check. Confirms the service has completed initialisation and all required dependencies (databases, caches, downstream services) are reachable. Returns `200 OK` when ready, `503 Service Unavailable` when not ready.

> TODO: Define the exact set of dependencies that must pass for `/ready` to return `200`. See Open Questions.

> TODO: Define the exact response body schema (fields, format). Minimum required field is `status` with values such as `"ok"` / `"unavailable"`.

## Compatibility & Breaking Changes

No existing endpoints are modified or removed. Both `/health` and `/ready` are net-new routes. There are no breaking changes to existing callers.

| Change | Impact | Migration Path |
|---|---|---|
| New route: `GET /health` | Additive only | No action required for existing callers |
| New route: `GET /ready` | Additive only | No action required for existing callers |
| Deployment probe config update | Infrastructure config change | TODO: Update orchestrator/load balancer probe definitions to reference new endpoints |

## Acceptance Criteria

1. **Given** the service process is running and the HTTP server has started, **when** a `GET /health` request is made, **then** the response status code is `200 OK`.
2. **Given** the service process is running and the HTTP server has started, **when** a `GET /health` request is made, **then** the response body contains a `status` field with a non-empty value.
3. **Given** the service has completed initialisation and all required dependencies are reachable, **when** a `GET /ready` request is made, **then** the response status code is `200 OK`.
4. **Given** one or more required dependencies are unreachable or the service has not completed initialisation, **when** a `GET /ready` request is made, **then** the response status code is `503 Service Unavailable`.
5. **Given** the service is in a non-ready state, **when** a `GET /ready` request is made, **then** the response body contains a `status` field that distinguishes the non-ready state from the ready state.
6. **Given** a `GET /health` request is made, **when** the request includes no authentication headers, **then** the endpoint responds without requiring authentication (endpoints must be publicly accessible to probes).
7. **Given** a `GET /ready` request is made, **when** the request includes no authentication headers, **then** the endpoint responds without requiring authentication.
8. **Given** the service is deployed in the target environment, **when** the orchestrator or load balancer executes its configured liveness probe against `/health`, **then** the probe reports the service as live within the configured timeout.
9. **Given** the service is deployed in the target environment, **when** the orchestrator or load balancer executes its configured readiness probe against `/ready`, **then** traffic is withheld from the instance until `/ready` returns `200 OK`.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What language, runtime, and HTTP framework is the service built on? This determines how routes are registered and what middleware applies. | TODO | TODO |
| 2 | What is the definitive list of dependencies (databases, caches, external services) that must be healthy for `/ready` to return `200`? | TODO | TODO |
| 3 | What is the agreed response body schema for both endpoints (field names, data types, optional metadata such as version or uptime)? | TODO | TODO |
| 4 | Should `/health` or `/ready` be excluded from access logs and metrics to avoid noise? If so, what is the mechanism for filtering them? | TODO | TODO |
| 5 | Are there security or network policy requirements that restrict which sources may call these endpoints (e.g., internal-only, no auth required)? | TODO | TODO |
| 6 | What is the target deployment platform (Kubernetes, ECS, bare metal, etc.) and what probe configuration parameters (timeout, interval, failure threshold) should be used? | TODO | TODO |
| 7 | Should `/ready` reflect a degraded-but-functional state separately from a fully unavailable state, or is a binary `200`/`503` sufficient? | TODO | TODO |