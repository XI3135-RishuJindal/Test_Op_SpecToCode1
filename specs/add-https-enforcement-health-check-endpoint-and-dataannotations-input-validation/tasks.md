# TASKS — HTTPS Enforcement, Health-Check Endpoint, and DataAnnotations Input Validation

> **Note:** The tech analysis did not supply specific runtime, framework, build tool, or file-level details. Tasks below are scoped strictly to the three stated goals. File and class names should be updated to match actual project structure before assignment.

---

## Prerequisites

- [ ] [XS] Confirm target runtime, framework version, and build tool by inspecting the repository root (e.g., `*.csproj`, `package.json`, `pom.xml`, `requirements.txt`) and record findings in a shared notes doc
- [ ] [XS] Verify that a valid TLS/SSL certificate (self-signed acceptable for non-production) is available or can be generated for local HTTPS testing
- [ ] [XS] Confirm that the CI environment exposes HTTPS-capable ports and that health-check routes are not blocked by firewall or reverse-proxy rules

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feature/https-healthcheck-validation` from the main branch
- [ ] [S] Capture the current test baseline by running the full existing test suite and recording pass/fail counts and coverage percentage in `docs/test-baseline.md`
- [ ] [XS] Audit existing middleware/filter pipeline (e.g., `Startup.cs`, `Program.cs`, `app.py`, or equivalent entry point) and document the current request pipeline order in `docs/pipeline-notes.md` to avoid ordering conflicts when inserting HTTPS and validation middleware
- [ ] [XS] Confirm no existing health-check route (`/health`, `/healthz`, or `/ping`) already exists by searching route definitions across the codebase to prevent duplicate-route errors

---

## Phase 2 — Core Upgrade

### HTTPS Enforcement

- [ ] [S] Add HTTPS redirect middleware to the application entry point (e.g., `Program.cs` / `Startup.cs` / `app.py` / `server.js`) so that all HTTP requests return a permanent redirect (301/308) to the HTTPS equivalent
- [ ] [S] Add HTTP Strict Transport Security (HSTS) header configuration in the middleware pipeline of the application entry point, setting `max-age`, `includeSubDomains`, and (for production) `preload` flags via environment-aware config
- [ ] [XS] Add or update the application configuration file (e.g., `appsettings.json`, `.env`, `config.yaml`) with explicit HTTPS port binding and TLS certificate path keys, guarded by environment (`Development` / `Production`)

### Health-Check Endpoint

- [ ] [M] Implement a `/healthz` GET endpoint in a new dedicated file (e.g., `HealthCheckController.cs`, `health_routes.py`, `healthRouter.js`) that returns HTTP 200 with a JSON body `{"status":"healthy","timestamp":"<UTC ISO-8601>"}` and HTTP 503 on failure
- [ ] [S] Register the health-check route in the application entry point / router configuration so it is reachable without authentication and excluded from HTTPS-redirect enforcement (to support load-balancer probes over HTTP on internal networks if required)
- [ ] [XS] Add a liveness vs. readiness distinction comment block in the health-check file to document intended future extension points without implementing them now

### DataAnnotations Input Validation

- [ ] [M] Identify all request input models / DTOs / schema classes that currently lack validation attributes and add appropriate `DataAnnotations` (or framework-equivalent) attributes — e.g., `[Required]`, `[StringLength]`, `[Range]`, `[EmailAddress]` — directly on each model property in the relevant model files
- [ ] [S] Add or update the validation middleware / filter in the application entry point so that invalid models automatically return HTTP 400 with a structured error body (field name + error message) before reaching controller/handler logic
- [ ] [S] Write unit tests for at least three representative input models in the existing test project / test directory, covering: (a) valid input passes, (b) missing required field returns 400, (c) out-of-range value returns 400

---

## Phase 3 — Testing & Validation

- [ ] [M] Write integration tests for the HTTPS redirect in the test project: assert HTTP → HTTPS redirect returns 301/308 and the `Location` header contains `https://`
- [ ] [M] Write integration tests for the `/healthz` endpoint: assert 200 response, correct `Content-Type: application/json`, and presence of `status` and `timestamp` fields in the response body
- [ ] [S] Run the full test suite and compare results against the baseline recorded in `docs/test-baseline.md`; document any regressions and resolve before merging
- [ ] [XS] Manually verify HTTPS enforcement and health-check endpoint in a local environment using `curl` or a browser, and record results in `docs/test-baseline.md`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration file (e.g., `.github/workflows/ci.yml`, `Jenkinsfile`, `.gitlab-ci.yml`) to add a health-check smoke-test step that calls `/healthz` after deployment to staging and fails the pipeline on non-200 response
- [ ] [XS] Update any Docker `HEALTHCHECK` instruction in `Dockerfile` (if present) to use `CMD curl -f http://localhost:<port>/healthz || exit 1`
- [ ] [XS] Ensure environment variables for TLS certificate path and HTTPS port are declared in CI secrets / environment variable configuration and documented in `docs/pipeline-notes.md`

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry (or update the existing one) describing the three changes: HTTPS enforcement, `/healthz` endpoint, and DataAnnotations validation, with the PR number and date
- [ ] [S] Update `README.md` (or equivalent runbook) with: (a) how to configure TLS locally, (b) the `/healthz` contract, and (c) how to add validation attributes to new models
- [ ] [XS] Verify that the staged rollout (dev → staging → production) sequence is documented in the deployment runbook and that the HTTPS redirect is toggled off for internal load-balancer probe traffic in production config before go-live

---

**Total estimated effort:** ~5–7 developer-days depending on framework specifics confirmed in Prerequisites.