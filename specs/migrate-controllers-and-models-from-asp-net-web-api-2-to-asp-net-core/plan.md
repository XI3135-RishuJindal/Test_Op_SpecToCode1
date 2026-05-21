# PLAN: Migrate Controllers and Models from ASP.NET Web API 2 to ASP.NET Core

---

## Overview

**Migration Strategy: Strangler-Fig (Incremental Migration)**

Given that the upgrade urgency is rated **medium** and the effort option is **moderate**, a big-bang rewrite carries unnecessary risk. The strangler-fig pattern is selected because:

- It allows individual controllers and models to be migrated one at a time, keeping the application functional throughout.
- Existing Web API 2 endpoints can remain live while new ASP.NET Core equivalents are built and validated alongside them.
- Rollback scope is limited to individual components rather than the entire application.
- The moderate effort estimate implies a non-trivial codebase where incremental delivery reduces integration risk.

> **NOTE:** Because the tech analysis did not supply specific framework versions, file paths, class names, or infrastructure details, several fields below are marked **TODO**. These must be resolved during the discovery sprint before implementation begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 0 — Discovery & Baseline | Inventory all controllers, models, filters, and route configurations. Establish test coverage baseline. Identify all `System.Web.Http` usages. | Access to full source repository | TODO (person-days — derive from actual file count once discovery is complete) |
| 1 — Project Scaffold | Create new ASP.NET Core project (or convert `.csproj` to SDK-style). Configure `Program.cs` / `Startup.cs` equivalents. Add compatibility shims if needed. | Phase 0 complete | TODO |
| 2 — Model Migration | Migrate request/response model classes. Replace `System.Web.Http` model validation attributes with `System.ComponentModel.DataAnnotations` equivalents. | Phase 1 complete | TODO |
| 3 — Controller Migration (Batch 1 — Low Risk) | Migrate read-only / low-complexity controllers. Replace `ApiController` base class with `ControllerBase`. Update routing attributes. | Phase 2 complete | TODO |
| 4 — Controller Migration (Batch 2 — High Risk) | Migrate controllers with complex filters, action results, or media formatters. | Phase 3 validated | TODO |
| 5 — Cross-Cutting Concerns | Migrate global filters, exception handlers, message handlers, and DI registrations. | Phase 4 complete | TODO |
| 6 — Validation & Cutover | Full regression suite. Remove legacy Web API 2 project/references. Route traffic to new stack. | Phase 5 complete | TODO |

> **Effort Note:** The upgrade option is described as "moderate" but no person-days figure was provided. All effort cells are marked TODO and must be populated after Phase 0 discovery.

---

## Component Changes

### Controllers

| Concern | Web API 2 | ASP.NET Core | Files Affected |
|---------|-----------|--------------|----------------|
| Base class | `System.Web.Http.ApiController` | `Microsoft.AspNetCore.Mvc.ControllerBase` | All `*Controller.cs` files |
| Route attribute | `[RoutePrefix]` + `[Route]` | `[Route]` on class + `[Route]` on action | All `*Controller.cs` files |
| HTTP verb attributes | `[HttpGet]`, `[HttpPost]` (same namespace, different assembly) | Same names, `Microsoft.AspNetCore.Mvc` namespace | All `*Controller.cs` files |
| Action return types | `IHttpActionResult` / `HttpResponseMessage` | `IActionResult` / `ActionResult<T>` | All action methods |
| `Ok()`, `BadRequest()`, etc. | `ApiController` helper methods | `ControllerBase` helper methods (same names, compatible) | All action methods |
| Model binding | `[FromUri]`, `[FromBody]` | `[FromQuery]`, `[FromBody]`, `[FromRoute]` | Action method parameters |
| Request object | `Request` (`HttpRequestMessage`) | `HttpContext.Request` (`HttpRequest`) | Any direct `Request.*` usages |
| DI in controllers | Constructor injection via resolver | Constructor injection via built-in DI | Controller constructors |

**Structural change:** Remove inheritance from `ApiController`; replace with `ControllerBase` (or `Controller` if views are needed). Add `[ApiController]` attribute to enable automatic model validation responses.

### Models

| Concern | Web API 2 | ASP.NET Core | Files Affected |
|---------|-----------|--------------|----------------|
| Validation attributes | `System.ComponentModel.DataAnnotations` | Same — no change required | All model `*.cs` files |
| Media type formatters | `MediaTypeFormatter` subclasses | `System.Text.Json` / `Newtonsoft.Json` via `AddJsonOptions` | `*Formatter.cs`, `WebApiConfig.cs` equivalent |
| `ModelState` | `ApiController.ModelState` | `ControllerBase.ModelState` | Controllers using manual validation |

### Filters & Exception Handling

| Concern | Web API 2 | ASP.NET Core |
|---------|-----------|--------------|
| Action filters | `System.Web.Http.Filters.ActionFilterAttribute` | `Microsoft.AspNetCore.Mvc.Filters.ActionFilterAttribute` |
| Exception filters | `ExceptionFilterAttribute` | `IExceptionFilter` / middleware |
| Global exception handler | `IExceptionHandler` | `UseExceptionHandler` middleware |
| Message handlers | `DelegatingHandler` | ASP.NET Core middleware |

### Startup / Configuration

| Concern | Web API 2 | ASP.NET Core |
|---------|-----------|--------------|
| App config | `WebApiConfig.Register(config)` in `Global.asax` | `builder.Services.AddControllers()` + `app.MapControllers()` in `Program.cs` |
| DI container | External (Unity, Autofac, etc.) or none | Built-in `IServiceCollection`; Autofac/other still supported |
| OWIN pipeline | `Startup.cs` (OWIN) | `Program.cs` / `WebApplication` builder |

**TODO:** Identify specific file names for `WebApiConfig`, `Global.asax`, and any OWIN `Startup.cs` once repository is accessible.

---

## Dependency Upgrade Plan

> **NOTE:** The tech analysis did not supply specific current or target version numbers. The table below lists the known dependency transitions for this migration pattern. All version numbers are marked **TODO** and must be confirmed against the actual `.csproj` / `packages.config` files during Phase 0.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `Microsoft.AspNet.WebApi.Core` | TODO | Remove entirely | Entire `System.Web.Http` namespace removed | Replace with `Microsoft.AspNetCore.Mvc` |
| `Microsoft.AspNet.WebApi.WebHost` | TODO | Remove entirely | `GlobalConfiguration`, `HttpServer` removed | Replaced by ASP.NET Core hosting model |
| `Microsoft.AspNetCore.Mvc` | N/A (new) | TODO | N/A | Add via SDK or NuGet |
| `Microsoft.AspNetCore.Routing` | N/A (new) | TODO | N/A | Included transitively via `Microsoft.AspNetCore.Mvc` |
| `Newtonsoft.Json` | TODO | TODO | Possible if major version jump | ASP.NET Core defaults to `System.Text.Json`; opt back in via `AddNewtonsoftJson()` if needed |
| `System.Web` (GAC) | TODO | Remove | `HttpContext`, `HttpRequest` types differ | Use `Microsoft.AspNetCore.Http` equivalents |
| DI container (e.g., Unity/Autofac) | TODO | TODO | Adapter package may be needed | Evaluate replacing with built-in DI or using `Autofac.Extensions.DependencyInjection` |

---

## Infrastructure Changes

**TODO:** No infrastructure details (Docker, Kubernetes, CI/CD, IaC) were provided in the tech analysis or code context. The following items must be investigated during Phase 0:

- **Docker base image:** TODO — Confirm whether the application is containerized. If so, replace `mcr.microsoft.com/dotnet/framework/aspnet` base image with `mcr.microsoft.com/dotnet/aspnet` (ASP.NET Core runtime image).
- **Kubernetes manifests:** TODO — Verify if any manifests reference framework-specific health check paths or environment variables.
- **CI/CD pipeline:** TODO — Confirm build tooling (MSBuild vs. `dotnet` CLI). SDK-style projects use `dotnet build` / `dotnet test`; pipeline scripts may need updating.
- **IaC:** TODO — Not mentioned in context.
- **Target framework moniker:** Change `<TargetFramework>` in `.csproj` from `net4x` to `net8.0` (or appropriate LTS version confirmed in tech analysis).

---

## Rollback Strategy

### Phase 1 — Project Scaffold
- Delete or revert the new SDK-style `.csproj` and restore the original project file from source control.
- No production traffic is affected at this stage.

### Phase 2 — Model Migration
- Revert migrated model files via `git revert` or branch deletion.
- Models are shared types; confirm no downstream consumers have been updated before reverting.

### Phase 3 — Controller Migration (Batch 1)
- Re-enable the original Web API 2 controller files (kept in source control, not deleted until Phase 6).
- Update routing configuration to point back to legacy controllers.
- If using a reverse proxy or API gateway: redirect routes back to the Web API 2 host. **TODO:** Confirm routing topology.

### Phase 4 — Controller Migration (Batch 2)
- Same as Phase 3. High-risk controllers should be behind a feature flag or separate route prefix during migration to allow instant toggle. **TODO:** Confirm feature-flag infrastructure availability.

### Phase 5 — Cross-Cutting Concerns
- Revert `Program.cs` middleware registrations and DI configuration to last known-good state via `git revert`.
- Restore any removed `DelegatingHandler` or `ExceptionFilterAttribute` registrations.

### Phase 6 — Cutover
- If traffic has been switched: re-point load balancer / reverse proxy to the Web API 2 host. **TODO:** Confirm infrastructure.
- Restore Web API 2 project from source control tag created immediately before cutover.
- This is the highest-risk rollback; a source control tag/release must be created before Phase 6 begins.

**General Rule:** Do not delete any Web API 2 source files until Phase 6 is signed off. Keep them in source control under a `legacy/` branch or clearly marked as `*.webapi2.bak.cs` (excluded from build) to enable fast rollback.

---

## Testing Strategy

### Test Pyramid

```
         /\
        /  \   E2E / Contract Tests
       /----\
      /      \  Integration Tests
     /--------\
    /          \ Unit Tests
   /____________\
```

#### Unit Tests
- **Tool:** xUnit (preferred for ASP.NET Core) or NUnit — **TODO:** confirm existing test framework.
- **Scope:** All migrated controller action methods, model validation logic, filter logic.
- **Approach:** Use `Microsoft.AspNetCore.Mvc.Testing` helpers; instantiate controllers directly with mocked dependencies.
- **Coverage Target:** ≥ 80% line coverage on all migrated controller and model files. **TODO:** Confirm baseline coverage from Phase 0.
- **CI Gate:** Build fails if coverage drops below baseline established in Phase 0.

#### Integration Tests
- **Tool:** `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory<T>`).
- **Scope:** Full HTTP request/response cycle for each migrated endpoint. Validate status codes, response shapes, and headers match the Web API 2 baseline.
- **Approach:** Record Web API 2 response snapshots during Phase 0; replay against ASP.NET Core in integration tests (snapshot/approval testing).
- **CI Gate:** All integration tests must pass before any phase is merged to `main`.

#### Regression Tests
- **Tool:** Existing test suite (TODO — identify framework) + Postman/Newman collection or equivalent for API contract validation.
- **Scope:** Full endpoint inventory captured in Phase 0. Every route, verb, and response code must be covered.
- **CI Gate:** Zero regression failures required for Phase 6 cutover approval.

#### Performance Tests
- **Tool:** TODO — confirm whether k6, NBomber, or similar is available.
- **Scope:** Baseline p95 latency and throughput captured against Web API 2 in Phase 0. ASP.NET Core must meet or exceed baseline.
- **CI Gate:** Performance gate on Phase 6 — block cutover if p95 latency regresses by > 10% vs. baseline.

### Additional CI Gates
- Static analysis / linting: TODO (confirm Roslyn analyzers or SonarQube usage).
- `dotnet build` with `--warnaserror` to catch namespace/API mismatches early.
- Dependency vulnerability scan on new NuGet packages before merge.

---

## Timeline

> All durations are relative (weeks from project start) because the upgrade option did not supply absolute person-days. Absolute dates and owners must be assigned during Phase 0 kickoff.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Repository access & tooling setup | 0 — Discovery | Week 1 | TODO |
| Full controller/model inventory complete | 0 — Discovery | Week 1 | TODO |
| Test coverage baseline established | 0 — Discovery | Week 1 | TODO |
| New ASP.NET Core project scaffolded & building | 1 — Scaffold | Week 2 | TODO |
| All model classes migrated & unit tested | 2 — Models | Week 3 | TODO |
| Batch 1 controllers migrated & integration tested | 3 — Controllers (Low Risk) | Week 4–5 | TODO |
| Batch 2 controllers migrated & integration tested | 4 — Controllers (High Risk) | Week 6–7 | TODO |
| Filters, middleware, DI migrated | 5 — Cross-Cutting | Week 8 | TODO |
| Full regression & performance suite green | 6 — Validation | Week 9 | TODO |
| Production cutover | 6 — Cutover | Week 10 | TODO |
| Legacy Web API 2 code removed from repository | Post-cutover | Week 11 | TODO |

> **TODO:** Assign concrete person-days per phase once Phase 0 discovery is complete and the codebase size is known. Re-derive timeline from actual effort figures at that point.