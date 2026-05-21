# TASKS: Introduce xUnit Integration Test Project with WebApplicationFactory

## Prerequisites

- [ ] [XS] Verify .NET SDK version installed locally supports `WebApplicationFactory<T>` (requires .NET 6+ / `Microsoft.AspNetCore.Mvc.Testing` ≥ 6.0) in developer environment setup
- [ ] [XS] Confirm the target ASP.NET Core web project name, assembly name, and solution file (`.sln`) path in the repository root
- [ ] [XS] Confirm NuGet feed access (nuget.org or internal feed) is available for restoring `xunit`, `xunit.runner.visualstudio`, and `Microsoft.AspNetCore.Mvc.Testing` packages

---

## Phase 1 — Preparation

- [ ] [XS] Create a new feature branch (e.g., `feature/integration-tests-webappfactory`) from the main branch in the repository
- [ ] [S] Audit the existing solution file (`.sln`) to identify the web host project entry point (the class that calls `CreateHostBuilder` or `WebApplication.CreateBuilder`) and record the fully-qualified type name for use as the `TEntryPoint` generic argument
- [ ] [XS] Record the current passing/failing state of any existing test projects as a baseline by running `dotnet test` and saving output to `docs/test-baseline-before.txt`

---

## Phase 2 — Core Upgrade

- [ ] [S] Create a new xUnit test project named `<WebProjectName>.IntegrationTests` using `dotnet new xunit -n <WebProjectName>.IntegrationTests` and add it to the solution with `dotnet sln add`
- [ ] [S] Add NuGet package references in `<WebProjectName>.IntegrationTests/<WebProjectName>.IntegrationTests.csproj`: `Microsoft.AspNetCore.Mvc.Testing`, `xunit`, `xunit.runner.visualstudio`, and `coverlet.collector` at versions compatible with the target .NET SDK
- [ ] [XS] Add a project reference from `<WebProjectName>.IntegrationTests.csproj` to the web host project (`.csproj`) so `TEntryPoint` is resolvable at compile time
- [ ] [XS] Set `<IsPackable>false</IsPackable>` and ensure `<Nullable>enable</Nullable>` and `<ImplicitUsings>enable</ImplicitUsings>` are configured in `<WebProjectName>.IntegrationTests.csproj`
- [ ] [M] Create `Infrastructure/CustomWebApplicationFactory.cs` inside the integration test project: implement `CustomWebApplicationFactory<TEntryPoint> : WebApplicationFactory<TEntryPoint>` with an override of `ConfigureWebHost(IWebHostBuilder builder)` that substitutes test-safe service registrations (e.g., in-memory database, stubbed external HTTP clients) via `builder.ConfigureTestServices(...)`
- [ ] [S] Create `Infrastructure/IntegrationTestBase.cs` implementing `IClassFixture<CustomWebApplicationFactory<TEntryPoint>>` to provide a shared `HttpClient` (created via `factory.CreateClient()`) and any common setup/teardown logic for test classes
- [ ] [S] Write a smoke-test class `Tests/HealthCheckTests.cs` with at least one `[Fact]` that calls a known endpoint (e.g., `/health` or `/`) via the shared `HttpClient` and asserts `HttpStatusCode.OK` to validate the factory wires up correctly
- [ ] [XS] Verify the integration test project builds and the smoke test passes locally with `dotnet test <WebProjectName>.IntegrationTests`

---

## Phase 3 — Testing & Validation

- [ ] [XS] Run `dotnet test --collect:"XPlat Code Coverage"` in `<WebProjectName>.IntegrationTests` and confirm no build errors or runtime exceptions from `WebApplicationFactory` startup
- [ ] [XS] Compare `dotnet test` output against `docs/test-baseline-before.txt` to confirm no regressions in pre-existing test projects
- [ ] [XS] Confirm the smoke test in `HealthCheckTests.cs` passes and that the `CustomWebApplicationFactory` correctly overrides services without affecting the production `Program.cs` / `Startup.cs`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Update the CI pipeline configuration (e.g., `.github/workflows/ci.yml`, `azure-pipelines.yml`, or equivalent) to include a `dotnet test` step targeting `<WebProjectName>.IntegrationTests` with `--no-build --verbosity normal`
- [ ] [XS] Ensure the CI pipeline step runs after the build step and that the integration test project is restored as part of `dotnet restore` on the solution file
- [ ] [XS] Add a CI environment variable or `appsettings.IntegrationTest.json` file in the test project to supply any required configuration values (connection strings, feature flags) needed by `CustomWebApplicationFactory` without hardcoding secrets

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry (or append to existing) describing the addition of the `<WebProjectName>.IntegrationTests` project and the `WebApplicationFactory`-based integration test pattern
- [ ] [S] Write a `docs/integration-testing-guide.md` covering: project structure, how to add new integration test classes using `IntegrationTestBase`, how to register additional test-double services in `CustomWebApplicationFactory`, and how to run tests locally
- [ ] [XS] Open a pull request from the feature branch, request review, and confirm CI pipeline passes the new integration test step before merging