# Migration Runbook: ASP.NET Web API to ASP.NET Core Web API

## Pre-Migration Checklist

All items below must be ✅ before proceeding:

- [ ] ✅ All project dependencies and libraries are documented.
- [ ] ✅ A full **backup** of the source repository is stored in a safe location.
- [ ] ✅ All critical business logic is covered by tests; existing tests are passing.
- [ ] ✅ Stakeholders notified of scheduled maintenance window.
- [ ] ✅ Access to necessary infrastructure, deployment, and backup tools is verified.
- [ ] ✅ Migration has been reviewed and signed off by tech lead/architect.
- [ ] ✅ CI/CD pipeline is green; able to run .NET Framework and .NET Core jobs as needed.

---

## Environment Setup

### Required Tooling

- **.NET 6/7/8 SDK** (as per target ASP.NET Core version)
- **Visual Studio 2022+** or **VS Code** with C# extension
- Up-to-date **NuGet** client
- Access to repository and current CI/CD pipeline

### Commands/Steps

**Local:**

```bash
# Install .NET SDK
# For example, for .NET 8:
winget install Microsoft.DotNet.SDK.8

# Confirm installation
dotnet --version

# Prepare local clone
git clone <REPO_URL>
cd <REPO_DIR>
```

**CI:**

- Install .NET SDK in build agents (update pipeline YAML/editor).
- Ensure agents have required test runners.

---

## Step-by-Step Migration Procedure

### 1. Create ASP.NET Core Web API Project Skeleton

- **Action:** Initialize a new ASP.NET Core Web API project in a new folder in the repo.
- **Expected outcome:** New project files (e.g., `.csproj`, `Program.cs`, `Controllers/`) added.
- **Verification command:**
  ```bash
  dotnet run --project <NewProjectPath>
  # Should show a message: "Now listening on: https://localhost:xxxx"
  ```
- **Rollback:** Delete the created project files and folders.

---

### 2. Incremental Port of Controllers and Models

- **Action:** Copy and adapt existing Web API controllers and model classes into the ASP.NET Core project, refactoring for compatibility (e.g., namespace changes, attribute updates).
- **Expected outcome:** All API endpoints are present in the Core project; code builds without errors.
- **Verification command:**
  ```bash
  dotnet build <NewProjectPath>
  ```
- **Rollback:** Remove migrated files from the new project.

---

### 3. Update Dependency Injection and Middleware

- **Action:** Migrate any `Global.asax` startup code, filters, and dependency registrations to `Program.cs`/`Startup.cs` in ASP.NET Core idioms.
- **Expected outcome:** Necessary services are registered, middleware is configured, and old lifecycle code is replaced.
- **Verification command:**
  ```bash
  dotnet run --project <NewProjectPath>
  # Hit a migrated endpoint; confirm functionality.
  ```
- **Rollback:** Restore previous `Program.cs`/`Startup.cs` content.

---

### 4. Adapt Authentication & Authorization

- **Action:** Refactor authentication/authorization logic using ASP.NET Core identity and middleware.
- **Expected outcome:** All protected endpoints behave as expected; authentication flows work.
- **Verification command:**
  - Curl or Postman requests to protected endpoints; confirm correct responses (401/403 for unauthenticated, 200 for valid credentials).
- **Rollback:** Revert changes to auth configuration files and code.

---

### 5. Migrate/Rewrite Configuration Files

- **Action:** Replace `web.config` settings with `appsettings.json` and ASP.NET Core configuration features.
- **Expected outcome:** All configuration is loaded correctly, settings are accessible in code.
- **Verification command:**
  ```bash
  dotnet run --project <NewProjectPath>
  # Confirm correct behavior that depends on config.
  ```
- **Rollback:** Revert configuration edits.

---

### 6. Update Unit and Integration Tests

- **Action:** Port or rewrite existing tests to use `xUnit`, `NUnit`, or supported test frameworks for .NET Core.
- **Expected outcome:** All critical endpoints and logic are covered with passing tests.
- **Verification command:**
  ```bash
  dotnet test <NewTestProjectPath>
  ```
- **Rollback:** Restore previous test project structure/code.

---

### 7. CI/CD Pipeline Update

- **Action:** Update the build and deployment pipeline to target .NET Core projects.
- **Expected outcome:** CI jobs build, test, and publish new ASP.NET Core project artifacts.
- **Verification command:**
  - Trigger manual/PR build in CI, ensure green checks.
- **Rollback:** Revert CI/CD pipeline configuration.

---

### 8. Cutover Deployment

- **Action:** Swap existing API deployment reference to the new ASP.NET Core artifact.
- **Expected outcome:** API endpoints are served by ASP.NET Core app in target environment.
- **Verification command:**
  - Curl/Postman key endpoints; confirm status codes and payloads.
- **Rollback:** Redeploy previous (legacy) API artifact.

---

## Verification & Smoke Tests

Run the following for final validation:

```bash
# Build and launch
dotnet build <NewProjectPath>
dotnet run --project <NewProjectPath>
```

- Exercise all endpoints (GET, POST, PUT, DELETE) via Curl/Postman.
- Validate protected endpoints using expected authentication tokens/credentials.
- Verify configuration values from `appsettings.json` are respected.
- Run test suite:
  ```bash
  dotnet test
  ```
- Confirm logs output to expected location.

---

## Rollback Procedure

If migration introduces blocking issues:

1. **Stop the ASP.NET Core instance** in all environments:
   ```bash
   # Stop new app service/container
   ```
2. **Redeploy legacy ASP.NET Web API artifact.**
   - Use existing CI/CD pipeline for previous builds, or manually redeploy.
3. **Restore `web.config` and old configuration.**
   - Confirm reverted settings/paths.
4. **Validate endpoints are responding as before.**
   - Run smoke tests on legacy endpoints.
5. **Notify stakeholders of rollback completion.**
6. **Document root cause and create follow-up action ticket.**

---

## Post-Migration Monitoring

For 24–48 hours post-deployment, monitor:

- **API health endpoints** (`/health`, `/status`) for 200 OK.
- **Application logs** for errors or exceptions (configure logging for Console/File/Cloud, as appropriate).
- **Response times** and latencies (APM or Application Insights if available).
- **Authentication/Authorization failures** in logs.
- **CI/CD pipeline green status** for new builds/deploys.
- **User feedback or bug reports.**

Recommended Alerts:

- High error rate (HTTP 5xx/4xx spikes)
- Service restarts or crashes
- Authentication/authorization failures

---

## Known Issues & Workarounds

- **N/A — not applicable to this task**
