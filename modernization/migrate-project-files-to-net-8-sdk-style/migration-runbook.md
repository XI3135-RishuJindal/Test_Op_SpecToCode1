# Migration Runbook: Migrate Project Files to .NET 8 SDK Style

## Pre-Migration Checklist

All items must be ✅ before proceeding.

- [ ] ✅ All source code is committed and pushed to the main repository.
- [ ] ✅ A stable backup of current project files (all `.csproj`, `.vbproj`, `.fsproj` and relevant `.sln` files) is archived.
- [ ] ✅ Current build process is green and reproducible locally and in CI.
- [ ] ✅ Installed `.NET 8 SDK` (run `dotnet --version` to verify; should report 8.x.x).
- [ ] ✅ Inventory of all project files to be migrated is documented.
- [ ] ✅ There is a rollback plan (see below section).
- [ ] ✅ Stakeholders notified of scheduled migration window.

---

## Environment Setup

Follow these steps to prepare both local and CI environments:

1. **Install .NET 8 SDK**

   ```sh
   # Linux/macOS
   wget https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh
   chmod +x dotnet-install.sh
   ./dotnet-install.sh --version 8.0.0

   # Windows (powershell)
   iex "& { $(irm https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.ps1) } -Version 8.0.0"
   ```

2. **Set global.json (if using multiple SDK versions)**
   
   ```sh
   dotnet --list-sdks
   echo '{ "sdk": { "version": "8.0.0" } }' > global.json
   ```

3. **CI Configuration**
   
   - Update CI build definition YAML/pipeline to use .NET 8 SDK on all build/test jobs.

---

## Step-by-Step Migration Procedure

### 1. Backup Project Files

- **Action:** Copy all project (`.csproj`, `.vbproj`, `.fsproj`) and solution files to a safe location.
- **Expected outcome:** Restorable backup is available.
- **Verification command:**
  
  ```sh
  cp *.csproj ../backup/
  ```
- **Rollback action:** Restore backup files.

---

### 2. Convert Project File(s) to SDK Style

- **Action:** For each project file:
  - Open the file.
  - Remove legacy XML elements (e.g., `<Import>`, `<TargetFrameworkVersion>`, `<Compile Include=...>`).
  - Replace root element with SDK-style form: `<Project Sdk="Microsoft.NET.Sdk">`
  - Add `<TargetFramework>net8.0</TargetFramework>` (or `net8.0-windows`/`net8.0` as appropriate).
  - Remove explicit `<Reference>` and `<Compile Include>` for files included by default.
  - Migrate NuGet package references to `<PackageReference>` form if not already used.

- **Expected outcome:** Project files use minimal, clean, SDK-style format compatible with .NET 8.

- **Verification command:**
  
  ```sh
  # Find SDK style in all project files
  grep 'Project Sdk="Microsoft.NET.Sdk' *.csproj
  # TargetFramework should now contain net8.0
  grep '<TargetFramework>' *.csproj
  ```

- **Rollback action:** Restore the original project file(s) from backup.

---

### 3. Update Solution File (if present)

- **Action:** Run `dotnet sln` commands to ensure all migrated projects are included properly.

  ```sh
  dotnet sln YourSolution.sln add path/to/YourProject.csproj
  ```

- **Expected outcome:** Solution references updated projects in SDK-style.

- **Verification command:**
  
  ```sh
  dotnet sln list
  ```

- **Rollback action:** Restore the original solution file from backup.

---

### 4. Build and Test Locally

- **Action:** Run clean build and test with .NET 8.

  ```sh
  dotnet clean
  dotnet build
  dotnet test
  ```

- **Expected outcome:** Solution builds and tests pass on .NET 8 SDK.

- **Verification command:**
  
  ```sh
  dotnet build --no-restore
  dotnet test --no-build
  ```

- **Rollback action:** Revert project files and/or dependency changes.

---

### 5. Commit and Push Changes

- **Action:** Commit all migrated project and solution files.

  ```sh
  git add *.csproj *.sln
  git commit -m "Migrate project files to .NET 8 SDK style"
  git push
  ```

- **Expected outcome:** Main branch is updated with migrated files.

- **Verification command:**
  
  ```sh
  git log -n 1
  ```

- **Rollback action:** Revert the commit and push.

---

### 6. Update Build & CI Pipelines

- **Action:** Ensure CI uses `.NET 8 SDK` for build/test.

- **Expected outcome:** CI build passes using new project format.

- **Verification command:** Check CI dashboard for build/test completion.

- **Rollback action:** Revert CI pipeline config and project file changes.

---

## Verification & Smoke Tests

- **Local smoke test:**
  
  ```sh
  dotnet build
  dotnet test
  dotnet run --project path/to/yourProject.csproj
  ```

- **CI build and test:** Confirm green builds on all relevant branches.

- **Manual validation:** Launch app (if applicable) and verify core features function correctly.

---

## Rollback Procedure

**If any step fails or after deployment issues occur, execute the following:**

1. **Stop ongoing deployments.**
2. **Restore project and solution files:**

   ```sh
   git checkout path/to/backup/*.csproj
   git checkout path/to/backup/*.sln
   ```

3. **Revert CI/CD configuration to use previous SDK/version.**
4. **Rebuild and test:**

   ```sh
   dotnet clean
   dotnet build
   dotnet test
   ```

5. **Communicate rollback to stakeholders.**

---

## Post-Migration Monitoring

- **Build pipeline:** Monitor all build and test runs for failures.
- **Error logs:** Monitor application logs for runtime exceptions, missing dependencies, or startup errors.
- **Metrics:** Watch app/service metrics for unusual errors or traffic drop.
- **Alerts:** Set alerts for build/test failures and unusual log entries for 48h post-migration.

---

## Known Issues & Workarounds

- **Issue:** Some third-party or legacy NuGet packages may not support .NET 8 SDK style projects.
  - **Workaround:** Check for compatible versions. If unavailable, consider multi-targeting or isolating legacy dependencies.

- **Issue:** Custom build targets/tasks may be lost during conversion.
  - **Workaround:** Manually migrate necessary tasks using `Directory.Build.targets`/`props` or MSBuild SDK-style extensions.

- **Issue:** Local tooling may cache old project artifacts.
  - **Workaround:** Always perform a `dotnet clean` before and after migration.

---