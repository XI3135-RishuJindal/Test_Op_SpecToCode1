# TASKS: Add ASP.NET Core Health-Check Endpoint

> **Scope:** Introduce a `/health` (and optionally `/health/ready`, `/health/live`) endpoint using the built-in `Microsoft.Extensions.Diagnostics.HealthChecks` infrastructure.
> **Urgency:** Medium
> **Note:** Runtime, build tool, and framework versions were not supplied in the tech analysis. Tasks reference canonical ASP.NET Core patterns; file paths should be adjusted to match the actual project structure before work begins.

---

## Prerequisites

- [ ] [XS] Confirm the target ASP.NET Core version (6, 7, 8, or 9) by inspecting the `.csproj` `<TargetFramework>` element and record it in the PR description
- [ ] [XS] Verify that `Microsoft.Extensions.Diagnostics.HealthChecks` is already transitively included (it ships in-box for ASP.NET Core ≥ 2.2) or identify whether a separate NuGet package is required in the `.csproj`
- [ ] [XS] Confirm developer has write access to the application repository and can open pull requests against the main branch
- [ ] [XS] Ensure a local `dotnet` SDK matching the project's `<TargetFramework>` is installed and `dotnet build` succeeds from a clean checkout

---

## Phase 1 — Preparation

- [ ] [XS] Create a feature branch named `feature/health-check-endpoint` from the default branch in the repository
- [ ] [S] Capture the current test baseline by running the existing test suite (`dotnet test`) and recording pass/fail counts and code-coverage percentage in a `baseline.txt` artifact committed to the branch
- [ ] [XS] Audit the `.csproj` file for any existing health-check–related NuGet references (e.g. `AspNetCore.HealthChecks.*`) to avoid duplicate or conflicting registrations

---

## Phase 2 — Core Upgrade

- [ ] [S] Register the health-check services in `Program.cs` (or `Startup.ConfigureServices` for older project styles) by adding `builder.Services.AddHealthChecks()` and any initial liveness/readiness checks
- [ ] [XS] Map the health-check endpoint in `Program.cs` (or `Startup.Configure`) by calling `app.MapHealthChecks("/health")` within the middleware pipeline, placed after authentication/authorization middleware but before catch-all routes
- [ ] [S] Create a dedicated `HealthChecks/` folder and add a `ReadinessHealthCheck.cs` class implementing `IHealthCheck` to verify any critical downstream dependency (e.g. database reachability), if applicable per actual project dependencies
- [ ] [S] Create `HealthChecks/LivenessHealthCheck.cs` implementing `IHealthCheck` for a lightweight in-process liveness signal (e.g. always-healthy canary), if a separate liveness probe is required
- [ ] [XS] Register readiness and liveness checks with tags in `Program.cs` using `.AddCheck<ReadinessHealthCheck>("readiness", tags: new[] { "ready" })` and `.AddCheck<LivenessHealthCheck>("liveness", tags: new[] { "live" })` so they can be filtered independently
- [ ] [XS] Map tagged sub-routes in `Program.cs`: `app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = r => r.Tags.Contains("ready") })` and the equivalent for `/health/live`
- [ ] [S] Add a custom `HealthCheckResponseWriter` helper in `HealthChecks/HealthCheckResponseWriter.cs` to serialize a structured JSON response (status, results, duration) instead of the plain-text default, and wire it into `HealthCheckOptions.ResponseWriter`

---

## Phase 3 — Testing & Validation

- [ ] [M] Add integration tests in the existing test project (e.g. `tests/<ProjectName>.Tests/`) using `WebApplicationFactory<Program>` to assert that `GET /health` returns `200 OK` with a valid JSON body when all checks pass
- [ ] [S] Add integration tests asserting that `GET /health/ready` and `GET /health/live` return correct status codes and tagged results independently
- [ ] [S] Add a unit test for `ReadinessHealthCheck.CheckHealthAsync` covering both healthy and degraded/unhealthy paths using a mocked dependency
- [ ] [XS] Re-run `dotnet test` and confirm no regressions against the `baseline.txt` counts captured in Phase 1; record new coverage delta in the PR description

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration file (e.g. `.github/workflows/ci.yml`, `azure-pipelines.yml`, or equivalent) to add a smoke-test step that calls `GET /health` against the deployed preview/staging environment and fails the pipeline on a non-`200` response
- [ ] [XS] If a `Dockerfile` exists, add or update the `HEALTHCHECK` instruction to `HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:<PORT>/health || exit 1` using the correct application port
- [ ] [XS] If Kubernetes manifests exist, add `livenessProbe` and `readinessProbe` stanzas pointing to `/health/live` and `/health/ready` respectively in the relevant `Deployment` YAML file

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry (or update the existing changelog) documenting the new `/health`, `/health/ready`, and `/health/live` endpoints, their response schema, and the ASP.NET Core version they target
- [ ] [XS] Update `README.md` (or the project's operations runbook) with a "Health Checks" section describing endpoint URLs, expected response codes, and how to interpret the JSON payload
- [ ] [XS] Verify that the health-check endpoints are excluded from authentication middleware (i.e. `AllowAnonymous` or placed before `UseAuthorization`) and document this decision in the PR description to prevent accidental lock-out of monitoring agents

---

> **Out of scope for this task:** database migrations, dependency version bumps unrelated to health checks, observability/metrics endpoints (e.g. Prometheus `/metrics`), and any changes to business logic.