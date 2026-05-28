# Plan: Add /health Readiness Endpoint

## Overview

**Migration Strategy: Feature-Flag Gated / Big-Bang (Single Increment)**

Adding a `/health` readiness endpoint is a net-new, additive change with no breaking modifications to existing functionality. The risk score is low — no existing code paths are altered, and the endpoint can be introduced in a single, self-contained increment.

A **big-bang delivery within a single phase** is appropriate here. Because the change is purely additive (a new route returning a status payload), there is no need for a strangler-fig or parallel-run strategy. A feature flag may optionally gate the endpoint in production until smoke tests pass, but is not architecturally required.

> **NOTE:** The tech analysis did not supply language, runtime, framework, or build-tool details. All technology-specific implementation notes below are marked **TODO** pending that context. The structural plan remains valid regardless of stack.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Design & agree on health-check contract (response schema, HTTP status codes, readiness criteria) | Stakeholder sign-off | TODO — derive from upgrade option person-days once provided |
| 2 | Implement `/health` endpoint and internal readiness probe logic | Phase 1 complete | TODO |
| 3 | Write unit + integration tests; set CI gate | Phase 2 complete | TODO |
| 4 | Deploy to staging, validate with orchestrator (e.g., Kubernetes readiness probe), promote to production | Phase 3 passing | TODO |

> **TODO:** Populate effort column (person-days) once the "moderate" upgrade option detail is provided.

---

## Component Changes

### New: Health Controller / Handler

- **What changes:** A new route handler is registered at `GET /health`.
- **Response contract (proposed):**
  ```json
  {
    "status": "ok" | "degraded" | "unavailable",
    "timestamp": "<ISO-8601>",
    "checks": {
      "<dependency_name>": "ok" | "fail"
    }
  }
  ```
- **HTTP status codes:**
  - `200 OK` — service is ready to accept traffic
  - `503 Service Unavailable` — service is not ready (e.g., dependency down)

- **Files affected:**
  - TODO — specific file paths unknown; no code context provided.
  - Expected additions:
    - `src/health/health.controller.<ext>` (or equivalent router file)
    - `src/health/health.service.<ext>` (readiness check logic)
    - `src/health/health.controller.test.<ext>`

### Modified: Application Entry Point / Router Registration

- **What changes:** The new health route must be registered in the application's main router or server bootstrap file.
- **Files affected:** TODO — main app/router file unknown without code context.
- **APIs modified:** None existing — additive registration only.

### Optional: Dependency Probe Utilities

- If the readiness check must verify downstream dependencies (database, cache, external APIs), a lightweight probe utility should be added.
- **Files affected:** TODO — depends on existing service/repository layer structure.

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> No dependency upgrades are required to add a `/health` endpoint. If a dedicated health-check library is desired (e.g., a framework-native health module), that selection is **TODO** pending stack identification.

---

## Infrastructure Changes

### Kubernetes (if applicable)

Add a `readinessProbe` to the relevant container spec in the Deployment manifest:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: <TODO: application port>
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

> **TODO:** Confirm manifest file path and port value from infrastructure context.

### Docker

- No base image changes required.
- **TODO:** Confirm whether a `HEALTHCHECK` instruction should be added to the `Dockerfile`:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:<PORT>/health || exit 1
  ```

### CI/CD Pipeline

- Add a post-deploy smoke-test step that calls `GET /health` and asserts `HTTP 200`.
- **TODO:** CI/CD tooling (GitHub Actions, Jenkins, etc.) unknown — adapt step syntax accordingly.

---

## Rollback Strategy

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 | Discard contract document; no code changes to revert. |
| Phase 2 | Revert the route registration commit; the new handler file can be deleted. No existing routes are affected. |
| Phase 3 | Remove test files added in Phase 3; CI gate removal is a single config line revert. |
| Phase 4 | **Staging:** Re-deploy previous image tag. **Production:** Re-deploy previous image tag; remove `readinessProbe` stanza from Kubernetes manifest if it was causing probe failures. Each step is independently reversible via a single `git revert` + redeploy. |

> Because the change is purely additive, rollback at any phase has zero impact on existing functionality.

---

## Testing Strategy

### Test Pyramid

| Layer | What to Test | Tooling | Coverage Target |
|-------|-------------|---------|----------------|
| **Unit** | Health service logic: correct status aggregation, correct HTTP status code selection, dependency probe mock responses | TODO — match project's existing test framework | 100% of new health service methods |
| **Integration** | Full HTTP round-trip: `GET /health` returns `200` when all probes pass; returns `503` when a probe is injected to fail | TODO — match project's existing integration test setup | All response branches covered |
| **Regression** | Existing endpoint tests must continue to pass unchanged | TODO | No regression in existing coverage |
| **Performance** | `/health` must respond within an acceptable SLA (suggested: < 200 ms p99) to avoid false-negative readiness probe failures | TODO — load testing tool (k6, Locust, etc.) | p99 < 200 ms under normal load |

### CI Gates

- Unit + integration tests must pass before merge to main branch.
- Smoke test (`GET /health` → `200`) must pass before promotion from staging to production.
- **TODO:** Specify exact CI pipeline file and job names once tooling is known.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Health-check contract agreed | Phase 1 | TODO | TODO |
| `/health` endpoint implemented | Phase 2 | TODO | TODO |
| Tests written & CI gate active | Phase 3 | TODO | TODO |
| Deployed to staging & validated | Phase 4 | TODO | TODO |
| Promoted to production | Phase 4 | TODO | TODO |

> **TODO:** Populate dates once the "moderate" upgrade option person-days estimate is provided and team capacity is known.