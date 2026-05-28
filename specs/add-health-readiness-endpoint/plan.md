# Plan: Add /health Readiness Endpoint

## Overview

**Migration Strategy: Feature-Flag Gated / Big-Bang (Single Increment)**

Adding a `/health` readiness endpoint is a net-new, additive change with no modification to existing functionality. The risk score is low — no existing code paths are altered, and the endpoint can be introduced in a single, self-contained increment.

A **big-bang delivery within one phase** is appropriate here: the endpoint is either present or absent, there is no legacy behavior to strangle, and no parallel-run infrastructure is needed. If the deployment platform supports it, the route can be placed behind a feature flag during initial rollout to allow safe validation in production before wiring it into load-balancer or orchestrator health checks.

> **Note:** The tech analysis did not supply language, runtime, framework, or build-tool details. All component-level specifics below are marked TODO and must be filled in once the codebase is identified.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Discovery & Design | Identify existing routing layer, agree on response schema, define readiness criteria (e.g., DB reachable, dependencies up) | Access to codebase and deployment manifests | TODO (derive from "moderate" option person-days once provided) |
| 2 — Implementation | Add `/health` route handler returning structured JSON; implement readiness checks | Phase 1 complete | TODO |
| 3 — Testing | Unit, integration, and contract tests for the endpoint | Phase 2 complete | TODO |
| 4 — Infrastructure Wiring | Update orchestrator/load-balancer health-check config to point to `/health` | Phase 3 passing in CI | TODO |
| 5 — Release & Validation | Deploy, monitor, confirm probes are green | Phase 4 complete | TODO |

> **TODO:** Populate effort columns (person-days) once the "moderate" upgrade option detail document is provided.

---

## Component Changes

### Route / Controller Layer
- **What changes:** A new route handler is registered for `GET /health`.
- **Files affected:** TODO — identify the primary router/controller file (e.g., `routes/index.*`, `app.*`, `server.*`, `controllers/health.*`).
- **API added:**
  - `GET /health`
  - Success response `200 OK`:
    ```json
    {
      "status": "ok",
      "checks": {
        "database": "ok",
        "dependencies": "ok"
      },
      "timestamp": "<ISO-8601>"
    }
    ```
  - Failure response `503 Service Unavailable`:
    ```json
    {
      "status": "unavailable",
      "checks": {
        "database": "error"
      },
      "timestamp": "<ISO-8601>"
    }
    ```

### Readiness Check Module
- **What changes:** A new module/class encapsulates individual readiness probes (e.g., database ping, downstream service reachability).
- **Files affected:** TODO — e.g., `health/readiness.*, src/checks/health.*`.
- **Classes/methods:** TODO — e.g., `HealthChecker.check()`, `DatabaseProbe.ping()`.

### Application Entry Point
- **What changes:** The new route is registered before the application starts accepting traffic.
- **Files affected:** TODO — e.g., `main.*`, `app.*`, `server.*`.

### Configuration
- **What changes:** Any timeout or threshold values for readiness probes should be externalized.
- **Config keys to add:**
  - `HEALTH_CHECK_TIMEOUT_MS` (default: `3000`)
  - `HEALTH_CHECK_DB_ENABLED` (default: `true`)

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> The `/health` endpoint is expected to be implemented using the existing framework already present in the codebase. No new third-party dependencies are required. If a dedicated health-check library is desired, TODO: evaluate options once the runtime/framework is confirmed.

---

## Infrastructure Changes

### Kubernetes (if applicable)
- **TODO:** Confirm whether the service runs on Kubernetes.
- If yes, add or update the `readinessProbe` stanza in the relevant `Deployment` manifest:
  ```yaml
  readinessProbe:
    httpGet:
      path: /health
      port: <TODO: app port>
    initialDelaySeconds: 5
    periodSeconds: 10
    failureThreshold: 3
  ```

### Docker
- **TODO:** Confirm base image and whether a `HEALTHCHECK` instruction should be added to the `Dockerfile`:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:<TODO:port>/health || exit 1
  ```

### Load Balancer / Reverse Proxy
- **TODO:** Update health-check path in load-balancer config (e.g., AWS Target Group, NGINX upstream, HAProxy backend) from any existing path to `/health`.

### CI/CD Pipeline
- **TODO:** Identify CI platform (GitHub Actions, Jenkins, GitLab CI, etc.).
- Add a smoke-test step post-deploy that calls `GET /health` and asserts `200 OK` before marking the deployment successful.

---

## Rollback Strategy

Each phase is independently reversible because the change is purely additive.

| Phase | Rollback Action |
|-------|----------------|
| 1 — Discovery & Design | No code changes; discard design artifacts. No action needed. |
| 2 — Implementation | Revert the commit(s) adding the route handler and readiness module. The application continues to function without the endpoint. |
| 3 — Testing | Revert test files alongside implementation commits. No production impact. |
| 4 — Infrastructure Wiring | **Before cutover:** restore previous health-check path in orchestrator/load-balancer config. **After cutover:** re-point probes to the previous path (or remove the `readinessProbe` stanza if none existed) and redeploy manifests. |
| 5 — Release & Validation | If probes fail in production: (a) remove `readinessProbe` from the Kubernetes manifest and redeploy to stop failed readiness checks from taking pods out of rotation; (b) revert application deployment to the previous image tag. |

---

## Testing Strategy

### Unit Tests
- **Scope:** Route handler logic; each individual readiness probe (database, downstream services).
- **Approach:** Mock all I/O dependencies. Assert correct HTTP status codes (`200` / `503`) and response body schema.
- **Tools:** TODO — confirm test framework once runtime is known (e.g., Jest, JUnit, pytest, Go testing).
- **Coverage target:** 100% of the new health module; no reduction in overall project coverage floor.

### Integration Tests
- **Scope:** Full request/response cycle against a locally running application instance with real (or containerized) dependencies.
- **Approach:** Spin up the app and a test database via Docker Compose; call `GET /health` and assert `200 OK`. Simulate a dependency failure (e.g., stop the DB container) and assert `503`.
- **Tools:** TODO — e.g., Supertest, RestAssured, httpx, `net/http/httptest`.

### Regression Tests
- **Scope:** Confirm no existing routes or behaviors are affected by the addition of the new route.
- **Approach:** Run the full existing test suite unchanged; zero new failures is the gate.

### Performance / Probe Overhead
- **Scope:** Ensure the `/health` endpoint responds within the configured `HEALTH_CHECK_TIMEOUT_MS` (default 3 000 ms) under normal load.
- **Approach:** TODO — run a brief load test (e.g., k6, wrk, Locust) targeting `/health` concurrently with normal traffic.
- **Gate:** p99 latency < 500 ms; no errors under expected probe frequency.

### CI Gates
- All unit and integration tests must pass before merge to main.
- The post-deploy smoke test (`GET /health` → `200 OK`) must pass before the pipeline marks the release successful.
- TODO: Add a required status check in the branch protection rules for the health-check test suite.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Design agreed, response schema signed off | 1 — Discovery & Design | TODO | TODO |
| `/health` route and readiness module implemented | 2 — Implementation | TODO | TODO |
| All tests written and passing in CI | 3 — Testing | TODO | TODO |
| Kubernetes/Docker/LB config updated | 4 — Infrastructure Wiring | TODO | TODO |
| Deployed to production, probes green | 5 — Release & Validation | TODO | TODO |

> **TODO:** Populate all estimated completion dates once the "moderate" upgrade option person-days breakdown is provided and team capacity is known.