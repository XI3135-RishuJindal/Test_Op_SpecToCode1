# CONSTITUTION
## Project: Containerised Development Environment

---

## Project Identity

**Name:** Containerised Development Environment Setup
**Purpose:** Introduce a `Dockerfile` and `docker-compose.yml` to the project, enabling consistent, reproducible containerised development environments for all contributors.
**High-Level Goal:** Eliminate "works on my machine" issues by defining the application's runtime environment as code, making local development setup a single-command operation.

---

## Guiding Principles

1. **Prefer a single-command setup (`docker compose up`) over multi-step manual installation** because onboarding friction is the primary problem this task solves.
2. **Prefer explicit base image tags (e.g. `node:20-alpine`) over `latest`** because unpinned tags introduce silent, non-reproducible environment drift.
3. **Prefer minimal, purpose-scoped images over general-purpose ones** because smaller images reduce build time, attack surface, and storage cost.
4. **Prefer `.dockerignore` exclusions over copying the full working directory** because build context bloat slows iteration and may leak secrets or local config.
5. **Prefer environment variable configuration over hard-coded values in Docker files** because it keeps secrets out of version control and supports multiple environments without file changes.

---

## Constraints

- **Timeline / Effort:** Moderate effort option selected; scope is limited strictly to adding `Dockerfile` and `docker-compose.yml` — no application code changes, no CI/CD pipeline work, no production deployment configuration.
- **Technology Mandates:**
  - TODO: Confirm target language, runtime version, and base image (e.g. `node:20-alpine`, `python:3.12-slim`). Constitution must be updated once the stack is identified.
  - TODO: Confirm whether any internal container registry must be used, or if Docker Hub is acceptable.
- **Scope Freeze:** This task does not include production Dockerfiles, Kubernetes manifests, or cloud deployment configuration. Any such additions are out of scope and must be tracked as separate tasks.
- **Secrets:** No credentials, API keys, or environment-specific secrets may be committed inside Docker files or the repository.

---

## Quality Standards

- **Functionality Gate:** `docker compose up` must successfully start all defined services with zero manual intervention on a clean clone of the repository.
- **Build Verification:** The Docker image must build without warnings or errors (`docker build` exits `0`) before a PR can be merged.
- **`.dockerignore` Required:** A `.dockerignore` file must be present and must exclude at minimum: dependency directories (e.g. `node_modules/`, `venv/`), `.env` files, `.git/`, and local IDE config.
- **Documentation:** `README.md` must be updated with a "Getting Started with Docker" section covering prerequisites, the startup command, and how to configure environment variables.
- **Code Review:** A minimum of one peer review is required before merging. The reviewer must verify the image builds and services start locally.
- **No Hardcoded Ports Conflicts:** Exposed ports must be documented and must not conflict with common local services; configurable via `.env` where possible.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Provide both `Dockerfile` and `docker-compose.yml` | `docker-compose.yml` orchestrates services (app, DB, etc.) for dev; `Dockerfile` defines the image — both are needed for a complete dev environment | Accepted |
| ADR-002 | Scope limited to development environment only | The upgrade option is moderate and the task description explicitly targets containerised *development*; production concerns are a separate workstream | Accepted |
| ADR-003 | Base image and runtime version — TODO | Language/runtime is unknown per tech analysis; must be decided before implementation begins | Proposed |
| ADR-004 | Use `.env` file pattern for local environment variables | Keeps secrets out of version control while remaining compatible with `docker compose` native `.env` support | Accepted |