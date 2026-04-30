# Migration Runbook: Update ASP.NET Web API to Latest Stable Version

## Pre-Migration Checklist
- [ ] Backup current project and database
- [ ] Ensure all unit tests pass in the current environment
- [ ] Review breaking changes in the new ASP.NET version
- [ ] Ensure all dependencies are compatible with the new ASP.NET version
- [ ] Confirm the latest stable version number
- [ ] Obtain approval from relevant stakeholders

## Environment Setup
1. Install the latest .NET SDK:
   ```bash
   dotnet new --install Microsoft.AspNetCore.Mvc.NewtonsoftJson
   ```
2. Update global.json (if applicable) to target the new SDK version.

3. Restore dependencies:
   ```bash
   dotnet restore
   ```

## Step-by-Step Migration Procedure
1. **Action:** Update the project file (.csproj) to target the latest version.  
   **Expected Outcome:** The project is configured to use the latest ASP.NET Web API.  
   **Verification Command:**  
   ```bash
   dotnet build
   ```  
   **Rollback Action if it Fails:** Revert changes in the .csproj file to the previous version.

2. **Action:** Update NuGet packages for ASP.NET components.  
   **Expected Outcome:** All relevant ASP.NET packages are updated to the latest stable version.  
   **Verification Command:**  
   ```bash
   dotnet list package --outdated
   ```  
   **Rollback Action if it Fails:** Use the following command to revert the package version:  
   ```bash
   dotnet add package <package_name> --version <previous_version>
   ```

3. **Action:** Modify the codebase to handle any breaking changes introduced by the new version.  
   **Expected Outcome:** The codebase is now compliant with the latest framework requirements.  
   **Verification Command:**  
   ```bash
   dotnet build
   ```  
   **Rollback Action if it Fails:** Restore the previous codebase using Git or similar version control.

4. **Action:** Run unit tests to validate functionality post-migration.  
   **Expected Outcome:** All tests pass successfully.  
   **Verification Command:**  
   ```bash
   dotnet test
   ```  
   **Rollback Action if it Fails:** Revert to the previous commit or restore codebase to the last known good state.

## Verification & Smoke Tests
- Execute the following command to ensure the API is functional:
  ```bash
  curl -I http://localhost:<port>/api/values 
  ```
- Verify that the response status code is 200 (OK).

## Rollback Procedure
1. Restore the previous project file (.csproj) to its last working state.
2. Revert any updated NuGet packages to their previous versions:
   ```bash
   dotnet remove package <package_name>
   dotnet add package <package_name> --version <previous_version>
   ```
3. Replace the modified code files with the backup or previous version from version control.
4. Run build and tests to validate the rollback was successful:
   ```bash
   dotnet build
   dotnet test
   ```

## Post-Migration Monitoring
- Monitor application performance metrics including:
  - Response times
  - Error rates
- Check application logs for warnings and errors related to the ASP.NET Web API.
- Set up alerts on critical services and APIs to catch any unexpected issues.

## Known Issues & Workarounds
- **Issue:** Some legacy middleware may no longer function correctly.
  **Workaround:** Update or replace middleware with compatible versions or alternatives.
- **Issue:** Possible discrepancies in JSON serialization behavior.
  **Workaround:** Implement custom converters or adjust configurations to ensure compatibility. 

N/A — not applicable to this task 