# PLAN: Create New ASP.NET Core 8 SDK-Style Project Structure

---

## Overview

**Migration Strategy: Big-Bang (Greenfield Scaffold)**

This task involves creating a new ASP.NET Core 8 SDK-style project structure rather than migrating an existing running system. Because the deliverable is a net-new scaffold (not a live service cutover), a **big-bang** approach is appropriate: the full SDK-style structure is created in a single coordinated effort, reviewed, and merged as a foundational baseline.

**Justification:**
- No existing runtime to protect; rollback risk is low (revert a branch, not a production deployment).
- SDK-style `.csproj` format is the standard for .NET 8 and carries no legacy compatibility constraints for a new project.
- Upgrade urgency is **medium**, meaning there is no emergency pressure, but the work should be completed in a single focused sprint to avoid structural drift.
- Effort is moderate; parallel-run or strangler-fig patterns would add unnecessary overhead for a scaffold task.

> **TODO:** If this scaffold is intended to replace an existing legacy project (not described in context), re-evaluate strategy as strangler-fig with a parallel-run phase.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Repository & solution setup: create `.sln`, establish folder conventions, configure `.gitignore` and `.editorconfig` for .NET 8 | None | TODO (derive from confirmed person-days estimate) |
| 2 | Core project scaffold: create SDK-style `.csproj` files (web host, class libraries, test projects) targeting `net8.0` | Phase 1 complete | TODO |
| 3 | Configuration & middleware baseline: `Program.cs` minimal hosting model, `appsettings.json` / `appsettings.{Environment}.json`, DI registration stubs | Phase 2 complete | TODO |
| 4 | CI pipeline integration: build, test, and lint gates wired to the new project structure | Phase 3 complete | TODO |
| 5 | Documentation & handoff: README, architecture decision records (ADRs), onboarding notes | Phase 4 complete | TODO |

> **TODO:** Populate effort cells (person-days) once the upgrade option detail document is provided. The option ID "moderate" was supplied without a numeric estimate.

---

## Component Changes

### Solution File
- **File:** `<SolutionName>.sln`
- Create using `dotnet new sln`; add all projects via `dotnet sln add`.
- No legacy `.sln` format quirks — SDK tooling manages this automatically.

### Web Host Project (`src/<ProjectName>.Web/<ProjectName>.Web.csproj`)
- **Format:** SDK-style, `<Project Sdk="Microsoft.NET.Sdk.Web">`
- **Target framework:** `<TargetFramework>net8.0</TargetFramework>`
- **Entry point:** `Program.cs` using the ASP.NET Core 8 minimal hosting model (no `Startup.cs` unless explicitly required).
- Remove: `packages.config`, `web.config` (replace with `appsettings.json`), `AssemblyInfo.cs` (attributes moved inline or auto-generated).
- Key structural files:
  - `Program.cs` — `WebApplication.CreateBuilder()` / `builder.Build()` / `app.Run()` pattern.
  - `appsettings.json` / `appsettings.Development.json`
  - `Properties/launchSettings.json`

### Class Library Projects (`src/<ProjectName>.Core/`, `src/<ProjectName>.Infrastructure/`)
- **Format:** SDK-style, `<Project Sdk="Microsoft.NET.Sdk">`
- **Target framework:** `net8.0`
- No `AssemblyInfo.cs`; version metadata declared in `.csproj` via `<Version>`, `<Authors>`, etc.
- Project references use `<ProjectReference>` elements (no NuGet-based internal references).

### Test Projects (`tests/<ProjectName>.UnitTests/`, `tests/<ProjectName>.IntegrationTests/`)
- **Format:** SDK-style, `<Project Sdk="Microsoft.NET.Sdk">`
- **Target framework:** `net8.0`
- Include `<IsPackable>false</IsPackable>` to prevent accidental NuGet publish.
- Reference test framework packages (see Dependency Upgrade Plan).

### Configuration
- `global.json` at solution root pinning SDK version to .NET 8 (e.g., `"version": "8.0.xxx"`).
- `.editorconfig` enforcing C# coding style.
- `Directory.Build.props` (optional but recommended) for shared MSBuild properties across all projects.
- `Directory.Packages.props` (optional) for Central Package Management if multi-project NuGet versions need to be unified.

> **TODO:** Confirm specific project names, namespace conventions, and layer boundaries from the team's architecture decision.

---

## Dependency Upgrade Plan

> **TODO:** The tech analysis provided does not include current dependency versions, framework names, or target versions. The table below lists the expected baseline dependencies for a new ASP.NET Core 8 project. All versions must be validated against the official tech analysis once supplied.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `Microsoft.AspNetCore.*` (framework) | N/A (new project) | `net8.0` (in-box) | N/A | Included via `Microsoft.NET.Sdk.Web`; no explicit package reference needed |
| `Microsoft.Extensions.Hosting` | N/A | TODO (match tech analysis) | N/A | Pulled transitively; pin only if diverging from framework version |
| xUnit / NUnit / MSTest (test framework) | N/A | TODO (match tech analysis) | N/A | Choose one; add to test `.csproj` only |
| `coverlet.collector` | N/A | TODO | N/A | Required for code coverage in CI |
| `Microsoft.NET.Test.Sdk` | N/A | TODO | N/A | Required for `dotnet test` discovery |
| Linting / analysis (`Microsoft.CodeAnalysis.NetAnalyzers`) | N/A | TODO | N/A | Enable via `<EnableNETAnalyzers>true</EnableNETAnalyzers>` in `Directory.Build.props` |

> **TODO:** Re-populate this table with exact version numbers from the tech analysis document once available.

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD system, IaC tooling) was provided. The following are placeholders pending confirmation.

- **Docker base image:** TODO — expected `mcr.microsoft.com/dotnet/aspnet:8.0` (runtime) and `mcr.microsoft.com/dotnet/sdk:8.0` (build stage); confirm with ops team.
- **Kubernetes manifests:** TODO — not described in context.
- **CI/CD pipeline:** TODO — pipeline system not identified. At minimum, the pipeline must invoke `dotnet restore`, `dotnet build`, `dotnet test`, and (if applicable) `dotnet publish`. Update any existing pipeline YAML to point to the new `.sln` path.
- **IaC:** TODO — not described in context.
- **`global.json`:** Pin SDK version at solution root to prevent accidental SDK float in CI agents.

---

## Rollback Strategy

Because this task creates a new structure (no production system is being modified), rollback is branch-level:

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 — Repo & solution setup | Delete or revert the feature branch; no downstream impact. |
| Phase 2 — Project scaffold | Revert commits on the feature branch; the main branch remains unaffected until merge. |
| Phase 3 — Configuration & middleware | Revert `Program.cs`, `appsettings.json`, and `.csproj` changes on the branch. |
| Phase 4 — CI pipeline integration | Revert pipeline YAML changes; CI reverts to prior configuration (or no-op if pipeline is new). |
| Phase 5 — Documentation | Revert or archive documentation files; no functional impact. |

**General rule:** Do not merge the feature branch to `main` / `trunk` until all CI gates in Phase 4 pass. This ensures `main` is never left in a broken scaffold state.

---

## Testing Strategy

| Layer | Tool | Target | CI Gate |
|-------|------|--------|---------|
| **Unit** | TODO (xUnit / NUnit / MSTest — confirm from tech analysis) | ≥ 80% line coverage on `Core` and `Infrastructure` projects | Block merge on failure |
| **Integration** | `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory<T>`) | Key HTTP endpoints and DI wiring smoke-tested | Block merge on failure |
| **Regression** | Re-run full unit + integration suite on every PR | No regression from baseline | Block merge on failure |
| **Performance** | TODO — tool not specified in context (e.g., `k6`, `BenchmarkDotNet`) | TODO — no baseline exists for a new project; establish benchmarks in Phase 4 | Advisory (non-blocking initially) |

**Coverage tooling:** `coverlet.collector` + `dotnet test --collect:"XPlat Code Coverage"` + TODO (report publisher, e.g., Codecov, SonarQube — not specified in context).

**Static analysis:** Enable `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` and `<EnableNETAnalyzers>true</EnableNETAnalyzers>` in `Directory.Build.props` to enforce code quality at build time.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Solution and repo structure committed | Phase 1 | TODO (person-days not provided) | TODO |
| All SDK-style `.csproj` files created and building | Phase 2 | TODO | TODO |
| `Program.cs` minimal host running locally | Phase 3 | TODO | TODO |
| CI pipeline green (build + test) | Phase 4 | TODO | TODO |
| README and ADRs merged | Phase 5 | TODO | TODO |

> **TODO:** Populate completion dates and owners once the upgrade option's person-days estimate and team assignments are confirmed. The option ID "moderate" was provided without a numeric breakdown.

---

*Document status: DRAFT — pending tech analysis version numbers, infrastructure context, person-days estimate, and team ownership assignments.*