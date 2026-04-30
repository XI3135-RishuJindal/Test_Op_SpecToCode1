# Software Modernization Design Document  
**Task:** Migrate Project Files to SDK-Style and Target .NET 8

---

## Architecture Overview

### Before Modernization
- Project files use the old (non-SDK-style) MSBuild format (`.csproj`, `.vbproj`, or analogous non-SDK project files)
- Target .NET Framework or earlier .NET Core versions (specific versions unknown)
- Build and deployment tools leverage legacy .NET build infrastructure (e.g., `packages.config`, separate assembly references, legacy NuGet, etc.)

### After Modernization
- All project files converted to SDK-style format
- Projects target `.NET 8` (LTS)
- Clean project file structure leveraging implicit package and SDK references
- Simplified transitive dependency management
- Modern build/deployment tooling fully compatible with .NET 8

---

## Migration Strategy

- **Approach:** Strangler Fig: Convert one project file at a time to SDK-style while maintaining compatibility with the existing solution/workspace.
- **Order:** Start with core libraries, then migrate application/entrypoint projects.
- **Build Validation:** Ensure each project builds both individually and as part of the complete solution after conversion.
- **Fallback:** Retain backups of old project files during migration for quick reversion if issues arise.

---

## Component Changes

| Component Type    | Change                                | Reason                                                 |
|-------------------|---------------------------------------|--------------------------------------------------------|
| Project Files     | Convert to SDK-style (`<Project Sdk="...">`), remove redundant configs.| Modern format, simpler syntax, maintainability, .NET 8 required.|
| Target Framework  | Change `<TargetFramework>` to `net8.0` | Move to latest LTS runtime, ensure security/support.   |
| Package References| Move from `packages.config` or `<Reference>` to SDK-style `<PackageReference>`| Simplifies dependency management.                      |
| Build Properties  | Remove obsolete/unsupported properties (e.g., explicit assembly info, binding redirects, etc.)| SDK-style projects infer most settings.                |
| Resource Inclusion| Migrate embedded resources, analyzers, content appropriately.| Maintain functionality in new SDK-style.               |
| Tooling           | Adjust for any build/deploy tools that leverage project format.| Ensure compatibility with new format.                  |

---

## Dependency Upgrade Plan

| Dependency                   | Current Version          | Target Version | Migration Notes                                         |
|------------------------------|-------------------------|----------------|--------------------------------------------------------|
| .NET runtime/framework       | Unknown (legacy/core)   | .NET 8        | Must ensure no deprecated APIs used in old codebase.   |
| NuGet Packages               | Various                 | Latest-Compatible| Validate compatibility with .NET 8, upgrade as needed.  |
| Microsoft.NET.Sdk            | Not used/implicit       | Latest        | Set `<Project Sdk="Microsoft.NET.Sdk">` in project file|
| 3rd-Party Tooling (if any)   | Unknown                 | N/A           | Review per-project; upgrade if required.               |

---

## CI/CD Pipeline Changes

- Update build runners/agents to use .NET 8 SDK.
- Update pipeline YAML/scripts to restore/build/test using `dotnet` CLI (e.g., `dotnet build`, `dotnet test`)
- Remove steps related to legacy project formats (e.g., `nuget restore` if all migrated to `<PackageReference>`)
- Ensure test runners target `.NET 8`
- Validate publish/package steps against new SDK-style build output.

---

## Infrastructure Changes

- **Build Agents:** Must have .NET 8 SDK/runtime installed.
- **Docker/Containers:** Update Dockerfiles to use base images with .NET 8 (e.g., `mcr.microsoft.com/dotnet/aspnet:8.0`).
- **Cloud Deployment:** N/A — not applicable to this task unless deployment process is tightly coupled to old framework.

---

## Rollback Plan

- Commit/preserve backups of legacy project files before migration.
- Migration per-project: revert individual SDK-style `.csproj` files to their previous versions if issues occur.
- Store migration changes as discrete commits or branches in version control for easy rollback.
- If builds fail post-migration, restore the old project files and retarget CI build agents to previous .NET version.

---

## Testing Strategy

- **Unit Tests:** Run full suite pre- and post-migration to ensure functional parity.
- **Integration Tests:** Execute after all dependencies are upgraded and project builds successfully on .NET 8.
- **Regression Tests:** Compare build, deployment, and runtime behaviors between old and new versions.
- **Performance Tests:** Optional — execute baseline checks to ensure .NET 8 migration does not affect performance.
- **Manual Validation:** For components where automated tests are not exhaustive, run targeted manual tests for critical scenarios.

---

*End of document.*