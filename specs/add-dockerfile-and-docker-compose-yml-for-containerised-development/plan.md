# Plan: Add Dockerfile and docker-compose.yml for Containerised Development

## Overview

**Migration Strategy: Big-Bang (Greenfield Addition)**

This task introduces net-new containerisation artefacts (`Dockerfile` and `docker-compose.yml`) to an existing project. Because no existing runtime files are being modified or replaced, the risk of regression is low. A big-bang approach is appropriate: the files are authored, reviewed, and merged in a single pull request without requiring a strangler-fig or parallel-run strategy.

> **Note:** The tech analysis reports the language, runtime, and build tool as unknown. All runtime-specific decisions below are marked as TODO and must be resolved during Phase 1 discovery before authoring the Dockerfile. This plan provides the structural framework; concrete values depend on that discovery.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Discovery** — Identify language, runtime version, build tool, exposed ports, environment variables, and any required backing services | Access to codebase and existing documentation | TODO (derive from actual codebase inspection; estimate ~0.5 person-days) |
| 2 | **Dockerfile Authoring** — Write and validate a multi-stage (or single-stage) `Dockerfile` based on Phase 1 findings | Phase 1 complete | TODO (estimate ~0.5–1 person-day) |
| 3 | **docker-compose.yml Authoring** — Write `docker-compose.yml` wiring the application container with any backing services (database, cache, etc.) | Phase 2 complete | TODO (estimate ~0.5 person-day) |
| 4 | **Validation & Documentation** — Smoke-test the full `docker compose up` workflow; update `README.md` with container usage instructions | Phase 3 complete | TODO (estimate ~0.5 person-day) |
| 5 | **Review & Merge** — Peer review, CI gate validation, merge to main branch | Phase 4 complete | TODO (estimate ~0.25 person-day) |

> **Total estimated effort:** ~2–3 person-days (to be confirmed once the upgrade option detail and codebase are available).

---

## Component Changes

### `Dockerfile` (new file — repository root)

- **What changes:** New file created from scratch.
- **Structure:**
  - `FROM` — TODO: base image to be determined from runtime discovery (e.g., official language slim/alpine image).
  - Multi-stage build recommended if the project has a separate build and run phase (TODO: confirm).
  - `WORKDIR` — TODO: set to appropriate application directory.
  - Dependency installation layer (copy dependency manifest first for layer caching).
  - Source copy and build step — TODO: build command to be determined.
  - `EXPOSE` — TODO: port(s) to be determined from application configuration.
  - `CMD` / `ENTRYPOINT` — TODO: application start command to be determined.
- **Files affected:** `Dockerfile` (created).

### `docker-compose.yml` (new file — repository root)

- **What changes:** New file created from scratch.
- **Structure:**
  - `services.app` — builds from local `Dockerfile`, maps host port to container port, mounts source volume for live-reload in development.
  - Additional services (e.g., `db`, `cache`) — TODO: to be determined from Phase 1 discovery of backing service dependencies.
  - `environment` block — TODO: enumerate required environment variables from application config.
  - `volumes` block — TODO: named volumes for any stateful services.
- **Files affected:** `docker-compose.yml` (created).

### `.dockerignore` (new file — repository root)

- **What changes:** New file to exclude build artefacts, local dependency directories, and secrets from the Docker build context.
- **Contents:** TODO: populate based on language/build tool (e.g., `node_modules/`, `__pycache__/`, `.env`, `dist/`, `target/`).
- **Files affected:** `.dockerignore` (created).

### `README.md` (existing file — if present)

- **What changes:** Add a "Running with Docker" section documenting `docker compose up`, environment variable setup, and port mappings.
- **Files affected:** `README.md` (modified).

---

## Dependency Upgrade Plan

N/A — not applicable to this task. No existing dependencies are being upgraded; only new infrastructure files are being introduced.

---

## Infrastructure Changes

### Docker Base Image

| Artefact | Current | Target | Notes |
|----------|---------|--------|-------|
| Base image | None | TODO | To be selected in Phase 1 based on runtime discovery. Prefer official slim or alpine variant for smaller image size. |

### CI/CD Pipeline

- **TODO:** Determine current CI/CD platform (GitHub Actions, GitLab CI, Jenkins, etc.) from repository context.
- Recommended addition: a CI job that runs `docker build .` on every pull request to validate the `Dockerfile` builds successfully.
- Recommended addition: optionally run `docker compose up -d` + a health-check smoke test in CI.

### Kubernetes / IaC

N/A — not applicable to this task. This task targets local containerised development only; no Kubernetes manifests or IaC changes are in scope.

---

## Rollback Strategy

Because this task adds only new files and does not modify existing application code, rollback is straightforward at every phase.

| Phase | Rollback Action |
|-------|----------------|
| 1 (Discovery) | No artefacts produced; nothing to roll back. |
| 2 (Dockerfile) | Delete `Dockerfile` and `.dockerignore` from the branch; the application continues to run as before. |
| 3 (docker-compose.yml) | Delete `docker-compose.yml` from the branch; no impact on non-containerised workflows. |
| 4 (Validation & Docs) | Revert `README.md` changes via `git revert` or by editing the PR. |
| 5 (Merge) | If issues are discovered post-merge, revert the merge commit (`git revert <merge-sha>`). The application is unaffected as no runtime files were changed. |

---

## Testing Strategy

### Unit / Lint
- **Tool:** [`hadolint`](https://github.com/hadolint/hadolint) — Dockerfile linter.
- **Gate:** `hadolint Dockerfile` must return exit code 0 with no errors before merge.

### Build Validation
- **Tool:** `docker build .`
- **Gate:** Image must build successfully with no errors. Run in CI on every PR.

### Compose Smoke Test
- **Tool:** `docker compose up -d` followed by a health-check (e.g., `curl -f http://localhost:<PORT>/health` or equivalent).
- **Gate:** Application container must reach healthy/running state within a defined timeout (TODO: set timeout once port and health endpoint are known).

### Integration
- TODO: If the project has an existing integration test suite, verify it can be executed inside the container (`docker compose run app <test-command>`).

### Performance / Image Size
- **Tool:** `docker image inspect` or [`dive`](https://github.com/wagoodman/dive) to audit layer sizes.
- **Gate:** Final image size should be reviewed and documented; no hard limit set until baseline is established.

### Coverage Targets
- TODO: Derive from existing project test configuration once runtime is known.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Runtime & dependency discovery complete | Phase 1 | TODO | TODO |
| `Dockerfile` and `.dockerignore` authored and building locally | Phase 2 | TODO | TODO |
| `docker-compose.yml` authored and `docker compose up` succeeds locally | Phase 3 | TODO | TODO |
| Smoke tests passing; `README.md` updated | Phase 4 | TODO | TODO |
| PR reviewed and merged; CI gates green | Phase 5 | TODO | TODO |

> All dates and owners are marked TODO pending team assignment and confirmation of the upgrade option effort estimate.