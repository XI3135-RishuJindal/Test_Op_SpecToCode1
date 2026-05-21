# CONSTITUTION
## Project: xUnit Integration Test Project with WebApplicationFactory

---

## Project Identity

**Name:** xUnit Integration Test Suite — WebApplicationFactory Integration

**Purpose:** Introduce a dedicated xUnit integration test project to the existing solution, leveraging ASP.NET Core's `WebApplicationFactory<T>` to enable realistic, in-process HTTP-level testing of the application without requiring a live deployed environment.

**High-Level Goal:** Establish a repeatable, maintainable integration testing baseline that validates application behavior end-to-end (routing, middleware, dependency injection, and response contracts) within the CI pipeline.

---

## Guiding Principles

1. **Prefer a separate test project over embedding integration tests in unit test projects** because mixing concerns increases build complexity and obscures test intent.
2. **Prefer `WebApplicationFactory<TEntryPoint>` over spinning up a real host** because it provides in-process testing with full DI and middleware participation while keeping tests fast and isolated.
3. **Prefer explicit test service overrides (e.g., replacing external dependencies with fakes/stubs) over hitting real external services** because integration tests must be deterministic and runnable offline.
4. **Prefer convention-aligned project naming (`*.IntegrationTests`) over ad-hoc naming** because discoverability and CI test filtering depend on consistent naming patterns.
5. **Prefer scoped `HttpClient` instances created via `WebApplicationFactory.CreateClient()` over shared static clients** because shared state between tests causes flaky results.

---

## Constraints

- **Effort ceiling:** Moderate option — scope is limited to introducing the test project and foundational scaffolding only. No new feature development or refactoring of production code is in scope.
- **Technology mandates:**
  - Test framework: **xUnit** (non-negotiable per task definition).
  - Test host: **ASP.NET Core `WebApplicationFactory<T>`** (`Microsoft.AspNetCore.Mvc.Testing` package).
  - Runtime version: TODO — confirm target .NET version from solution's existing `.csproj` / `global.json` before selecting package versions.
  - Language: TODO — confirm C# version in use to ensure test project `<LangVersion>` aligns.
- **Scope freeze:** This task does not include migrating existing tests, adding load/performance tests, or modifying production application code.
- **Build tool:** TODO — confirm whether the solution uses `dotnet CLI`, `MSBuild`-only, or a wrapper (e.g., `Cake`, `NUKE`) to ensure the new project integrates correctly.

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Test project builds clean | Zero build warnings/errors on `dotnet build` in CI |
| Baseline test coverage | At minimum **1 smoke test** per registered HTTP endpoint that asserts `2xx` or expected status code before merge |
| No skipped tests at merge | `[Skip]` attributes require a linked issue; PRs with unexplained skips are blocked |
| CI gate | Integration test project must be included in the CI pipeline and all tests must pass before merge to default branch |
| Package references | All NuGet packages must be pinned to explicit versions in `.csproj`; no floating `*` version ranges |
| Code review | Minimum **1 approving review** from a team member familiar with ASP.NET Core testing before merge |
| Documentation | `README` or inline XML doc must describe how to run integration tests locally and how to override services for test scenarios |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use xUnit as the test framework | Explicitly required by the task definition | Accepted |
| ADR-002 | Use `Microsoft.AspNetCore.Mvc.Testing` / `WebApplicationFactory<T>` as the test host | Explicitly required by the task definition; provides in-process, full-stack test execution | Accepted |
| ADR-003 | Create a dedicated `*.IntegrationTests` project rather than adding to an existing test project | Separation of concerns; allows independent CI filtering and execution | Accepted |
| ADR-004 | Target runtime/SDK version | TODO — must be confirmed against existing solution before project creation |Proposed |
| ADR-005 | Strategy for replacing external dependencies in tests (fakes, mocks, test doubles) | TODO — depends on what external dependencies the application under test has | Proposed |