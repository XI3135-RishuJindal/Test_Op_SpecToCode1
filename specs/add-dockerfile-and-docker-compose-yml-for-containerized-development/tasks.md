# TASKS: Add Dockerfile and docker-compose.yml for Containerized Development

> **Scope:** Introduce container support for local development via a `Dockerfile` and `docker-compose.yml`. No runtime, framework, or dependency upgrade is in scope.

---

## Prerequisites

- [ ] [XS] Confirm Docker Engine (≥ 20.10) and Docker Compose (≥ 2.x) are installed on all developer workstations
- [ ] [XS] Confirm repository write access and ability to open pull requests against the main branch
- [ ] [XS] Identify and document the application's exposed port(s), required environment variables, and any external service dependencies (e.g. database, cache) by reviewing existing run instructions or README

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch `feat/containerized-dev` from the main branch
- [ ] [XS] Audit the repository root for any existing `.dockerignore`, `Dockerfile`, or `docker-compose.yml` files to avoid conflicts
- [ ] [XS] Document the current local development startup steps (commands, env vars, ports) in a scratch note to serve as the specification for container configuration

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `Dockerfile` at the repository root with a multi-stage build: a `builder` stage that installs dependencies and compiles/builds the application, and a lean `runtime` stage that copies only the production artifact
- [ ] [XS] Create `.dockerignore` at the repository root to exclude version-control metadata, local dependency directories, build output, and editor config from the Docker build context
- [ ] [S] Create `docker-compose.yml` at the repository root defining a `app` service that builds from the local `Dockerfile`, maps the correct host-to-container port, mounts the source directory as a volume for live-reload during development, and loads environment variables from a `.env` file
- [ ] [XS] Create `.env.example` at the repository root listing all required environment variable keys with placeholder values, to serve as the template for developer `.env` files
- [ ] [XS] Add `.env` to `.gitignore` (if not already present) to prevent accidental credential commits

---

## Phase 3 — Testing & Validation

- [ ] [S] Perform a local end-to-end smoke test: run `docker compose up --build`, verify the `app` container starts without errors, and confirm the application responds on the expected port
- [ ] [XS] Verify that source-code changes made on the host are reflected inside the running container (volume mount / live-reload validation)
- [ ] [XS] Verify `docker compose down` cleanly stops and removes containers and networks with no orphan resources

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a CI job step (in the existing pipeline configuration file) that runs `docker build .` as a build-validation gate to catch `Dockerfile` regressions on every pull request
- [ ] [XS] Confirm the CI runner environment has Docker available; document any runner-label or service requirement needed to enable the Docker build step

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `README.md` to add a **"Running with Docker"** section documenting the `cp .env.example .env`, `docker compose up --build` workflow and listing all configurable environment variables
- [ ] [XS] Add a `CHANGELOG` entry (or equivalent) noting the addition of `Dockerfile` and `docker-compose.yml` for containerized development
- [ ] [XS] Announce the new workflow to the team and confirm at least one other developer successfully runs the stack using only the documented Docker instructions