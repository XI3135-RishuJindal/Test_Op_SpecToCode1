# Migration Runbook: Upgrade ASP.NET Web API to Latest Version

## Pre-Migration Checklist
- [ ] Ensure current version of ASP.NET Web API is documented.
- [ ] Backup the current application and database.
- [ ] Review the latest ASP.NET Web API change log for breaking changes.
- [ ] Validate that no critical features will be affected by the upgrade.
- [ ] Ensure all tests (unit, integration) are passing on the current version.
- [ ] Inform stakeholders about the planned upgrade and expected downtime.

## Environment Setup
1. Install the latest version of .NET SDK:
   ```bash
   dotnet tool install --global dotnet-sdk --version <latest-version>
   ```

2. Update the project files:
   - Open the `.csproj` file and update the `TargetFramework` to the latest version.
   - Restore NuGet packages:
   ```bash
   dotnet restore
   ```

3. Ensure your CI environment has access to the latest SDK by updating the CI pipeline configuration.

## Step-by-Step Migration Procedure
1. **Action**: Update NuGet packages.
   - **Expected outcome**: All the dependencies are upgraded to their latest versions.
   - **Verification command**: 
     ```bash
     dotnet list package --outdated
     ```
   - **Rollback action if it fails**: Restore the project to the previous working state using:
     ```bash
     dotnet restore
     ```

2. **Action**: Run the upgrade tool for ASP.NET Web API.
   - **Expected outcome**: The upgrade tool updates your API codebase to compatible code with the latest framework version.
   - **Verification command**: 
     ```bash
     dotnet aspnet-api-upgrade --check
     ```
   - **Rollback action if it fails**: Manually revert changes to the API files or retrieve from backup.

3. **Action**: Execute the application.
   - **Expected outcome**: The application compiles and runs without errors.
   - **Verification command**: 
     ```bash
     dotnet run
     ```
   - **Rollback action if it fails**: Restore to previous revision of the application from version control.

4. **Action**: Run all unit and integration tests.
   - **Expected outcome**: All tests pass successfully ensuring functionality.
   - **Verification command**: 
     ```bash
     dotnet test
     ```
   - **Rollback action if it fails**: Investigate failing tests, fix the issue, or revert code to prior version until resolved.

## Verification & Smoke Tests
- Verify API endpoint responses:
```bash
curl -X GET http://localhost:<port>/api/values
```
- Check application logs for errors:
```bash
tail -f /path/to/application/logs/app.log
```

## Rollback Procedure
1. Check for any potential test failures or errors in logs.
2. Restore the previous code base from version control:
   ```bash
   git checkout <previous-commit-id>
   ```
3. Restore the previous version of the database if updates were made:
   ```bash
   # Depending on your database, restore commands will vary.
   ```
4. Inform stakeholders about the rollback completion.
5. Conduct a full review of issues encountered during the upgrade to identify root causes.

## Post-Migration Monitoring
- Monitor application performance metrics (CPU, memory usage) using APM tools.
- Track the following logs for errors:
  - HTTP 500 errors
  - 404 errors indicating missing endpoints
- Set up alerts for abnormal application behavior or performance degradation for the first 24-48 hours.

## Known Issues & Workarounds
- N/A — not applicable to this task