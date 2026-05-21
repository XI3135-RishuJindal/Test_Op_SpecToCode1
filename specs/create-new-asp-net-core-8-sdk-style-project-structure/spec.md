# Spec: Create New ASP.NET Core 8 SDK-Style Project Structure

## Summary

This spec covers the creation of a new ASP.NET Core 8 SDK-style project structure as part of a modernization effort. The expected outcome is a clean, standards-compliant project layout using the modern SDK-style `.csproj` format targeting `net8.0`, replacing or superseding any legacy project structure currently in use. This establishes the foundation upon which subsequent migration and upgrade work will be layered.

## Motivation

- **Modernization baseline:** The existing project structure is not confirmed to use SDK-style project files, which are required for full compatibility with modern .NET tooling, NuGet package management, and CI/CD pipelines.
- **ASP.NET Core 8 target:** ASP.NET Core 8 is the current Long-Term Support (LTS) release of .NET, providing extended support and access to current platform features.
- **Upgrade urgency:** Rated **medium** — the project is not in an immediate crisis state, but delaying structural modernization increases the cost of future upgrades and tooling compatibility work.
- **Tech debt reduction:** The legacy project format (if applicable) carries tooling friction, limits cross-platform build support, and restricts the use of modern SDK features such as implicit `using` directives, nullable reference types, and central package management.
- **Compliance and supportability:** Targeting a supported LTS runtime ensures the project remains eligible for security patches and vendor support.

> **Note:** Specific CVEs, EOL dates for the current runtime, and the existing build tool are marked TODO due to absent context in the provided tech analysis.

## Current State

The current project structure details are largely unconfirmed from the provided context. The following represents what is known and what is unknown:

| Attribute | Current Value |
|---|---|
| Language | TODO — not specified in tech analysis |
| Runtime / Target Framework | TODO — not specified in tech analysis |
| Build Tool | TODO — not specified in tech analysis |
| Project File Format | TODO — SDK-style vs. legacy `.csproj` unconfirmed |
| Existing NuGet references style | TODO — `packages.config` vs. `PackageReference` unconfirmed |
| Solution file structure | TODO — number and layout of projects unconfirmed |
| Existing startup/host model | TODO — `Startup.cs` pattern vs. minimal hosting unconfirmed |
| Configuration keys / `appsettings` schema | TODO — not provided in context |
| Key classes / interfaces affected | TODO — not provided in context |

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Project file format | TODO (legacy or unconfirmed format) | SDK-style `.csproj` targeting `net8.0` | TODO |
| Target framework moniker (TFM) | TODO | `net8.0` | Y — if TFM changes, runtime behavior and available APIs change |
| NuGet package reference style | TODO (`packages.config` or unconfirmed) | `PackageReference` in SDK-style `.csproj` | Y — if migrating from `packages.config` |
| Host/startup model | TODO (`Startup.cs` or unconfirmed) | ASP.NET Core 8 minimal hosting model or retained `Startup.cs` pattern (see Open Questions) | TODO |
| Solution structure | TODO | Organized SDK-style solution with updated `.sln` file | N (structural only) |
| Implicit usings | TODO | Enabled via SDK-style project property | N |
| Nullable reference types | TODO | Enabled via SDK-style project property | TODO — may surface new warnings/errors |
| Assembly and package metadata | TODO (may be in `AssemblyInfo.cs`) | Consolidated into SDK-style `.csproj` properties | N — if `AssemblyInfo.cs` is removed, duplication errors must be resolved |

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| Target framework change (if TFM is being upgraded) | APIs removed or changed between old TFM and `net8.0` may cause compile or runtime errors | TODO — requires full API compatibility audit once current TFM is confirmed |
| `packages.config` → `PackageReference` | Package resolution behavior differs; transitive dependencies become implicit | All packages must be re-evaluated; `packages.config` file removed; restore behavior validated |
| `AssemblyInfo.cs` attributes duplicated by SDK auto-generation | Build errors due to duplicate assembly attributes | Auto-generated attributes must be suppressed or `AssemblyInfo.cs` removed/trimmed |
| Nullable reference types enabled | Existing code may produce new warnings or errors | Warnings should be reviewed; suppression or code fixes applied incrementally |
| Startup model change (if applicable) | `Startup.cs`-based configuration wiring may not directly translate | TODO — migration path depends on confirmed current host model |
| Any removed or renamed NuGet packages targeting older frameworks | Compile-time or runtime failures | TODO — requires package compatibility check once current dependencies are confirmed |

## Acceptance Criteria

1. **Given** the repository is checked out on a clean machine with the .NET 8 SDK installed, **when** the solution is built using the standard build command, **then** the build completes with zero errors.

2. **Given** the new SDK-style `.csproj` files are in place, **when** the target framework is inspected, **then** all application projects target `net8.0` exclusively.

3. **Given** the project file format has been updated, **when** the `.csproj` files are examined, **then** they conform to SDK-style format (i.e., contain the `Sdk="Microsoft.NET.Sdk.Web"` or equivalent attribute) and contain no legacy `<Import>` references to `Microsoft.CSharp.targets` or `Microsoft.WebApplication.targets`.

4. **Given** NuGet references have been migrated, **when** the solution directory is inspected, **then** no `packages.config` file exists and all package references appear as `<PackageReference>` elements within `.csproj` files.

5. **Given** the new project structure is in place, **when** `dotnet restore` is executed, **then** all packages restore successfully with no errors or unresolved dependencies.

6. **Given** the application project is built, **when** the output is inspected, **then** no duplicate assembly attribute errors are present (confirming `AssemblyInfo.cs` conflicts are resolved).

7. **Given** the application is built and run in a local development environment, **when** the application starts, **then** it reaches a healthy/ready state without runtime exceptions on startup.

8. **Given** the CI pipeline is configured, **when** a pull request is opened against the main branch, **then** the build and restore steps complete successfully in CI using the .NET 8 SDK.

9. **Given** nullable reference types are enabled in the project, **when** the project is built, **then** the build produces zero nullable-related **errors** (warnings are tracked separately and addressed incrementally per team agreement).

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current language version and runtime/TFM being used? This is required to assess the full scope of breaking changes. | TODO | TODO |
| 2 | Is the current project format legacy `.csproj` (non-SDK), SDK-style, or something else (e.g., `.vbproj`, website project)? | TODO | TODO |
| 3 | What is the current build tool (MSBuild version, `dotnet` CLI, Visual Studio version)? | TODO | TODO |
| 4 | Should the new structure adopt the ASP.NET Core 8 minimal hosting model, or retain the `Startup.cs` pattern for this phase of work? | TODO | TODO |
| 5 | Are there multiple projects in the solution? If so, what is the dependency graph and which projects are in scope for this task? | TODO | TODO |
| 6 | Is Central Package Management (CPM / `Directory.Packages.props`) in scope for this task or deferred? | TODO | TODO |
| 7 | Are there any existing CI/CD pipeline definitions that must be updated to reference the new project structure or SDK version? | TODO | TODO |
| 8 | Are there any platform-specific constraints (e.g., Windows-only APIs, IIS hosting requirements) that affect the SDK or TFM choice? | TODO | TODO |
| 9 | What is the agreed policy for nullable reference type warnings — treat as errors, suppress, or fix incrementally? | TODO | TODO |