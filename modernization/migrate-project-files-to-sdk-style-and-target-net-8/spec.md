# SPEC: Migrate Project Files to SDK-Style and Target .NET 8

## Current State

The following elements are relevant for the migration to SDK-style projects and targetting .NET 8:

- **Project Files**: Currently use the old "non-SDK-style" (classic) .csproj, .vbproj, or .fsproj formats.
    - Typically verbose, explicit `<Compile Include=... />`, manual package and framework references.
    - `TargetFrameworkVersion` typically set to `.NET Framework` versions (e.g., v4.7.2) or earlier .NET Core versions.
- **APIs & Interfaces**: N/A — not applicable to this task.
- **Data Models**: N/A — not applicable to this task.
- **Key Behaviours**:
    - Build and publish processes rely on legacy project file settings.
    - May use older configurations for NuGet, references, or custom build events.

## Target State

- **Project Files**: Convert all project files to the SDK-style format.
    - Top-level `<Project Sdk="Microsoft.NET.Sdk">` or variant (`Microsoft.NET.Sdk.Web`, etc.)
    - Implicit includes for sources and resources, simple dependency declarations.
    - Simplified and modernized property usage.
    - Remove unnecessary explicit `<Compile>`, `<None>`, `<Content>`, and `<Reference>` items if possible.
    - Remove or migrate any legacy build events and packaging steps.
- **Target Framework**: 
    - Use `TargetFramework` or `TargetFrameworks` set to `net8.0`.
- **APIs & Interfaces**: N/A — not applicable to this task.
- **Data Models**: N/A — not applicable to this task.

## Compatibility & Breaking Changes

| Breaking Change                                                   | Migration Path / Mitigation                                                                             |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Projects no longer compatible with .NET Framework or older targets | Ensure all code dependencies are compatible with .NET 8. Update/rewrite any incompatible APIs/usages.  |
| Obsolete or unsupported NuGet packages                            | Identify incompatible packages and update or replace with .NET 8-compliant versions.                   |
| Build customizations/scripts may not transfer directly             | Refactor custom build logic as necessary to use new targets/hooks or separate MSBuild props/targets.   |
| IDE/tooling requirements: Visual Studio 2022 17.8+ or .NET 8 CLI  | Update developer environments to use compatible tools.                                                 |

## Key Flows (before vs after)

### Build & Run

#### Before (Classic Project)

1. Open .csproj file in Visual Studio or msbuild.
2. Build using old-style configuration; dependencies and files must be explicitly managed.
3. May require older Visual Studio/MSBuild.

#### After (SDK-Style Project, .NET 8)

1. Open SDK-style project in Visual Studio 2022 17.8+ or use `dotnet` CLI.
2. Build is simplified; sources/resources are implicitly included.
3. Uses up-to-date dependency resolution and modern build features.
4. Targets only .NET 8 unless otherwise specified.

## Data Model Changes

N/A — not applicable to this task.

## Configuration Changes

- **Project File Properties**:
    - Switch from `TargetFrameworkVersion` (e.g. `v4.7.2`) or legacy multi-targeting to `TargetFramework` (e.g. `net8.0`).
    - Top-line switches to `<Project Sdk="...">`.
    - Remove or update legacy build events (`<PreBuildEvent>`, `<PostBuildEvent>`), instead use modern MSBuild targets/hooks as needed.
- **Environment Variables**: N/A — not applicable to this task.
- **Feature Flags**: N/A — not applicable to this task.
- **Config Files**: 
    - Review `Directory.Build.props`, `Directory.Build.targets` for cross-project configuration that may reference outdated settings; update as needed.

---

**End of SPEC**