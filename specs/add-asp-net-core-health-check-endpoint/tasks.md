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
- [ ] [S] Capture the current test baseline by running the existing test suite (`dotnet test`) and saving the output (pass count, coverage %) to `docs/test-baseline-pre-healthcheck.txt` for regression comparison
- [ ] [XS] Audit `Program.cs` (or `Startup.cs`) for any existing middleware registrations that could conflict with a new `/health` route (e.g., catch-all route handlers, authentication middleware applied globally)
- [ ] [XS] Confirm whether the project uses the minimal-hosting model (`WebApplication.CreateBuilder` in `Program.cs`) or the classic `Startup.cs` pattern, and note which migration path applies

---

## Phase 2 — Core Upgrade

- [ ] [S] Register the health-check services by adding `builder.Services.AddHealthChecks()` (minimal hosting) or `services.AddHealthChecks()` (Startup.cs `ConfigureServices`) in `Program.cs` / `Startup.cs`
- [ ] [S] Map the health-check endpoint by adding `app.MapHealthChecks("/health")` (minimal hosting) or `app.UseHealthChecks("/health")` (Startup.cs `Configure`) in `Program.cs` / `Startup.cs`
- [ ] [M] Create `HealthChecks/` directory and implement a custom `IHealthCheck` class (e.g., `DatabaseHealthCheck.cs`) if the application has a database dependency, registering it via `.AddCheck<DatabaseHealthCheck>("database")` in the service registration call
- [ ] [S] Add a dedicated `HealthCheckOptions` configuration to return a JSON response body by creating `Configuration/HealthCheckResponseWriter.cs` with a `WriteResponse` method using `System.Text.Json` and wiring it into `MapHealthChecks("/health", options)` in `Program.cs`
- [ ] [XS] Exclude the `/health` endpoint from authentication/authorization middleware by applying `.AllowAnonymous()` or configuring `RequireHost` / `RequireAuthorization(false)` on the `MapHealthChecks` call in `Program.cs` to prevent false negatives from probes

---

## Phase 3 — Testing & Validation

- [ ] [M] Add an integration test class `Tests/HealthCheckEndpointTests.cs` using `WebApplicationFactory<Program>` that asserts `GET /health` returns HTTP `200 OK` and a `Content-Type` of `application/json`
- [ ] [S] Add a test case in `Tests/HealthCheckEndpointTests.cs` that simulates a degraded dependency (mock the `IHealthCheck` to return `Unhealthy`) and asserts the endpoint returns HTTP `503 Service Unavailable`
- [ ] [XS] Run `dotnet test` and confirm all pre-existing tests still pass; compare pass count against `docs/test-baseline-pre-healthcheck.txt`
- [ ] [XS] Perform a manual smoke test against a locally running instance: `curl -i http://localhost:<port>/health` and verify the JSON payload contains `"status": "Healthy"`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (`.github/workflows/*.yml`, `azure-pipelines.yml`, or equivalent) to add a post-deploy smoke-test step that calls `GET /health` and fails the pipeline if the response is not `200`
- [ ] [XS] If a `Dockerfile` exists, verify the `EXPOSE` instruction includes the application port and that any container health-check instruction (`HEALTHCHECK CMD curl --fail http://localhost:<port>/health`) is added to the `Dockerfile`
- [ ] [XS] If Kubernetes manifests exist (`k8s/*.yaml` or `helm/`), add `livenessProbe` and `readinessProbe` stanzas pointing to `/health` in the relevant `Deployment` resource

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `## Health Check` section to `README.md` documenting the `/health` endpoint URL, expected response schema, and HTTP status codes (`200 Healthy`, `503 Unhealthy/Degraded`)
- [ ] [XS] Update `CHANGELOG.md` with an entry under the current version describing the addition of the `/health` endpoint
- [ ] [XS] Notify the infrastructure/ops team of the new endpoint path so load-balancer and uptime-monitor configurations can be updated to use `/health` for probe checks