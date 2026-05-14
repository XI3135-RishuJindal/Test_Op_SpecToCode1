# Python 3.12 Migration Runbook

This runbook guides the upgrade of the project’s Python runtime to version 3.12. Follow each section carefully to ensure a safe and verified migration.

---

## Pre-Migration Checklist

All requirements below **must be satisfied and checked ✅ before starting** the upgrade.

- [ ] ✅ All application source code is committed and pushed to version control.
- [ ] ✅ Unit/integration test suites are passing on the current Python version.
- [ ] ✅ A comprehensive list of dependencies (requirements.txt, Pipfile, pyproject.toml, etc.) is available and up-to-date.
- [ ] ✅ All maintainers and stakeholders have been notified of the upgrade schedule.
- [ ] ✅ A tested and documented rollback process is ready.
- [ ] ✅ Access/permissions to update CI configurations and deployment environments.
- [ ] ✅ Backup of the current production/staging deployment artifacts and environments taken.

---

## Environment Setup

Prepare both local and CI environments for the migration.

### Update Local Python Environment

1. **Install Python 3.12**

    - **Ubuntu/Debian:**  
      ```bash
      sudo apt update
      sudo apt install python3.12 python3.12-venv python3.12-dev
      ```
    - **macOS (Homebrew):**  
      ```bash
      brew install python@3.12
      ```

2. **Create and Activate New Virtual Environment**
    ```bash
    python3.12 -m venv venv-py312
    source venv-py312/bin/activate
    ```

### Update CI Configuration

- Update the CI workflow (e.g., GitHub Actions, GitLab CI, Jenkins) to use `python: 3.12` or similar as the Python runtime.
    - _Example (GitHub Actions):_
        ```yaml
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/setup-python@v4
                with:
                  python-version: '3.12'
        ```

---

## Step-by-Step Migration Procedure

1. **Update Dependency Files for Python 3.12**
    - **Action:** Update `requirements.txt`, `Pipfile`, or `pyproject.toml` to ensure compatibility with Python 3.12. Update package versions if necessary.
    - **Expected Outcome:** All dependencies declare support for Python 3.12.
    - **Verification Command:**  
      ```bash
      pip install -r requirements.txt
      ```
    - **Rollback Action:** Revert dependency files to previous state from version control.

2. **Install Project Dependencies Using Python 3.12**
    - **Action:** In the new virtual environment, reinstall all dependencies.
    - **Expected Outcome:** No install errors; all dependencies installed cleanly.
    - **Verification Command:**  
      ```bash
      pip check
      ```
    - **Rollback Action:** Reactivate previous Python environment and reinstall previous dependencies.

3. **Run Tests with Python 3.12**
    - **Action:** Execute the full test suite using Python 3.12.
    - **Expected Outcome:** All tests pass or are updated for Python 3.12 compatibility.
    - **Verification Command:**  
      ```bash
      pytest  # or the project’s test runner
      ```
    - **Rollback Action:** Investigate and fix incompatibilities; otherwise, revert to previous Python version.

4. **Update Shebangs and Runtime Paths (if used in scripts)**
    - **Action:** Update any hardcoded `python`/`python3` shebangs to reference `python3.12`.
    - **Expected Outcome:** Scripts use the correct Python interpreter.
    - **Verification Command:**  
      ```bash
      head -n 1 path/to/scripts/*.py | grep python3.12
      ```
    - **Rollback Action:** Restore previous shebang lines.

5. **Update Deployment/Container Configuration**
    - **Action:** Update Dockerfiles, deployment scripts, or platform/runtime configurations to use Python 3.12.
    - **Expected Outcome:** All deployed runtimes specify Python 3.12.
    - **Verification Command:**  
      - For Docker:  
        ```bash
        docker run --rm your-image python --version
        ```
      - For managed platforms: check configuration UI or deployment logs.
    - **Rollback Action:** Rollback deployment/container definitions to prior Python version.

6. **Deploy to Staging Environment**
    - **Action:** Deploy using Python 3.12 to pre-production environment.
    - **Expected Outcome:** App runs and passes smoke tests on staging.
    - **Verification Command:**  
      Check staging logs; run smoke tests (see next section).
    - **Rollback Action:** Redeploy staging with previous artifact or configuration.

7. **Deploy to Production**
    - **Action:** Release code and containers using Python 3.12 to production.
    - **Expected Outcome:** Production workloads utilize Python 3.12 with no runtime issues.
    - **Verification Command:**  
      ```bash
      python --version
      ```
      (on production hosts/containers), and validate logs.
    - **Rollback Action:** Trigger full rollback procedure.

---

## Verification & Smoke Tests

Run these commands in the upgraded environment to verify successful migration:

```bash
python --version   # Should print Python 3.12.x
pip check          # Should show "No broken requirements found."
pytest             # Or your test suite; all tests should pass
```

- Ensure application starts without errors:
    ```bash
    ./manage.py runserver  # For Django
    flask run              # For Flask
    # or your framework’s command
    ```

- End-to-end application smoke tests:
    - Confirm major endpoints/features respond as expected.

---

## Rollback Procedure

1. **Restore Dependency/Configuration Files**
    - Checkout previous versions of dependency files and configuration from version control.

2. **Restore Python Runtime**
    - Switch environments or Docker base images back to the prior Python version.

3. **Reinstall Dependencies**
    - In the previous Python environment, reinstall dependencies.
    ```bash
    pip install -r requirements.txt
    ```

4. **Revert CI Configuration**
    - Update CI/CD pipeline(s) to use previous Python version.

5. **Redeploy Application**
    - Deploy previous artifact or configuration to all environments (staging, then production).

6. **Run Smoke Tests**
    - Validate that the application is functional on the previous version.
    ```bash
    python --version   # Should print previous version
    pytest             # Confirm tests pass
    ```

---

## Post-Migration Monitoring

Monitor the following for 24–48 hours after production deployment:

- **Application error logs:** Watch for new or increased Python errors/exceptions.
- **Crash/restart rates:** Unusual increases may indicate hidden runtime issues.
- **CI/CD pipeline results:** Monitor for new failures on merge/test pipelines.
- **Key business metrics:** Drop in throughput, latency spikes, or failed transactions.

_Set up alerts for:_ Unhandled exceptions, increased 5xx errors, and service restarts.

---

## Known Issues & Workarounds

N/A — not applicable to this task

---