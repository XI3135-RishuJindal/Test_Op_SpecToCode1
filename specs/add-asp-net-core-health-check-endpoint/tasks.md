# TASKS: Add ASP.NET Core Health-Check Endpoint

> **Scope:** Introduce a `/health` (and optionally `/health/ready`, `/health/live`) endpoint using the built-in `Microsoft.Extensions.Diagnostics.HealthChecks` infrastructure.
> **Urgency:** Medium
> **Note:** Runtime, build tool, and framework versions were not supplied in the tech analysis. Tasks reference canonical ASP.NET Core patterns; file paths should be adjusted to match the actual project structure before work begins.

---

## Prerequisites

- [ ] [XS] Confirm the target ASP.NET Core version (6, 7, 8, or 9) by inspecting the `.csproj` `<TargetFramework>` element and record it in the PR description
- [ ] [XS] Verify that `Microsoft.Extensions.Diagnostics.HealthChecks` is already transitively included (it ships in-box for ASP.NET Core ≥ 2.2) or identify whether a separate NuGet package is required, in the project `.csproj` file
- [ ] [XS] Confirm developer has write access to the application repository and can push a feature branch and open a pull request

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feature/health-check-endpoint` from the main integration branch
- [ ] [S] Capture the current passing test count and code-coverage baseline by running the existing test suite locally and saving the summary output to `docs/test-baseline-pre-healthcheck.txt`
- [ ] [XS] Audit existing `Program.cs` (or `Startup.cs`) for any conflicting `/health` route registrations or middleware that could intercept the new endpoint, and document findings in a PR comment

---

## Phase 2 — Core Upgrade

- [ ] [S] Register the health-checks service by adding `builder.Services.AddHealthChecks()` (and any initial liveness/readiness checks) in `Program.cs` (or `Startup.ConfigureServices()`)
- [ ] [S] Map the health-check endpoint by adding `app.MapHealthChecks("/health")` in the middleware pipeline in `Program.cs` (or `Startup.Configure()`), positioned after authentication/authorization middleware if present
- [ ] [M] Create a `HealthChecks/` folder and implement a concrete `IHealthCheck` class (e.g., `DatabaseHealthCheck.cs`) for each critical dependency (database, cache, external API) identified during prerequisite review, returning `HealthCheckResult.Healthy/Degraded/Unhealthy` with descriptive messages
- [ ] [S] Register each custom `IHealthCheck` implementation with appropriate tags (`"ready"`, `"live"`) via `builder.Services.AddHealthChecks().AddCheck<DatabaseHealthCheck>("database", tags: new[] { "ready" })` in `Program.cs`
- [ ] [S] Add separate `/health/ready` and `/health/live` mapped endpoints using `MapHealthChecks` with `HealthCheckOptions` tag filters in `Program.cs`, if liveness/readiness split is required by the deployment platform
- [ ] [XS] Configure `HealthCheckOptions.ResponseWriter` to emit JSON (using `UIResponseWriter` from `AspNetCore.HealthChecks.UI.Client` or a custom writer) so consumers receive structured output, in `Program.cs`

---

## Phase 3 — Testing & Validation

- [ ] [M] Write integration tests using `WebApplicationFactory<Program>` that assert `/health` returns `HTTP 200` when all checks pass, in `tests/<ProjectName>.Tests/HealthCheck/HealthEndpointTests.cs`
- [ ] [S] Write integration tests that assert `/health` returns `HTTP 503` when a mocked `IHealthCheck` returns `Unhealthy`, in `tests/<ProjectName>.Tests/HealthCheck/HealthEndpointTests.cs`
- [ ] [S] Write unit tests for each custom `IHealthCheck` class (e.g., `DatabaseHealthCheckTests.cs`) covering healthy, degraded, and unhealthy code paths, in `tests/<ProjectName>.Tests/HealthCheck/`
- [ ] [XS] Run the full test suite and confirm no pre-existing tests regressed; compare pass count against `docs/test-baseline-pre-healthcheck.txt`
- [ ] [XS] Manually invoke `GET /health` against a locally running instance and verify the JSON response body contains `status`, `duration`, and per-check `entries`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a health-check smoke-test step to the CI pipeline configuration (e.g., `.github/workflows/ci.yml` or `azure-pipelines.yml`) that starts the app and curls `/health`, failing the build if the response is not `HTTP 200`
- [ ] [XS] If a `Dockerfile` exists, add a `HEALTHCHECK` instruction pointing to `/health` with appropriate `--interval`, `--timeout`, and `--retries` values in `Dockerfile`
- [ ] [XS] If a Kubernetes deployment manifest exists (`k8s/deployment.yaml` or equivalent), add `livenessProbe` and `readinessProbe` HTTP GET entries targeting `/health/live` and `/health/ready` respectively

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry under an `[Unreleased]` section describing the new `/health`, `/health/ready`, and `/health/live` endpoints and their expected response schema
- [ ] [S] Update (or create) `docs/runbook.md` with a section covering: endpoint URLs, expected healthy/degraded/unhealthy response bodies, how to interpret each registered check, and on-call remediation steps for a `503` response
- [ ] [XS] Confirm with the team that no API gateway, load-balancer ACL, or firewall rule blocks unauthenticated access to `/health` in staging; document any required allow-list changes
- [ ] [XS] Deploy to the staging environment and verify the health endpoint is reachable and returns `200 Healthy` before merging to the main branch