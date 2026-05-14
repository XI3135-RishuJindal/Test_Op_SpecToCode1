# MIGRATION RUNBOOK: Remove Hardcoded Secrets and Use Environment Variables for Configuration

---

## Pre-Migration Checklist

All items in this list must be ✅ before beginning migration.

- [ ] ✅ **Inventory all hardcoded secrets** (API keys, passwords, tokens, credentials) present in the codebase.
- [ ] ✅ **Identify code sections/files** where secrets are present.
- [ ] ✅ **Create a secure mechanism for environment variable management** (e.g., `.env` file, system environment, CI/CD secrets store).
- [ ] ✅ **Document all required environment variables** names and purposes.
- [ ] ✅ **Prepare credential rotation/replacement if existing secrets will be changed.**
- [ ] ✅ **Update documentation** (README, developer onboarding) to reference new configuration via environment variables.
- [ ] ✅ **Perform backup of existing codebase and deployment configuration.**

---

## Environment Setup

**Local Environment:**
1. Ensure you have access to the mechanism chosen for managing environment variables (`.env` file, OS vars, etc.)
2. If using a `.env` file, create it in the project root (and ensure it is git-ignored):

    ```sh
    cp .env.example .env
    ```

3. Populate the `.env` file or set system environment variables with all required secrets.
4. Remove secrets from code:

    ```sh
    grep -r '[hardcoded_secret_string]' .
    # or use editor/find-in-files to confirm removal
    ```

5. Confirm the application reads from environment variables without fallback to hardcoded secrets.

**CI Environment:**
1. Update CI/CD system (e.g., GitHub Actions, GitLab CI, Jenkins) to inject secrets into environment variables:
    - Example for GitHub Actions: Set secrets in repository > Settings > Secrets and reference in workflow.

---

## Step-by-Step Migration Procedure

### 1. Remove Hardcoded Secrets from Source Code

**Action:**  
Replace all hardcoded secret values in code with references to environment variables (e.g., `os.environ['SECRET_KEY']`).

**Expected Outcome:**  
Code no longer contains visible secret values; pulls secrets from environment at runtime.

**Verification Command:**  
```sh
grep -r '[actual_secret_value]' .
```
This should return no results.

**Rollback Action if It Fails:**  
Revert changes to the affected code files using source control:
```sh
git checkout <previous_commit_hash> -- <affected_file>
```

---

### 2. Define Required Environment Variables

**Action:**  
Create/update a `.env.example` template file or documentation to list all required configuration keys.

**Expected Outcome:**  
Team members and CI/CD can clearly see which env vars are required.

**Verification Command:**  
Verify `.env.example` exists and lists all new environment variables.
```sh
cat .env.example
```

**Rollback Action if It Fails:**  
Restore `.env.example` from previous backup or source control.

---

### 3. Inject Secrets via Environment Variables in Local & CI

**Action:**  
Populate the relevant environment variables for local development and within CI/CD tooling.

**Expected Outcome:**  
Secrets are no longer present in the code repository or configuration files (except in the secure secrets managers or environment variables).

**Verification Command:**  
Run application startup process and ensure no missing secret errors:
```sh
# Example: Run the application
./run-server.sh
```

**Rollback Action if It Fails:**  
Revert CI secret injections and local `.env` changes to previous known-good configurations.

---

### 4. Remove Legacy Hardcoded Fallbacks

**Action:**  
If any environment variable read includes a fallback to a previous hardcoded secret, remove the fallback permanently.

**Expected Outcome:**  
Application will only start if the correct environment variable is set.

**Verification Command:**  
Unset the secret env var and start the app. It should fail gracefully with a clear error about missing config.

**Rollback Action if It Fails:**  
Restore the removed fallback logic from version control.

---

## Verification & Smoke Tests

- **Secrets present as environment variables:**  
    ```sh
    env | grep -i <SECRET_ENV_VAR_NAME>
    ```
- **Application starts without hardcoded secrets:**
    ```sh
    ./run-server.sh
    ```
- **Codebase contains no secrets:**
    ```sh
    grep -r 'password\|api_key\|token\|secret' .  # manual review required
    ```
- **Application access test:**  
    Run key authentication/authorization flows and confirm success.

---

## Rollback Procedure

1. **Restore Previous Secret Handling:**
   - Revert codebase using version control to the commit immediately prior to migration:
     ```sh
     git reset --hard <previous_commit_hash>
     ```
2. **Restore Previous CI/CD Config:**
   - Reset CI/CD variables and deployment configuration to the previous state.
3. **Replace Local `.env` with Previous Version:**
   - Copy backup of `.env` or remove if it was not used previously.
4. **Redeploy Application:**
   - Follow existing deployment routine.
5. **Validation:**
   - Ensure application runs using restored hardcoded secrets and passes all authentication flows.

---

## Post-Migration Monitoring

- **Metrics:**
  - Application login/authentication error rate
  - 4xx/5xx error trends
- **Logs:**
  - Application startup logs (check for configuration loading failures)
  - Any errors relating to missing, unset, or incorrect environment variables
- **Alerts:**
  - Sudden increase in authentication/connection errors
  - Application failing to start/restart loops due to configuration issues

Monitor for at least 24–48 hours after migration.

---

## Known Issues & Workarounds

- **Issue:** Application fails to start due to missing environment variables.  
  **Workaround:** Double-check that all required environment variables are set in the local/CI environment.
- **Issue:** Environment-specific secrets may be missing in certain environments (dev, staging, prod).  
  **Workaround:** Ensure each environment's secrets store is populated and mapped appropriately before deployment.
- **Issue:** Application code was previously dependent on fallback logic for secrets.  
  **Workaround:** Explicitly manage secret presence by failing fast and logging clear errors if environment variables are missing.

---