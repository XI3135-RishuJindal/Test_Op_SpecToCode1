# CONSTITUTION

## Project Identity

**Name:** xUnit Integration Test Project — WebApplicationFactory Introduction

**Purpose:** Introduce a structured xUnit integration test project to the existing solution, leveraging ASP.NET Core's `WebApplicationFactory<T>` to enable realistic, in-process HTTP-level integration testing against the application's actual startup pipeline.

**High-Level Goal:** Deliver a working, maintainable integration test project that validates end-to-end request/response behaviour without requiring an external running server, establishing a repeatable testing baseline for future development.

---

## Guiding Principles

1. **Prefer `WebApplicationFactory<T>` over external test servers** because in-process hosting eliminates environment-setup overhead and keeps tests deterministic and portable across CI and local machines.
2. **Prefer a dedicated test project over embedding integration tests in unit test projects** because separation of concerns prevents slow I/O-bound tests from blocking fast unit-test feedback loops.
3. **Prefer explicit test fixture lifetime management (`IClassFixture<>`) over per-test factory instantiation** because spinning up the host once per class reduces test-suite execution time and resource contention.
4. **Prefer environment-specific configuration overrides (`"Testing"` environment) over mutating production configuration** because test isolation must not risk leaking test doubles or fake credentials into other environments.
5. **Prefer clearly named, single-responsibility test classes over large omnibus test files** because discoverability and maintainability are critical when the test suite grows beyond the initial scope.

---

## Constraints

- **Timeline / Effort:** Effort ceiling follows the *moderate* upgrade option. No scope beyond introducing the integration test project and demonstrating it with representative baseline tests is authorised within this increment.
- **Technology Mandates:**
  - Test framework: **xUnit** (mandatory per task specification).
  - Host factory: **`Microsoft.AspNetCore.Mvc.Testing` / `WebApplicationFactory<T>`** (mandatory per task specification).
  - Runtime/language version: TODO — confirm target .NET version from project's existing solution file before selecting NuGet package versions.
  - Build tool: TODO — confirm MSBuild / `dotnet CLI` conventions in use.
- **Scope Freeze:** This task covers *introduction* only. Migrating or rewriting existing tests, adding load/performance tests, or changing application source code beyond what is minimally required to support testability are out of scope.

---

## Quality Standards

- **Coverage Floor:** The new integration test project must contain a minimum of **one passing smoke test** (e.g., `GET /health` or equivalent) before the work is considered complete. Additional coverage targets are TODO pending identification of critical endpoints.
- **Build Gate:** The integration test project must compile and all tests must pass in CI (`dotnet test`) with zero failures and zero skipped tests at merge time.
- **Code Review:** All test project files require at least **one peer review approval** before merging to the main branch.
- **Documentation:** A `README` section (or inline XML doc on the fixture class) must explain how to run the integration tests locally and how to add new test cases.
- **No Flakiness Policy:** Any test that fails intermittently must be quarantined (marked `[Trait("Category", "Quarantine")]`) and tracked as a defect before the PR is merged.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use xUnit as the integration test framework | Explicitly required by the task specification | Accepted |
| ADR-002 | Use `WebApplicationFactory<T>` for host bootstrapping | Explicitly required by the task specification; provides in-process ASP.NET Core hosting with no external dependencies | Accepted |
| ADR-003 | Create a separate `*.IntegrationTests` project rather than adding to an existing test project | Keeps integration tests isolated from unit tests; aligns with Principle 2 | Accepted |
| ADR-004 | Target .NET version for the test project | TODO — must match the application project's target framework once confirmed | Proposed |
| ADR-005 | Strategy for test database / external dependencies (real vs. fake) | TODO — depends on application's data layer, which is not yet analysed | Proposed |