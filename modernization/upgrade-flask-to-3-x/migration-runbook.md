# Flask 3.x Upgrade Migration Runbook

## Pre-Migration Checklist

- [ ] ✅ All application and test dependencies are up-to-date and compatible versions identified for Flask 3.x.
- [ ] ✅ The current application is passing all tests (unit, integration, e2e) on both local and CI environments.
- [ ] ✅ Codebase scanned for usage of removed/deprecated Flask APIs and corresponding changes are planned.
- [ ] ✅ Backup of production environment and source code repository completed.
- [ ] ✅ Stakeholders notified of the planned maintenance window.
- [ ] ✅ Rollback plan is reviewed and tested on a staging environment.

---

## Environment Setup

### Local Environment

1. **Create a new virtual environment** (if applicable):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Upgrade pip and setuptools (if needed):**
   ```bash
   pip install --upgrade pip setuptools
   ```

3. **Install dependencies using requirements file:**
   ```bash
   pip install -r requirements.txt
   ```

### Continuous Integration (CI) Environment

1. **Update build config** (e.g., `.github/workflows`, `Jenkinsfile`, etc.) to use Python version compatible with Flask 3.x (Python >=3.8 is recommended).
2. **Ensure CI configuration installs dependencies from the updated requirements file.**
3. **Enable test jobs for any new/changed dependencies.**

---

## Step-by-Step Migration Procedure

1. **Update Flask version in dependency file**
   - **Action**: Change the Flask version specification in `requirements.txt`/`Pipfile`/`pyproject.toml` to `Flask>=3.0,<4.0`
   - **Expected outcome**: Project dependency file references correct Flask version.
   - **Verification command**:  
     ```bash
     grep Flask requirements.txt   # or your specific dependency file
     ```
   - **Rollback action**: Revert dependency file to original Flask version.

2. **Install/Update dependencies**
   - **Action**: Upgrade project dependencies to use Flask 3.x.
   - **Expected outcome**: Flask 3.x and compatible versions of dependencies are installed.
   - **Verification command**:  
     ```bash
     pip freeze | grep Flask
     ```
   - **Rollback action**: Reinstall dependencies with old requirements file.

3. **Scan and update deprecated/removed API usages**
   - **Action**: Identify and update usage of any Flask APIs deprecated or removed in 3.x (e.g., `flask.ext.*` imports, old extension patterns, `jsonify` behavior, custom CLI commands).
   - **Expected outcome**: Source code is compatible with Flask 3.x API surface.
   - **Verification command**:  
     ```bash
     grep -r "flask.ext" .   # and other patterns matching legacy APIs
     ```
   - **Rollback action**: Revert changed code or restore from source VCS.

4. **Run all unit and integration tests**
   - **Action**: Execute test suite locally and on CI.
   - **Expected outcome**: All tests pass.
   - **Verification command**:  
     ```bash
     pytest    # or your test runner, e.g. python -m unittest discover
     ```
   - **Rollback action**: Restore dependencies and/or code to last known good state.

5. **Smoke test the application locally**
   - **Action**: Start the app locally, hit a representative sample of routes/pages.
   - **Expected outcome**: Application starts, major features work, no critical errors.
   - **Verification command**:  
     ```bash
     flask run  # or your application's specific start command
     ```
   - **Rollback action**: Stop the app, revert code and dependencies.

6. **Deploy to staging/pre-production environment**
   - **Action**: Promote changes to a non-production environment for final validation.
   - **Expected outcome**: Application works as expected in staging.
   - **Verification command**:  
     - Application health checks/pages load.
     - Error logs do not show Flask-related tracebacks.
   - **Rollback action**: Redeploy previous version.

7. **Deploy to production**
   - **Action**: Release the upgrade to the live environment.
   - **Expected outcome**: Application operates normally, no Flask 3.x-specific issues.
   - **Verification command**:  
     - Application health checks.
     - Monitor error logs.
     - Smoke test major endpoints.
   - **Rollback action**: Redeploy previous (backed-up) environment.

---

## Verification & Smoke Tests

- Run test suite:
  ```bash
  pytest                     # or relevant runner
  ```
- Health check key endpoints:
  ```bash
  curl -I http://localhost:5000/        # replace URL/port as appropriate
  curl -I http://localhost:5000/api/...
  ```
- Check application logs for errors:
  ```bash
  tail -f logs/app.log         # or journalctl, docker logs, etc.
  ```
- Manually exercise authentication, key CRUD operations, and any custom routes or CLI commands.

---

## Rollback Procedure

1. **Restore Flask version in dependencies**  
   - Change dependency file back to original Flask version (`Flask==<old version>`).

2. **Reinstall previous dependencies**  
   - Run:
     ```bash
     pip install -r requirements.txt
     ```

3. **Revert any code changes made for Flask 3.x compatibility**  
   - Use:
     ```bash
     git checkout <last-known-good-commit> .
     ```

4. **Redeploy application to appropriate environment (staging/production) using the backed-up state.**

5. **Verify application functionality by running smoke tests and checking for normal operation.**

---

## Post-Migration Monitoring

- **Key metrics to monitor (24–48h):**
  - Application error rate (especially HTTP 500s)
  - Request latency
  - Traffic levels and patterns

- **Logs to watch:**
  - Application logs for traceback errors mentioning Flask or extensions
  - Web server logs (e.g., Gunicorn, uWSGI, etc.)

- **Alerts:**
  - Automated alerts for application outage, unusual error rates, or dependency errors

---

## Known Issues & Workarounds

- **Incompatible Extensions:**  
  Some Flask extensions may not yet be compatible with Flask 3.x. Refer to each extension's documentation for 3.x support. If incompatible, do not upgrade until the extension is updated.

- **Removed Deprecated APIs:**  
  Any code using APIs removed in Flask 3.x must be updated per Flask’s [3.0 migration guide](https://flask.palletsprojects.com/en/3.0.x/changes/#version-3-0-0).

- **Werkzeug and Jinja2 compatibility:**  
  Flask 3.x requires recent versions of Werkzeug and Jinja2. Pin compatible versions in your dependencies if needed.

- **Custom CLI Commands:**  
  Migration may require updates for custom Flask CLI commands due to changes in Click integration or API.

---

*(End of Runbook)*