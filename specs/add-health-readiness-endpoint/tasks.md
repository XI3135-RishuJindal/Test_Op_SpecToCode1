# Tasks: Add /health Readiness Endpoint

## Prerequisites

- [ ] [XS] Confirm target port and base path for the health endpoint with the team and record the decision in a shared notes doc or ticket comment
- [ ] [XS] Confirm expected HTTP response contract (status code, response body shape, e.g. `{"status":"ok"}`) and document in the ticket before implementation begins
- [ ] [XS] Verify that the service's existing router/framework supports adding new GET routes without additional dependencies

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch (e.g. `feature/health-readiness-endpoint`) from the main branch
- [ ] [XS] Identify and document the existing routing entry point file where the new `/health` route will be registered
- [ ] [XS] Capture the current test suite baseline (pass/fail count, coverage %) so regression comparison is possible after changes

---

## Phase 2 — Core Upgrade

- [ ] [S] Implement the `GET /health` handler function that returns HTTP 200 with a JSON body `{"status":"ok"}` in the appropriate controller or handler module
- [ ] [XS] Register the `GET /health` route in the application's main router or routing configuration file
- [ ] [XS] Ensure the `/health` endpoint is excluded from any authentication or authorization middleware that would block unauthenticated readiness checks

---

## Phase 3 — Testing & Validation

- [ ] [S] Write a unit test for the `/health` handler asserting HTTP 200 and correct response body in the project's test directory
- [ ] [S] Write an integration/route test that boots the application and performs an HTTP GET to `/health`, asserting the full response contract
- [ ] [XS] Run the full test suite and confirm no regressions against the baseline captured in Phase 1

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Add a health check probe pointing to `GET /health` in the service's container or process manager configuration (e.g. Docker `HEALTHCHECK`, Kubernetes `readinessProbe`), if applicable
- [ ] [XS] Confirm CI pipeline executes the new tests added in Phase 3 and gates the build on their passing

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) describing the new `GET /health` readiness endpoint
- [ ] [XS] Update the service's API documentation or README to document the `/health` endpoint, its expected response, and its intended use for readiness checks
- [ ] [XS] Deploy to a staging environment and manually verify `GET /health` returns HTTP 200 with the correct body before promoting to production