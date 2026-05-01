# Software Modernization Specification: ASP.NET Web API Upgrade

## Current State
- **Interfaces and APIs**: The current version of ASP.NET Web API is 5.2.6. This version uses `System.Web.Http` for routing and controllers. The API exposes RESTful endpoints, but does not support asynchronous methods natively, which impacts performance and scalability.
- **Data Models**: Current data models use Entity Framework 6 for database interactions, with a code-first approach.
- **Key Behaviors**: Authentication and authorization are handled using OWIN middleware; however, token-based authentication is lacking the improvements available in newer versions, leading to potential security vulnerabilities.

## Target State
- **Interfaces and APIs**: The target version is ASP.NET Core Web API 7.0. The new routing system utilizes `Microsoft.AspNetCore.Mvc` and supports attribute routing, along with full asynchronous programming capabilities, improving performance and response times.
- **Data Models**: The data models will be updated to work with Entity Framework Core 7.0, allowing for better performance optimizations and additional features, such as improved tracking and change detection.
- **Key Behaviors**: The new setup will employ JWT bearer tokens for improved security, integrated natively within the ASP.NET Core framework for better performance and scalability.

## Compatibility & Breaking Changes
- **Breaking Change**: Migration from `System.Web.Http` to `Microsoft.AspNetCore.Mvc`.
  - **Migration Path**: Replace controller classes that inherit from `ApiController` with classes inheriting from `ControllerBase`. Update routing attributes used in controllers to use attribute routing.
  
- **Breaking Change**: Entity Framework 6 to Entity Framework Core 7.0.
  - **Migration Path**: Update DbContext classes to inherit from `DbContext` in EF Core and refactor database queries to use EF Core syntax.

- **Breaking Change**: OWIN middleware authentication to built-in JWT authentication.
  - **Migration Path**: Implement `AddAuthentication` and `AddJwtBearer` methods in `Startup.cs` to configure JWT authentication.

## Key Flows (before vs after)
- **Flow 1: API Call Handling**
  - **Before**: Incoming HTTP request is handled through `WebApiConfig.cs` and routed to corresponding API controller methods.
  - **After**: Incoming HTTP request is processed through `Startup.cs`, utilizing endpoint routing and controller actions defined with attribute routing.

- **Flow 2: Database Access**
  - **Before**: Database interaction utilizes `DbContext` from Entity Framework 6 with synchronous calls.
  - **After**: Database access is handled through `DbContext` from Entity Framework Core 7.0, fully leveraging asynchronous programming features.

## Data Model Changes
| Class             | Change                           |
|-------------------|----------------------------------|
| ApplicationDbContext | Update from EF 6 to EF Core 7.0 |
| UserModel        | Adjust migration attributes and change configurations for EF Core alignment |

## Configuration Changes
- **Environment Variables**: 
  - `ASPNETCORE_ENVIRONMENT` should be set to `Development` or `Production` (no changes, existing variable name remains).
  
- **Config Files**: 
  - Update `appsettings.json`: Add section for JWT settings including `Issuer`, `Audience`, and `Key`.
  
- **Feature Flags**: 
  - N/A — not applicable to this task.