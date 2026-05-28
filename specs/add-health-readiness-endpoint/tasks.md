# Tasks: Add /health Readiness Endpoint

## Prerequisites

- [ ] [XS] Confirm the web framework and routing mechanism in use by inspecting the project's entry point and dependency manifest (e.g., `package.json`, `requirements.txt`, `pom.xml`, `go.mod`, or equivalent)
- [ ] [XS] Confirm the existing server port and base path configuration in the application config file (e.g., `config.yaml`, `.env`, `application.properties`, or equivalent)
- [ ] [XS] Verify that no existing `/health` or `/readyz` route conflicts exist by searching the codebase for registered route definitions

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `feature/health-readiness-endpoint`) from the main branch
- [ ] [XS] Record the current set of registered routes and their response contracts as a baseline reference document (`docs/route-baseline.md` or equivalent) before any changes are made

---

## Phase 2 — Core Upgrade

- [ ] [S] Implement the `GET /health` route handler that returns HTTP `200 OK` with a JSON body `{"status":"ok"}` when the service is ready, in the application's primary router or controller file
- [ ] [XS] Implement a readiness check function that validates any critical dependencies (e.g., database connectivity, required env vars) and returns a degraded status (`{"status":"degraded"}`) with HTTP `503` when checks fail, co-located with the route handler
- [ ] [XS] Register the `/health` route in the application's main router configuration file, ensuring it is reachable without authentication middleware

---

## Phase 3 — Testing & Validation

- [ ] [S] Write a unit test for the `/health` handler covering: (1) healthy path returns `200` + `{"status":"ok"}`, and (2) degraded path returns `503` + `{"status":"degraded"}`, in the project's existing test directory
- [ ] [XS] Perform a manual smoke test by running the service locally and issuing `curl -i http://localhost:<PORT>/health` to confirm the response code and body match the contract

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Add a health check directive to the `Dockerfile` (if present) using `HEALTHCHECK CMD curl --fail http://localhost:<PORT>/health || exit 1`
- [ ] [XS] Add or update the liveness/readiness probe in the deployment manifest (e.g., `kubernetes/deployment.yaml` or `docker-compose.yml`) to point to `GET /health`

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` documenting the addition of the `GET /health` readiness endpoint, its response contract, and the HTTP status codes it returns
- [ ] [XS] Update the API reference or `README.md` with the `/health` endpoint specification (method, path, response schema, and status codes)