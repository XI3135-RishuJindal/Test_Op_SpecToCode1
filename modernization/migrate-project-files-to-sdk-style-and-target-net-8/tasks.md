# TASKS: Migrate Project Files to SDK-Style and Target .NET 8

## Prerequisites

- [ ] [XS] Confirm .NET 8 SDK is installed and available for all development and CI environments  
- [ ] [S] Inventory all project files (*.csproj, *.vbproj, *.fsproj) in the repository  
- [ ] [XS] Backup current project files to a safe location (e.g., feature branch or copy)  
- [ ] [XS] Ensure access to project build and runtime documentation (if available)  

## Phase 1 — Preparation

- [ ] [XS] Identify and list all non-SDK-style project files as upgrade candidates  
- [ ] [XS] Check for custom build tasks, targets, and msbuild props in project files and solutions  

## Phase 2 — Core Upgrade

- [ ] [M] Migrate each project file to SDK-style format using .NET migration tools or manual conversion   
- [ ] [S] For each migrated project, update the `TargetFramework` to `net8.0`  
- [ ] [S] Remove obsolete or unsupported msbuild properties, settings, and package references during conversion  
- [ ] [M] Verify and manually port custom build events, targets, and import logic to SDK-style equivalents  
- [ ] [S] Update solution files (*.sln) to reference new SDK-style project files if paths or names changed  

## Phase 3 — Testing & Validation

- [ ] [S] Build each converted project individually and resolve all build errors/warnings related to project file changes  
- [ ] [S] Build and restore dependencies for the overall solution in .NET 8  
- [ ] [M] Run all project tests (unit, integration, etc.) to validate successful migration post-upgrade  
- [ ] [S] Confirm application(s) launch and run basic smoke test scenarios  

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Update build and deployment pipeline definitions to use .NET 8 SDK/tooling  
- [ ] [S] Validate that automated builds, restores, and deployments succeed in CI/CD after migration  

## Phase 5 — Documentation & Rollout

- [ ] [S] Document major changes in the migration (project format, targets, build process) in the developer README  
- [ ] [XS] Announce migration completion to the team and provide upgrade instructions for local development environments  

## Post-Migration Cleanup

- [ ] [XS] Remove backup/copy of legacy project files from source control  
- [ ] [XS] Remove any migration tools or scripts that are no longer needed  
- [ ] [XS] Confirm no references to old project structure remain in documentation or automation scripts  
