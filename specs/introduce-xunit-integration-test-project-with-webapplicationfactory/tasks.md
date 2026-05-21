# TASKS: Introduce xUnit Integration Test Project with WebApplicationFactory

## Prerequisites

- [ ] [XS] Verify .NET SDK version installed locally supports `WebApplicationFactory<T>` (requires .NET 6+ / ASP.NET Core 6+) by running `dotnet --version` and confirming compatibility with the target project's `<TargetFramework>` in the main project's `.csproj`
- [ ] [XS] Confirm the main ASP.NET Core project exposes a `Program` class (or partial class) accessible to the test project — check `Program.cs` for `public partial class Program {}` or equivalent visibility
- [ ] [XS] Confirm NuGet package source access (nuget.org or internal feed) is available for `Microsoft.AspNetCore.Mvc.Testing`, `xunit`, and `xunit.runner.visualstudio`

---

## Phase 1 — Preparation

- [ ] [XS] Identify the main ASP.NET Core project name, assembly name, and `.csproj` path to use as the `TEntryPoint` for `WebApplicationFactory<T>`
- [ ] [XS] Create a new xUnit test project via `dotnet new xunit -n <MainProjectName>.IntegrationTests` in the `/tests` (or equivalent) directory of the repository
- [ ] [S] Add the new `<MainProjectName>.IntegrationTests.csproj` to the solution file via `dotnet sln add` and verify it appears under the correct solution folder
- [ ] [XS] Add a `<ProjectReference>` to the main ASP.NET Core project inside `<MainProjectName>.IntegrationTests.csproj`
- [ ] [XS] Add NuGet package references `Microsoft.AspNetCore.Mvc.Testing`, `xunit`, `xunit.runner.visualstudio`, and `coverlet.collector` to `<MainProjectName>.IntegrationTests.csproj` with versions pinned to match the main project's ASP.NET Core version

---

## Phase 2 — Core Upgrade

- [ ] [S] Add `public partial class Program {}` at the bottom of `Program.cs` in the main project (if not already present) to make the entry point accessible to the test assembly
- [ ] [S] Create `CustomWebApplicationFactory.cs` in `<MainProjectName>.IntegrationTests` implementing `WebApplicationFactory<Program>`, with a `ConfigureWebHost` override stub for future test-specific service replacements (e.g., in-memory database, mock services)
- [ ] [S] Create `IntegrationTestBase.cs` in `<MainProjectName>.IntegrationTests` as a base class implementing `IClassFixture<CustomWebApplicationFactory>`, exposing a shared `HttpClient` created via `Factory.CreateClient()`
- [ ] [M] Write a first smoke-test class `HealthCheckTests.cs` (or equivalent endpoint test) in `<MainProjectName>.IntegrationTests` that inherits `IntegrationTestBase`, sends a GET request to a known route (e.g., `/health` or `/`), and asserts `HttpStatusCode.OK` — confirming the factory wires up correctly end-to-end

---

## Phase 3 — Testing & Validation

- [ ] [XS] Run `dotnet build <MainProjectName>.IntegrationTests.csproj` and resolve any compilation errors related to `Program` visibility or missing package references
- [ ] [S] Run `dotnet test <MainProjectName>.IntegrationTests.csproj --logger trx` and confirm the smoke test passes; capture the `.trx` output as the baseline test report
- [ ] [XS] Verify no existing unit test projects are broken by the `public partial class Program {}` change by running `dotnet test` across the full solution

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline definition (e.g., `.github/workflows/*.yml`, `azure-pipelines.yml`, or equivalent) to include a `dotnet test` step targeting `<MainProjectName>.IntegrationTests.csproj`, placed after the build step and before any deployment stages
- [ ] [XS] Ensure the CI pipeline step passes `--no-build` if a prior build step already compiles the solution, and sets `--configuration Release` to match the main build configuration

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `README.md` (or update the existing one) inside `<MainProjectName>.IntegrationTests/` documenting how to run integration tests locally, how to extend `CustomWebApplicationFactory` to swap services, and the naming convention for test classes
- [ ] [XS] Update the top-level repository `CHANGELOG.md` or equivalent with an entry noting the addition of the xUnit integration test project and `WebApplicationFactory` infrastructure