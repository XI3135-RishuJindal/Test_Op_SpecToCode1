# TASKS: Externalize All Configuration to Environment Variables

> **Goal:** Replace hardcoded and file-embedded configuration values with environment variable references throughout the codebase.
> **Urgency:** Medium
> **Note:** Language, runtime, and build tooling were not specified in the tech analysis. Tasks below are written to be adapted to the actual stack discovered during the audit phase.

---

## Prerequisites

- [ ] [XS] Confirm repository access and create a dedicated working branch (e.g., `feat/externalize-config`) in version control
- [ ] [XS] Identify and document the actual language, runtime, and build tool by inspecting the repository root (look for `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Gemfile`, `*.csproj`, etc.)
- [ ] [XS] Confirm that all team members who will run the service locally have access to a shared `.env.example` template (to be created in this work)
- [ ] [XS] Verify that the target deployment environment (server, container, or platform) supports injecting environment variables before work begins

---

## Phase 1 — Preparation

- [ ] [M] Audit the entire codebase for all hardcoded configuration values (database URLs, API keys, ports, hostnames, feature flags, secrets, timeouts) and produce a flat inventory list saved as `docs/config-inventory.md`
- [ ] [S] Audit all existing configuration files (e.g., `config.json`, `settings.py`, `application.properties`, `appsettings.json`, `.env`, `config.yaml`) and document which keys are candidates for externalization in `docs/config-inventory.md`
- [ ] [XS] Capture the current test suite pass/fail baseline on the main branch before any changes, and record results in `docs/test-baseline.md`
- [ ] [XS] Add a CI gate (lint or test step) that will fail if any known secret patterns (e.g., hardcoded passwords, tokens) are committed — configure in the existing CI pipeline configuration file

---

## Phase 2 — Core Upgrade

- [ ] [S] Create a `.env.example` file at the repository root listing every externalized variable with placeholder values and inline comments describing each variable's purpose and expected format
- [ ] [M] Replace all hardcoded configuration values identified in `docs/config-inventory.md` with environment variable reads in the application's primary configuration module/file (exact file to be confirmed during Phase 1 audit)
- [ ] [S] Implement a startup validation routine in the application entry point that checks all required environment variables are present and non-empty, and exits with a descriptive error message if any are missing
- [ ] [S] Remove all hardcoded secrets, credentials, and environment-specific values from tracked configuration files and replace with environment variable references
- [ ] [XS] Add `.env` (the local secrets file) to `.gitignore` if not already present, ensuring `.env.example` remains tracked
- [ ] [S] Update any local development setup script or `Makefile`/`justfile`/`scripts/` entry point to copy `.env.example` to `.env` on first run and document required values

---

## Phase 3 — Testing & Validation

- [ ] [M] Update all unit and integration tests that previously relied on hardcoded config values to instead set the required environment variables in test setup/teardown (fixture files, test helpers, or CI environment blocks)
- [ ] [S] Write or update smoke tests that assert the application starts successfully when all required environment variables are provided, and fails with a clear error when required variables are absent
- [ ] [S] Run the full test suite with the new environment-variable-driven configuration and compare results against the baseline recorded in `docs/test-baseline.md`; document any regressions
- [ ] [XS] Manually verify local development workflow end-to-end using only `.env.example` values to confirm no hardcoded fallbacks remain

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Update the CI pipeline configuration file to inject all required environment variables as CI secrets or environment blocks for each job that builds or tests the application
- [ ] [S] Update any deployment configuration (e.g., `docker-compose.yml`, Kubernetes manifests, platform config files) to pass environment variables to the running service rather than mounting hardcoded config files
- [ ] [XS] Confirm that no plaintext secret values are stored in the CI/CD pipeline configuration files themselves — all secrets must reference the CI platform's secret store

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `README.md` with a "Configuration" section that lists all environment variables, their purpose, default values (if any), and whether they are required or optional — referencing `.env.example`
- [ ] [S] Update or create a runbook entry (e.g., `docs/runbook.md`) describing how to rotate secrets, add new environment variables, and troubleshoot missing-variable startup failures
- [ ] [XS] Add a `CHANGELOG` entry describing the externalization change and any action required by operators or developers on next deploy
- [ ] [XS] Communicate the change to all developers and operators, confirming they have populated their local `.env` files and that deployment environments have been updated before merging to the main branch

---

> **Reminder:** The exact file names, module paths, and config keys referenced in Phase 2 tasks must be filled in from the findings of the Phase 1 audit. Tasks are intentionally written at the pattern level given the unspecified stack.