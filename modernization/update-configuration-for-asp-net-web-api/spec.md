# Software Modernization Specification Document

## Current State
The existing ASP.NET Web API application utilizes a legacy configuration system based on `Web.config` files. Configuration settings, such as connection strings and application settings, are tightly coupled with the application and require recompiling for any changes. This configuration is managed through XML, leading to difficulties in readability and manageability. Current versions of ASP.NET Web API are not leveraging .NET Core’s `appsettings.json` or the dependency injection pattern for configurations.

## Target State
Post-modernization, the ASP.NET Web API will adopt the `appsettings.json` configuration model. This will store configuration settings in a more structured JSON format. The application will also utilize .NET Core Dependency Injection for managing configuration settings, allowing settings to be injected into services/classes. The application will be upgraded to .NET 6, which is supported until November 2024. Key configurations will include:

- `appsettings.json` for application settings.
- Connection strings stored in `ConnectionStrings` section.
- Environment-specific settings managed through `appsettings.Development.json` or `appsettings.Production.json`.

## Compatibility & Breaking Changes
1. **Configuration Source Change**: 
   - **Old**: XML-based `Web.config`.
   - **New**: JSON-based `appsettings.json`.
   - **Migration Path**: 
     - Convert all settings from `Web.config` to `appsettings.json`. 
     - Use the .NET Core Configuration API in Startup.cs to replace any usage of `ConfigurationManager`.

2. **Dependency Injection Introduction**: 
   - **Old**: Manual instantiation of services.
   - **New**: Services configured via `Startup.cs` and injected across the app.
   - **Migration Path**: 
     - Identify all service instantiation points and refactor to receive dependencies through constructors.

3. **ASP.NET Version Upgrade**:
   - **Old**: Target framework is .NET Framework 4.x.
   - **New**: Target framework is .NET 6.
   - **Migration Path**: Update all project files to .NET 6, ensuring compatibility with existing code.

## Key Flows (before vs after)
1. **Loading Configuration**:
   - **Before**: 
     1. Application starts and invokes `ConfigurationManager.AppSettings["SettingName"]`.
   - **After**: 
     1. Application starts and reads configuration from `appsettings.json` using:
        ```csharp
        var setting = Configuration["SettingName"];
        ```

2. **Service Creation**:
   - **Before**: 
     1. Instantiate a service directly in the controller.
   - **After**: 
     1. Inject service via constructor:
        ```csharp
        private readonly MyService _myService;

        public MyController(MyService myService)
        {
            _myService = myService;
        }
        ```

## Data Model Changes
N/A — not applicable to this task

## Configuration Changes
- **Configuration Files**:
  - Remove `Web.config`.
  - Add `appsettings.json` and `appsettings.Development.json`.
  
- **Configuration Keys**:
  - Migrate keys from:
    - `Web.config -> appsettings.json` 
  - Example mapping:
    ```json
    {
      "ConnectionStrings": {
        "DefaultConnection": "Server=myServer;Database=myDB;User Id=myUser;Password=myPass;"
      },
      "ApiSettings": {
        "ApiKey": "12345-abcde"
      }
    }
    ```

- **Environment Variables**: 
   - Introduce the use of environment-specific settings to maintain different configurations for Development and Production environments. 

- **Feature Flags**: 
   - This is not applicable unless explicitly defined in context to features being controlled in settings.