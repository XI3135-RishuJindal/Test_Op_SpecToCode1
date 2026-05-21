# Tasks: Create New ASP.NET Core 8 SDK-Style Project Structure

## Prerequisites

- [ ] [XS] Verify .NET 8 SDK is installed (run `dotnet --version`, confirm `8.x.x`) on all developer machines and CI agents
- [ ] [XS] Verify Visual Studio 2022 (17.8+) or JetBrains Rider (2023.3+) is available for SDK-style project support
- [ ] [XS] Confirm repository write access and branch protection rules allow creation of a feature branch
- [ ] [XS] Confirm NuGet feed access (nuget.org or internal feed) is reachable from the build environment

---

## Phase 1 — Preparation

- [ ] [XS] Create feature branch `feature/aspnetcore8-sdk-project-structure` from the default branch in the repository
- [ ] [S] Document the intended project layout (solution file, project folders, test project) in a `STRUCTURE.md` file at the repository root before any scaffolding begins
- [ ] [XS] Confirm target namespace, assembly name, and root namespace conventions with the team and record them in `STRUCTURE.md`

---

## Phase 2 — Core Upgrade

- [ ] [S] Scaffold new solution file using `dotnet new sln -n <SolutionName>` at the repository root
- [ ] [S] Scaffold the main web application project using `dotnet new webapi -n <ProjectName> --framework net8.0` and add it to the solution with `dotnet sln add`
- [ ] [XS] Set `<TargetFramework>net8.0</TargetFramework>` and `<Nullable>enable</Nullable>` and `<ImplicitUsings>enable</ImplicitUsings>` in the main `.csproj` file
- [ ] [XS] Remove any auto-generated placeholder files (`WeatherForecast.cs`, `WeatherForecastController.cs`) from the scaffolded project
- [ ] [S] Configure `Program.cs` with the minimal hosting model entry point, registering `WebApplication.CreateBuilder`, service collection, and middleware pipeline stubs
- [ ] [XS] Add a `Directory.Build.props` file at the solution root to centralise shared MSBuild properties (`<Nullable>`, `<ImplicitUsings>`, `<LangVersion>latest</LangVersion>`)
- [ ] [XS] Add a `Directory.Packages.props` file at the solution root and enable Central Package Management (`<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`)
- [ ] [S] Scaffold a unit test project using `dotnet new xunit -n <ProjectName>.Tests --framework net8.0` and add it to the solution with `dotnet sln add`
- [ ] [XS] Set `<TargetFramework>net8.0</TargetFramework>` and add `<IsPackable>false</IsPackable>` in `<ProjectName>.Tests.csproj`
- [ ] [XS] Add a project reference from `<ProjectName>.Tests.csproj` to the main project using `dotnet add reference`
- [ ] [XS] Create a `.editorconfig` file at the solution root with C# formatting rules aligned to the team's coding standards
- [ ] [XS] Create a `global.json` file at the repository root pinning `sdk.version` to the target .NET 8 SDK patch version

---

## Phase 3 — Testing & Validation

- [ ] [XS] Run `dotnet build <SolutionName>.sln` and confirm zero errors and zero warnings on a clean checkout
- [ ] [XS] Run `dotnet test <SolutionName>.sln` and confirm the placeholder xUnit test passes, establishing a green baseline
- [ ] [XS] Run `dotnet publish -c Release` on the main project and confirm the output directory is populated correctly under `bin/Release/net8.0/publish/`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a CI pipeline definition (`.github/workflows/build.yml` for GitHub Actions, or equivalent) that runs `dotnet restore`, `dotnet build`, and `dotnet test` targeting `net8.0` on `ubuntu-latest` with the `actions/setup-dotnet@v4` action pinned to .NET 8
- [ ] [XS] Set the `DOTNET_SKIP_FIRST_TIME_EXPERIENCE` and `DOTNET_NOLOGO` environment variables in the pipeline definition to reduce noise in CI logs
- [ ] [XS] Add a `.dockerignore` file excluding `bin/`, `obj/`, and `.git/` directories
- [ ] [S] Add a `Dockerfile` at the repository root using `mcr.microsoft.com/dotnet/aspnet:8.0` as the runtime image and `mcr.microsoft.com/dotnet/sdk:8.0` as the build image, with a multi-stage build targeting the published output

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update (or create) `README.md` with prerequisites (`.NET 8 SDK`), build instructions (`dotnet build`), run instructions (`dotnet run`), and test instructions (`dotnet test`)
- [ ] [XS] Add a `CHANGELOG.md` entry recording the creation of the ASP.NET Core 8 SDK-style project structure with the date and branch name
- [ ] [XS] Open a pull request from `feature/aspnetcore8-sdk-project-structure` to the default branch, request review, and confirm CI pipeline passes before merge