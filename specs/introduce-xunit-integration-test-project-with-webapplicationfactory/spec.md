# Spec: Introduce xUnit Integration Test Project with WebApplicationFactory

## Summary

This spec covers the introduction of a new xUnit-based integration test project that uses `WebApplicationFactory` to host the application under test in-process. The expected outcome is a dedicated integration test project wired into the existing build and CI pipeline, enabling end-to-end HTTP-level tests against the real application stack without requiring an external deployment.

## Motivation

The codebase currently lacks integration test coverage at the HTTP boundary. Unit tests alone cannot verify middleware ordering, routing, authentication pipelines, serialization contracts, or database interactions as a composed system. Introducing `WebApplicationFactory`-based integration tests addresses this gap by:

- Providing confidence that components work correctly when assembled together, reducing regression risk during future modernization work.
- Establishing a repeatable, CI-friendly test harness that does not depend on external infrastructure.
- Supporting the medium-urgency modernization effort by creating a safety net before further upgrades are applied.
- Aligning with current ASP.NET Core testing best practices, reducing long-term maintenance burden.

Upgrade urgency is rated **medium** per the tech analysis.

## Current State

- There is no existing integration test project in the solution.
- No `WebApplicationFactory` usage exists anywhere in the codebase.
- The existing test coverage, if any, is limited to unit tests without HTTP-level harness.
- The application entry point, startup configuration, service registrations, and middleware pipeline are defined in the main application project (specific class names and config keys are **TODO** — not provided in context).
- CI pipeline configuration exists but does not include an integration test execution step (**TODO** — confirm CI tooling and pipeline file location).

## Proposed Changes

For each affected component, the changes are described below.

| Component | Before | After | Breaking? |
|---|---|---|---|
| Solution structure | No integration test project | New xUnit integration test project added to solution | N |
| Test dependencies | N/A | xUnit, xUnit runner, `Microsoft.AspNetCore.Mvc.Testing` (WebApplicationFactory) added to new project | N |
| CI pipeline | Runs unit tests only (TODO — confirm) | Runs both unit tests and integration tests | N |
| Application entry point / startup | Unchanged | Must be accessible to `WebApplicationFactory` (may require `InternalsVisibleTo` or a public entry point — TODO confirm current accessibility) | N |
| Test data / environment configuration | N/A | Integration test project uses a test-specific environment configuration (e.g., in-memory database or test doubles for external dependencies — TODO confirm strategy) | N |

**What is added:**
- A new integration test project targeting the same runtime as the main application.
- A custom `WebApplicationFactory` subclass (or direct usage) that overrides service registrations as needed for test isolation.
- At least one smoke-test verifying the application starts and a known endpoint returns an expected HTTP status code.

**What is removed:**
- Nothing is removed from the existing codebase.

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Application entry point visibility | If the entry point class is `internal`, `WebApplicationFactory` cannot reference it from the test project | Expose entry point or add `InternalsVisibleTo` attribute to the main project — TODO confirm current visibility |
| Environment-specific configuration | Integration tests may inadvertently connect to production/staging resources if environment is not overridden | Test project must set environment to a dedicated test environment and override external dependencies — TODO confirm dependency list |
| Shared test infrastructure | If other test projects exist, they may need to be reorganized to avoid duplication | TODO — confirm existing test project structure |

## Acceptance Criteria

1. **Given** the solution is checked out and dependencies are restored, **when** the integration test project is built, **then** the build completes with zero errors and zero warnings treated as errors.

2. **Given** the integration test project exists, **when** the test runner executes all tests in that project, **then** all tests pass and results are reported in a format consumable by the CI pipeline (e.g., TRX or JUnit XML).

3. **Given** a `WebApplicationFactory` instance is created in a test, **when** an HTTP GET request is sent to the application's health-check or root endpoint, **then** the response HTTP status code is `200 OK` (or the documented expected status — TODO confirm endpoint).

4. **Given** the integration tests are running, **when** any external dependency (database, message broker, third-party API) would normally be contacted, **then** the test harness uses a test double or in-memory substitute so no real external calls are made (TODO — confirm which external dependencies exist).

5. **Given** the CI pipeline runs on a pull request, **when** the pipeline executes, **then** the integration test project is compiled and all integration tests are executed as a required step before merge is permitted.

6. **Given** a test in the integration test project fails, **when** the CI pipeline reports results, **then** the failure is surfaced with sufficient diagnostic output (test name, failure message, and stack trace) to identify the root cause without running locally.

7. **Given** the integration test project is added to the solution, **when** the solution is opened or built, **then** no existing unit test project or application project requires modification to its build configuration (i.e., the addition is non-breaking to existing projects).

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact runtime version and target framework moniker to use for the new test project? | TODO | TODO |
| 2 | What is the application entry point class name and its current access modifier? | TODO | TODO |
| 3 | Which external dependencies (databases, queues, APIs) does the application use that must be stubbed during integration tests? | TODO | TODO |
| 4 | What CI tooling is in use (GitHub Actions, Azure DevOps, Jenkins, etc.) and where is the pipeline definition file? | TODO | TODO |
| 5 | Is there an existing health-check or known stable endpoint that can serve as the smoke-test target? | TODO | TODO |
| 6 | Should integration tests run against an in-memory database, a containerized database (e.g., Testcontainers), or a shared test database? | TODO | TODO |
| 7 | Are there existing test projects in the solution, and if so, is there shared test infrastructure (fixtures, helpers) that the new project should reuse? | TODO | TODO |
| 8 | What naming convention and solution folder structure should the new project follow? | TODO | TODO |