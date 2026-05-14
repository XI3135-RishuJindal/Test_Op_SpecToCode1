# .NET 8 SDK-Style Project File Migration — Design Document

## Architecture Overview

**Before:**  
Project files are not using the .NET SDK-style format (could be legacy .csproj/.vbproj/.fsproj, possibly referencing packages with `<packages.config>`, explicit file inclusions, verbose configuration).

**After:**  
All project files migrated to .NET 8 SDK-style format:
- Concise, clean project files.
- Implicit file inclusions.
- Package references consolidated with `<PackageReference>`.
- Utilization of new SDK capabilities (multi-targeting, simplified properties).
- Aligned with modern .NET build and tooling support.

---

## Migration Strategy

Chosen approach: **Strangler Fig Pattern (Incremental Migration)**

- Migrate one project file at a time.
- Each migration is self-contained and followed by a build/test verification.
- Minimize risk by isolating changes and enabling rapid rollback.
- Continue regular development work in parallel, resolving any merge issues case-by-case.

---

## Component Changes

### Project Files (.csproj/.vbproj/.fsproj)
- **What changes:**  
  - Convert format to SDK style (add `Sdk="Microsoft.NET.Sdk"` at top).
  - Remove explicit file lists (`<Compile Include=...>` and `<Content Include=...>`) in favor of implicit inclusion.
  - Replace `<packages.config>` with `<PackageReference>` items in the project file.
  - Remove obsolete build properties/settings incompatible with .NET SDK-style projects.
  - Ensure target framework(s) is updated to `net8.0`, or multi-target as required.
- **Why:**  
  - Required to leverage .NET 8 features and modern tooling.
  - Simplifies project files and maintenance.
  - Enables improved build performance and dependency management.

### Build Scripts
- **What changes:**  
  - Update any references to old project file structure or custom MSBuild targets/tasks.
  - Remove or replace with tasks compatible with SDK-style format.
- **Why:**  
  - Ensures existing automation works with new project file style.

---

## Dependency Upgrade Plan

| Dependency         | Current Version | Target Version | Migration Notes                                      |
|--------------------|----------------|---------------|------------------------------------------------------|
| .NET SDK           | Unknown        | 8.0           | All projects standardized to .NET 8 SDK              |
| NuGet Packages     | Unspecified    | Latest Stable | Upgrade as needed to versions compatible with .NET 8  |
| MSBuild/TFS Tasks  | Unknown        | Compatible    | Replace legacy targets/tasks with SDK-style ones      |

_Note: Complete the table during the migration process as specific dependencies are discovered._

---

## CI/CD Pipeline Changes

- Update build agents/environments to use .NET 8 SDK.
- Update build/test script paths to point to SDK-style project files.
- Remove steps related to `<packages.config>` restore (nuget.exe); rely on `dotnet restore`.
- Update any deployment scripts to expect modern build output directory structure.
- Validate test and code coverage tools are compatible with .NET 8 projects.

---

## Infrastructure Changes

- Upgrade build servers/containers to install .NET 8 SDK.
- Update Dockerfiles (if present) to use `mcr.microsoft.com/dotnet/sdk:8.0` for build and `mcr.microsoft.com/dotnet/aspnet:8.0` for runtime if relevant.

---

## Rollback Plan

- Commit each project migration separately in version control.
- To revert:  
  - Roll back specific commit(s) that apply SDK-style migration.
  - Restore original project files from source control.
  - Restore previous CI/CD settings and build environment if necessary.

---

## Testing Strategy

- **Unit Tests:**  
  - Ensure all unit tests pass after each project file migration.
- **Integration Tests:**  
  - Run integration tests as part of the build to catch issues arising from project reference/package changes.
- **Regression Testing:**  
  - Compare build artifacts and test outputs before and after migration.
- **Performance Testing:**  
  - Optional unless builds become significantly slower; monitor build time briefly.

---

## Out-of-Scope Sections

### Frameworks
N/A — not applicable to this task

### Application Runtime Changes
N/A — not applicable to this task

### Application Logic or Module Refactoring
N/A — not applicable to this task

### Data Storage/Database Migration
N/A — not applicable to this task

### User-Facing Feature Changes
N/A — not applicable to this task

---

**End of Design Document.**