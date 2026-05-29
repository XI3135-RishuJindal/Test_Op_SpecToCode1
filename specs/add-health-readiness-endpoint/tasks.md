# TASKS: Add /health Readiness Endpoint

> **Task:** Add `/health` readiness endpoint
> **Upgrade Option:** moderate
> **Urgency:** medium

---

## Prerequisites

- [ ] [XS] Confirm the application's language, runtime, and build tool by inspecting the repository root (e.g., `package.json`, `pom.xml`, `go.mod`, `requirements.txt`, `Gemfile`) before any work begins
- [ ] [XS] Confirm the web framework in use (e.g., Express, Spring Boot, FastAPI, Gin) by reviewing the primary dependency manifest
- [ ] [XS] Confirm whether a reverse proxy or load balancer (e.g., nginx, AWS ALB) is in front of the application, as this affects how the readiness probe is consumed
- [ ] [XS] Verify that the team has write access to the repository and can open pull requests against the main branch

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feature/health-readiness-endpoint` from the default branch
- [ ] [XS] Document the current list of application startup dependencies (database, cache, external services) in a scratch note or PR description — these will determine what the readiness check must verify
- [ ] [XS] Confirm no existing `/health`, `/healthz`, or `/ready` route is already registered in the application's router/controller layer to avoid conflicts

---

## Phase 2 — Core Upgrade

- [ ] [S] Register a `GET /health` route in the application's primary router or controller file that returns HTTP `200 OK` with a JSON body `{"status":"ok"}` when the application is ready to serve traffic
- [ ] [S] Implement readiness logic inside the `/health` handler to check each critical startup dependency (e.g., database reachability, required env vars present) and return HTTP `503 Service Unavailable` with `{"status":"unavailable","reason":"<detail>"}` if any check fails
- [ ] [XS] Ensure the `/health` endpoint is excluded from authentication middleware so probes are never blocked by auth guards — update the middleware configuration file accordingly
- [ ] [XS] Ensure the `/health` endpoint does not emit application-level access log noise by suppressing or filtering its log entries in the logging configuration file

---

## Phase 3 — Testing & Validation

- [ ] [S] Write a unit test for the `/health` handler covering: (a) all dependencies healthy → `200 {"status":"ok"}`, (b) one dependency unhealthy → `503 {"status":"unavailable",...}` — place tests in the existing test directory alongside related handler tests
- [ ] [XS] Manually verify the endpoint returns `200` on a local running instance via `curl -i http://localhost:<PORT>/health`
- [ ] [XS] Manually verify the endpoint returns `503` when a dependency (e.g., database) is intentionally unreachable in a local environment

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a readiness probe configuration pointing to `GET /health` in the container orchestration config (e.g., Kubernetes `deployment.yaml` `readinessProbe` block, or `docker-compose.yml` `healthcheck` block) with appropriate `initialDelaySeconds`, `periodSeconds`, and `failureThreshold` values
- [ ] [XS] Verify the CI pipeline runs the new unit tests added in Phase 3 and that the pipeline fails if they do not pass

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) describing the new `GET /health` endpoint, its response contract, and the dependencies it checks
- [ ] [XS] Update the project `README.md` or operations runbook to document the `/health` endpoint URL, expected responses, and how it is used by the readiness probe
- [ ] [XS] Deploy to a staging environment and confirm the readiness probe transitions the instance to `Ready` state before live traffic is routed to it
- [ ] [XS] Monitor application logs and orchestrator events for the first 30 minutes post-deployment to confirm no unexpected `503` responses or probe failures