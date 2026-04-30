# ASP.NET Web API to ASP.NET Core Web API Modernization Design Document

## Architecture Overview

### Before Modernization

- **Framework:** ASP.NET Web API (Full .NET Framework)
- **Project Structure:** Typically monolithic, possibly using `Global.asax`, `Web.config`, and old-style `System.Web` dependencies.
- **Hosting:** IIS-bound, runs on Windows.
- **Dependency Injection:** Manual or using legacy libraries (or none).
- **Middleware:** HTTP modules and handlers.

### After Modernization

- **Framework:** ASP.NET Core Web API (.NET 6+ or LTS target)
- **Project Structure:** Modern, with `Program.cs` and `Startup.cs` (or minimal hosting model), no `Global.asax` or `Web.config`.
- **Hosting:** Cross-platform (Windows, Linux, macOS) via Kestrel; can still be reverse-proxied behind IIS or Nginx.
- **Dependency Injection:** Built-in DI framework.
- **Middleware:** ASP.NET Core middleware pipeline.

---

## Migration Strategy

**Chosen Approach:** Strangler Fig

- **Rationale:** Allows incremental migration. Parts of the API can be ported module-by-module while the legacy system continues to serve non-migrated endpoints. This reduces risk and allows gradual adoption.

**Steps:**

1. **Set up parallel ASP.NET Core Web API project targeting .NET 6 or LTS.**
2. **Implement a BFF (backend-for-frontend) or gateway pattern to route requests:** Non-migrated endpoints go to legacy, migrated endpoints to Core.
3. **Incrementally rewrite/migrate controllers and services, validating each one.**
4. **Retire legacy endpoint only after each is ported/tested in production.**

---

## Component Changes

| Component             | Changes Required                                          | Rationale                        |
|-----------------------|----------------------------------------------------------|----------------------------------|
| Controllers           | Rewrite using ASP.NET Core attributes and DI              | Differences in controller base classes, routing, model binding. |
| Routing               | Use attribute-based or endpoint routing in Core          | ASP.NET Core uses unified routing model. |
| Configuration         | Migrate from `Web.config` to `appsettings.json` / `IConfiguration` | Modern configuration patterns.   |
| Dependency Injection  | Replace legacy DI (if any) with built-in ASP.NET Core DI | Built-in DI is standard in Core. |
| Middleware            | Replace HTTP modules/handlers with Core middleware       | Middleware pipeline is different in Core. |
| Authentication/Authorization | Migrate to ASP.NET Core middleware and policies | Integrated auth system in Core.  |
| Logging               | Use Microsoft.Extensions.Logging                         | Unified logging interface.       |
| Static Files          | Use ASP.NET Core Static Files middleware (if needed)     | Static file serving changed.     |
| Filters/Action Results| Rewrite filters, action results using Core primitives    | API surface is different.        |

---

## Dependency Upgrade Plan

| Dependency                    | Current Version (Web API) | Target Version (Core) | Migration Notes                                                   |
|-------------------------------|--------------------------|-----------------------|-------------------------------------------------------------------|
| ASP.NET Web API packages       | 5.x                      | N/A                   | Replace with ASP.NET Core Web API                                  |
| Newtonsoft.Json               | <=12.0.x                 | Latest or use System.Text.Json | Verify any custom converters/options; Core uses `System.Text.Json` by default |
| Microsoft.Extensions.*        | N/A                      | Latest                | Use for configuration, logging, DI, etc.                          |
| Swashbuckle/Swagger           | 5.x or not used          | Latest for Core       | Use Swashbuckle.AspNetCore for OpenAPI docs                       |
| Authentication packages       | Forms, JWT, external     | Latest Core equivalents| Use Microsoft.AspNetCore.Authentication.* packages                |

---

## CI/CD Pipeline Changes

- **Build Tool:** Update to use `dotnet build`, `dotnet test`, etc. Ensure the pipeline runs on cross-platform agents if possible.
- **Tasks:** Remove pre-MSBuild/.NET Framework specific tasks, scripts, or tools.
- **Testing:** Wire up XUnit or MSTest for .NET Core / .NET 6.
- **Artifacts:** Build self-contained or framework-dependent deployments.
- **Deployment:** Update to use `dotnet publish`; package as Docker images if containerization planned.

---

## Infrastructure Changes

- **Docker:** Optional, but recommend adding Dockerfile for containerized deployments. Use official ASP.NET Core runtime base images.
- **Web Server/Hosting:** May move from IIS-only hosting to Kestrel (w/optional reverse proxy).
- **Config Files:** Replace `Web.config` with `appsettings.json` and environment variables.
- **Cloud Resources:** N/A — not applicable to this task unless existing hosting model requires changes.

---

## Rollback Plan

- **Parallel Run:** Keep the ASP.NET Web API app live until all endpoints are verified on ASP.NET Core.
- **Routing Switch:** Use API gateway or routing rules to revert traffic to legacy endpoints.
- **Rollback Steps:**
  1. If a migrated endpoint fails, update the gateway/router to point back to the legacy implementation.
  2. If major issue, revert DNS or load balancer to direct all traffic to legacy.
  3. Maintain backup/clone of legacy deployment for the duration of migration.

---

## Testing Strategy

- **Unit Tests:** Rewrite existing tests (if any) for migrated code using xUnit, NUnit, or MSTest for .NET Core. Test logic isolated from framework code.
- **Integration Tests:** Test controllers, middleware, and dependency integration using ASP.NET Core's `WebApplicationFactory` or similar tools.
- **Regression Tests:** Ensure the migrated endpoints return identical responses, status codes, and error handling to their legacy counterparts.
- **Performance Tests:** Use a tool like k6 or JMeter to run load tests and compare responses/timings to legacy system.
- **Manual Testing:** For corner cases, legacy-specific behaviors, or authentication flows.
- **CI Integration:** Tests run automatically in pipeline on each commit.

---

