# Migration Runbook: Update Runtime Configuration and Application Settings for .NET 8

---

## Pre-Migration Checklist

- [ ] ✅ Source control is up-to-date and working branches are committed/pushed
- [ ] ✅ All required .NET 8 runtime and SDK installations are available on dev and CI environments
- [ ] ✅ QA and staging environments can be used for smoke testing
- [ ] ✅ Rollback plan is documented and tested for the previous runtime
- [ ] ✅ Application dependencies are compatible with .NET 8 (if not, blocked until they are)
- [ ] ✅ Notification has been sent to impacted parties about potential downtime

---

## Environment Setup

1. **Install .NET 8 SDK and Runtime**

   ```bash
   # Check if .NET 8 is already installed
   dotnet --list-sdks
   # Install .NET 8 SDK if missing (instructions: https://dotnet.microsoft.com/download/dotnet/8.0)
   ```

2. **Update Environment Variables (if applicable)**
   
   - Ensure environment variables are set for .NET 8 in CI and deployment scripts.
   - Example: Update any hardcoded `DOTNET_VERSION` variables.

3. **Restore Dependencies**

   ```bash
   dotnet restore
   ```

---

## Step-by-Step Migration Procedure

### 1. Update Runtime Configuration File(s)

- **Action:**  
  Edit each project’s `runtimeconfig.json` (or `.csproj` file) to target `.NET 8` (net8.0).
- **Expected outcome:**  
  The runtime configuration references net8.0.
- **Verification command:**  
  ```bash
  grep -R net8.0 . 
  ```
- **Rollback action:**  
  Revert the file(s) to the previous target framework (e.g., net6.0/net7.0).

---

### 2. Update Application Settings (if present)

- **Action:**  
  Review and update `appsettings.json`, `appsettings.{Environment}.json`, and/or environment variables for any settings deprecated/changed in .NET 8.  
  Check the `.NET 8` release notes for changes in configuration keys or new best practices.
- **Expected outcome:**  
  Configuration files are aligned with .NET 8 requirements, obsolete keys removed/replaced.
- **Verification command:**  
  ```bash
  # Example: Search for deprecated configuration keys (replace with actual keys if known)
  grep -E 'ObsoleteKey1|ObsoleteKey2' appsettings*.json
  ```
- **Rollback action:**  
  Restore the previous version of configuration files from version control.

---

### 3. Update CI/CD Pipeline Step(s)

- **Action:**  
  Update any build/deploy scripts or CI configuration (`.yaml`/`.yml`/Dockerfile) to use `.NET 8` images and tooling.
- **Expected outcome:**  
  All builds and deployments use .NET 8 runtime/tooling.
- **Verification command:**  
  Trigger a pipeline build and inspect logs for SDK/runtime version.
- **Rollback action:**  
  Revert pipeline scripts to previous version and re-deploy.

---

### 4. Rebuild and Redeploy Application

- **Action:**  
  Execute the build and redeploy steps via CI/CD or manually:
  ```bash
  dotnet clean
  dotnet build
  dotnet publish --configuration Release
  ```
  Deploy published outputs to the target environment.
- **Expected outcome:**  
  Application runs on .NET 8 in all target environments.
- **Verification command:**  
  Check application logs or “about” page for .NET version confirmation.  
  Example (if hosting on Linux):
  ```bash
  dotnet --info | grep 'Version: 8'
  ```
- **Rollback action:**  
  Redeploy the last known good artifact built against the previous runtime.

---

## Verification & Smoke Tests

Run after deployment to confirm the system is operational.

- **Basic application health check endpoint:**
  ```bash
  curl -i http://<application-url>/health
  ```
  - Expect HTTP 200/healthy and application responds as expected.
- **Critical workflow(s):**
  - Log in, submit a form, sample API request, etc.
- **Runtime version verification (if available):**
  - Application info endpoint returns `.NET 8.0.x`.
- **Application logs:**
  - No errors related to missing/broken configs or incompatible runtime.

---

## Rollback Procedure

1. **Restore Previous Configuration Files**
    - Checkout previous versions of `runtimeconfig.json`, `.csproj`, and all updated configuration files.
    - Commit and redeploy.

2. **Update CI/CD Pipeline Back to Previous Runtime**
    - Revert to old image or runtime version in builds/pipelines.

3. **Redeploy Application**
    - Deploy previous build artifacts to all target environments.

4. **Verification**
    - Confirm application is running on the previous runtime.
    - Run smoke tests to ensure the application is functional.

---

## Post-Migration Monitoring

Monitor for at least 24-48 hours post-deployment:

- **Metrics:**
  - Application uptime/availability
  - Error rates (particularly related to configuration or runtime exceptions)

- **Logs:**
  - “Failed to load configuration” or “runtime” errors
  - Warnings related to deprecated configuration keys

- **Alerts:**
  - Application crash/restart alerts
  - Latency, throughput, and critical business process failures

---

## Known Issues & Workarounds

N/A — not applicable to this task

---