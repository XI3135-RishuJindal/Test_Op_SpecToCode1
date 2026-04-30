# Tasks: Migrate and Reconfigure OpenAPI/Swagger Using Swashbuckle.AspNetCore

## Prerequisites

- [ ] [XS] Identify and document current OpenAPI/Swagger implementation method (legacy Swagger, NSwag, custom middleware, etc.)
- [ ] [S] Ensure .NET Core or .NET 5+ is being used (Swashbuckle.AspNetCore compatibility requirement)

## Phase 1 — Preparation

- [ ] [XS] Add/Update Swashbuckle.AspNetCore NuGet package to latest stable version in solution/project file
- [ ] [S] Remove any prior Swagger/OpenAPI libraries and related configuration from project

## Phase 2 — Core Upgrade

- [ ] [S] Add Swashbuckle middleware setup in Startup.cs or Program.cs (as per .NET version) for OpenAPI endpoint and Swagger UI
- [ ] [M] Reimplement custom configuration and metadata (info, contact, license, etc.) in Swashbuckle configuration
- [ ] [S] Update or recreate any document filters, security schemes (e.g., JWT), and operation filters to equivalent Swashbuckle features
- [ ] [M] Migrate or replace XML comments and data annotation integrations for API documentation enhancements
- [ ] [M] Test and validate correct OpenAPI specification generation by Swashbuckle for representative endpoints

## Phase 3 — Testing & Validation

- [ ] [S] Verify accessibility and rendering of Swagger UI at expected endpoint
- [ ] [S] Manually inspect generated OpenAPI specification (swagger.json) for key endpoints and metadata
- [ ] [S] Validate that any custom security, authentication, or versioning schemes appear and function as expected in UI
- [ ] [S] Collect screenshots and generate sample OpenAPI JSON to document results

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [S] Update developer onboarding/README/documentation to reflect new usage and configuration of Swashbuckle.AspNetCore
- [ ] [XS] List any breaking changes or noteworthy migration notes for downstream integrators or API consumers

## Post-Migration Cleanup

- [ ] [XS] Remove obsolete documentation or sample files related to prior Swagger/OpenAPI tooling
- [ ] [XS] Delete any unused config files, old middleware, or startup logic no longer required after migration