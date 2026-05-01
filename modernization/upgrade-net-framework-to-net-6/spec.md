# Software Modernization Specification Document

## Current State
- **Interfaces**: Existing APIs are built using .NET Framework 4.8, using standard ASP.NET MVC for web applications, and WebAPI for RESTful services.
- **Data Models**: The current data model relies on Entity Framework 6 with traditional SQL database connections.
- **Key Behaviours**: Application is stateful with session management using `System.Web.SessionState`. 

## Target State
- **Interfaces**: APIs will be transitioned to ASP.NET Core 6, enabling better performance with minimal middleware and an improved routing system.
- **Data Models**: Migration to Entity Framework Core 6 to utilize new features like LINQ improvements, better performance, and support for additional database types.
- **Key Behaviours**: Application will become stateless, utilizing JWT authentication for session management instead of traditional session state.

## Compatibility & Breaking Changes
1. **Framework Version Change**: 
   - **Breaking Change**: Transition from .NET Framework 4.8 to .NET 6.
   - **Migration Path**: 
     - Update all project files to SDK style.
     - Change target framework in the `.csproj` file:
       ```xml
       <TargetFramework>net6.0</TargetFramework>
       ```

2. **Entity Framework Migration**:
   - **Breaking Change**: Change from Entity Framework 6 to Entity Framework Core 6.
   - **Migration Path**:
     - Install EF Core packages.
     - Update `DbContext` and data model classes per EF Core conventions.
     - Modify LINQ queries where necessary to align with EF Core.

3. **Session State Handling**:
   - **Breaking Change**: Change from `System.Web.SessionState` to JWT authentication.
   - **Migration Path**:
     - Implement middleware for JWT token generation and validation.
     - Replace session management logic throughout the application.

## Key Flows (before vs after)
1. **User Authentication Flow**:
   - **Before**: User logs in -> Server validates credentials against stored session -> User is redirected based on session state.
   - **After**: User logs in -> Server generates JWT -> User receives JWT and uses it for subsequent requests to authenticate.

2. **Data Retrieval Flow**:
   - **Before**: WebAPI call -> Entity Framework 6 retrieves data from SQL database -> Data sent as HTTP response.
   - **After**: WebAPI call -> Entity Framework Core retrieves data from SQL database -> Data sent as HTTP response.

## Data Model Changes
| Entity                | Property Changes                                          |
|-----------------------|----------------------------------------------------------|
| User                  | Change `PasswordHash` to `string` from `byte[]`         |
| Product               | New property `IsActive` (boolean) for soft deletes       |
| Order                 | Remove `Status` as an enum and use string based status   |
| OrderItem             | Update relationships to accommodate EF Core conventions  |

## Configuration Changes
- **Environment Variables**:
    - Add `ASPNETCORE_ENVIRONMENT` to manage environment-specific configurations.

- **Feature Flags**:
    - New flags for enabling/disabling JWT authentication feature.

- **Config Files**:
    - Update `appsettings.json` to include new settings for JWT:
      ```json
      {
        "Jwt": {
          "Key": "YourSuperSecretKey",
          "Issuer": "YourIssuer",
          "Audience": "YourAudience",
          "ExpiryMinutes": 60
        }
      }
      ```