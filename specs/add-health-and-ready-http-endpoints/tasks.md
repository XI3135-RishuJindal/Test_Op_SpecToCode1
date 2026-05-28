# TASKS: Add /health and /ready HTTP endpoints

> **Scope:** Implement `/health` and `/ready` HTTP endpoints.
> **Upgrade Option:** moderate
> **Note:** Language, runtime, build tool, and framework are unspecified in the tech analysis. Tasks below are written at the logical/intent level; assignee must confirm file paths and naming conventions before starting.

---

## Prerequisites

- [ ] [XS] Confirm the language, runtime, and web framework in use and record findings in a `DECISIONS.md` or equivalent notes file before any implementation begins
- [ ] [XS] Confirm the existing HTTP server entry point (e.g., main application file, router registration file) so endpoint registration targets are unambiguous
- [ ] [XS] Confirm whether a health-check library already exists as a dependency (e.g., a framework-native health module) to avoid duplicating functionality

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch `feature/health-ready-endpoints` from the main branch
- [ ] [XS] Identify and document all external dependencies (database, cache, downstream services) that the `/ready` check must verify, recorded in a short spec comment at the top of the new health module
- [ ] [S] Capture the current integration-test baseline (run existing test suite, save output) so regressions introduced by new routing can be detected in Phase 3

---

## Phase 2 — Core Upgrade

- [ ] [S] Create a dedicated health-check module/file (e.g., `health.{ext}` or `healthcheck.{ext}`) that exports two handler functions: `handleHealth` and `handleReady`
- [ ] [XS] Implement `handleHealth` to return `HTTP 200` with body `{"status":"ok"}` and a `Content-Type: application/json` header, representing a lightweight liveness signal
- [ ] [M] Implement `handleReady` to perform dependency checks (confirm each dependency identified in Phase 1 is reachable), return `HTTP 200 {"status":"ready"}` when all pass, and `HTTP 503 {"status":"unavailable","reason":"<detail>"}` when any fail
- [ ] [XS] Register `GET /health` route pointing to `handleHealth` in the main router/application entry-point file
- [ ] [XS] Register `GET /ready` route pointing to `handleReady` in the main router/application entry-point file
- [ ] [XS] Ensure both endpoints are excluded from authentication middleware (if any auth middleware is applied globally) by adding explicit bypass rules in the middleware configuration file

---

## Phase 3 — Testing & Validation

- [ ] [S] Write unit tests for `handleHealth`: assert `HTTP 200`, correct `Content-Type`, and `{"status":"ok"}` body in the project's existing test file or a new `health.test.{ext}` file
- [ ] [M] Write unit tests for `handleReady`: assert `HTTP 200` when all dependency mocks succeed, and `HTTP 503` with a descriptive `reason` field when each dependency mock fails individually, in `health.test.{ext}`
- [ ] [S] Write an integration/smoke test that starts the server and issues real HTTP requests to `/health` and `/ready`, confirming correct status codes end-to-end
- [ ] [XS] Run the full test suite and confirm no regressions against the baseline captured in Phase 1

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a CI pipeline step that calls `GET /health` (and optionally `GET /ready`) against the running test server as a post-start smoke-gate, failing the build if either returns a non-`2xx` response
- [ ] [XS] Update any Docker `HEALTHCHECK` instruction (if a `Dockerfile` exists) to use `CMD curl -f http://localhost:<PORT>/health || exit 1`
- [ ] [XS] Update any container orchestration configuration (e.g., Kubernetes liveness probe → `/health`, readiness probe → `/ready`) if such config files exist in the repository

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry describing the two new endpoints, their expected responses, and the dependency checks performed by `/ready`
- [ ] [XS] Update the project `README` (or API reference doc) with a brief description of `/health` and `/ready`, including example `curl` commands and sample responses
- [ ] [XS] Update the operations runbook (if one exists) to document how to interpret a `503` from `/ready` and the remediation steps for each dependency failure scenario
- [ ] [XS] Deploy to a staging environment and manually verify both endpoints return expected responses before merging to main

---

**Total estimated effort:** ~3–5 days depending on number of dependencies wired into `/ready` and the complexity of the existing middleware stack.