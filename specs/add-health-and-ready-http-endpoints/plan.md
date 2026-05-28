# Plan: Add /health and /ready HTTP endpoints

## Overview

**Migration Strategy: Feature-flag gated / Big-bang (small scope)**

The task is narrowly scoped to adding two new HTTP endpoints (`/health` and `/ready`) to an existing service. Because these are additive, non-breaking changes that introduce no modifications to existing endpoints or business logic, a **big-bang delivery** within a single, short development cycle is appropriate. There is no existing functionality to strangle or migrate, and no parallel-run infrastructure is required.

Risk is low: the endpoints are read-only, stateless (or lightly stateful for readiness), and can be deployed behind a feature flag if the team requires a staged rollout. The upgrade urgency is rated **medium**, and the effort is small, making a single-phase delivery the most pragmatic choice.

> **Note:** The tech analysis did not identify the language, runtime, build tool, or framework in use. All file names, class names, and tooling references below are marked **TODO** where specifics cannot be derived from context. These must be filled in by the implementing team before work begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Discovery & design: confirm runtime, framework, existing router/server entry point, and health-check contract (response schema, HTTP status codes) | Access to codebase and deployment manifests | TODO person-days (derive from "moderate" option once details are provided) |
| 2 | Implementation: add `/health` (liveness) and `/ready` (readiness) route handlers, wire into existing HTTP server | Phase 1 complete | TODO person-days |
| 3 | Testing: unit + integration tests for both endpoints; update CI gates | Phase 2 complete | TODO person-days |
| 4 | Infrastructure wiring: update Kubernetes liveness/readiness probes (or equivalent), update CI/CD pipeline | Phase 2 complete | TODO person-days |
| 5 | Release & validation: deploy to staging, verify probe behaviour, promote to production | Phases 3 & 4 complete | TODO person-days |

---

## Component Changes

### HTTP Router / Server Entry Point

- **File:** TODO — identify the file that registers HTTP routes (e.g., `server.js`, `app.py`, `main.go`, `Application.java`, etc.)
- **Change:** Register two new routes on the existing HTTP server instance:
  - `GET /health` → liveness handler
  - `GET /ready` → readiness handler
- **APIs modified:** None existing. Two new handler functions/methods are added.

### Liveness Handler (`/health`)

- **Purpose:** Confirms the process is alive and the HTTP server is accepting connections.
- **Behaviour:** Returns `HTTP 200 OK` with a minimal JSON body, e.g. `{"status":"ok"}`. Should never perform I/O or call downstream dependencies.
- **File:** TODO — e.g., `handlers/health.{ext}`, `src/health_handler.{ext}`
- **Class/Method:** TODO — e.g., `HealthHandler.handle()`, `health_check()`, `HandleHealth()`

### Readiness Handler (`/ready`)

- **Purpose:** Confirms the service is ready to receive traffic (dependencies reachable, warm-up complete).
- **Behaviour:**
  - Checks required dependencies (database connection, cache, downstream services — TODO: enumerate from codebase).
  - Returns `HTTP 200 OK` with `{"status":"ready"}` when all checks pass.
  - Returns `HTTP 503 Service Unavailable` with `{"status":"not_ready","reason":"<detail>"}` when any check fails.
- **File:** TODO — e.g., `handlers/ready.{ext}`, `src/ready_handler.{ext}`
- **Class/Method:** TODO — e.g., `ReadinessHandler.handle()`, `readiness_check()`, `HandleReady()`

### Dependency Check Abstraction (optional but recommended)

- **Purpose:** Encapsulate each dependency check behind a common interface so checks are independently testable and composable.
- **File:** TODO — e.g., `health/checks.{ext}`
- **Class/Method:** TODO — e.g., interface `HealthCheck` with method `check() -> (ok bool, reason string)`

---

## Dependency Upgrade Plan

N/A — not applicable to this task. No existing dependencies require upgrading to implement these endpoints. If the chosen framework lacks built-in health-check support, a lightweight helper library may be evaluated, but no specific version is mandated by the tech analysis.

---

## Infrastructure Changes

### Kubernetes (if applicable)

- **Liveness probe:** Add or update `livenessProbe` in the Deployment manifest to call `GET /health`.
- **Readiness probe:** Add or update `readinessProbe` in the Deployment manifest to call `GET /ready`.

Example manifest snippet (adjust `port`, `initialDelaySeconds`, `periodSeconds` to match service SLOs):

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: TODO   # match service container port
  initialDelaySeconds: TODO
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: TODO
  initialDelaySeconds: TODO
  periodSeconds: 5
  failureThreshold: 3
```

- **Manifest file:** TODO — e.g., `k8s/deployment.yaml`, `helm/templates/deployment.yaml`

### Docker

- TODO — confirm whether the base image or `EXPOSE` directive needs updating to reflect the health-check port. If the service already exposes its HTTP port, no change is required.

### CI/CD Pipeline

- Add a smoke-test step post-deploy that curls `/health` and `/ready` and asserts `HTTP 200` before marking the deployment successful.
- **Pipeline file:** TODO — e.g., `.github/workflows/deploy.yml`, `Jenkinsfile`, `.gitlab-ci.yml`

---

## Rollback Strategy

Each phase is independently reversible because all changes are additive.

| Phase | Rollback Action |
|-------|----------------|
| 1 (Discovery) | No code changes; nothing to roll back. |
| 2 (Implementation) | Revert the route registration commit. The two new handler files can be deleted. No existing routes or logic are modified, so revert has zero blast radius. |
| 3 (Testing) | Revert or delete the new test files. CI gates revert to their prior state. |
| 4 (Infrastructure) | Remove or revert the `livenessProbe` / `readinessProbe` blocks from the Kubernetes manifest and re-apply (`kubectl apply -f TODO`). Kubernetes will stop probing the new endpoints; the pod lifecycle reverts to its previous behaviour. |
| 5 (Release) | Re-deploy the previous container image tag via the existing deployment pipeline. Because no schema or data migrations are involved, rollback is instantaneous. |

---

## Testing Strategy

> Specific tooling is marked TODO because the language and framework are unknown.

### Unit Tests
- **Scope:** Each handler function in isolation.
- **Cases:**
  - `/health` always returns `200` with correct body.
  - `/ready` returns `200` when all dependency checks pass (mock dependencies returning healthy).
  - `/ready` returns `503` when any dependency check fails (mock dependencies returning unhealthy).
  - Each individual dependency check (unit-test the check abstraction).
- **Tool:** TODO (e.g., Jest, pytest, Go `testing`, JUnit)
- **Coverage target:** 100% line coverage of the new handler and check files.

### Integration Tests
- **Scope:** Spin up the real HTTP server (in-process or via test container) and issue actual HTTP requests to `/health` and `/ready`.
- **Cases:**
  - Happy path: all dependencies available → `200`.
  - Degraded path: simulate a dependency failure → `503` with correct JSON body.
- **Tool:** TODO (e.g., Supertest, `httptest`, TestContainers, RestAssured)

### Regression Tests
- **Scope:** Confirm no existing endpoints are affected by the new route registrations.
- **Approach:** Run the full existing integration/API test suite unchanged and assert zero regressions.
- **CI gate:** Existing test suite must remain green.

### Performance / Smoke Tests
- **Scope:** Confirm the endpoints respond within an acceptable latency budget under load (they must not become a bottleneck for probe traffic).
- **Target:** p99 < 50 ms under probe-level concurrency (typically low).
- **Tool:** TODO (e.g., k6, wrk, hey)
- **CI gate:** Post-deploy smoke test in pipeline asserts `HTTP 200` from both endpoints before traffic is shifted.

---

## Timeline

> Effort values are marked TODO because the "moderate" upgrade option details were not provided. Populate with actual person-day estimates once the option is detailed and the runtime/framework is confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Runtime & framework confirmed; health-check contract agreed | 1 — Discovery | TODO | TODO |
| `/health` and `/ready` handlers implemented and code-reviewed | 2 — Implementation | TODO | TODO |
| Unit & integration tests written; coverage gate passing | 3 — Testing | TODO | TODO |
| Kubernetes probes updated; CI smoke-test step added | 4 — Infrastructure | TODO | TODO |
| Deployed to staging; probes verified; promoted to production | 5 — Release | TODO | TODO |