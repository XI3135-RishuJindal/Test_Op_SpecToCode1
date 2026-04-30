# SPEC: Migrate and Reconfigure OpenAPI/Swagger Using Swashbuckle.AspNetCore

---

## Current State

### Existing Interfaces and APIs
- OpenAPI/Swagger documentation is currently enabled, but the implementation details (e.g., version of Swashbuckle.AspNetCore, configuration style) are **unknown**.
- Possible current use of legacy configurations, such as:
  - Swagger 2.0 definitions (`swagger.json`)
  - Nonstandard endpoints for docs (e.g., `/api-docs`)
  - Minimal or generic API info (title, version, contact details, etc.)
- Existing code may register Swagger in `Startup.cs` (for .NET Core 3.x or earlier) or in `Program.cs` (for .NET 6+ minimal APIs).

### Data Models and Key Behaviours
- API documentation may lack annotations, security, or additional metadata (descriptions, summaries, examples).
- No confirmation of support for custom operations, XML comments, complex authentication flows, or versioned docs.

---

## Target State

### New Interfaces and APIs
- Use **Swashbuckle.AspNetCore** version 6.x or higher (preferably latest stable).
- Documentation exposed at `/swagger/{documentName}/swagger.json` and UI at `/swagger`.
- API information enriched with:
  - Title
  - Version
  - Description
  - (Optional) Contact, License, etc.
- Integration with annotated XML comments (if present in project).
- Support for OAuth2/ApiKey/Basic authentication schemes as required.
- If multiple API versions exist, grouped documentation per version.
- Consistent configuration using latest .NET dependency injection, typically in `Program.cs`.
- Custom operation filters or schema filters implemented via latest middleware pattern (as needed).

---

## Compatibility & Breaking Changes

| Change Description                    | Breaking? | Migration Path                                                 |
|----------------------------------------|----------|---------------------------------------------------------------|
| New Swashbuckle version                | Yes      | Update NuGet package to Swashbuckle.AspNetCore 6.x or higher. |
| Configuration moved to `Program.cs`    | Yes      | Migrate from `Startup.cs` service/register code to new style. |
| Changed default endpoints              | Yes      | Update docs/UI URLs from e.g., `/swagger.json` to `/swagger/v1/swagger.json` and `/swagger`. |
| Enhanced/stricter schema generation    | Yes      | Add missing annotations, resolve validation warnings.          |
| Security schemes require redefinition  | Yes      | Explicitly define security schemes in new Swashbuckle config.  |

---

## Key Flows (before vs after)

### 1. Setting Up Swagger in the Application

**Before (possible, existing):**
1. Add Swashbuckle package to project (unknown version).
2. In `Startup.cs`, call `services.AddSwaggerGen()` in `ConfigureServices`.
3. In `Configure`, call `app.UseSwagger()` and `app.UseSwaggerUI()`.
4. Minimal configuration; default info used.

**After (target, Swashbuckle.AspNetCore 6+):**
1. Add/upgrade Swashbuckle.AspNetCore (6.x+) NuGet package.
2. In `Program.cs` (for .NET 6+), call `builder.Services.AddSwaggerGen(options => { ... })`.
   - Configure API info (title, version, description, etc.).
   - Optionally, configure security schemes, operation filters.
   - Integrate XML comments via `options.IncludeXmlComments(path)`.
3. Call `app.UseSwagger()` and `app.UseSwaggerUI(options => { ... })` in the proper pipeline sequence.
4. Enhanced documentation and custom UI endpoint (e.g., at `/swagger`).

### 2. Accessing the Swagger UI

**Before:**
- User accesses UI at `/swagger` or possibly custom endpoint.

**After:**
- User accesses UI at `/swagger` by default.
- OpenAPI JSON is available at `/swagger/v1/swagger.json`.

---

## Data Model Changes

N/A — not applicable to this task

---

## Configuration Changes

- NuGet package reference updated to `Swashbuckle.AspNetCore` version 6.x or newer.
- Swagger configuration now performed in `Program.cs` (for .NET 6+), using the modern dependency injection APIs.
- Default endpoints for documentation are standardized to `/swagger` and `/swagger/v1/swagger.json`.
- Environment variable and application setting changes:
  - If gating Swagger, use feature flag (e.g., `ENABLE_SWAGGER=true`) or configure in `appsettings.json`.
  - To use XML comments, ensure `GenerateDocumentationFile` is set in `.csproj`.

---

## Notes

- Actual migration specifics may vary depending on existing codebase structure.
- This specification does **not** cover runtime/.NET Core major version upgrades or refactors unrelated to Swashbuckle/OpenAPI documentation.