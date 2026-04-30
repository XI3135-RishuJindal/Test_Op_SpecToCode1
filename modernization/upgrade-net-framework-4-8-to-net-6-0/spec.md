# Specification Document for Software Modernization: Upgrade .NET Framework 4.8 to .NET 6.0

## Current State
- **Interfaces**: The application currently uses various .NET Framework 4.8 libraries, providing RESTful APIs via ASP.NET Web API. Common interfaces for authentication and data access are built on System.Web.
- **APIs**: The existing APIs are secured using Windows Authentication and implemented through controllers in System.Web.Mvc, with routing managed via the traditional Web API routing.
- **Data Models**: The application utilizes Entity Framework 6 for data access and relies on models defined using C# classes. Data annotations for validation and Entity Framework migrations are also in use.
- **Key Behaviours**: The application has synchronous methods for data access; long-running operations block the UI. It uses the old app.config configuration format and Newtonsoft.Json for handling JSON serialization.

## Target State
- **Interfaces**: The application will migrate to ASP.NET Core 6, using minimal APIs or controllers as needed. Authentication will be modernized, opting for JWT Bearer tokens instead of Windows Authentication.
- **APIs**: The APIs will be updated to follow the ASP.NET Core routing paradigm. There will be improvements in versioning strategy to support multiple API versions.
- **Data Models**: The data access layer will transition to Entity Framework Core, leveraging new features like efficient change tracking and improved LINQ capabilities.
- **Key Behaviours**: Shift from synchronous to asynchronous methods for data access, enhancing performance and user experience. Configuration will be handled through appsettings.json, simplifying management.

## Compatibility & Breaking Changes
1. **Breaking Change**: Migration from ASP.NET Web API to ASP.NET Core
   - **Migration Path**: Update existing controllers to use Microsoft.AspNetCore.Mvc, adapting the routing and action methods.
2. **Breaking Change**: Change in authentication mechanism
   - **Migration Path**: Implement JWT authentication using Microsoft.AspNetCore.Authentication.JwtBearer. Update user login flows to provide JWT tokens.
3. **Breaking Change**: Transition from Entity Framework 6 to Entity Framework Core
   - **Migration Path**: Replace data access logic, reconfigure DB context, and update migrations to use EF Core. Migrate from DbSet and LINQ expressions to compatible EF Core constructs.
4. **Breaking Change**: Change from app.config to appsettings.json
   - **Migration Path**: Convert configuration settings from XML format in app.config to JSON format in appsettings.json.

## Key Flows (before vs after)
1. **User Authentication**
   - **Before**: User sends credentials via form-based submission, server validates using Windows Authentication.
   - **After**: User submits credentials, server validates and issues a JWT token for subsequent requests.

2. **Data Retrieval**
   - **Before**: Client sends synchronous HTTP GET request, server retrieves data from EF6 and returns response.
   - **After**: Client sends asynchronous HTTP GET request, server retrieves data asynchronously using EF Core and returns response.

## Data Model Changes
| Existing Class/Schema                        | Updated Class/Schema                      |
|----------------------------------------------|-------------------------------------------|
| Entity Framework 6 DbContext                 | Entity Framework Core DbContext           |
| Data Annotations from System.ComponentModel.DataAnnotations | Data Annotations with Microsoft.EntityFrameworkCore.Metadata.Builders |
| Custom validation attributes                  | Utilize new FluentValidation package as an option for complex validation |

## Configuration Changes
- **app.config** will be replaced by **appsettings.json**:
  - Configuration keys (e.g., database connection strings) will need to be converted to the JSON format.
- **Feature Flags**: Introduce feature flags via the Microsoft.FeatureManagement library, replacing any old mechanism.
- **Environment Variables**: New environment variables such as `ASPNETCORE_ENVIRONMENT` will be required for the hosting environment.

      Note: Example:
      ```json
      {
          "ConnectionStrings": {
              "DefaultConnection": "YourConnectionString"
          },
          "Logging": {
              "LogLevel": {
                  "Default": "Information"
              }
          }
      }
      ```