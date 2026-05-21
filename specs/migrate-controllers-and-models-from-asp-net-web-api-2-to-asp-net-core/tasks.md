# Tasks: Migrate Controllers and Models from ASP.NET Web API 2 to ASP.NET Core

> **Scope:** Lift-and-shift of ASP.NET Web API 2 controllers and models to ASP.NET Core MVC/Web API. Tasks are ordered for sequential AI-agent pickup. Where specific filenames are not yet known, tasks reference the discovery step that will surface them.

---

## Prerequisites

- [ ] [XS] Confirm .NET SDK version installed locally supports ASP.NET Core target (minimum .NET 6 SDK recommended) — verify with `dotnet --version` in terminal
- [ ] [XS] Confirm Visual Studio 2022 (v17+) or `dotnet` CLI is available for building ASP.NET Core projects
- [ ] [XS] Verify source control access and ability to create feature branches in the repository
- [ ] [XS] Confirm all existing Web API 2 unit/integration tests pass on `main` before any changes — run existing test suite and record baseline pass/fail counts
- [ ] [S] Enumerate all Web API 2 controller files (classes inheriting `ApiController`) and model files across the solution — produce a flat inventory list saved as `migration-inventory.md`

---

## Phase 1 — Preparation

- [ ] [XS] Create a long-lived feature branch `feature/aspnetcore-migration` from `main` in the repository
- [ ] [S] Audit all NuGet packages in the existing `.csproj` / `packages.config` for Web API 2 dependencies (`Microsoft.AspNet.WebApi.*`, `System.Web.*`) — document each in `migration-inventory.md` with its ASP.NET Core equivalent or removal status
- [ ] [S] Capture full test baseline: run all existing tests, export results (counts, names, pass/fail) to `test-baseline.md` for regression comparison in Phase 3
- [ ] [XS] Identify and document all uses of `HttpResponseMessage`, `IHttpActionResult`, `ApiController`, `[RoutePrefix]`, `[FromUri]`, `[FromBody]`, and `HttpRequestMessage` across controller files — append findings to `migration-inventory.md`
- [ ] [XS] Identify all model classes using `System.ComponentModel.DataAnnotations` vs. any Web API 2-specific validation attributes — append findings to `migration-inventory.md`
- [ ] [XS] Identify all custom `DelegatingHandler`, `HttpMessageHandler`, or `ActionFilterAttribute` subclasses that must be ported to ASP.NET Core middleware or filters — append to `migration-inventory.md`

---

## Phase 2 — Core Upgrade

> Tasks are ordered by dependency chain: project scaffold → models → controllers → filters/middleware → startup wiring.

- [ ] [M] Create a new ASP.NET Core Web API project (targeting .NET 6 or .NET 8) alongside the existing project in the solution — add `<ProjectName>.Core.csproj` with `Microsoft.AspNetCore.App` framework reference and minimal `Program.cs` / `Startup.cs`
- [ ] [S] Remove `System.Web`, `Microsoft.AspNet.WebApi.Core`, `Microsoft.AspNet.WebApi.WebHost`, and related packages from the new project's `.csproj`; add `Microsoft.AspNetCore.Mvc` and any required ASP.NET Core NuGet packages identified in Phase 1 audit
- [ ] [M] Migrate all model classes: remove any `System.Web`-specific imports, confirm `System.ComponentModel.DataAnnotations` attributes are retained as-is, and move model files into the new project's `Models/` directory — one PR per logical model group from `migration-inventory.md`
- [ ] [M] Replace `ApiController` base class with `ControllerBase` in each controller file — update `using` directives, remove `System.Web.Http` references, and add `[ApiController]` + `[Route]` attributes in each controller identified in `migration-inventory.md`
- [ ] [M] Replace all `IHttpActionResult` return types with `IActionResult` or typed `ActionResult<T>` in each controller — update `Ok()`, `BadRequest()`, `NotFound()`, `Content()`, `ResponseMessage()` calls to their ASP.NET Core equivalents
- [ ] [S] Replace all `HttpResponseMessage` return types and `Request.CreateResponse()` usages with `IActionResult` equivalents in controllers — verify each occurrence from `migration-inventory.md`
- [ ] [S] Replace `[RoutePrefix("...")]` on controller classes with `[Route("...")]` and update any `[Route]` attributes on action methods to remove route prefix duplication — apply across all controller files
- [ ] [S] Replace `[FromUri]` parameter binding attributes with `[FromQuery]` and confirm `[FromBody]` behavior is unchanged in all controller action signatures
- [ ] [S] Migrate custom `ActionFilterAttribute` subclasses from `System.Web.Http.Filters.ActionFilterAttribute` to `Microsoft.AspNetCore.Mvc.Filters.ActionFilterAttribute` — update `OnActionExecuting`/`OnActionExecuted` signatures in each filter class
- [ ] [M] Migrate any custom `DelegatingHandler` or `HttpMessageHandler` pipeline components to ASP.NET Core middleware — create equivalent `IMiddleware` or `RequestDelegate`-based classes in `Middleware/` directory
- [ ] [S] Wire up services, middleware, and route configuration in `Program.cs` (or `Startup.cs`) — replace `WebApiConfig.Register(config)` / `GlobalConfiguration` patterns with `builder.Services.AddControllers()` and `app.MapControllers()`
- [ ] [S] Migrate any global exception handling from `ExceptionFilterAttribute` or `IExceptionHandler` to ASP.NET Core `IExceptionHandler` or `UseExceptionHandler` middleware in `Program.cs`
- [ ] [XS] Remove all `Global.asax` / `WebApiApplication` bootstrap code that is now superseded by `Program.cs` entry point

---

## Phase 3 — Testing & Validation

- [ ] [M] Update all existing unit tests that reference `System.Web.Http`, `ApiController`, or `HttpResponseMessage` test helpers — replace with `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory`) equivalents and `HttpClient`-based assertions
- [ ] [S] Re-run full test suite against the new ASP.NET Core project and compare pass/fail counts against `test-baseline.md` — document any new failures in `migration-delta.md`
- [ ] [S] Execute manual or automated integration tests against all routes enumerated in `migration-inventory.md` — verify HTTP status codes, response bodies, and content-type headers match pre-migration baseline
- [ ] [XS] Verify model validation responses (400 Bad Request with `ValidationProblemDetails`) behave equivalently to Web API 2 `ModelState` responses for all model classes
- [ ] [XS] Confirm route templates produce identical URL paths as the original Web API 2 `[RoutePrefix]` + `[Route]` combinations — use a route listing tool or integration test assertions

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline build step to target the new `.csproj` — replace any `msbuild` Web API 2 publish targets with `dotnet build` and `dotnet publish` commands for the ASP.NET Core project
- [ ] [S] Update the CI pipeline test step to run `dotnet test` against the updated test project referencing `Microsoft.AspNetCore.Mvc.Testing`
- [ ] [XS] Remove any IIS-specific `web.config` `<system.webServer>` handler mappings for Web API 2 (`ExtensionlessUrlHandler-Integrated-4.0`) — replace with ASP.NET Core-compatible `web.config` generated by `dotnet publish` if IIS hosting is retained

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `CHANGELOG.md` with a migration entry describing the move from ASP.NET Web API 2 to ASP.NET Core, listing breaking changes to route paths or response shapes if any were identified in `migration-delta.md`
- [ ] [XS] Review and update `README.md` build/run instructions to replace Web API 2 / IIS Express steps with `dotnet run` or updated IIS deployment steps
- [ ] [S] Conduct a staged rollout: deploy the ASP.NET Core version to a staging environment and validate all endpoints against the pre-migration baseline before promoting to production
- [ ] [XS] Set up post-migration monitoring: confirm HTTP 4xx/5xx error rate alerts are active in the existing monitoring tool for the migrated API endpoints and establish a 48-hour observation window post-production deployment