# MIGRATION RUNBOOK: Flask 3.x Upgrade

---

## Pre-Migration Checklist

- [ ] ✅ **All code is committed and pushed to the main branch; backup in place.**
- [ ] ✅ **Automated test suite passes on current Flask version (pre-3.x).**
- [ ] ✅ **All dependencies (Flask extensions, libraries) have confirmed Flask 3.x compatibility or are ready for update.**
- [ ] ✅ **A rollback plan with previous requirements/environment artifacts is available.**
- [ ] ✅ **Stakeholders notified of maintenance window and potential impact.**

---

## Environment Setup

### Prepare Local Development

1. **Clone repository and create a new branch for migration:**  
   ```bash
   git checkout -b flask3-upgrade
   ```

2. **Create and activate a fresh virtual environment:**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install current dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests to confirm environment stability (pre-upgrade):**  
   ```bash
   pytest  # or the project's chosen test runner
   ```

### Prepare CI Pipeline

- Update CI configuration if a Python version bump is needed for Flask 3.x (requires Python 3.8+).
- Add a temporary extra build step to test both the existing and Flask 3.x versions, if possible.

---

## Step-by-Step Migration Procedure

### 1. Upgrade Flask Dependency

- **Action:**  
  Update the Flask requirement in your `requirements.txt` or `pyproject.toml`:
  - If `requirements.txt`: Replace any line with `Flask==...` or `Flask>=...` with `Flask>=3.0,<4.0`
  - Alternatively, run:
    ```bash
    pip install --upgrade "Flask>=3.0,<4.0"
    ```

- **Expected outcome:**  
  Flask 3.x is installed in the environment.

- **Verification command:**  
  ```bash
  python -c "import flask; print(flask.__version__)"
  ```
  Output should be `3.x.x`.

- **Rollback action if it fails:**  
  Reinstall the previous Flask version:
  ```bash
  pip install "Flask==<PREVIOUS_VERSION>"
  ```
  Restore original `requirements.txt` from VCS.

---

### 2. Update Flask Extensions and Dependencies

- **Action:**  
  Upgrade all Flask extensions and related dependencies to versions compatible with Flask 3.x.
  For each extension (e.g., Flask-Login, Flask-WTF), check release notes for Flask 3.x support and upgrade as needed:
  ```bash
  pip install --upgrade <extension-name>
  ```

- **Expected outcome:**  
  All dependencies support Flask 3.x.

- **Verification command:**  
  ```bash
  pip check
  ```
  Should report no conflicts.

- **Rollback action if it fails:**  
  Reinstall compatible versions known to work with Flask <3.x:
  ```bash
  pip install "<extension-name>==<PREVIOUS_VERSION>"
  ```

---

### 3. Refactor Deprecated / Removed API Usage

- **Action:**  
  Update code where Flask 3.x removes or changes previously deprecated functions, e.g.:
    - Remove use of `flask.ext.*` imports.
    - Migrate `app.json_encoder`/`json_decoder` (use `app.json`).
    - Address removed APIs from [Flask 3.0 changelog](https://flask.palletsprojects.com/en/3.0.x/changes/).

- **Expected outcome:**  
  Source code has no usage of removed APIs, deprecated behavior, or old import patterns.

- **Verification command:**  
  Run:
  ```bash
  pytest
  ```
  All tests should pass.

- **Rollback action if it fails:**  
  Revert code changes via git:
  ```bash
  git checkout -- <affected_file>
  ```

---

### 4. Run Full Test Suite

- **Action:**  
  Execute all unit, integration, and system tests.

- **Expected outcome:**  
  All tests pass with Flask 3.x.

- **Verification command:**  
  ```bash
  pytest
  ```

- **Rollback action if it fails:**  
  Investigate failing tests; if unresolved, revert to pre-upgrade state and dependencies.

---

### 5. Build and Deploy to Staging

- **Action:**  
  Build and deploy the application to a staging/pre-production environment matching production settings.

- **Expected outcome:**  
  Application deploys and runs successfully on Flask 3.x.

- **Verification command:**  
  - Check deployment status via logs or monitoring tools.
  - Manually test key endpoints.

- **Rollback action if it fails:**  
  Revert staging environment to the previous image or artifacts.

---

## Verification & Smoke Tests

After migration, verify:

```bash
# Basic server start
python run.py  # or correct Flask entrypoint

# Key endpoint checks
curl -I http://localhost:5000/
curl -I http://localhost:5000/health  # if available
curl -I http://localhost:5000/api/...

# Run functional tests
pytest

# Check logs for errors
tail -n 50 app.log  # or journalctl, as appropriate
```

All endpoints should return 2xx/3xx codes, and tests should pass.

---

## Rollback Procedure

1. **Restore previous Flask and extension versions**
    ```bash
    pip install "Flask==<PREVIOUS_VERSION>"
    pip install -r requirements.txt  # with previous, backed-up file
    ```
2. **Revert any code changes due to API refactoring**
    ```bash
    git checkout <previous_commit_hash>
    ```

3. **Re-deploy application to target environment**
    - Redeploy from known-good artifact or image.

4. **Smoke test to confirm last known good state**

---

## Post-Migration Monitoring

Monitor the following for the next 24–48 hours:

- **Error logs:** Seek `ImportError`, `AttributeError`, or new warnings.
- **Application process health:** Automatic restarts or crashes.
- **Endpoint monitoring:** Uptime pings and load tests to main endpoints.
- **Performance metrics:** Response time, throughput, error rates.
- **User bug reports or support tickets.**

Examples:
```bash
tail -f app.log | grep -i error
```
Or review APM/monitoring dashboards for alert spikes.

---

## Known Issues & Workarounds

- **Extension incompatibility:** Some older Flask extensions are not yet Flask 3.x-ready. Pin the affected extension to the last known-compatible version and monitor for official updates.
- **Deprecated API removals:** If code heavily uses now-removed Flask internals, consult the [Flask 3.x migration guide](https://flask.palletsprojects.com/en/3.0.x/changes/) for replacement patterns.

If blockers cannot be resolved: rollback as per above.

---