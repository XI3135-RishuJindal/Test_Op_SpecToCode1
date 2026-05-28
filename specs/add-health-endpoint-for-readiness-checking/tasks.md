# TASKS: Add /health Endpoint for Readiness Checking

> **Scope:** Implement a `/health` endpoint suitable for readiness checking.
> **Upgrade Option:** moderate
> **Note:** Runtime, language, and build tool are unspecified in the tech analysis. Tasks are written at the logical/file level; assignee should substitute concrete filenames once the codebase is confirmed.

---

## Prerequisites

- [ ] [XS] Confirm the application's language, runtime, and framework by inspecting the repository root (e.g., `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Gemfile`) before any work begins
- [ ] [XS] Confirm the existing routing/controller layer entry point file so the `/health` route can be registered in the correct location
- [ ] [XS] Verify that the team has write access to the repository and that a feature branch can be created from the default branch

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `feature/health-endpoint`) from the default branch in the repository
- [ ] [XS] Document the current set of existing routes/endpoints in a scratch note or PR description to establish a baseline before changes are introduced
- [ ] [XS] Identify whether any existing middleware (authentication, rate-limiting, logging) must be bypassed or applied to the `/health` route, and record the decision in the PR description

---

## Phase 2 — Core Upgrade

- [ ] [S] Implement the `/health` route handler in the application's primary routing/controller file, returning HTTP `200 OK` with a JSON body `{"status": "ok"}` under normal conditions
- [ ] [S] Implement readiness logic inside the `/health` handler to check critical dependencies (e.g., database connectivity, required environment variables) and return HTTP `503 Service Unavailable` with `{"status": "unavailable", "reason": "<detail>"}` when the service is not ready
- [ ] [XS] Register the `/health` route in the application's route definition file so it is reachable at exactly `GET /health`
- [ ] [XS] Ensure the `/health` endpoint is excluded from any authentication or authorization middleware in the middleware configuration file, so probes are never blocked by auth checks

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for the `/health` handler covering: (a) healthy state returns `200` with `{"status":"ok"}`, (b) dependency failure returns `503` with `{"status":"unavailable"}`, in the appropriate test file alongside the handler
- [ ] [S] Write an integration/smoke test that starts the application and issues a real HTTP `GET /health` request, asserting the response code and body shape, in the project's integration test directory
- [ ] [XS] Manually verify the endpoint locally with `curl -i http://localhost:<port>/health` and record the output in the PR description

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a readiness probe configuration pointing to `GET /health` in the deployment manifest (e.g., `deployment.yaml`, `docker-compose.yml`, or equivalent IaC file), with appropriate `initialDelaySeconds`, `periodSeconds`, and `failureThreshold` values
- [ ] [XS] Confirm the CI pipeline runs the new unit and integration tests added in Phase 3 by checking the pipeline configuration file (e.g., `.github/workflows/ci.yml` or equivalent) and adding the test step if absent

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry describing the new `/health` endpoint, its contract (`200`/`503`), and the checks it performs
- [ ] [XS] Update the project `README` or API reference document to document the `/health` endpoint, expected responses, and its intended use for readiness probing
- [ ] [XS] Confirm with the infrastructure/platform team that the readiness probe is active in the staging environment and that the service correctly cycles through `Unavailable → Ready` on startup before merging to the default branch

---

> **Open question for assignee:** Because the runtime is unspecified, the exact file names in Phase 2 and Phase 3 must be confirmed before work starts. All other task descriptions remain valid regardless of language/framework.