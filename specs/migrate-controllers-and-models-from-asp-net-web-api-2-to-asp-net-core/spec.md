# Spec: Migrate Controllers and Models from ASP.NET Web API 2 to ASP.NET Core

---

## Summary

This spec covers the migration of HTTP controllers and associated model classes from ASP.NET Web API 2 to ASP.NET Core. The expected outcome is that all existing API endpoints and request/response contracts are preserved and functional under the ASP.NET Core hosting and routing pipeline, with obsolete Web API 2 abstractions replaced by their ASP.NET Core equivalents.

---

## Motivation

ASP.NET Web API 2 runs on the legacy `System.Web` stack, which is not supported on .NET Core or .NET 5+. Continued reliance on this stack blocks adoption of modern .NET runtimes, limits cross-platform deployment, and prevents access to current performance improvements and security patches. The upgrade urgency for this migration is rated **medium**.

Specific drivers include:

- **End-of-life risk:** ASP.NET Web API 2 is tied to the .NET Framework lifecycle; no new feature development occurs on this stack.
- **Security posture:** The `System.Web` pipeline does not receive the same cadence of security updates as ASP.NET Core.
- **Performance:** ASP.NET Core's Kestrel-based pipeline offers measurably lower latency and higher throughput than the IIS-bound `System.Web` pipeline.
- **Ecosystem alignment:** Modern tooling (OpenAPI generation, middleware libraries, cloud-native hosting) targets ASP.NET Core exclusively.

> **Note:** Specific CVE identifiers, exact framework version numbers, and compliance requirements were not provided in the tech analysis. See [Open Questions](#open-questions).

---

## Current State

The existing codebase uses ASP.NET Web API 2 patterns. The following abstractions and behaviours are in scope:

### Controllers
- Controllers inherit from `ApiController` (`System.Web.Http.ApiController`).
- Routing is configured via `HttpRouteCollection` (typically in `WebApiConfig.Register`) using attribute routes (`[RoutePrefix]`, `[Route]`) and/or convention-based routes.
- Action results are returned as `IHttpActionResult` or raw `HttpResponseMessage`.
- HTTP method binding uses `[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpDelete]`, `[HttpPatch]` from `System.Web.Http`.
- Dependency injection is wired through a custom `IDependencyResolver` (`System.Web.Http.Dependencies.IDependencyResolver`).

### Models
- Request/response models are plain C# classes (POCOs).
- Model validation uses `System.ComponentModel.DataAnnotations` attributes and `ModelState` is accessed via `ApiController.ModelState`.
- Media-type formatting is handled by `MediaTypeFormatter` subclasses registered in `HttpConfiguration.Formatters`.

### Filters & Middleware
- Cross-cutting concerns (auth, logging, error handling) are implemented as `System.Web.Http` action filters (`ActionFilterAttribute`), exception filters (`ExceptionFilterAttribute`), or message handlers (`DelegatingHandler`).

### Configuration
- Global configuration lives in `HttpConfiguration` (e.g., `GlobalConfiguration.Configuration`).
- CORS is configured via `EnableCorsAttribute` or `config.EnableCors()` from `Microsoft.AspNet.WebApi.Cors`.

> **TODO:** Confirm the full inventory of controllers, filters, message handlers, and custom `MediaTypeFormatter` implementations present in the codebase.

---

## Proposed Changes

### Summary Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Controller base class | `ApiController` (`System.Web.Http`) | `ControllerBase` (`Microsoft.AspNetCore.Mvc`) | Y |
| Action result type | `IHttpActionResult` / `HttpResponseMessage` | `IActionResult` / `ActionResult<T>` | Y |
| Route registration | `HttpRouteCollection` in `WebApiConfig` | ASP.NET Core endpoint routing (`MapControllers`) | Y |
| Route attributes | `[RoutePrefix]` + `[Route]` (Web API) | `[Route]` on controller + `[Route]` on action (ASP.NET Core) | Y |
| HTTP method attributes | `System.Web.Http.[HttpGet/Post/…]` | `Microsoft.AspNetCore.Mvc.[HttpGet/Post/…]` | Y |
| Model state validation | `ApiController.ModelState` | `ControllerBase.ModelState`; auto-validation via `[ApiController]` | N (API compatible) |
| Dependency injection | `IDependencyResolver` (Web API) | Built-in ASP.NET Core DI (`IServiceCollection`) | Y |
| Action/exception filters | `System.Web.Http` filter attributes | `Microsoft.AspNetCore.Mvc` filter attributes | Y |
| Message handlers | `DelegatingHandler` (Web API pipeline) | ASP.NET Core middleware (`IMiddleware` / `Use`) | Y |
| Media-type formatters | `MediaTypeFormatter` in `HttpConfiguration.Formatters` | `InputFormatter` / `OutputFormatter` in MVC options | Y |
| CORS configuration | `Microsoft.AspNet.WebApi.Cors` | `Microsoft.AspNetCore.Cors` (`AddCors` / `UseCors`) | Y |
| Global configuration | `HttpConfiguration` / `GlobalConfiguration` | `WebApplication` builder + `IServiceCollection` | Y |
| Model classes (POCOs) | Unchanged | Unchanged (no migration required) | N |
| DataAnnotations validation | `System.ComponentModel.DataAnnotations` | `System.ComponentModel.DataAnnotations` (same namespace) | N |

### Detail Notes

- **`[RoutePrefix]`** has no direct equivalent in ASP.NET Core; it is replaced by placing a `[Route]` attribute at the controller class level.
- **`[ApiController]`** attribute in ASP.NET Core enables automatic 400 responses for invalid model state, removing the need for explicit `ModelState.IsValid` guards in most actions.
- **`HttpResponseMessage`** return types must be replaced; where raw response manipulation is needed, `IActionResult` helpers (`Ok()`, `BadRequest()`, `StatusCode()`) or `ActionResult<T>` are used instead.
- **Message handlers** that perform cross-cutting work (e.g., token inspection, request logging) must be re-expressed as ASP.NET Core middleware components.
- **Custom `MediaTypeFormatter`** implementations must be re-expressed as ASP.NET Core `InputFormatter`/`OutputFormatter` subclasses.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `ApiController` removed | All controllers fail to compile | Replace base class with `ControllerBase`; add `[ApiController]` and `[Route]` attributes |
| `IHttpActionResult` removed | All action return types fail to compile | Replace with `IActionResult` or `ActionResult<T>` |
| `HttpResponseMessage` return types | Actions returning raw responses fail to compile | Replace with `IActionResult` helpers or `ActionResult<T>` |
| `[RoutePrefix]` removed | Route attributes fail to compile | Move prefix to a `[Route]` attribute on the controller class |
| Web API `[HttpGet/Post/…]` namespace | Attribute resolution fails | Update `using` directives to `Microsoft.AspNetCore.Mvc` |
| `IDependencyResolver` removed | DI container wiring fails at startup | Re-register all services in `IServiceCollection` |
| Web API filter attributes | Filters fail to compile or execute | Re-implement using `Microsoft.AspNetCore.Mvc` filter interfaces |
| `DelegatingHandler` pipeline | Handlers are not invoked | Re-implement as ASP.NET Core middleware |
| `MediaTypeFormatter` | Custom formatters not invoked | Re-implement as `InputFormatter`/`OutputFormatter` |
| `HttpConfiguration` / `GlobalConfiguration` | Startup configuration fails | Migrate to `WebApplication` builder pattern and `IServiceCollection` |
| `Microsoft.AspNet.WebApi.Cors` package | CORS policy not applied | Replace with `Microsoft.AspNetCore.Cors`; configure via `AddCors`/`UseCors` |
| `GlobalConfiguration.Configuration.Filters` | Global filters not registered | Register global filters via `MvcOptions.Filters` in `AddControllers` |

---

## Acceptance Criteria

1. **Given** the migrated project is built, **when** the build pipeline runs, **then** the build completes with zero errors and zero warnings related to `System.Web.Http` or `ApiController` references.

2. **Given** the application is started, **when** each previously existing API endpoint is called with a valid request, **then** the response status code, response body schema, and `Content-Type` header match those produced by the Web API 2 baseline.

3. **Given** a request is sent with an invalid model (failing DataAnnotations constraints), **when** the endpoint processes the request, **then** a `400 Bad Request` response is returned containing a machine-readable error body, consistent with the previous behaviour.

4. **Given** a request is sent that previously triggered a custom action filter (e.g., an authorization or logging filter), **when** the endpoint is called, **then** the filter executes and produces the same observable side-effect (log entry, rejection response, etc.) as the Web API 2 implementation.

5. **Given** a request is sent that previously traversed a `DelegatingHandler`, **when** the equivalent middleware is active, **then** the middleware executes and the request/response is modified identically to the previous handler behaviour.

6. **Given** a CORS preflight request is sent from an origin that was previously allowed, **when** the request is processed, **then** the response includes the correct `Access-Control-Allow-Origin` header and a `204` or `200` status.

7. **Given** the application starts, **when** all services previously registered via the custom `IDependencyResolver` are requested from the DI container, **then** they resolve without error and with the same lifetime (singleton/scoped/transient) as before.

8. **Given** a request body requiring a custom media-type formatter is sent, **when** the endpoint processes the request, **then** the body is deserialized correctly and the response is serialized in the expected format, matching the previous formatter behaviour.

9. **Given** the full automated test suite is executed against the migrated application, **when** all tests complete, **then** no test that passed against the Web API 2 baseline fails against the ASP.NET Core implementation.

10. **Given** the migrated application is deployed to the target hosting environment, **when** a smoke-test suite covering all public endpoints is executed, **then** all smoke tests pass with no `5xx` responses.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current .NET Framework version targeted by the Web API 2 project? | TODO | TODO |
| 2 | What is the target ASP.NET Core version for the migration (e.g., ASP.NET Core 6, 7, 8)? | TODO | TODO |
| 3 | What is the complete inventory of controllers, action methods, and route templates? | TODO | TODO |
| 4 | Are there custom `MediaTypeFormatter` implementations, and if so, what formats do they handle? | TODO | TODO |
| 5 | Are there `DelegatingHandler` message handlers in the pipeline, and what is their responsibility? | TODO | TODO |
| 6 | What DI container is currently used with the `IDependencyResolver` (e.g., Autofac, Unity, Ninject)? | TODO | TODO |
| 7 | Are there any endpoints that return `HttpResponseMessage` directly for streaming or file-download scenarios? | TODO | TODO |
| 8 | Are there specific CVEs or compliance requirements driving the urgency rating? | TODO | TODO |
| 9 | Is OData or any other Web API 2 extension library (`System.Web.OData`, etc.) in use? | TODO | TODO |
| 10 | What is the target hosting model post-migration (IIS in-process, IIS out-of-process, Kestrel standalone, containerised)? | TODO | TODO |