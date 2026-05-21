# PLAN: Introduce xUnit Integration Test Project with WebApplicationFactory

## Overview

**Migration Strategy: Feature-Flag Gated / Additive (Greenfield Test Project)**

This effort introduces a *net-new* xUnit integration test project alongside the existing solution. Because no production code is modified and no existing tests are removed, the strategy is purely additive — the new project is wired into CI as an optional gate initially, then promoted to a required gate once baseline coverage is established.

This approach carries minimal risk: the existing build and test pipeline is unaffected until the new project is explicitly added to CI required checks. The effort is moderate (see Phases), consistent with the "moderate" upgrade option designation.

> **Note:** The tech analysis did not supply language version, runtime version, build tool, or existing framework details. Where these are unknown, entries are marked **TODO**. All decisions below are based on standard .NET / xUnit / `WebApplicationFactory<T>` conventions — adjust once the actual project context is confirmed.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit existing solution structure; identify the target API/web project under test; confirm .NET SDK version and existing test projects | None | 0.5 person-days |
| 2 | Scaffold new xUnit integration test project; add NuGet references (`xunit`, `Microsoft.AspNetCore.Mvc.Testing`, `coverlet.collector`) | Phase 1 complete | 0.5 person-days |
| 3 | Implement `CustomWebApplicationFactory<TEntryPoint>` base class; configure test service overrides (DB, external services) | Phase 2 complete | 1 person-day |
| 4 | Write initial integration test suite covering critical HTTP endpoints / application startup smoke tests | Phase 3 complete | 1 person-day |
| 5 | Wire project into CI pipeline as a required gate; enforce coverage threshold | Phase 4 complete | 0.5 person-days |
| **Total** | | | **~3.5 person-days** |

---

## Component Changes

### New Project: `<SolutionName>.IntegrationTests`

**What changes structurally:**
- A new `.csproj` is added to the solution; no existing projects are modified.
- The project references the target web/API project (or its assembly) so `WebApplicationFactory<TEntryPoint>` can resolve the entry point.

**Files to create:**

| File | Purpose |
|------|---------|
| `<SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj` | Project file with NuGet references |
| `Infrastructure/CustomWebApplicationFactory.cs` | Subclass of `WebApplicationFactory<TEntryPoint>`; overrides `ConfigureWebHost` to swap real dependencies for test doubles |
| `Infrastructure/HttpClientExtensions.cs` | (Optional) Helper extension methods for typed HTTP calls in tests |
| `Tests/<Feature>ControllerTests.cs` | First concrete integration test class(es) |
| `xunit.runner.json` | xUnit runner configuration (parallelism, diagnostics) |

**Key class / method details:**

```
CustomWebApplicationFactory<TEntryPoint>
  └── override ConfigureWebHost(IWebHostBuilder builder)
        ├── builder.UseEnvironment("IntegrationTest")
        ├── services.RemoveAll<DbContext>()          // TODO: confirm DbContext type name
        ├── services.AddDbContext<...>(useInMemory)  // or Testcontainers
        └── services.Replace<IExternalService, FakeExternalService>()
```

> **TODO:** Confirm the entry-point class name (typically `Program` or `Startup`) in the target web project. In minimal-API projects the entry point is the implicit `Program` class.

**Existing projects affected:**
- The target web/API `.csproj` may need `<InternalsVisibleTo>` added if `Program` is internal (common in .NET 6+ minimal APIs):
  ```xml
  <!-- In the web project's .csproj or a partial Program.cs -->
  [assembly: InternalsVisibleTo("<SolutionName>.IntegrationTests")]
  ```

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not supply current or target version numbers. The table below lists the required packages with their roles. **TODO: populate exact version numbers once the target .NET SDK version is confirmed.**

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `xunit` | TODO — not present | TODO (latest stable for target TFM) | N/A — new dependency | Core test framework |
| `xunit.runner.visualstudio` | TODO — not present | TODO | N/A | Enables VS Test Explorer & `dotnet test` integration |
| `Microsoft.AspNetCore.Mvc.Testing` | TODO — not present | TODO (must match web project's `Microsoft.AspNetCore.App` version) | N/A | Provides `WebApplicationFactory<T>` and `TestServer` |
| `coverlet.collector` | TODO — not present | TODO (latest stable) | N/A | In-process coverage collection for `dotnet test` |
| `Microsoft.NET.Test.Sdk` | TODO — not present | TODO | N/A | Required MSBuild targets for test projects |
| `FluentAssertions` *(optional)* | TODO | TODO | N/A | Improves assertion readability; add if team standard |
| `Testcontainers` *(optional)* | TODO | TODO | N/A | Use instead of in-memory DB if real DB fidelity is required |

---

## Infrastructure Changes

**CI/CD Pipeline:**
- Add a new pipeline step (after the existing build/unit-test step) that executes:
  ```bash
  dotnet test <SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj \
    --configuration Release \
    --collect:"XPlat Code Coverage" \
    --results-directory ./coverage
  ```
- Initially mark this step as **non-blocking** (warning only); promote to **required gate** after Phase 4 baseline is established.
- **TODO:** Identify CI platform (GitHub Actions, Azure DevOps, Jenkins, etc.) and update the relevant YAML/pipeline definition file.

**Docker / Kubernetes:**
- TODO — no container or Kubernetes context was provided. Integration tests typically run in the CI agent, not in a container, unless Testcontainers is adopted (which manages its own Docker socket).

**IaC:**
- TODO — no IaC context provided.

---

## Rollback Strategy

Each phase is independently reversible because no existing code is modified.

| Phase | Rollback Action |
|-------|----------------|
| 1 (Audit) | No artifacts produced; nothing to roll back. |
| 2 (Scaffold project) | Delete the new `.csproj` and its directory; remove the project reference from the `.sln` file. |
| 3 (Factory implementation) | Delete `Infrastructure/CustomWebApplicationFactory.cs`; revert any `InternalsVisibleTo` attribute added to the web project. |
| 4 (Test suite) | Delete test class files; the project scaffold can remain dormant without affecting the build. |
| 5 (CI gate) | Remove or comment out the new pipeline step in the CI YAML; the test project remains in source but is not executed. |

> Because all changes are additive, a full rollback at any phase is a simple file/config deletion with no impact on production code or existing tests.

---

## Testing Strategy

This section describes the test pyramid *for the integration test project itself* and how it fits into the broader quality strategy.

### Test Pyramid

```
         [ E2E / Contract ]   ← out of scope for this task
        [  Integration Tests  ]  ← THIS TASK
       [    Unit Tests (existing)   ]
```

### Layers

| Layer | Tool | Scope | Coverage Target | CI Gate |
|-------|------|-------|----------------|---------|
| Unit (existing) | TODO (existing framework) | Existing unit test project | TODO (existing threshold) | Required (existing) |
| Integration (new) | xUnit + `WebApplicationFactory<T>` | HTTP endpoints, middleware pipeline, startup configuration | ≥ 60% line coverage on the web project (initial baseline; raise over time) | Required after Phase 5 |

### Concrete Testing Approach

1. **Startup smoke test** — Assert that `CreateClient()` succeeds without throwing; validates DI container configuration.
2. **Happy-path HTTP tests** — `GET`/`POST` against critical endpoints; assert HTTP status codes and response shape.
3. **Authentication/Authorization tests** — Use `WebApplicationFactory` to inject test JWT or cookie; assert 401/403 on protected routes.
4. **Database isolation** — Each test class uses a fresh in-memory DB (or Testcontainer instance) via `IClassFixture<CustomWebApplicationFactory<Program>>`.

### CI Gates

- `dotnet test` exit code must be `0` (all tests pass).
- Coverage report generated via `coverlet`; threshold enforced via `<CoverletThreshold>` MSBuild property or a Reportgenerator quality gate step.
- **TODO:** Confirm coverage reporting destination (Codecov, SonarQube, Azure DevOps coverage tab, etc.).

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Solution audit complete; entry-point class and .NET version confirmed | 1 | Day 1 | TODO |
| New test project scaffolded and building in CI | 2 | Day 1 | TODO |
| `CustomWebApplicationFactory` implemented with service overrides | 3 | Day 2 | TODO |
| Initial integration test suite passing locally and in CI | 4 | Day 3 | TODO |
| CI required gate active; coverage baseline documented | 5 | Day 4 | TODO |

> Total estimated duration: **~3.5 person-days** (aligned with the moderate upgrade option). Elapsed calendar time may extend to 1 week depending on review cycles and TODO resolution.