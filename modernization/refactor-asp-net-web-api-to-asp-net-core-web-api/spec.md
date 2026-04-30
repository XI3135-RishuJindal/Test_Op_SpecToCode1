# ASP.NET Web API to ASP.NET Core Web API Modernization Specification

## Current State

- **Framework**: ASP.NET Web API (System.Web.Http)  
- **Entrypoints and Routing**:  
  - Uses `Global.asax` and `WebApiConfig.Register` for route registration  
  - Attribute and convention-based routes supported via `[Route]` and `routes.MapHttpRoute`
- **Controllers**: Derive from `ApiController`  
- **Dependency Injection**:  
  - Optional; if present, custom or third-party integration  
  - Service resolution via constructors rare  
- **Middleware**:  
  - Pipeline managed via `GlobalConfiguration`  
  - Standard handlers (e.g., message handlers, filters)  
- **Configuration**:  
  - Primarily web.config for settings and system-wide configuration
- **Data Models**:  
  - Classes used as DTOs or entity models  
- **Serialization**:  
  - Uses `Newtonsoft.Json` or default XML Serializer (`MediaTypeFormatter`)  
- **API Behavior**:  
  - Uses IHttpActionResult, HttpResponseMessage  
- **Authentication**:  
  - Typically [Authorize] attribute, configured in web.config or via OWIN middlewares  
- **Build/Runtime Environment**:  
  - .NET Framework 4.x  
  - IIS hosting/integration

## Target State

- **Framework**: ASP.NET Core Web API (`Microsoft.AspNetCore.App`), targeting `.NET 6.0`  
- **Entrypoints and Routing**:  
  - Startup via `Program.cs`/`Startup.cs` using `WebApplication` or `IHostBuilder`  
  - Minimal and attribute routing with `[Route]`, `[HttpGet]`, etc.
- **Controllers**: Derive from `ControllerBase`  
- **Dependency Injection**:  
  - Built-in .NET Core DI container  
  - Constructor-injected services
- **Middleware**:  
  - Pipeline managed in `Program.cs`/`Startup.cs` via `app.UseX`  
  - Custom middleware handled via delegates  
- **Configuration**:  
  - `appsettings.json`, environment variables, strongly typed config binding  
- **Data Models**:  
  - DTO/Model classes; potential changes for nullable reference types  
- **Serialization**:  
  - Default `System.Text.Json` (with optional switch to `Newtonsoft.Json`)  
- **API Behavior**:  
  - `ActionResult<T>`, `IActionResult` return types  
- **Authentication**:  
  - AuthenticationScheme/AuthorizationPolicy via middleware in pipeline  
  - `[Authorize]` attribute
- **Build/Runtime Environment**:  
  - .NET 6.0+  
  - Cross-platform: Windows, Linux, macOS  
  - Out-of-process/self-hosted Kestrel, with optional IIS reverse proxy

## Compatibility & Breaking Changes

1. **Namespace and Base Class Changes**  
   - `ApiController` replaced with `ControllerBase`
   - `System.Web.Http` replaced with `Microsoft.AspNetCore.Mvc`

   **Migration**: Update all controllers to inherit from `ControllerBase`, update using/imports, and refactor base class usages.

2. **Startup/Configuration Pipeline**  
   - No more `Global.asax`, `Web.config`, or `WebApiConfig.Register`.
   - Application starts in `Program.cs`/`Startup.cs`.
   
   **Migration**: Port route registration and pipeline configuration to new hosting model.

3. **Dependency Injection**  
   - `.NET Core` uses built-in DI with constructor injection natively, not from custom providers.
   
   **Migration**: Register all services in `ConfigureServices(IServiceCollection)`.

4. **Routing Changes**  
   - Routing is attribute-based by default; conventional routes defined in builder.
   - `MapHttpRoute` no longer available.
   
   **Migration**: Update routing attributes and ensure endpoints are mapped in builder.

5. **Configuration Files**  
   - `web.config` replaced by `appsettings.json` and environment variables.
   
   **Migration**: Move app-specific config to new `.json` structure and update code binding.

6. **Serialization**  
   - Default serializer is `System.Text.Json`, not `Newtonsoft.Json`.
   
   **Migration**: Migrate custom converters/formatters or opt-in to (re)add `Newtonsoft.Json`.

7. **Return Types**  
   - `IHttpActionResult`, `HttpResponseMessage` replaced by `IActionResult`, `ActionResult<T>`.
   
   **Migration**: Update return signatures and response creation.

8. **Authentication**  
   - Authentication is handled in middleware and via options, not config file/OWIN
  
   **Migration**: Port authentication schemes to `AddAuthentication`, use `[Authorize]` as before.

9. **Hosting**  
   - No IIS-inProc hosting; runs on Kestrel by default.
   
   **Migration**: Update deployment procedures, can use IIS as a reverse proxy if required.

## Key Flows (before vs after)

### 1. API Request Processing

**Before:**  
1. IIS receives HTTP request.  
2. `Global.asax` (if present) initializes pipeline.  
3. Request routed via `WebApiConfig` and handled by `ApiController`.  
4. Dependency resolution, request handled, response serialized via configured formatters.

**After:**  
1. Kestrel receives HTTP request (optionally via IIS reverse proxy).  
2. `Program.cs`/`Startup.cs` configures pipeline.  
3. Request dispatched via attribute-based routing to `ControllerBase`-derived controller.  
4. Dependency injection via constructor, request handled, response serialized via `System.Text.Json`.

### 2. Configuration Injection

**Before:**  
1. Values read from `web.config` (e.g., `<appSettings>`).  
2. Accessed via `ConfigurationManager.AppSettings["key"]`.

**After:**  
1. Values read from `appsettings.json`/environment variables.  
2. Injected via IOptions<T> into controller/service, or accessed via `Configuration["key"]`.

## Data Model Changes

- DTO/model classes may need adjustment for nullability if project enables nullable context.
- No schema changes unless required for serializer compatibility (e.g., date formats, enum casing).
- Breaking: Optional use of record types, nullable annotations.

## Configuration Changes

- Replace all settings in `web.config` with entries in `appsettings.json` (JSON format) or environment variables.
- No more system.web/system.webServer or IIS-specific settings in project file.
- New settings for ASP.NET Core middleware and authentication moved to `Program.cs`/`Startup.cs`.
- Add/alter environment variables as needed for required configuration keys.

---

**End of specification**