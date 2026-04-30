# Swashbuckle.AspNetCore Migration & Reconfiguration — Design Document

## Architecture Overview

**Before Migration**  
- OpenAPI/Swagger documentation is generated via an unknown mechanism. Existing implementation details, such as which package or tool is used for Swagger/OpenAPI documentation, are unspecified.
- Swagger UI and JSON may be exposed at default or non-configurable endpoints.
- Swagger/OpenAPI configuration is potentially minimal or not aligned with modern practices.

**After Migration**  
- Documentation and UI are generated and served via [Swashbuckle.AspNetCore](https://github.com/domaindrivendev/Swashbuckle.AspNetCore), a modern, official OpenAPI generator for ASP.NET Core.
- Endpoints for Swagger JSON and Swagger UI are explicitly configured as per current best practices.
- Enhanced customization and extensibility for headers, doc comments, versioning, security schemes, etc.
- Improved maintainability and upgrade path for future versions of .NET and ASP.NET Core.

---

## Migration Strategy

- **Strangler Fig Pattern:**  
  Introduce Swashbuckle.AspNetCore alongside the existing Swagger/OpenAPI implementation.
  - Initially, both Swagger endpoints exist in parallel (if feasible), ensuring current consumers are unaffected.
  - Once Swashbuckle.AspNetCore is fully configured and tested, decommission the legacy Swagger/OpenAPI implementation and remove associated dependencies.
  - Fully migrate to Swashbuckle.AspNetCore for all OpenAPI/Swagger documentation.

---

## Component Changes

| Component                          | Changes                                                        | Reason                               |
|-------------------------------------|----------------------------------------------------------------|--------------------------------------|
| API Project Startup/Program/Config  | Add and configure Swashbuckle.AspNetCore services and middleware. Replace or reconfigure existing Swagger/OpenAPI setup. | Enable and customize modern Swagger integration. |
| Dependency Management (csproj)      | Add Swashbuckle.AspNetCore NuGet package. Remove/outdate legacy Swagger/OpenAPI dependencies. | Ensure up-to-date, supported package usage. |
| Documentation Annotations           | Optionally, introduce or update XML comments, attribute decorations, or code annotations for improved doc generation. | Leverage Swashbuckle capabilities for richer docs. |
| Swagger UI Endpoint                 | Ensure endpoint(s) are aligned with new configuration (typically `/swagger`). | Unified, predictable docs browsing. |
| Security Scheme Docs                | Migrate and/or update security definitions in OpenAPI to Swashbuckle syntax. | Accurate depiction of API security expectations. |

---

## Dependency Upgrade Plan

| Dependency                     | Current Version    | Target Version      | Migration Notes                        |
|---------------------------------|-------------------|---------------------|----------------------------------------|
| Swashbuckle.AspNetCore          | N/A – not present | Latest stable (e.g. 6.5.0; verify at migration time) | Must add package via NuGet.           |
| Existing Swagger/OpenAPI tool   | Unknown           | N/A (to remove)     | Identify and remove from project file. |

---

## CI/CD Pipeline Changes

- Update `dotnet build` to ensure it restores and builds the new Swashbuckle.AspNetCore dependency.
- If there are steps to publish Swagger JSON (e.g., artifact storage), adjust the path to the Swashbuckle-generated doc.
- Remove publish/test steps related to obsolete Swagger/OpenAPI package/tool.
- Optionally, add automation to validate that the Swagger endpoint returns valid OpenAPI schema as part of CI test suite.

---

## Infrastructure Changes

N/A — not applicable to this task

---

## Rollback Plan

- Retain the original Swagger/OpenAPI implementation until Swashbuckle.AspNetCore is verified in deployment.
- If the migration causes issues, restore the previous configuration (including package references and middleware), and disable Swashbuckle.AspNetCore via commenting out/removal from `Startup.cs`/`Program.cs`.
- Rollback can be performed by reverting migration commits, as both sets of dependencies and configurations are clearly isolated.

---

## Testing Strategy

- **Unit Tests:**  
  N/A — not applicable to this task (Swagger configuration typically not covered by unit tests).

- **Integration Tests:**  
  - Ensure `/swagger/v1/swagger.json` (and other configured endpoints) return expected OpenAPI output (status 200, valid JSON).
  - Validate Swagger UI loads and provides correct, navigable documentation.

- **Regression Tests:**  
  - Compare endpoint definitions, descriptions, and security schemes between legacy Swagger/OpenAPI and Swashbuckle output for breaking or missing changes.
  - Confirm that all publicly documented endpoints remain visible and accurate.

- **Performance Tests:**  
  N/A — not applicable to this task (Swagger UI generation has negligible performance impact in most cases).

---

# End of Design Document