# Migration Runbook: Remove Hardcoded Secrets and Use Environment Variables for Configuration

---

## Pre-Migration Checklist

All items **must** be ✅ before proceeding.

- [ ] ✅ Source code has been fully backed up and stored in a secure location.
- [ ] ✅ You have reviewer/owner approval to proceed.
- [ ] ✅ All locations with hardcoded secrets have been identified across the codebase.
- [ ] ✅ A secure secret store (or .env file) solution and inject/load approach has been agreed upon.
- [ ] ✅ CI/CD pipelines support passing environment variables securely.
- [ ] ✅ All necessary secrets have been provisioned and are available as environment variables in each target environment (dev, staging, prod).
- [ ] ✅ Unit and integration test environments are available and support env var injection.
- [ ] ✅ All internal documentation references to hardcoded secrets have been updated to mention new environment variable use.

---

## Environment Setup

**Local Development:**

1. Install dotenv loader or similar tool for your language/runtime (if required).  
   _Example (Node.js):_  
   ```bash
   npm install dotenv
   ```
2. Create a `.env` file at the project root (do **not** commit this file):
   ```
   SECRET_KEY=your-local-secret
   API_TOKEN=your-local-token
   ```
3. Ensure `.env` is listed in `.gitignore`.

**CI/CD Pipeline:**

1. In your CI/CD provider, securely add all required secrets as protected environment variables.
2. Remove hardcoded secrets from build scripts and pipeline YAML/config files.
3. Update any scripts that used secrets as plaintext to pull from the environment.

---

## Step-by-Step Migration Procedure

### 1. Locate and Remove Hardcoded Secrets

- **Action**:  
  Search for all plain secrets directly embedded in source code, config files, or scripts. Replace each instance with a reference to an environment variable.

- **Expected outcome**:  
  No secrets remain hardcoded; only environment variable references exist.

- **Verification command**:  
  _Generic (assuming git):_  
  ```bash
  git grep 'your-secret-value'
  ```
  _Replace `your-secret-value` with actual previous secret values to confirm removal._

- **Rollback action**:  
  Restore original source files from backup.

---

### 2. Load Environment Variables in Application

- **Action**:  
  Implement (if necessary) loading of environment variables in your application entrypoint or configuration loader.

- **Expected outcome**:  
  At runtime, application reads secrets exclusively from environment variables.

- **Verification command**:  
  _Generic example (adjust to your language):_  
  ```bash
  printenv | grep SECRET_KEY
  ```
  Or test application startup:
  ```bash
  ./start-application
  ```
  Confirm no errors regarding missing secrets.

- **Rollback action**:  
  Revert loader/config changes, re-add previous config.

---

### 3. Update Deployment and Runtime Environments

- **Action**:  
  Ensure all non-local environments (staging, production) have secrets available as environment variables (via secure injection method).

- **Expected outcome**:  
  Application runs successfully in each target environment with environment-provided secrets.

- **Verification command**:  
  - For containerized environments:  
    ```bash
    docker exec <container> printenv | grep SECRET_KEY
    ```
  - For cloud deployment:  
    Use platform CLI/UI to inspect env vars.

- **Rollback action**:  
  Restore previous deployment configuration with hardcoded or legacy secret passing.

---

### 4. Test All Affected Functionality

- **Action**:  
  Re-run all relevant unit, integration, and smoke tests, focusing on components that consume secrets.

- **Expected outcome**:  
  All tests pass; application behaves as before.

- **Verification command**:  
  ```bash
  ./run-tests
  ```

- **Rollback action**:  
  Rollback to previously tested version.

---

## Verification & Smoke Tests

- Start the application and verify no errors related to secrets/config.
- Manually test all paths that require secrets (e.g., authentication, API calls).
- Run automated regression and security tests:
  ```bash
  ./run-tests
  ```
- If possible, try intentionally omitting one secret to confirm the application logs a clear error.

---

## Rollback Procedure

1. **Restore Source Code**  
   - Use version control to revert to the previous commit:  
     ```bash
     git checkout <previous_commit>
     ```

2. **Restore Deployment Configurations**  
   - Revert to previous hardcoded secrets/config files in all environments.

3. **Remove Environment Variable Setup**  
   - Remove newly-added environment variable configurations from all CI/CD and deployment systems.

4. **Restart Application/Services**  
   - Deploy or restart services to restore previous working state.

5. **Verify Functionality**  
   - Run smoke tests to ensure the app is working as before.

---

## Post-Migration Monitoring

- Monitor authentication/API failure rates (any increase may indicate a secret misconfiguration).
- Check application error logs for missing environment variables or failed secret access.
- Set alerts for:
  - Application startup failures
  - 5xx errors
  - Unauthorized or forbidden API calls
- Validate that no secrets are written to logs or error messages.

---

## Known Issues & Workarounds

- **Issue**: Application process does not see environment variables.
  - **Workaround**: Confirm the secret is set in the correct scope (process/user/system), restart the application, or reconfigure your secrets injection mechanism.

- **Issue**: Secrets unintentionally checked into version control (.env or config).
  - **Workaround**: Add `.env` and all similar files to `.gitignore`. Contact security to rotate any exposed secrets immediately.

- **Issue**: Old hardcoded secrets left in dead code/configs.
  - **Workaround**: Use `git grep` or equivalent to re-audit source and configuration files for string remnants.

---

**END OF RUNBOOK**