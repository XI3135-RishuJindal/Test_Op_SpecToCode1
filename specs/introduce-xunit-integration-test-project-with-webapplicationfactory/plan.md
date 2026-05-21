# PLAN: Introduce xUnit Integration Test Project with WebApplicationFactory

## Overview

**Migration Strategy: Feature-Flag Gated / Additive (Greenfield Test Project)**

This effort introduces a *net-new* xUnit integration test project alongside the existing solution. Because no production code is modified and no existing tests are removed, the strategy is purely additive — the new project is wired into CI as an optional gate initially, then promoted to a required gate once baseline coverage is established.

This approach carries minimal risk: the existing build and test pipeline is unaffected until the new project is explicitly added to CI required checks. The effort is moderate (see Phases below), consistent with the "moderate" upgrade option.

**Justification:** The risk score is low (no breaking changes to production code), and the effort is bounded to scaffolding, configuration, and writing an initial set of integration tests. A big-bang or strangler-fig strategy is unnecessary for a greenfield test project.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Scaffold xUnit integration test project, add to solution, configure `WebApplicationFactory` base class | Existing ASP.NET Core web project must be identified and referenced | 2 person-days |
| 2 | Implement initial integration test suite (happy-path HTTP endpoint tests, auth/middleware smoke tests) | Phase 1 complete; test environment configuration (connection strings, secrets) available | 2 person-days |
| 3 | Wire integration test project into CI pipeline as a required gate; add coverage reporting | Phase 2 complete; CI pipeline access | 1 person-day |

> **Total estimated effort: ~5 person-days** (derived from "moderate" option baseline).

---

## Component Changes

### New Project: `<SolutionName>.IntegrationTests`

**What changes structurally:**
- A new `.csproj` is created and added to the solution (`.sln` file updated via `dotnet sln add`).
- The project references the main web application project to enable `WebApplicationFactory<TEntryPoint>`.

**Files introduced:**

| File | Purpose |
|------|---------|
| `<SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj` | Project file with xUnit, `Microsoft.AspNetCore.Mvc.Testing`, and `coverlet.collector` references |
| `<SolutionName>.IntegrationTests/CustomWebApplicationFactory.cs` | Subclass of `WebApplicationFactory<TEntryPoint>` — overrides `ConfigureWebHost` to swap in test doubles, in-memory DB, or test configuration |
| `<SolutionName>.IntegrationTests/IntegrationTestBase.cs` | Abstract base class implementing `IClassFixture<CustomWebApplicationFactory>`, exposes `HttpClient` to test classes |
| `<SolutionName>.IntegrationTests/Tests/<Feature>IntegrationTests.cs` | Concrete test classes per feature/controller |
| `<SolutionName>.IntegrationTests/appsettings.Testing.json` | Test-specific configuration overrides (connection strings, feature flags) |

**APIs modified:**

- `Program.cs` (or `Startup.cs`) in the main web project: may require `internal` visibility to be changed to `public`, or a `public partial class Program {}` stub added at the bottom of `Program.cs` to expose the entry point to `WebApplicationFactory<Program>`.

  ```csharp
  // Program.cs — add at end of file if using top-level statements
  public partial class Program { }
  ```

- `CustomWebApplicationFactory.cs` overrides:
  - `ConfigureWebHost(IWebHostBuilder builder)` — sets `ASPNETCORE_ENVIRONMENT` to `"Testing"`, replaces real service registrations with test doubles.

**No existing production classes or methods are structurally modified** beyond the `Program` visibility stub.

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not supply specific current or target version numbers. The table below lists the required packages with version guidance marked as TODO where exact versions cannot be confirmed from context.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `xunit` | N/A (new project) | TODO — match solution's target framework | None (new addition) | Add to new `.csproj` only |
| `xunit.runner.visualstudio` | N/A (new project) | TODO | None | Required for `dotnet test` discovery |
| `Microsoft.AspNetCore.Mvc.Testing` | N/A (new project) | TODO — must match ASP.NET Core version in main project | None | Provides `WebApplicationFactory<T>` |
| `Microsoft.NET.Test.Sdk` | N/A (new project) | TODO | None | Required test SDK |
| `coverlet.collector` | N/A (new project) | TODO | None | Enables `--collect:"XPlat Code Coverage"` in CI |
| `FluentAssertions` *(optional)* | N/A | TODO | None | Recommended for readable HTTP response assertions |

**Action:** Confirm exact versions by running `dotnet list package` on the main project and matching the `Microsoft.AspNetCore.Mvc.Testing` version to the ASP.NET Core version in use.

---

## Infrastructure Changes

**CI/CD Pipeline:**

- Add a new pipeline step (after the existing unit test step) to execute:
  ```bash
  dotnet test <SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj \
    --configuration Release \
    --collect:"XPlat Code Coverage" \
    --results-directory ./coverage
  ```
- In Phase 3, promote this step from *informational* to a *required gate* (fail the build on test failure).
- TODO: Specific CI platform (GitHub Actions, Azure DevOps, Jenkins, etc.) is not identified in context — adapt step syntax accordingly.

**Docker / Kubernetes:** TODO — not mentioned in context. If the test project requires a running database or external dependency, a `docker-compose.override.yml` for test infrastructure may be needed.

**IaC:** TODO — not mentioned in context.

---

## Rollback Strategy

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | 1. Run `dotnet sln remove <SolutionName>.IntegrationTests/<SolutionName>.IntegrationTests.csproj`. 2. Delete the `<SolutionName>.IntegrationTests/` directory. 3. Revert any changes to `Program.cs` (remove `public partial class Program {}`). 4. Commit revert — no production behavior is affected. |
| **Phase 2** | Same as Phase 1 — test code is isolated in the new project; no production code was changed. |
| **Phase 3** | 1. Remove or comment out the integration test CI step. 2. If the step was a required gate, demote it back to informational in the pipeline configuration. 3. No code changes required. |

All phases are independently reversible with no impact on production deployments.

---

## Testing Strategy

```
┌─────────────────────────────────────────────────────┐
│  Performance (optional, Phase 3+)                   │  TODO — tooling not specified
├─────────────────────────────────────────────────────┤
│  Regression                                         │  Full integration suite run on every PR
├─────────────────────────────────────────────────────┤
│  Integration (THIS EFFORT)                          │  xUnit + WebApplicationFactory
├─────────────────────────────────────────────────────┤
│  Unit (existing — unchanged)                        │  Existing test project(s)
└─────────────────────────────────────────────────────┘
```

**Integration Test Layer (this effort):**

| Concern | Approach |
|---------|---------|
| **Test framework** | xUnit 2.x |
| **HTTP client** | `HttpClient` from `WebApplicationFactory.CreateClient()` |
| **Test isolation** | Each test class uses `IClassFixture<CustomWebApplicationFactory>` — factory created once per class |
| **Data isolation** | Override `ConfigureWebHost` to use EF Core in-memory provider or SQLite in-memory (TODO: confirm ORM in use) |
| **Coverage target** | ≥ 80% line coverage on HTTP-reachable endpoints (measured via `coverlet`) |
| **CI gate (Phase 3)** | Build fails if any integration test fails; coverage report published as artifact |
| **Assertions** | `FluentAssertions` for HTTP status codes, response body shape; `System.Net.Http.Json` for deserialization |

**Concrete test scenarios to implement in Phase 2:**
1. `GET /health` (or equivalent health endpoint) returns `200 OK`.
2. Authenticated endpoints return `401` when no token is provided.
3. Happy-path CRUD operations for at least one primary resource.
4. Middleware/exception handler returns structured error response on invalid input.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| New test project scaffolded, builds green, `WebApplicationFactory` base class in place | Phase 1 | End of Day 2 | TODO |
| Initial integration test suite written, all tests passing locally | Phase 2 | End of Day 4 | TODO |
| CI pipeline updated, integration tests run as required gate, coverage report published | Phase 3 | End of Day 5 | TODO |

> Dates are relative to kick-off day. Assign owners once team allocation is confirmed.