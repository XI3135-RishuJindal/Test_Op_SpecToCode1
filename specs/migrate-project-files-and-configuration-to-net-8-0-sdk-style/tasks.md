## Prerequisites

- [ ] [XS] Verify access to the repository containing all .csproj and solution files
- [ ] [XS] Install .NET 8.0 SDK (ensure version 8.0.x is present)
- [ ] [XS] Install compatible IDE tooling (e.g., Visual Studio 2022 17.8+, Rider 2023.3+, VS Code with C# extension)
- [ ] [XS] Ensure write permissions for updating project and configuration files

## Phase 1 — Preparation

- [ ] [XS] Create branch `feature/dotnet8-sdk-projects` from latest main
- [ ] [XS] Capture current list of all .csproj, .sln, and configuration files
- [ ] [XS] Capture current output of `dotnet build` and `dotnet test` for reference

## Phase 2 — Core Upgrade

- [ ] [M] Migrate all .csproj files to SDK-style format for .NET 8.0
- [ ] [S] Update each .csproj `<TargetFramework>` property to `net8.0`
- [ ] [XS] Remove obsolete or incompatible properties (e.g., `<PackagesConfig>`, `<ProjectTypeGuids>`) in .csproj files
- [ ] [XS] Update solution (.sln) files to reference SDK-style .csproj files as needed
- [ ] [XS] Review and, if found, update global.json to reference .NET 8.0 SDK

## Phase 3 — Testing & Validation

- [ ] [S] Run `dotnet restore`, `dotnet build`, and `dotnet test` for all upgraded projects
- [ ] [XS] Compare build/test output to pre-migration baseline for regressions
- [ ] [XS] Validate applications start and run under .NET 8.0 (manual or smoke test)

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline configuration files (e.g., .github/workflows/ci.yml) to use `dotnet 8.0.x`
- [ ] [XS] If present, update Dockerfile `FROM` statements to use `mcr.microsoft.com/dotnet/aspnet:8.0` or `mcr.microsoft.com/dotnet/runtime:8.0`
- [ ] [XS] Validate successful CI build and test with .NET 8.0 pipeline

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update README.md with supported .NET version and migration summary
- [ ] [XS] Add migration notes to CHANGELOG.md
- [ ] [XS] Review and update any internal deployment/runbooks with .NET 8.0 specifics
- [ ] [XS] Monitor post-deployment logs for startup/runtime failures on .NET 8.0

---

**Notes:**  
- N/A — not applicable to this task: No runtime, application code, or library-specific upgrade tasks included due to lack of context.  
- N/A — not applicable to this task: No framework or build tool migration tasks outside of project file format and .NET 8.0 configuration.