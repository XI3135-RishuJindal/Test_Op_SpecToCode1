# Software Modernization Specification Document

## Current State
- **Interfaces**: The existing ASP.NET Web API is built using an earlier version of ASP.NET, potentially 4.x or an earlier Core version. The interfaces are HTTP APIs built on top of `ApiController`, with routes defined in a legacy manner.
- **APIs**: The existing APIs are using routes defined in `WebApiConfig.cs` with attributes such as `[Route]`, and are potentially using `HttpGet`, `HttpPost`, etc., for defining endpoint actions.
- **Data Models**: Data models are likely structured using Entity Framework 6 or an older version. Data annotations are used for validation.
- **Key Behaviours**: Existing features may include outdated authentication mechanisms, such as Windows Authentication or Forms Authentication, and may rely on legacy middlewares for functionalities like CORS and logging.

## Target State
- **Interfaces**: The new ASP.NET Web API will utilize the latest ASP.NET Core version (e.g., 7.x) with improved routing mechanisms using `MapControllers()` and attribute routing for more concise endpoint definitions.
- **APIs**: The API endpoints will leverage features such as endpoint routing, minimal APIs, and new `IResult` types for better response handling. Use of `async/await` for better performance in API calls.
- **Data Models**: Data models will be restructured to work with Entity Framework Core (latest version). Data annotations will remain but will now take advantage of the newer validation attributes.
- **Key Behaviours**: The upgraded API will include modern authentication methods, like JWT Bearer tokens, integrated middleware for functionality such as CORS, logging with built-in providers and structured error handling.

## Compatibility & Breaking Changes
- **Breaking Change: API Route Changes**
  - **Migration Path**: Update the route definitions to use `MapControllers()` in `Program.cs` instead of `WebApiConfig.cs`. All existing routes defined with attributes may need to be validated for proper binding in the new settings.
  
- **Breaking Change: Dependency Injection**
  - **Migration Path**: Update constructor injection patterns. Replace static instances with DI container registrations in `Startup.cs`.
  
- **Breaking Change: Entity Framework**
  - **Migration Path**: Migrate to Entity Framework Core APIs. The way DbContext is set up and utilized has changed, requiring all service registrations and data access code to be refactored.

- **Breaking Change: Model Binding and Validation**
  - **Migration Path**: Existing model binding and validation need to be changed to accommodate the new model binding system in ASP.NET Core.

## Key Flows (before vs after)
1. **Flow: API Request Handling**
   - **Before**: API requests routed through `WebApiConfig.cs` using legacy routing attributes.
   - **After**: API requests now handled through `MapControllers()` and defined in a modular fashion with attribute routing.

2. **Flow: Authentication Process**
   - **Before**: Utilizes legacy Forms Authentication or Windows Authentication.
   - **After**: Segregates authentication using JWT Bearer tokens integrated with ASP.NET Core Identity.

## Data Model Changes
- **Change Reference**: 
  - **Entity Framework Migration**: Change from `EntityFramework` to `EntityFrameworkCore`. This impacts context sets, which may alter the way navigational properties are managed.
  
| Old Class                  | New Class                 |
|---------------------------|---------------------------|
| `UserContext : DbContext` | `AppDbContext : DbContext`|
| `User`                    | `User` (optional changes) |

- **Data Annotations**: Migration to newer validation attributes available in Entity Framework Core.

## Configuration Changes
- **Environment Variables**:
  - **New**: Required environment variable for JWT Secret Key: `JWT_SECRET_KEY`.
  
- **Feature Flags**: 
  - Adjust configuration for CORS by using `services.AddCors()` instead of legacy configuration settings.
  
- **Config Files Changes**:
  - Update `appsettings.json` to include new configurations for logging, JWT token settings, and CORS policies, replacing the legacy `web.config` setup.

| Config Key                            | New Settings          |
|---------------------------------------|-----------------------|
| `Logging:LogLevel`                    | Updated structure for logging settings. |
| `JwtSettings:Issuer`                  | New JWT Token Issuer. |
| `JwtSettings:Audience`                | New JWT Token Audience.|

This document outlines the key elements for upgrading from the legacy ASP.NET Web API to the latest version. Detailed migration paths and transformation steps should be followed in accordance with breaking changes if the transition is to be seamless and effective.