# Specification: Migrating Project Files to .NET 8 SDK Style

## Current State

- **Project File Format:** Legacy project file format (`.csproj`, `.vbproj`, `.fsproj`), likely pre-SDK-style (pre-.NET Core 1.0, e.g., targeting .NET Framework 4.x).
- **Structure:** Project files may include:
    - `<Compile Include=... />`, `<Reference Include=... />`, and explicit file references.
    - Custom build and import steps, possibly XAML or manually managed file lists.
    - Targeting via `<TargetFrameworkVersion>`, such as "v4.6.2".
- **Key Behaviours:**
    - Tight coupling to MSBuild and/or Visual Studio.
    - NuGet packages restored via `packages.config` or via explicit package references.
    - Limited multi-target support.
    - Bulky project files, hard to diff and maintain.
- **Interfaces/APIs:** N/A — project file format only, not runtime code or APIs.
- **Data Models:** N/A — project file only.

## Target State

- **Project File Format:** Modern .NET 8 SDK-style project files (attribute-based, minimal, e.g., constructed around `<Project Sdk="Microsoft.NET.Sdk">`).
- **Structure:**
    - File inclusions are implicit (all code files in project folder included by default).
    - References via `<PackageReference>`, `<ProjectReference>`, `<FrameworkReference>`.
    - `<TargetFramework>net8.0</TargetFramework>` or `<TargetFrameworks>` for multi-target builds.
    - Clean, minimal project files, easier to maintain and review.
- **Build Tool:** Compatible with `dotnet build`/`dotnet run`.
- **Interfaces/APIs:** N/A — not affected.
- **Data Models:** N/A — not affected.

## Compatibility & Breaking Changes

- **Target Framework Change:**
    - **Breaking:** Upgrading from .NET Framework or older .NET Core/.NET Standard versions to `net8.0`.
    - **Migration:** Ensure all dependencies support .NET 8; update code where necessary to account for removed/changed APIs.
- **Project File Format:**
    - **Breaking:** Old MSBuild extensions or legacy NuGet workflows (`packages.config`) are not supported.
    - **Migration:** Migrate NuGet package references to `<PackageReference>`.
- **Implicit File Inclusion:**
    - **Breaking:** Custom, non-standard file inclusion/exclusion logic may break if not explicitly reconfigured with `<ItemGroup Remove=...>`.
    - **Migration:** Use `<Compile Remove=...>`, `<None Remove=...>`, or `<Content Remove=...>` as needed.
- **Global Imports:**
    - **Breaking:** Global imports, custom build logic or legacy `.targets`/`.props` files not supported natively.
    - **Migration:** Refactor customizations into supported SDK targets, or find alternatives.

## Key Flows (before vs after)

### Build & Package Flow

**Current State (before):**
1. Developer invokes build via Visual Studio or `msbuild MyProject.csproj`.
2. Project file explicitly lists all source files and references.
3. Dependencies restored via `packages.config` or manual process.
4. Output and build artefacts generated.

**Target State (after):**
1. Developer invokes build via `dotnet build` or Visual Studio.
2. SDK-style project implicitly includes all relevant source files.
3. Dependencies restored via `<PackageReference>` during `dotnet build` or `dotnet restore`.
4. Output generated according to modern .NET conventions.

## Data Model Changes

N/A — not applicable to this task.

## Configuration Changes

- **Environment Variables:** N/A — not applicable to this task.
- **Feature Flags:** N/A — not applicable to this task.
- **Config Files:**
    - **Project File:** `.csproj`/`.fsproj`/`.vbproj` updated to SDK-style format.
    - **NuGet Package References:** Migration from `packages.config` to `<PackageReference>` in the project file.
    - **TargetFramework:** Set to `net8.0` in project file.
    - **Custom Build Logic:** Any custom steps from old project file must be ported or replaced using supported SDK properties and targets.

---

End of specification.