# .NET Framework to .NET 6 Migration Runbook

## Pre-Migration Checklist
- [ ] Ensure all team members are informed and available for migration timing.
- [ ] Backup current application and database.
- [ ] Review application code for deprecated APIs and components.
- [ ] Confirm availability of all third-party libraries compatible with .NET 6.
- [ ] Upgrade development environment to support .NET 6.
- [ ] Apply any necessary code refactoring to make the code .NET 6 friendly.
- [ ] Prepare a change management plan for the updated architecture.

## Environment Setup
1. **Install .NET 6 SDK**
   ```bash
   wget https://dot.net/v1/dotnet-install.sh
   chmod +x dotnet-install.sh
   ./dotnet-install.sh --channel 6.0
   ```

2. **Update Environment Variables**
   - Ensure the .NET 6 installation path is added to the system's PATH variable.
   - Verify installation:
     ```bash
     dotnet --version
     ```

3. **Configure CI/CD Pipeline**
   - Update build agents to use .NET 6 SDK.
   - Adjust build configuration files (e.g., YAML, `.csproj`) to target `.NET 6`.

## Step-by-Step Migration Procedure
1. **Action**
   Update the target framework in the project files.
   - Open `.csproj` file.
   - Change `<TargetFramework>net48</TargetFramework>` to `<TargetFramework>net6.0</TargetFramework>`.

   **Expected Outcome**
   The project file reflects the target framework change.

   **Verification Command**
   ```bash
   dotnet build
   ```

   **Rollback Action if it Fails**
   Restore the original target framework entry in the `.csproj` file.

2. **Action**
   Execute the `dotnet restore` command to restore packages.
   
   **Expected Outcome**
   All dependencies for .NET 6 are correctly restored.

   **Verification Command**
   ```bash
   dotnet restore
   ```

   **Rollback Action if it Fails**
   Revert any package updates or changes made during restoration.

3. **Action**
   Refactor the code to resolve any compilation errors and update types/methods that are deprecated in .NET 6.

   **Expected Outcome**
   Code compiles without errors.

   **Verification Command**
   ```bash
   dotnet build
   ```

   **Rollback Action if it Fails**
   Use version control to roll back changed files to a previous commit.

4. **Action**
   Run unit tests to ensure application logic is intact post-migration.

   **Expected Outcome**
   All unit tests pass successfully.

   **Verification Command**
   ```bash
   dotnet test
   ```

   **Rollback Action if it Fails**
   Review changes made during refactoring and revert to stable codebase if necessary.

5. **Action**
   Deploy the application to the staging environment.

   **Expected Outcome**
   Staging environment runs the updated application without issues.

   **Verification Command**
   Monitor logs in the staging environment for errors.

   **Rollback Action if it Fails**
   Roll back to the previous stable version of the application in staging.

## Verification & Smoke Tests
1. **Verify Application Start**
   ```bash
   dotnet run
   ```

2. **Check API Endpoints**
   Use Postman or CURL to hit the main HTTP endpoints:
   ```bash
   curl http://localhost:[PORT]/api/[ENDPOINT]
   ```

3. **Access Application Logs**
   Ensure no critical errors can be found in application logs:
   - Check logs in `logs/` directory or configured logging service.

## Rollback Procedure
1. **Stop the Application**
   ```bash
   dotnet stop [APPLICATION_NAME]
   ```

2. **Restore Previous Project Files**
   Revert to backup versions of `.csproj` and any code files altered during migration.

3. **Restore Previous Dependencies**
   - Restore previous package versions in `packages.config` or ensure the package-lock file reflects previous dependencies in use.
   ```bash
   dotnet restore
   ```

4. **Redeploy the Previous Version**
   Deploy the version just before the migration attempt to the production environment.

5. **Verify Application Functionality Post-Rollback**
   Run smoke tests as described above to confirm that the application is functioning as expected before migration.

## Post-Migration Monitoring
- **Metrics to Watch**
  - Application performance metrics (CPU, memory usage).
  - Response times for API endpoints.

- **Logs**
  - Review application logs for exceptions and errors specifically linked to migration changes.

- **Alerts**
  - Set alerts for error logs and performance dips.
  - Monitor application stability for up to 48 hours post-deployment.

## Known Issues & Workarounds
N/A — not applicable to this task.