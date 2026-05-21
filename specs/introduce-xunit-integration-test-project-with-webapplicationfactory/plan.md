# PLAN: Introduce xUnit Integration Test Project with WebApplicationFactory

## Overview

**Migration Strategy: Feature-Flag Gated / Additive (Greenfield Test Project)**

This effort introduces a *net-new* xUnit integration test project alongside the existing solution. Because no production code is modified and no existing tests are removed, the strategy is purely additive — the new project is wired into CI as an optional gate initially, then promoted to a required gate once baseline coverage is established.

This approach carries minimal risk: the existing build and test pipeline is unaffected until the new project is explicitly added to CI required checks. The effort is moderate (see Phases below), consistent with the "moderate" upgrade option.

> **Note:** The tech analysis did not supply language version, runtime version, build tool, or existing framework details. Where these are unknown, entries are marked **TODO**. All decisions below are based on standard .NET / ASP.NET Core conventions implied by the use of `WebApplicationFactory`, which is an ASP.NET Core-specific type.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Scaffold integration test project (`.csproj`, folder structure, NuGet references) | Existing solution file (`.sln`) accessible; target web project identified | 1 person-day |
| 2 | Implement `CustomWebApplicationFactory<TEntryPoint>` and shared test fixtures | Phase 1 complete; entry-point class (`Program` / `Startup`) identified in host project | 1 person-day |
| 3 | Write initial integration test suite (smoke tests + critical-path endpoint tests) | Phase 2 complete; API surface documented or discoverable | 2 person-days |
| 4 | Wire project into CI pipeline as a required gate | Phase 3 complete; CI configuration file accessible | 0.5 person-days |
| 5 | Documentation & team onboarding | Phase 4 complete | 0.5 person-days |

**Total estimated effort: ~5 person-days**

---

## Component Changes

### 1. New Project: `<SolutionName>.IntegrationTests`

**What changes structurally:**
- A new `.csproj` file is created; it is added to the existing `.sln` via `dotnet sln add`.
- The project references the host/web project under test (project reference, not package reference).
- No files in the existing web project are modified unless `Program.cs` / `Startup.cs` requires a minor accessibility fix (see below).

**Files introduced:**

| File | Purpose |
|------|---------|
| `<SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj` | Project definition, NuGet references |
| `Infrastructure/CustomWebApplicationFactory.cs` | Subclass of `WebApplicationFactory<TEntryPoint>`; overrides `ConfigureWebHost` to swap services for test doubles |
| `Infrastructure/IntegrationTestBase.cs` | Abstract base class providing `HttpClient` and fixture lifecycle helpers |
| `Tests/<FeatureArea>Tests.cs` | Concrete test classes (one file per feature area / controller) |
| `xunit.runner.json` | xUnit runner configuration (parallelism, diagnostics) |
| `appsettings.Testing.json` | Test-environment configuration overrides (connection strings, feature flags) |

**APIs / classes modified in the host project (if needed):**

- `Program.cs` — If the entry-point uses top-level statements, a `public partial class Program {}` declaration must be appended (or already present) so `WebApplicationFactory<Program>` can reference it from the test assembly. This is a one-line, non-breaking addition.
- `Startup.cs` (if present) — No changes required; `WebApplicationFactory<Startup>` works without modification.

**Key class signatures:**

```csharp
// Infrastructure/CustomWebApplicationFactory.cs
public class CustomWebApplicationFactory<TEntryPoint> 
    : WebApplicationFactory<TEntryPoint> where TEntryPoint : class
{
    protected override void ConfigureWebHost(IWebHostBuilder builder) { … }
}

// Infrastructure/IntegrationTestBase.cs
public abstract class IntegrationTestBase 
    : IClassFixture<CustomWebApplicationFactory<Program>>, IAsyncLifetime
{
    protected HttpClient Client { get; }
    …
}
```

---

## Dependency Upgrade Plan

> **TODO:** The tech analysis did not supply current version numbers for any dependency. Target versions below reflect the standard packages required for this task. Confirm exact versions against the solution's current `global.json` / `Directory.Build.props` / `Directory.Packages.props` before applying.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `xunit` | TODO | TODO (match runtime TFM) | N/A — new dependency | Add to test `.csproj` only |
| `xunit.runner.visualstudio` | TODO | TODO (match runtime TFM) | N/A — new dependency | Required for VS Test Explorer and `dotnet test` |
| `Microsoft.NET.Test.Sdk` | TODO | TODO (match runtime TFM) | N/A — new dependency | Required for `dotnet test` discovery |
| `Microsoft.AspNetCore.Mvc.Testing` | TODO | TODO (match runtime TFM) | N/A — new dependency | Provides `WebApplicationFactory<T>` |
| `coverlet.collector` | TODO | TODO | N/A — new dependency | Optional; enables coverage collection via `dotnet test --collect:"XPlat Code Coverage"` |

> All version numbers **must** be reconciled against the project's target framework moniker (TFM) before merging. Use `dotnet add package <name>` with an explicit `--version` flag after confirming the TFM.

---

## Infrastructure Changes

**CI/CD Pipeline:**

- Add a new pipeline step (after the existing build/unit-test step) that executes:
  ```
  dotnet test <SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj \
    --configuration Release \
    --logger "trx;LogFileName=integration-results.trx" \
    --collect:"XPlat Code Coverage"
  ```
- Publish the `.trx` results file as a test artifact.
- **Phase 4:** Promote this step to a required status check on pull requests.

> **TODO:** Specific CI/CD platform (GitHub Actions, Azure DevOps, Jenkins, etc.) and pipeline file path are not provided in context. Adapt the command above to the platform's YAML/DSL syntax.

**Docker / Kubernetes / IaC:**

> N/A — Integration tests run in the CI agent process using `WebApplicationFactory` (in-process test server). No additional containers, Kubernetes manifests, or IaC changes are required.

---

## Rollback Strategy

Because this task is purely additive, rollback at any phase is low-risk:

| Phase | Rollback Action |
|-------|----------------|
| 1 — Project scaffolded | `dotnet sln remove <SolutionName>.IntegrationTests.csproj`; delete the project folder; revert `.sln` file. No other files affected. |
| 2 — Factory implemented | Same as Phase 1 (the factory lives entirely within the new project). |
| 3 — Tests written | Same as Phase 1. |
| 4 — CI gate added | Remove or comment out the new CI step; the pipeline reverts to its prior state. The test project can remain in the repo without being a required gate. |
| 5 — Documentation merged | Revert documentation commits independently; no code impact. |

> The one-line `public partial class Program {}` addition to the host project (if applied) is safe to leave in place — it has zero runtime impact — but can be reverted independently if desired.

---

## Testing Strategy

This section describes the testing approach *for the integration test project itself* and how it fits into the broader test pyramid.

### Test Pyramid

| Layer | Tool | Scope | Coverage Target | CI Gate |
|-------|------|-------|----------------|---------|
| Unit | TODO (existing framework) | Existing unit tests — unchanged | TODO (existing baseline) | Required (existing) |
| **Integration** | **xUnit + `WebApplicationFactory`** | **HTTP endpoints, middleware pipeline, service wiring** | **≥ 80% of public API surface (endpoints)** | **Required after Phase 4** |
| Regression | xUnit integration suite (subset tagged `[Trait("Category","Regression")]`) | Critical user journeys | All critical paths covered | Required |
| Performance / Load | TODO | TODO | TODO | TODO |

### Concrete Practices

- **Test isolation:** Each test class receives a fresh `HttpClient` from `CustomWebApplicationFactory`. Database state (if any) is reset via `IAsyncLifetime.InitializeAsync` using an in-memory provider or a test-scoped transaction.
- **Parallelism:** Set `parallelizeAssembly: false` in `xunit.runner.json` initially to avoid port/resource conflicts; enable per-collection parallelism once fixture isolation is confirmed.
- **Naming convention:** `<MethodUnderTest>_<Scenario>_<ExpectedOutcome>` (e.g., `GetProduct_ValidId_Returns200`).
- **CI coverage gate:** `dotnet test` with `--collect:"XPlat Code Coverage"` + `reportgenerator` to enforce the ≥ 80% endpoint coverage threshold; fail the build if threshold is not met.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Test project scaffolded and building | Phase 1 | Day 1 | TODO |
| `CustomWebApplicationFactory` and base fixtures complete | Phase 2 | Day 2 | TODO |
| Initial test suite covering critical endpoints | Phase 3 | Day 4 | TODO |
| CI pipeline step added (non-required) | Phase 4 (soft) | Day 4 | TODO |
| CI pipeline step promoted to required gate | Phase 4 (hard) | Day 5 | TODO |
| Documentation and team onboarding complete | Phase 5 | Day 5 | TODO |

> Effort derived from the 5 person-day estimate in the Phases section. Calendar dates are relative to project kick-off (Day 0). Assign concrete dates and owners once the team is allocated.