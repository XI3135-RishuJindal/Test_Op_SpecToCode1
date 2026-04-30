# Migration Runbook: Update NuGet Dependencies to .NET 8 Compatible Versions

---

## Pre-Migration Checklist

All items must be ✅ before proceeding.

- [ ] ✅ Source code is under version control and latest changes are committed.
- [ ] ✅ Current build is passing in both local and CI environments.
- [ ] ✅ All existing NuGet package references are inventoried and their .NET 8 compatibility checked.
- [ ] ✅ All .csproj or package.config files are backed up.
- [ ] ✅ Target .NET 8 SDK installed and available on all local and CI environments.
- [ ] ✅ Rollback plan is reviewed and easily executable.
- [ ] ✅ Stakeholders notified about planned dependency upgrades and potential downtime (if any).
- [ ] ✅ Access verified for all relevant NuGet package feeds.

---

## Environment Setup

### Local Environment

```sh
# Install latest .NET 8 SDK if not present
dotnet --list-sdks | grep 8 || \
    (echo "Installing .NET 8 SDK" && \
    brew install --cask dotnet-sdk || \
    sudo apt-get install -y dotnet-sdk-8.0)

# Ensure NuGet CLI is available (if using NuGet directly)
nuget help || dotnet tool install -g NuGet.CommandLine

# Restore current packages to verify baseline
dotnet restore
```

### CI Environment

- Update CI definition (`.yml`, `.yaml`, etc.) to use a .NET 8 build agent.
- Ensure CI cache is cleared for NuGet to fetch updated dependencies:
  - In Azure DevOps, set `clean: true` on `NuGetToolInstaller` task or equivalent.
  - In GitHub Actions, add a step to delete cached `~/.nuget/packages` if needed.

---

## Step-by-Step Migration Procedure

1. **Update NuGet Dependencies to .NET 8 Compatible Versions**

    - **Action:**  
      Update all NuGet package references to versions that are compatible with .NET 8.  
      For `PackageReference` (`.csproj`):  
      ```sh
      # For each project file:
      dotnet list package --outdated
      dotnet add <path_to_project.csproj> package <PackageId> --version <LatestNet8CompatibleVersion>
      ```
      For `packages.config`:  
      ```sh
      nuget update <path_to_packages.config>
      ```
    - **Expected outcome:**  
      All projects reference .NET 8 compatible package versions.
    - **Verification command:**  
      ```sh
      dotnet restore
      dotnet build
      ```
      Confirm zero errors/warnings related to package compatibility.
      Optionally, verify in UI/IDE that `.csproj` or `packages.config` references updated versions.
    - **Rollback action if it fails:**  
      Revert `.csproj`/`packages.config` and `packages.lock.json` to backup copies (`git checkout <file>`), or use `git reset --hard`.

2. **Run Full Solution Build**

    - **Action:**  
      Build the solution to check for compile-time issues after dependency upgrades.
      ```sh
      dotnet build
      ```
    - **Expected outcome:**  
      Solution builds successfully without errors.
    - **Verification command:**  
      Review output; ensure no build errors.
    - **Rollback action if it fails:**  
      Revert package version updates as above.

3. **Run Automated Tests**

    - **Action:**  
      Execute all automated tests (unit/integration) against the upgraded dependencies.
      ```sh
      dotnet test --no-build --logger "console;verbosity=detailed"
      ```
    - **Expected outcome:**  
      All tests pass successfully.
    - **Verification command:**  
      Review test results for failures.
    - **Rollback action if it fails:**  
      Revert to previous package versions and rerun tests to confirm they pass.

4. **Push Changes to Remote and Trigger CI**

    - **Action:**  
      Commit dependency upgrade changes and push to staging/testing branch. Trigger the full CI pipeline.
    - **Expected outcome:**  
      CI passes all build and test steps with updated dependencies.
    - **Verification command:**  
      Review CI pipeline status.
    - **Rollback action if it fails:**  
      Revert branch to previous commit and re-run CI pipeline.

---

## Verification & Smoke Tests

- Run a minimal set of user journey or API smoke tests (manual or automated) in a staging/test environment.
- Key verification commands:
    ```sh
    # Restore and build (should give no errors/warnings)
    dotnet restore
    dotnet build

    # Run all tests
    dotnet test

    # (Optional) Run an application binary / API endpoint test
    dotnet run --project <MainProject>
    curl http://localhost:<port>/health
    ```
- Confirm that:
  - Application starts without dependency errors.
  - Core features (loading, login, basic interaction) work as expected.

---

## Rollback Procedure

1. **Revert Changes Locally**
    - Use Git to roll back all dependency/version changes:
      ```sh
      git reset --hard <last-known-good-commit>
      ```

2. **Restore Previous Packages**
    - Restore project to previous package versions:
      ```sh
      dotnet restore
      dotnet build
      dotnet test
      ```
    - Confirm the build and tests pass as before.

3. **Push Rollback to Remote**
    - Push the rollback commit to remote repository.
      ```sh
      git push --force-with-lease
      ```
    - Monitor CI to confirm build and test pipeline is green.

4. **Inform Stakeholders**
    - Notify relevant teams of rollback and next steps.

---

## Post-Migration Monitoring

- **Monitor for:**
  - Application startup failures (logs, exceptions on missing methods/types)
  - Build and release pipeline for new warnings or errors
  - Increased error rates in application logs (Error, Critical)
  - Support channels for user-reported issues related to upgraded dependencies
  - Specific package-based runtime errors (e.g., due to breaking changes in dependencies)

- **Useful Metrics:**
  - Exception rates (Application Insights, Sentry, etc.)
  - Healthcheck endpoints availability
  - Performance metrics (response time/RPS, if available)

- **Alerts (set for next 24-48 hours):**
  - Application/service down
  - Unhandled exceptions
  - Spike in HTTP 5xx responses

---

## Known Issues & Workarounds

- N/A — not applicable to this task

---