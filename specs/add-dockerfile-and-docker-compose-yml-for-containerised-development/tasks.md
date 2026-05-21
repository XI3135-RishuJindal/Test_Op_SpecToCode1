# TASKS: Add Dockerfile and docker-compose.yml for Containerised Development

> **Scope:** Introduce container support for local development via a `Dockerfile` and `docker-compose.yml`. No runtime, framework, or build-tool specifics were provided in the tech analysis; tasks are scoped strictly to what is known.

---

## Prerequisites

- [ ] [XS] Confirm Docker Engine (≥ 20.10) and Docker Compose (≥ 2.x) are installed on all developer machines and CI runners
- [ ] [XS] Confirm repository access and that a working branch can be created from the default branch
- [ ] [XS] Identify and document the application's exposed port(s), required environment variables, and any volume mount paths needed for local development — record findings in a `CONTAINER_NOTES.md` scratch file for use in later tasks

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch (e.g. `feat/add-docker-support`) from the default branch in the repository
- [ ] [XS] Audit the repository root for any existing `.dockerignore`, `Dockerfile`, or `docker-compose.yml` files to avoid conflicts, and document findings in `CONTAINER_NOTES.md`
- [ ] [XS] Identify all files and directories that should be excluded from the Docker build context (build artefacts, local config, secrets) and list them in preparation for `.dockerignore` authoring

---

## Phase 2 — Core Upgrade

- [ ] [S] Author `.dockerignore` in the repository root, excluding build artefacts, local environment files (`.env*`), version-control metadata, and any directories identified in Phase 1
- [ ] [M] Author `Dockerfile` in the repository root with a multi-stage build structure: a `builder` stage for dependency installation and compilation, and a lean `runtime` stage copying only production artefacts — base images to be confirmed once runtime is known
- [ ] [S] Author `docker-compose.yml` in the repository root defining at minimum an `app` service that builds from the local `Dockerfile`, maps the confirmed application port(s), mounts source code as a volume for live-reload during development, and loads environment variables from a `.env` file
- [ ] [XS] Author `.env.example` in the repository root listing all environment variables referenced in `docker-compose.yml` with placeholder values and inline comments describing each variable
- [ ] [XS] Add `.env` (not `.env.example`) to `.gitignore` in the repository root to prevent accidental secret commits

---

## Phase 3 — Testing & Validation

- [ ] [S] Perform a local `docker build -t app:dev .` from the repository root and resolve any build errors in `Dockerfile`
- [ ] [S] Perform a local `docker compose up` and verify the `app` service starts, the application is reachable on the mapped port, and volume mounts reflect live source changes
- [ ] [XS] Verify that files listed in `.dockerignore` are absent from the built image by inspecting image layers (`docker image inspect` / `docker history`)
- [ ] [XS] Confirm that running `docker compose down` cleanly removes containers and that no orphaned volumes are left behind

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Add a CI job (in the existing pipeline configuration file, location to be confirmed) that runs `docker build .` on every pull request targeting the default branch, failing the build if the image cannot be constructed
- [ ] [XS] Ensure the CI runner environment has Docker available, or add a setup step (e.g. `docker/setup-buildx-action` for GitHub Actions) in the pipeline configuration file

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `README.md` (or create it if absent) with a **"Running with Docker"** section covering prerequisites, `cp .env.example .env` setup step, `docker compose up` usage, port mapping reference, and how to rebuild after dependency changes
- [ ] [XS] Add a `CHANGELOG.md` entry (or update the existing one) recording the addition of `Dockerfile`, `docker-compose.yml`, `.dockerignore`, and `.env.example`
- [ ] [XS] Archive and delete `CONTAINER_NOTES.md` scratch file once all tasks are complete and information has been incorporated into `README.md`

---

> **Note:** Base image names, specific port numbers, volume paths, and environment variable names are left as placeholders pending confirmation of the application runtime and build tool. Update the relevant tasks in Phase 2 once those details are known.