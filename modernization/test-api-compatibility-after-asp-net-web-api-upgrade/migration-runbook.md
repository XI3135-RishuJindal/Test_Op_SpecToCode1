# Migration Runbook for Testing API Compatibility after ASP.NET Web API Upgrade

## Pre-Migration Checklist
- [ ] Ensure all relevant stakeholders are informed of the migration schedule.
- [ ] Backup current API configuration and data.
- [ ] Clone the repository containing the API code.
- [ ] Set up a test environment that mirrors the production API environment.
- [ ] Review and resolve any outstanding tech debt that may affect the upgrade.
- [ ] Ensure CI/CD pipeline is functional and can deploy to the test environment.

## Environment Setup
1. Install the latest version of .NET SDK compatible with the upgraded ASP.NET Web API.
   ```bash
   dotnet sdk install <version>
   ```
2. Restore NuGet packages for the API project.
   ```bash
   dotnet restore
   ```
3. Ensure that relevant database migrations are applied to the test environment.
   ```bash
   dotnet ef database update
   ```
4. Start the ASP.NET Web API locally.
   ```bash
   dotnet run
   ```

## Step-by-Step Migration Procedure
1. **Action**: Update project dependencies to the latest stable version.
   - **Expected outcome**: All necessary dependencies are updated without version conflicts.
   - **Verification command**: 
     ```bash
     dotnet list package --outdated
     ```
   - **Rollback action if it fails**: Restore the original version of packages from backup.

2. **Action**: Apply any necessary code refactoring to align with upgraded framework best practices.
   - **Expected outcome**: Codebase is compliant with latest ASP.NET Web API standards.
   - **Verification command**: Run static analysis tools to check for code quality:
     ```bash
     dotnet analyzers
     ```
   - **Rollback action if it fails**: Revert to previous commit before the update.

3. **Action**: Test the API endpoints using automated test cases.
   - **Expected outcome**: All test cases pass, confirming compatibility.
   - **Verification command**: 
     ```bash
     dotnet test
     ```
   - **Rollback action if it fails**: Rollback to last working state of the repository.

4. **Action**: Manually test key API features to ensure critical functionality.
   - **Expected outcome**: Critical API functionality works as expected.
   - **Verification command**: Use Postman or similar tool to test endpoints.
   - **Rollback action if it fails**: Revert feature changes that caused the failure.

## Verification & Smoke Tests
- Run the smoke test suite to confirm the API is functional:
  ```bash
  dotnet test --filter "Smoke"
  ```
- Check specific endpoints for expected responses:
  ```bash
  curl -X GET http://localhost:5000/api/endpoint
  ```
- Validate database connection and data integrity:
  ```bash
  SELECT COUNT(*) FROM my_table;
  ```

## Rollback Procedure
1. Revert the codebase to the last stable commit:
   ```bash
   git checkout <last-stable-commit-hash>
   ```
2. Restore the original versions of updated dependencies in the project file.
3. Redeploy the last stable build to the test environment.
   ```bash
   dotnet publish -c Release
   ```
4. Restart the API service using the last working build.

## Post-Migration Monitoring
- Monitor API response times through logging (look for anomalies) for the next 24-48 hours:
  - Check log files located in `/logs` directory.
  - Look for slow request handling or failures.
- Set up alerting on error rates in your monitoring dashboard (e.g., Application Insights).
- Track performance metrics such as CPU and memory usage.

## Known Issues & Workarounds
- N/A — not applicable to this task