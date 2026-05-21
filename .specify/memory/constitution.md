# CONSTITUTION
## Project: Introduce xUnit Integration Test Project with WebApplicationFactory

---

## Project Identity

**Name:** xUnit Integration Test Project Introduction

**Purpose:** Introduce a dedicated xUnit integration test project to the existing solution, leveraging `WebApplicationFactory<TEntryPoint>` to host the application in-process during tests.

**High-Level Goal:** Establish a reliable, maintainable integration testing baseline that validates end-to-end HTTP behavior without requiring external infrastructure, enabling confident ongoing development and regression detection.

---

## Guiding Principles

1. **Prefer `WebApplicationFactory<TEntryPoint>` over external test hosts** because in-process hosting eliminates environment drift and reduces test setup complexity.
2. **Prefer xUnit over other test frameworks** because this is the explicitly stated technology mandate for this task; consistency within the solution test suite is required.
3. **Prefer isolated, self-contained test fixtures over shared mutable state** because integration tests that share state produce non-deterministic results and undermine confidence in the test suite.
4. **Prefer explicit test project boundaries (separate `.csproj`) over embedding integration tests in unit test projects** because separation clarifies intent, allows independent CI execution, and avoids conflating fast unit tests with slower integration tests.
5. **Prefer minimal real dependencies over full production wiring** because integration tests should validate HTTP contracts and application composition, not external service availability.

---

## Constraints

- **Timeline/Effort:** Moderate effort ceiling (exact person-days not provided — TODO: confirm with project lead before sprint planning).
- **Technology Mandates:**
  - Test framework: **xUnit** (non-negotiable per task definition).
  - Host abstraction: **`Microsoft.AspNetCore.Mvc.Testing` / `WebApplicationFactory`** (non-negotiable per task definition).
  - Target runtime: **TODO — confirm .NET version from solution's existing `.csproj` / `global.json`.**
  - Build tool: **TODO — confirm (assumed `dotnet CLI` / MSBuild).**
- **Scope Freeze:** This task covers introduction of the integration test project and foundational scaffolding only. Feature-level test coverage expansion is out of scope.
- **No production code changes** are permitted unless strictly required to support testability (e.g., exposing `Program` class as `public partial`).

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Test project builds clean | Zero build errors or warnings on `dotnet build` in CI |
| Baseline test coverage | At minimum **1 passing smoke/health-check integration test** must exist before the project is merged |
| No flaky tests at merge | All integration tests must pass **3 consecutive CI runs** before PR is approved |
| Code review | Minimum **1 peer approval** required; reviewer must verify `WebApplicationFactory` usage pattern is correct |
| Documentation | `README` section added describing how to run integration tests locally (`dotnet test --filter`) |
| Dependency hygiene | No package versions added that conflict with or downgrade existing solution dependencies |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use xUnit as the integration test framework | Explicitly mandated by the modernization task | Accepted |
| ADR-002 | Use `WebApplicationFactory<TEntryPoint>` for in-process hosting | Explicitly mandated by the modernization task; standard ASP.NET Core testing pattern | Accepted |
| ADR-003 | Create a separate `.csproj` for integration tests | Keeps integration tests independently executable and clearly scoped from unit tests | Accepted |
| ADR-004 | Runtime/SDK version to match existing solution | Avoids multi-targeting complexity; exact version is TODO pending solution inspection | Proposed |
| ADR-005 | Production `Program` class made `public partial` if needed | Required by `WebApplicationFactory` to reference the entry point assembly; minimal production code change | Proposed |

---

*All TODOs must be resolved before the first spec or plan document is authored against this constitution.*