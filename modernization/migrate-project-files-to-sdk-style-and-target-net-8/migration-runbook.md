# Migration Runbook: Migrate Project Files to SDK-Style and Target .NET 8

---

## Pre-Migration Checklist

All items in this section **must** be ✅ before proceeding.

- [ ] ✅ Current branch is up-to-date with main/master.
- [ ] ✅ All tests pass in the current branch (before migration).
- [ ] ✅ All existing project files are version-controlled and committed.
- [ ] ✅ A backup branch for the current state has been created.
- [ ] ✅ The team has reviewed and approved the migration plan.
- [ ] ✅ .NET 8 SDK is installed locally and on CI/CD agents.
- [ ] ✅ Any custom build targets or tasks are documented.
- [ ] ✅ Inventory of all project references and NuGet packages is complete.

---

## Environment Setup

### Local Environment

1. **Install .NET 8 SDK**
   ```bash
   dotnet --list-sdks
   ```
   - Verify that `8.x.x` appears in the list. If not:
   ```bash
   # Visit https://dotnet.microsoft.com/en-us/download/dotnet/8.0 and install the latest SDK
   ```

2. **Restore tools/packages**
   ```bash
   dotnet restore
   ```

### CI/CD Updates

1. **Update CI/CD configuration** (e.g., Dockerfile, GitHub Actions, Azure Pipelines, etc.)  
   - Ensure all build/test environments use .NET 8 SDK.
   - Example for GitHub Actions:
     ```yaml
     - name: Setup .NET
       uses: actions/setup-dotnet@v3
       with:
         dotnet-version: '8.0.x'
     ```
2. **Test pipeline with .NET 8**  
   - Run a test job to confirm agents have .NET 8 available.

---

## Step-by-Step Migration Procedure

1. **Backup Current Project Files**
   - **Action:** Create a migration branch and copy current `.csproj`, `.fsproj`, `.vbproj` files to a backup directory.
   - **Expected outcome:** Project files safely backed up in version control.
   - **Verification command:**  
     ```bash
     git status
     # Ensure backup directory and files are present and staged
     ```
   - **Rollback action:** Revert to backup project files in case migration fails.

2. **Upgrade Project File Format to SDK-Style**
   - **Action:** Replace legacy project file content with SDK-style format.  
     - At the top of each project file (e.g., for C#):
       ```xml
       <Project Sdk="Microsoft.NET.Sdk">
         <PropertyGroup>
           <TargetFramework>net8.0</TargetFramework>
         </PropertyGroup>
         <!-- Add additional properties/references as needed -->
       </Project>
       ```
     - Migrate references, assembly info, and custom build actions as per Microsoft documentation ([guidance](https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview)).
   - **Expected outcome:** Project files are in SDK-style format, referencing `net8.0`.
   - **Verification command:**
     ```bash
     cat *.csproj | grep "<TargetFramework>"
     # Should report: <TargetFramework>net8.0</TargetFramework>
     ```
   - **Rollback action:** Restore project files from backup directory.

3. **Restore NuGet Packages**
   - **Action:** Clean and restore all NuGet dependencies.
     ```bash
     dotnet clean
     dotnet restore
     ```
   - **Expected outcome:** All packages restored; no unresolved dependency errors.
   - **Verification command:**
     ```bash
     dotnet restore --verbosity minimal
     # Should complete without errors
     ```
   - **Rollback action:** Audit package references; revert if restore issues persist.

4. **Build the Solution**
   - **Action:** Build all projects targeting .NET 8.
     ```bash
     dotnet build --configuration Release
     ```
   - **Expected outcome:** Successful build with no errors.
   - **Verification command:** 
     ```bash
     dotnet build --configuration Release
     # Look for 'Build succeeded.'
     ```
   - **Rollback action:** Revert to backup project files.

5. **Run All Automated Tests**
   - **Action:** Run all existing unit/integration tests on .NET 8 build.
     ```bash
     dotnet test
     ```
   - **Expected outcome:** All test suites pass as prior to migration.
   - **Verification command:**
     ```bash
     dotnet test --no-build --verbosity minimal
     # Should report all tests passed
     ```
   - **Rollback action:** Revert to backup project files and previous target framework.

6. **Commit and Push Changes**
   - **Action:** Commit the migrated project files and push migration branch.
     ```bash
     git add .
     git commit -m "Migrate project files to SDK-style and .NET 8"
     git push origin <migration-branch>
     ```
   - **Expected outcome:** Changes tracked and available for PR/review.
   - **Verification command:**
     ```bash
     git log -1
     # Confirm commit message and diff
     ```
   - **Rollback action:** Revert commit or force-push the backup branch.

---

## Verification & Smoke Tests

- **Application/Library Build:**
  ```bash
  dotnet build --configuration Release
  ```
  - Output: Build succeeds without errors.

- **Dependency Validation:**
  ```bash
  dotnet list package --outdated
  ```
  - Output: Confirm package compatibility with .NET 8.

- **Smoke Test Application Execution:**
  - For applications:
    ```bash
    dotnet run --configuration Release
    ```
    - Observe for startup/logging output.
  - For libraries:
    - Run example/console or unit tests as above.

- **CI/CD Passes:**
  - Confirm all CI jobs pass (build, test, deploy).

---

## Rollback Procedure

1. **Reset Project Files**
   - **Action:** Restore legacy project files from backup directory.
     ```bash
     git checkout <backup-branch>
     git checkout HEAD -- <path-to-project-files>
     ```
2. **Restore Original Target Frameworks**
   - **Action:** Replace `<TargetFramework>net8.0</TargetFramework>` with previous framework version(s) in project files.
3. **Restore Build/CI Config**
   - **Action:** Revert any CI/CD changes to use previous .NET SDK version.
4. **Restore NuGet Packages**
   - **Action:** Re-run `dotnet restore` with previous settings.
5. **Validate Rollback**
   - **Action:** Build and test to confirm functionality is restored.
     ```bash
     dotnet build
     dotnet test
     ```
6. **Push Rollback State**
   - **Action:** Commit and push rollback to version control.
     ```bash
     git add .
     git commit -m "Rollback SDK-style/.NET 8 migration"
     git push origin <branch>
     ```

---

## Post-Migration Monitoring

- **Build Pipeline Status**
  - Monitor CI builds for all environments for failures or increased build times.

- **Application Logs**
  - If applicable, monitor runtime logs for:
    - Assembly binding errors
    - TypeLoadException, MissingMethodException

- **Error/Telemetry Systems**
  - Watch for increases in fatal errors or regressions

- **Support Channels**
  - Monitor issue trackers or team communication channels for reports of upgrade-related bugs

---

## Known Issues & Workarounds

- **NuGet Package Compatibility**  
  Some packages may not support `.NET 8.0`.  
  _Workaround:_ Check for package updates or alternatives. [NuGet compatibility](https://www.nuget.org/packages?framework=net8.0).

- **Custom Build Targets Loss**  
  SDK-style projects do not always preserve custom `BeforeBuild`, `AfterBuild` hooks or other MSBuild customizations.  
  _Workaround:_ Migrate MSBuild targets into SDK-style or separate `.targets` files as appropriate.

- **Multi-targeting Complexity**  
  If previous projects targeted multiple frameworks, consult [multi-targeting docs](https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview#multi-targeting).

- **Unsupported Project Types**  
  Some legacy project types (e.g., Web Forms, older WCF services) are not directly supported.  
  _Workaround:_ Review migration guides; consider isolating or rewriting before attempting SDK-style conversion.

---

