# Plan: Add /health Readiness Endpoint

## Overview

**Migration Strategy: Big-Bang (Single-Phase Delivery)**

Adding a `/health` readiness endpoint is a net-new, additive change with no modification to existing functionality. It carries low risk of regression and requires no data migration or breaking API changes. A big-bang approach — delivering the endpoint in a single focused phase — is appropriate given the bounded scope and medium urgency rating.

> **Note:** The tech analysis does not specify a language, runtime, framework, or build tool. Sections below are written at a pattern level. File names, class names, and tooling references are marked **TODO** where they cannot be derived from context.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Design & contract definition — agree on response schema, HTTP status codes, and readiness criteria | None | TODO (derive from option person-days — option detail not provided) |
| 2 | Implementation — add route handler, readiness logic, and response serialization | Phase 1 complete | TODO |
| 3 | Testing — unit, integration, and CI gate wiring | Phase 2 complete | TODO |
| 4 | Infrastructure wiring — register endpoint in load balancer / orchestrator health checks | Phase 3 complete | TODO |

> **TODO:** Effort in person-days cannot be populated — the upgrade option was provided as `moderate` without a numeric estimate. Assign estimates during sprint planning once runtime stack is confirmed.

---

## Component Changes

### Route / Controller Layer

- **What changes:** A new route `GET /health` is registered in the application's router or controller layer.
- **Files affected:** TODO — router/controller file(s) unknown without codebase context.
- **API added:**
  - `GET /health`
  - **Success response (HTTP 200):**
    ```json
    {
      "status": "ok",
      "timestamp": "<ISO-8601>",
      "checks": {}
    }
    ```
  - **Not-ready response (HTTP 503):**
    ```json
    {
      "status": "unavailable",
      "timestamp": "<ISO-8601>",
      "checks": {}
    }
    ```

### Health Check Logic

- **What changes:** A dedicated health/readiness module is introduced to encapsulate individual readiness checks (e.g., database reachability, downstream dependency ping).
- **Files affected:** TODO — suggest creating `health_check.{ext}` or `HealthCheckService.{ext}` in a `health/` or `diagnostics/` module directory.
- **Key methods to implement:**
  - `checkReadiness() → { status, checks }` — aggregates all sub-checks.
  - Individual sub-checks (e.g., `checkDatabase()`, `checkCache()`) — TODO, depends on application dependencies.

### Application Entry Point

- **What changes:** The new route must be registered before the application starts accepting traffic.
- **Files affected:** TODO — main application bootstrap file.

---

## Dependency Upgrade Plan

N/A — not applicable to this task. No dependency upgrades are required to add a `/health` endpoint. Any health-check helper library selection is TODO pending runtime stack confirmation.

---

## Infrastructure Changes

### Kubernetes (if applicable)

If the application runs on Kubernetes, add a `readinessProbe` to the relevant container spec:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: <app-port>   # TODO: confirm port
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

> **TODO:** Confirm whether Kubernetes manifests exist and their location in the repository.

### Load Balancer / Reverse Proxy

- **TODO:** If a load balancer (e.g., NGINX, ALB, HAProxy) is in use, configure it to use `GET /health` as the backend health check target.

### CI/CD Pipeline

- Add a smoke-test step post-deploy that asserts `GET /health` returns HTTP 200 before marking the deployment successful.
- **TODO:** CI/CD platform and pipeline file location unknown — apply to existing pipeline configuration file.

### Docker

- **TODO:** No base image changes are required for this task. If a `HEALTHCHECK` instruction is desired in the Dockerfile, add:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:<port>/health || exit 1
  ```

---

## Rollback Strategy

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 | Discard contract document; no code changes to revert. |
| Phase 2 | Revert the route registration commit; the endpoint will return 404, restoring prior behavior. No existing routes are affected. |
| Phase 3 | Remove or skip the new test suite; does not affect application behavior. |
| Phase 4 | Remove the `readinessProbe` block from the Kubernetes manifest and re-apply (`kubectl apply`). Remove the Dockerfile `HEALTHCHECK` instruction and rebuild the image. Revert load balancer health check target to its previous value. |

Each phase is independently reversible via a single commit revert or config change. No database migrations or destructive operations are involved.

---

## Testing Strategy

### Unit Tests
- **Target:** `checkReadiness()` and each sub-check function in the health module.
- **Coverage target:** 100% of the health module (it is new code with no legacy debt).
- **Tool:** TODO — depends on runtime stack.
- **Cases:** all checks pass → HTTP 200; one check fails → HTTP 503; check throws unexpectedly → HTTP 503 (fail-safe).

### Integration Tests
- **Target:** `GET /health` via the running application (in-process test server or test container).
- **Tool:** TODO — depends on runtime stack.
- **Cases:** happy path with real dependencies available; degraded path with a dependency stubbed as unavailable.

### Regression Tests
- Verify no existing routes return unexpected status changes after the new route is registered.
- **Tool:** TODO — existing regression suite, if present.

### Performance Tests
- The `/health` endpoint must respond within **200 ms** at p99 under normal load (it will be polled frequently by orchestrators).
- **Tool:** TODO — depends on stack (e.g., k6, wrk, Locust).
- **CI gate:** Block merge if p99 latency exceeds 200 ms or error rate exceeds 0%.

### CI Gate Summary
1. Unit tests must pass with 100% coverage of the health module.
2. Integration test for `GET /health → 200` must pass.
3. Post-deploy smoke test (`curl /health`) must return 200 before traffic is shifted.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Response schema & readiness criteria agreed | Phase 1 | TODO | TODO |
| `/health` route and health module implemented | Phase 2 | TODO | TODO |
| Unit & integration tests passing in CI | Phase 3 | TODO | TODO |
| Infrastructure probes configured and verified | Phase 4 | TODO | TODO |

> **TODO:** Dates and owners cannot be assigned without team capacity data and a confirmed sprint start date. Populate during sprint planning. Effort baseline is `moderate` — recommend treating this as a 1–3 day task once the runtime stack is confirmed.