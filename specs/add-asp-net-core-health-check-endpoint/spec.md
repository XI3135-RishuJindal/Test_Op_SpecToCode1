# Spec: Add ASP.NET Core Health-Check Endpoint

## Summary

This spec covers the addition of a standard ASP.NET Core health-check endpoint to the application. The expected outcome is a dedicated HTTP endpoint that reports the application's operational status, enabling load balancers, container orchestrators (e.g., Kubernetes liveness/readiness probes), and monitoring systems to programmatically determine service health without relying on application-specific logic or manual inspection.

## Motivation

- **Operational visibility:** The application currently lacks a standardized health-check surface, making automated health monitoring and orchestration-level decisions (restart, traffic routing) impossible without custom workarounds.
- **Container/orchestration readiness:** Modern deployment targets (Kubernetes, Azure Container Apps, AWS ECS, etc.) require a dedicated health endpoint to implement liveness and readiness probes. Absence of this endpoint is a medium-urgency gap that blocks safe automated deployments.
- **Upgrade urgency:** Medium — the application is deployable today but is not production-safe in orchestrated environments without this capability.
- **Compliance/reliability:** Health endpoints are a baseline requirement for 12-factor application compliance and SRE observability standards.

> **Note:** Specific runtime version, framework version, and build toolchain details were not provided in the tech analysis. See [Open Questions](#open-questions) for items that must be resolved before implementation begins.

## Current State

- **Health monitoring:** TODO — no existing health-check endpoint or middleware has been identified in the provided context. Confirm whether any ad-hoc liveness route (e.g., a `/ping` or `/status` controller action) exists.
- **Startup/middleware pipeline:** TODO — the specific startup configuration class or minimal-API bootstrap file is unknown from the provided context. The middleware registration point must be identified.
- **Configuration:** TODO — no existing health-check configuration keys have been identified.
- **Dependencies checked:** TODO — it is unknown which downstream dependencies (databases, caches, external APIs) are in scope for health reporting.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP routing | No `/health` route exists | `GET /health` returns health status (HTTP 200/503) | N |
| Middleware pipeline | No health-check middleware registered | ASP.NET Core `HealthCheckMiddleware` registered in the request pipeline | N |
| Service registration | No health-check services registered | Health-check services added to the DI container | N |
| Health checks (liveness) | N/A | Basic liveness check confirming the process is running | N |
| Health checks (readiness) | N/A | TODO — readiness checks for downstream dependencies (DB, cache, etc.) to be defined | N |
| Response format | N/A | JSON body with status field; HTTP 200 for `Healthy`, HTTP 503 for `Unhealthy` or `Degraded` | N |
| Configuration keys | N/A | TODO — any threshold or dependency-specific config keys to be named once dependencies are confirmed | N |

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New route `GET /health` | Additive only — no existing route is displaced | No migration required; callers must opt in to consume the new endpoint |
| New route `GET /health/live` (liveness sub-path, if adopted) | Additive | No migration required |
| New route `GET /health/ready` (readiness sub-path, if adopted) | Additive | No migration required |
| DI service registration added to startup | No breaking change to existing registrations expected | TODO — confirm no naming collision with any existing custom service named `HealthCheck` |
| TODO — if an existing ad-hoc `/ping` or `/status` route is found | Potential duplication or conflict | TODO — define whether the legacy route is removed, aliased, or retained alongside the new endpoint |

## Acceptance Criteria

1. **Given** the application is running and healthy, **when** an HTTP GET request is made to `/health`, **then** the response status code is `200 OK` and the response body contains a status field with the value `Healthy`.

2. **Given** the application is running and healthy, **when** an HTTP GET request is made to `/health`, **then** the response `Content-Type` header is `application/json`.

3. **Given** a registered downstream dependency (e.g., database) is unreachable, **when** an HTTP GET request is made to `/health`, **then** the response status code is `503 Service Unavailable` and the response body reflects an `Unhealthy` or `Degraded` status.

4. **Given** the application is running, **when** an HTTP GET request is made to `/health` by an unauthenticated client, **then** the endpoint responds without requiring authentication (i.e., the health route is excluded from auth middleware). *(TODO — confirm authorization policy with security owner.)*

5. **Given** the application is deployed in a Kubernetes environment, **when** the liveness probe is configured to call `GET /health` (or `GET /health/live`), **then** the probe succeeds within the configured timeout and the pod is not restarted under normal operating conditions.

6. **Given** the application is deployed in a Kubernetes environment, **when** the readiness probe is configured to call `GET /health` (or `GET /health/ready`), **then** the probe returns unhealthy and the pod is removed from the load-balancer pool when a required dependency is unavailable.

7. **Given** the health-check endpoint is called, **when** the application is under normal load, **then** the endpoint responds in under 500 ms (p99) as verified by a load-test or integration-test assertion.

8. **Given** the CI pipeline runs, **when** integration tests execute, **then** at least one automated test asserts the `/health` endpoint returns `200 OK` with a `Healthy` status against a locally running instance of the application.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact runtime and ASP.NET Core version in use? This determines which `Microsoft.Extensions.Diagnostics.HealthChecks` package version to target. | TODO | TODO |
| 2 | Which downstream dependencies (databases, caches, message brokers, external APIs) must be included in readiness health checks? | TODO | TODO |
| 3 | Should the endpoint expose a single `/health` route or separate `/health/live` and `/health/ready` sub-paths for liveness vs. readiness? | TODO | TODO |
| 4 | Is there an existing ad-hoc health or ping route that must be removed or aliased? | TODO | TODO |
| 5 | What authorization policy applies to the health endpoint — fully public, IP-restricted, or internal-network only? | TODO (Security Owner) | TODO |
| 6 | Should the health response body include detailed dependency-level status, or only a top-level aggregate status? (Detailed output may expose internal topology.) | TODO (Security Owner) | TODO |
| 7 | What is the build toolchain and project structure? This determines where service registration and middleware pipeline changes are made. | TODO | TODO |
| 8 | Are there any existing monitoring or alerting integrations (e.g., Application Insights, Datadog) that should consume the new endpoint automatically? | TODO | TODO |