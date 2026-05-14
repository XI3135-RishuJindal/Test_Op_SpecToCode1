# MIGRATION RUNBOOK: Upgrade Python Runtime to 3.12

---

## Pre-Migration Checklist

All must be ✅ before proceeding:

- [ ] ✅ The current application is running and stable.
- [ ] ✅ Source control has a clean, up-to-date branch for migration.
- [ ] ✅ Application and all dependencies have been reviewed for Python 3.12 compatibility.
- [ ] ✅ All tests pass on the current Python runtime.
- [ ] ✅ A backup of the current environment and configuration has been created.
- [ ] ✅ Stakeholders have been notified of the planned upgrade window.
- [ ] ✅ Rollback plan is documented and tested.

---

## Environment Setup

### Local Environment

1. **Install Python 3.12:**  
   ```bash
   # macOS (Homebrew)
   brew install python@3.12

   # Ubuntu
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt-get update
   sudo apt-get install python3.12 python3.12-venv python3.12-dev

   # Windows: Download installer from https://www.python.org/downloads/
   ```
2. **Update virtual environment:**  
   ```bash
   python3.12 -m venv venv-py312
   source venv-py312/bin/activate
   pip install --upgrade pip
   ```

### CI Environment

- Update the CI configuration (e.g., `.github/workflows/`, `circleci/config.yml`) to use `python:3.12`.
- Ensure dependency install and test steps reference Python 3.12.
- Example (`GitHub Actions`):
  ```yaml
  jobs:
    build:
      runs-on: ubuntu-latest
      strategy:
        matrix:
          python-version: [3.12]
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: 3.12
        # ...
  ```

---

## Step-by-Step Migration Procedure

1. **Update Local Development Environment**
   - **Action:** Install Python 3.12 and recreate the virtual environment.
   - **Expected outcome:** Local environment uses Python 3.12 and dependencies install without errors.
   - **Verification command:**
     ```bash
     python --version
     pip install -r requirements.txt
     ```
   - **Rollback action:** Re-activate previous virtual environment using previous Python version.

2. **Update CI/CD Pipeline**
   - **Action:** Change pipeline configuration to use Python 3.12.
   - **Expected outcome:** Pipeline uses Python 3.12, builds, and runs tests successfully.
   - **Verification command:** Trigger a pipeline run and confirm logs show Python 3.12 is used.
   - **Rollback action:** Revert CI/CD configuration to previous Python version.

3. **Update Deployment Scripts/Runtime Configuration**
   - **Action:** Modify deployment scripts, Dockerfiles, or runtime configs to use Python 3.12.
   - **Expected outcome:** Production/staging deploys with Python 3.12.
   - **Verification command:** SSH into running app instance/container, then:
     ```bash
     python --version
     ```
   - **Rollback action:** Revert deployment scripts/configs to use previous Python version, redeploy.

4. **Run All Tests on Python 3.12**
   - **Action:** Execute unit, integration, and smoke tests in Python 3.12 environment.
   - **Expected outcome:** All tests pass.
   - **Verification command:**  
     ```bash
     pytest tests/
     ```
   - **Rollback action:** Investigate and fix test failures, or return to previous environment.

5. **Deploy to Staging/QA Environment**
   - **Action:** Deploy application with Python 3.12 to a staging environment.
   - **Expected outcome:** Application starts and functions normally.
   - **Verification command:** Access application endpoints; run smoke and functional tests.
   - **Rollback action:** Redeploy staging with previous Python version.

6. **Production Deployment**
   - **Action:** Deploy to production with Python 3.12.
   - **Expected outcome:** Production app operates normally with no errors.
   - **Verification command:**  
     ```bash
     python --version
     # Application health check endpoints
     ```
   - **Rollback action:** Redeploy with previous Python version using backup/rollback scripts.

---

## Verification & Smoke Tests

- **Confirm Python Version:**
  ```bash
  python --version  # Should output: Python 3.12.x
  ```
- **Run Unit/Integration Tests:**
  ```bash
  pytest tests/
  ```
- **Application Health Checks:**  
  - Manually or using scripts, check primary application endpoints.
- **Key CLI Operations:**  
  - Run a typical CLI command relevant to the app:  
    ```bash
    python manage.py runserver   # OR other core commands
    ```

---

## Rollback Procedure

1. **Restore Previous Runtime Configuration:**
   - Revert deployment and environment scripts from Python 3.12 to previous version.
2. **Revert Virtual Environment:**
   - Recreate or reactivate previous virtual environment using the prior Python version.
3. **Update CI/CD Pipeline:**
   - Change CI configs back to the previous Python version; rerun pipeline.
4. **Re-install Dependencies:**
   - Reinstall all packages in the previous environment:
     ```bash
     pip install -r requirements.txt
     ```
5. **Redeploy Application:**
   - Deploy application with the previous Python version to all affected environments.
6. **Verification:**
   - Confirm application functionality and health endpoints are back to normal.
   - Run tests to confirm pass status.

---

## Post-Migration Monitoring

- **Metrics to Monitor:**
  - Application error rates
  - Request/response latency
  - Service uptime

- **Logs:**
  - Monitor for Python runtime errors/exceptions in system/application logs
  - Check for any import/module errors or deprecation warnings

- **Alerts:**
  - Set up alerts for increased HTTP 5xx responses
  - New/unknown error types reported

- **Duration:**  
  - Monitor for minimum 24-48 hours post-deployment

---

## Known Issues & Workarounds

N/A — not applicable to this task

---