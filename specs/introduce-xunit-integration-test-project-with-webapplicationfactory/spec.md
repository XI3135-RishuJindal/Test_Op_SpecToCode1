# Spec: Introduce xUnit Integration Test Project with WebApplicationFactory

## Summary

This spec covers the introduction of a new xUnit-based integration test project that uses `WebApplicationFactory` to host the application under test in-process. The expected outcome is a dedicated integration test project wired into the existing build and CI pipeline, enabling end-to-end HTTP-level tests against the real application stack without requiring an external running server.

## Motivation

- **Gap in test coverage:** The codebase currently lacks integration tests that exercise the full HTTP request/response pipeline, middleware, routing, and dependency injection composition. Unit tests alone cannot catch regressions at these layers.
- **Industry standard tooling:** `WebApplicationFactory<TEntryPoint>` (part of `Microsoft.AspNetCore.Mvc.Testing`) is the established, Microsoft-supported mechanism for in-process integration testing of ASP.NET Core applications. Adopting it aligns the project with current best practices.
- **Tech debt reduction:** Absence of integration tests is identified as existing tech debt in the modernization analysis. Introducing this project addresses that debt at medium urgency.
- **CI confidence:** Without integration tests, breaking changes to API contracts, middleware ordering, or DI registrations may go undetected until production. This project provides a CI gate for those scenarios.

## Current State

- **No integration test project exists.** There is no project in the solution dedicated to integration or end-to-end HTTP testing.
- **Test infrastructure:** TODO — the existing unit test project name, framework version, and runner configuration are not confirmed in the provided context.
- **Application entry point:** TODO — the specific entry point class/program used as `TEntryPoint` for `WebApplicationFactory` is not confirmed.
- **Build tool / CI pipeline:** TODO — the exact build tool (e.g., MSBuild, `dotnet CLI`) and CI system are not confirmed; integration of the new project into CI must be verified once confirmed.
- **Existing test conventions:** TODO — naming conventions, shared fixtures, and test output configuration used in any existing test projects are not confirmed.

## Proposed Changes

For each affected component:

| Component | Before | After | Breaking? |
|---|---|---|---|
| Solution structure | No integration test project | New xUnit integration test project added to solution | N |
| Test dependencies | N/A | `Microsoft.AspNetCore.Mvc.Testing` package reference added to new project | N |
| xUnit runner | N/A | xUnit and xUnit runner packages added to new project | N |
| CI pipeline | Runs existing test projects only | Updated to also execute the new integration test project | N |
| Application project | No `InternalsVisibleTo` or test-host configuration | May require exposure of entry point to test project | TODO — confirm if breaking |
| Shared test fixtures | N/A | `WebApplicationFactory`-based fixture introduced in new project | N |

### What is added
- A new integration test project targeting the same runtime as the main application.
- A `WebApplicationFactory<TEntryPoint>` fixture class providing an `HttpClient` configured against the in-process test server.
- At least one smoke-test verifying the application starts and a known endpoint returns an expected HTTP status code.
- Project reference from the new test project to the application-under-test project.

### What is removed
- Nothing is removed from existing projects.

### What changes
- The solution file is updated to include the new project.
- The CI pipeline configuration is updated to include the new project in the test execution step.

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Application entry point exposed to test project | Requires the entry point type to be accessible from the test assembly | Add `InternalsVisibleTo` attribute or make the entry point `public`; TODO — confirm exact requirement based on application structure |
| CI pipeline test step updated | Existing test runs are unaffected; new project is additive | No migration required for callers; CI owners must verify pipeline syntax |
| TODO — any custom `WebApplicationFactory` overrides needed (e.g., replacing external services, databases) | Could affect application startup configuration | TODO — define environment-specific overrides once application dependencies are confirmed |

## Acceptance Criteria

1. **Given** the solution is checked out and dependencies are restored, **when** the build command is executed, **then** the new integration test project compiles without errors or warnings.

2. **Given** the integration test project is built, **when** the test runner executes all tests in the new project, **then** all tests pass and the runner exits with a zero exit code.

3. **Given** the `WebApplicationFactory` fixture is initialized, **when** a test requests a known healthy endpoint (e.g., a health-check or root route) via the factory-provided `HttpClient`, **then** the response HTTP status code is in the 2xx range.

4. **Given** the CI pipeline runs on a pull request, **when** the pipeline executes the test stage, **then** the integration test project is included in the test execution and its results are reported alongside existing test results.

5. **Given** the integration test project exists in the solution, **when** the solution is opened or built, **then** no existing unit test project is modified, broken, or has its test results affected.

6. **Given** a test that intentionally calls a non-existent route, **when** the `HttpClient` sends the request, **then** the response status code is `404 Not Found`, confirming the test server is routing correctly and not returning a default fallback for all requests.

7. **Given** the `WebApplicationFactory` fixture is used across multiple tests in the same test class, **when** those tests run, **then** the factory is instantiated once per class (using `IClassFixture<>`) and disposed after all tests in the class complete, verified by observing no duplicate startup log entries per class.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact runtime version and SDK version targeted by the main application? This determines the `Microsoft.AspNetCore.Mvc.Testing` package version to reference. | TODO | TODO |
| 2 | What is the application entry point class name to be used as `TEntryPoint` in `WebApplicationFactory<TEntryPoint>`? | TODO | TODO |
| 3 | Does the entry point need to be made `public` or have `InternalsVisibleTo` added? | TODO | TODO |
| 4 | Are there external dependencies (database, message broker, external APIs) that must be stubbed or replaced in the test host? If so, what is the strategy (in-memory, test doubles, containers)? | TODO | TODO |
| 5 | What is the CI system (e.g., GitHub Actions, Azure DevOps, Jenkins) and what changes are needed to include the new project in the test stage? | TODO | TODO |
| 6 | What naming convention should the new project follow to be consistent with existing projects in the solution? | TODO | TODO |
| 7 | Are there existing test helper utilities or shared fixtures in the current test project that should be reused or referenced by the new integration test project? | TODO | TODO |
| 8 | Is there a code coverage requirement that must also be satisfied by the integration test project? | TODO | TODO |