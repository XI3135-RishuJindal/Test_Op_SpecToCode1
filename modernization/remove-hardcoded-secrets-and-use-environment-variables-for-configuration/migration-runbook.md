# Migration Runbook: Remove Hardcoded Secrets and Use Environment Variables for Configuration

---

## Pre-Migration Checklist

- [ ] ✅ **Inventory All Hardcoded Secrets**  
  Search source code for secrets (passwords, API keys, tokens, private keys, etc). Document file, variable name, and usage for each.
- [ ] ✅ **Gather Required Secrets**  
  Obtain all secrets and confirm their current/valid values.
- [ ] ✅ **Agree on Environment Variable Names**  
  Standardize names (e.g., `DATABASE_PASSWORD`, `API_KEY`, etc).
- [ ] ✅ **Update .env or Secret Injection Mechanism in all Environments**  
  Add required variables to local `.env` files and CI/CD secrets injectors (e.g., GitHub Actions secrets, Docker Secrets, Kubernetes Secrets).
- [ ] ✅ **Backup Current Source Code**  
  Ensure VCS (e.g., Git) is up to date and code is backed up.
- [ ] ✅ **Notify Team and Schedule Downtime (if needed)**  
  Communicate planned migration window and potential impact.

---

## Environment Setup

### Local Development

1. **Add all required environment variables:**  
   Update `.env` or equivalent file with:
   ```
   SECRET_ONE=value1
   SECRET_TWO=value2
   ```

2. **Ensure application loads environment variables:**  
   Install dependencies if using a loader (e.g., `python-dotenv`, `dotenv` npm package).

### Continuous Integration (CI) / Production

1. **Add secrets to CI/CD tool:**  
   Use secured secrets manager (e.g., GitHub Actions Secrets, GitLab CI variables, AWS Secrets Manager).

2. **Ensure environment variables are available at app startup:**  
   Configure deployment scripts or manifests to export/retrieve secrets.

---

## Step-by-Step Migration Procedure

1. **Identify and Remove Hardcoded Secrets**
   - **Action:**  
     Search for and replace all hardcoded secrets (API keys, DB passwords, etc.) with corresponding environment variable lookups in source code.
   - **Expected outcome:**  
     No secrets remain in plaintext within the codebase.
   - **Verification command:**  
     ```sh
     git grep -i -E 'password|secret|key|token|api' | grep '='
     ```
     All findings should reference environment variable access (e.g., `process.env.SECRET`, `os.environ["SECRET"]`).
   - **Rollback action if it fails:**  
     Revert affected files to pre-migration commit.

2. **Update Configuration and Dependency Files**
   - **Action:**  
     Update all configuration files to reference environment variables instead of literal secret values.
   - **Expected outcome:**  
     Config files (e.g., `config.js`, `settings.py`) now load secrets from the environment.
   - **Verification command:**  
     Manually review config files. Optionally, run:
     ```sh
     git diff <pre-migration-commit> | grep -E 'password|secret|key|token|api'
     ```
   - **Rollback action if it fails:**  
     Restore configuration files from backup or version control.

3. **Test Application with Environment Variables Locally**
   - **Action:**  
     Start application locally with `.env` or exported environment variables containing secrets.
   - **Expected outcome:**  
     Application starts and functions as expected, retrieving secrets from environment.
   - **Verification command:**  
     Application log should confirm secrets loaded from environment, not default values. 
   - **Rollback action if it fails:**  
     Double-check variable names or restore environment file and code.

4. **Update CI/CD and Deployment Manifests**
   - **Action:**  
     Add secrets to CI/CD pipeline, container orchestration, or deployment descriptors to inject at runtime.
   - **Expected outcome:**  
     Build and deployments have the required secrets set as environment variables.
   - **Verification command:**  
     Trigger pipeline and inspect environment, e.g.:
     ```sh
     echo $SECRET_ONE
     ```
   - **Rollback action if it fails:**  
     Remove variables, restore prior deployment setup.

5. **Commit and Push Changes**
   - **Action:**  
     Commit the code with secrets removed and environment variable logic implemented.
   - **Expected outcome:**  
     Codebase is updated, secrets not in code, ready for deployment.
   - **Verification command:**  
     ```sh
     git log -p
     git grep -i 'SECRET='
     ```
     Ensure only non-production values in code, actual secrets are not present.
   - **Rollback action if it fails:**  
     Revert commit(s).

---

## Verification & Smoke Tests

- Start application in all target environments (dev/staging/production) and confirm key functionality:
  * Authentication/login (if secrets used for identity)
  * External API calls
  * Database/connectivity

- **Verify environment variables loaded:**
  - For UNIX-based systems, ssh into container/VM and:
    ```sh
    printenv | grep 'SECRET'
    ```
  - For logs, confirm "Loaded X from environment" messages.

- Automated smoke tests (run as applicable):
  ```
  ./run_smoke_tests.sh
  ```

- Confirm _absence of hardcoded secrets_:
  ```
  git grep -i -E 'password|secret|key|token|api'
  # Output should NOT show secrets assigned directly in code/config
  ```

---

## Rollback Procedure

1. **Revert Source Code**
   - Checkout previous commit:
     ```sh
     git checkout <pre-migration-commit>
     ```

2. **Restore Configuration Files**
   - Replace updated configuration files with pre-migration versions.

3. **Remove Injected Environment Secrets**
   - Remove new environment variables from `.env`, CI/CD secrets, and deployment configs.

4. **Redeploy Application**
   - Deploy/restart application with prior configuration.

5. **Verify Application Functionality**
   - Run standard smoke tests to ensure system is operational.

---

## Post-Migration Monitoring

- **Metrics to Watch:**
  - Application start failures or crashes
  - Authentication/connection errors (e.g., "invalid credentials", "failed to connect to DB/API")
  - Unauthorized/forbidden errors in logs

- **Logs:**
  - Application logs for errors on secrets retrieval
  - Monitor for missing or unset environment variable errors

- **Alerts:**
  - Configure alerting for increased error rate, authorization failures, or secrets not found

- Monitor intensively for **24-48 hours** after deployment.

---

## Known Issues & Workarounds

- **Issue:** Some frameworks require additional configuration to load environment variables (e.g. using dotenv packages).  
  **Workaround:** Ensure required loaders (e.g., `dotenv`, `python-dotenv`) are installed and initialized before config loads.

- **Issue:** Secrets may not propagate in some CI/CD environments without a restart or pipeline variable refresh.  
  **Workaround:** Clear pipelines' cache, force variable reload, or restart relevant runners/agents.

- **Issue:** Legacy code may reference removed hardcoded secrets.  
  **Workaround:** Grep the entire codebase after migration to ensure no residual hardcoded secrets remain.

---