# Modernization_Service.Tasks

## Prerequisites

- [ ] [S] Ensure access to all source repositories containing existing .NET project files (*.csproj, *.vbproj, etc.)
- [ ] [XS] Verify developer workstations are equipped with .NET 8 SDK
- [ ] [XS] Install latest IDE compatibility (e.g., Visual Studio 2022 or Rider with .NET 8 support)

## Phase 1 — Preparation

- [ ] [S] Inventory all existing project files to be migrated
- [ ] [XS] Identify and list all non-SDK style project files (pre-SDK csproj, vbproj, etc.)
- [ ] [XS] Create a backup branch for all targeted repositories/projects prior to migration

## Phase 2 — Core Upgrade

- [ ] [M] Convert each project file to .NET 8 SDK-style format (one PR per project file)
- [ ] [S] Update TargetFramework to net8.0 in each project file
- [ ] [S] Remove legacy/obsolete msbuild properties incompatible with SDK style
- [ ] [M] Migrate NuGet package references to <PackageReference> format where needed
- [ ] [S] Validate and refactor any post-build and pre-build event settings to equivalent SDK MSBuild properties

## Phase 3 — Testing & Validation

- [ ] [S] Restore and build each migrated project with dotnet build to verify successful conversion
- [ ] [M] Run existing automated and/or manual tests to ensure functional parity with pre-migration build

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update build pipelines (YAML/scripts) to use dotnet CLI commands and target net8.0
- [ ] [S] Verify build agent images support .NET 8 and required language support

## Phase 5 — Documentation & Rollout

- [ ] [XS] Document the migration process in CHANGELOG or MIGRATION.md
- [ ] [XS] Communicate upgrade steps and impacts to relevant stakeholders

## Post-Migration Cleanup

- [ ] [XS] Remove deprecated config files or scripts made obsolete by SDK-style conversion
- [ ] [XS] Delete backup branches after confirming successful migration and stabilization

---

_Note: Only tasks directly relevant to migration to .NET 8 SDK-style project files are included. All other section content is:_

N/A — not applicable to this task