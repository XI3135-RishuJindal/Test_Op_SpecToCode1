# Spec: Add ASP.NET Core Health-Check Endpoint

## Summary

This spec covers the addition of a standard ASP.NET Core health-check endpoint to the application. The expected outcome is a dedicated HTTP endpoint that reports the live/ready status of the service, enabling orchestration platforms (e.g., Kubernetes, load balancers, monitoring tools) to probe application health without relying on ad-hoc workarounds or application-specific conventions.

---

## Motivation

- **Operational visibility:** The application currently lacks a standardized health-check surface, making it difficult for infrastructure tooling to determine whether the service is healthy, degraded, or unavailable.
- **Orchestration compatibility:** Container orchestrators (e.g., Kubernetes) require liveness and readiness probes. Without a dedicated endpoint, deployments rely on TCP checks or custom scripts, which are fragile and incomplete.
- **Upgrade urgency:** Medium — the absence of health checks is a recognized operational gap that increases mean time to detection (MTTD) for service degradation.
- **Tech debt:** Lack of a health-check endpoint is a missing baseline capability for any production-grade ASP.NET Core service. ASP.NET Core has included first-party health-check middleware (`Microsoft.Extensions.Diagnostics.HealthChecks`) since version 2.2; not using it represents accumulated tech debt against the platform standard.

> **Note:** Specific runtime and framework versions were not provided in the tech analysis. See [Open Questions](#open-questions).

---

## Current State

- **No existing health-check endpoint** has been identified in the application. There is no route, controller action, or middleware currently serving a standardized health or readiness response.
- **No registration** of `IHealthChecksBuilder` or `AddHealthChecks()` in the service registration pipeline has been confirmed.
- **No middleware** mapping (e.g., `MapHealthChecks`) is present in the request pipeline configuration.
- Specific classes, configuration keys, and startup/program entry points are TODO pending codebase review.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Service registration (DI container) | No health-check services registered | `AddHealthChecks()` registered with relevant dependency checks | N |
| Request pipeline / middleware | No health-check route mapped | Health-check endpoint mapped at a defined route (e.g., `/health` or `/healthz`) | N |
| Liveness probe route | Not present | Dedicated liveness route returning live/not-live status | N |
| Readiness probe route | Not present | Dedicated readiness route returning ready/not-ready status (if applicable) | N |
| Health-check response format | N/A | Standard JSON or plain-text response conforming to ASP.NET Core `HealthReport` schema | N |
| Authentication/authorization on health route | N/A | Health endpoint explicitly excluded from authentication requirements (or scoped as appropriate) | N |

**What is added:**
- Registration of the ASP.NET Core built-in health-check infrastructure.
- One or more named health checks covering critical dependencies (e.g., database connectivity, external service reachability — specifics TODO).
- Mapped HTTP route(s) for health probes.

**What is removed:**
- Any ad-hoc ping/status endpoints that duplicate this concern (TODO — confirm whether any exist).

---

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| New `/health` (or `/healthz`) route added | Minimal — additive change; no existing route is modified | No caller migration required; infrastructure teams should update probe configurations to use the new route |
| Existing ad-hoc status endpoints (if any) deprecated | Callers relying on the old endpoint will need to update | TODO — identify callers and coordinate cutover before removing legacy endpoint |
| Authorization policy applied (or explicitly bypassed) to health route | Security posture change | TODO — confirm policy with security/platform team before finalizing |

---

## Acceptance Criteria

1. **Given** the application is running, **when** an HTTP GET request is made to the health-check endpoint, **then** the response status code is `200 OK` and the body indicates a healthy status.

2. **Given** a registered dependency (e.g., database) is unavailable, **when** an HTTP GET request is made to the health-check endpoint, **then** the response status code is `503 Service Unavailable` and the body indicates an unhealthy or degraded status identifying the failing check by name.

3. **Given** the application is running, **when** the health-check endpoint is called, **then** the response is returned within 5 seconds under normal operating conditions.

4. **Given** the application's authentication middleware is active, **when** an unauthenticated HTTP GET request is made to the health-check endpoint, **then** the response is not `401 Unauthorized` (the endpoint is accessible without credentials, or per the agreed authorization policy — TODO confirm policy).

5. **Given** a CI pipeline build, **when** the application starts in the test environment, **then** an automated probe of the health-check endpoint returns `200 OK`, confirming the endpoint is reachable and all registered checks pass.

6. **Given** the health-check endpoint is called, **when** the response body is inspected, **then** it conforms to the expected schema (status field present; individual check results enumerable) as defined by the ASP.NET Core `HealthReport` response writer in use.

7. **Given** a liveness and readiness route are configured separately, **when** each route is probed independently, **then** each returns a response reflecting only the checks registered to that probe group.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact ASP.NET Core runtime version in use? This determines which health-check API surface is available. | TODO | TODO |
| 2 | What specific dependencies (database, cache, external APIs) must be covered by registered health checks? | TODO | TODO |
| 3 | Should liveness and readiness be split into separate routes, or is a single `/health` route sufficient? | TODO | TODO |
| 4 | What is the agreed URL path for the health endpoint (`/health`, `/healthz`, `/status`, etc.)? | TODO | TODO |
| 5 | Should the health endpoint be excluded from authentication, or require a specific role/policy? | TODO | TODO |
| 6 | Are there any existing ad-hoc ping/status endpoints that should be deprecated once this endpoint is live? | TODO | TODO |
| 7 | What response format is required — plain text, JSON `HealthReport`, or a custom schema expected by the monitoring platform? | TODO | TODO |
| 8 | Does the health-check endpoint need to be excluded from access logs or rate limiting to avoid noise? | TODO | TODO |