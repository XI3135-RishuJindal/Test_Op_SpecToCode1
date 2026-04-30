# Migration Runbook: Migrate and Reconfigure OpenAPI/Swagger Using Swashbuckle.AspNetCore

---

## Pre-Migration Checklist

All must be ✅ before proceeding.

- [ ] ✅ Source code repository backed up.
- [ ] ✅ All environments (dev, QA, prod) identified and access verified.
- [ ] ✅ Existing API documentation exported (if possible).
- [ ] ✅ Current Swagger/OpenAPI configuration identified and documented.
- [ ] ✅ Migration approved by technical owner/Product Owner.
- [ ] ✅ CI/CD pipeline access and triggers verified.
- [ ] ✅ Application can be built and run locally.
- [ ] ✅ Version control on main branch is up-to-date and ready for feature branches.
- [ ] ✅ Open API consumers notified of impending migration.

---

## Environment Setup

1. **Install Swashbuckle.AspNetCore via NuGet**

   ```sh
   dotnet add package Swashbuckle.AspNetCore
   ```
   
2. **Restore NuGet packages**

   ```sh
   dotnet restore
   ```
   
3. **Ensure .NET SDK is installed (min. .NET Core 3.1 recommended; check project compatibility)**

   ```sh
   dotnet --version
   ```

4. **Set up environment variables for local development (if any OpenAPI keys/config needed).**

5. **Ensure build agent in CI supports .NET and can restore and build NuGet packages.**

6. **Prepare a migration feature branch in version control.**

   ```sh
   git checkout -b migrate-swashbuckle
   ```

---

## Step-by-Step Migration Procedure

### 1. Remove Existing Swagger/OpenAPI Packages

- **Action:** Uninstall previous Swagger/OpenAPI dependencies (if present).
  - For example, uninstall `NSwag.AspNetCore` or `Swashbuckle.AspNetCore` (old versions).
- **Expected outcome:** Old dependencies are removed; only Swashbuckle.AspNetCore will be used.
- **Verification command:**

  ```sh
  dotnet list package
  # Confirm old packages not listed
  ```
- **Rollback action:** Reinstall previously removed packages using NuGet.

---

### 2. Install Swashbuckle.AspNetCore

- **Action:** Add Swashbuckle.AspNetCore NuGet package (see Environment Setup).
- **Expected outcome:** Package is listed in project dependencies.
- **Verification command:**

  ```sh
  dotnet list package | grep Swashbuckle.AspNetCore
  ```
- **Rollback action:** Remove package:

  ```sh
  dotnet remove package Swashbuckle.AspNetCore
  ```

---

### 3. Edit Startup/Program to Add Swagger Services

- **Action:** In `Startup.cs` (or `Program.cs` for minimal hosting), add Swagger services:

  ```csharp
  // In ConfigureServices() or builder.Services
  services.AddSwaggerGen();
  ```

- **Expected outcome:** Build succeeds with Swagger services registered.
- **Verification command:**

  ```sh
  dotnet build
  ```
- **Rollback action:** Remove the above line and recompile.

---

### 4. Configure Swagger UI Middleware

- **Action:** In `Configure` (or middleware pipeline), enable Swagger and SwaggerUI:

  ```csharp
  // Add these in AppBuilder (for classic ASP.NET Core):
  app.UseSwagger();
  app.UseSwaggerUI();
  ```

  - For minimal APIs:

    ```csharp
    app.MapSwagger();
    app.UseSwaggerUI();
    ```

- **Expected outcome:** Application starts and serves Swagger documentation endpoint.
- **Verification command:** Start the API. In a browser, visit:

  ```
  http://localhost:<port>/swagger
  ```

  You should see the Swagger UI.

- **Rollback action:** Remove middleware lines and restart the app.

---

### 5. Migrate and Reconfigure OpenAPI Settings

- **Action:** Replicate/custom-tailor the previous OpenAPI configuration (metadata, security, UI customizations) using `SwaggerGenOptions`. Edit `AddSwaggerGen` as needed.

  Example customization:
  ```csharp
  services.AddSwaggerGen(c =>
  {
      c.SwaggerDoc("v1", new OpenApiInfo
      {
          Title = "My API",
          Version = "v1"
      });
      // Copy additional settings like XML comments, security, etc.
  });
  ```

- **Expected outcome:** Swagger endpoint reflects project-specific metadata and settings.
- **Verification command:** Reload `/swagger` UI, inspect doc info and settings.
- **Rollback action:** Comment/remove new configuration and revert to default.

---

### 6. Remove Deprecated/Obsolete Swagger Configuration & Clean Up

- **Action:** Delete obsolete/unused Swagger/OpenAPI configuration files, code, or scripts.
- **Expected outcome:** Solution contains only relevant Swagger/Swashbuckle code.
- **Verification command:** Search project for deprecated package usage or duplicate Swagger config.
- **Rollback action:** Restore config from version control if needed.

---

### 7. Commit and Push Changes

- **Action:** Commit changes and open a PR for review.
- **Expected outcome:** Feature branch pushed with clear migration commit message.
- **Verification command:**

  ```sh
  git status
  git commit -am "Migrate to Swashbuckle.AspNetCore for OpenAPI/Swagger"
  git push
  ```
- **Rollback action:** Revert/close PR.

---

## Verification & Smoke Tests

Run these checks post-migration:

1. **Build and Run Locally**

   ```sh
   dotnet build
   dotnet run
   ```

2. **Swagger UI available:**  
   Visit `http://localhost:<port>/swagger` and ensure UI loads without errors.

3. **Swagger JSON served:**  
   Visit `http://localhost:<port>/swagger/v1/swagger.json`  
   Confirm valid OpenAPI JSON is returned.

4. **Endpoints are documented:**  
   All expected API endpoints appear in Swagger docs.

5. **CI/CD Build:**  
   Trigger a pipeline build; verify build/test steps succeed and artifacts (if any) include updated Swagger docs.

6. **(Optional) Integration Test:**  
   If automation exists, run automated contract/integration tests against the API.

---

## Rollback Procedure

If migration fails or breaks functionality, follow these steps:

1. **Restore previous branch (before migration):**

   ```sh
   git checkout main
   git reset --hard <pre-migration-commit-hash>
   ```

2. **Re-add old/OpenAPI dependencies as they were:**

   ```sh
   dotnet add package <old-swagger-package>
   ```

3. **Restore previous Swagger/OpenAPI configuration code and files.**

4. **Rebuild and redeploy application.**

   ```sh
   dotnet build
   dotnet run
   ```

5. **Verify API docs are restored via old endpoint.**

6. **Notify stakeholders of rollback.**

---

## Post-Migration Monitoring

Monitor the following for 24–48 hours post-deployment:

- **Application logs:** Watch for exceptions related to Swagger/OpenAPI middleware.
- **Health checks:** Monitor endpoint response times and error rates.
- **API consumers:** Listen for reports of missing or malformed documentation.
- **Availability:** Ensure Swagger UI and JSON endpoints remain up.
- **CI/CD pipeline status:** Monitor build and deploy logs for Swagger-related failures.

---

## Known Issues & Workarounds

- **Issue:** Swagger UI 404 or not loading
  - *Workaround:* Confirm `app.UseSwagger()` and `app.UseSwaggerUI()` middleware ordering and presence.

- **Issue:** Swagger JSON missing endpoints
  - *Workaround:* Check for `[ApiExplorerSettings(IgnoreApi = true)]` attributes or misconfigured routing. Ensure controllers/actions are public.

- **Issue:** Custom OpenAPI metadata lost
  - *Workaround:* Explicitly port all metadata/customizations to new `AddSwaggerGen` config.

- **Issue:** Security schemes not migrated
  - *Workaround:* Add security definitions manually in `SwaggerGenOptions`.

---