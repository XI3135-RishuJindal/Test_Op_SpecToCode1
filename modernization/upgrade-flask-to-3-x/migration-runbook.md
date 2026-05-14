# Flask 3.x Upgrade — Migration Runbook

## Pre-Migration Checklist

**All items must be ✅ before proceeding:**

- [ ] Codebase is under version control and latest branch is pushed to remote.
- [ ] All existing tests (unit, integration, end-to-end) are passing.
- [ ] Python version is compatible with Flask 3.x (≥3.8).
- [ ] No uncommitted local changes; working directory is clean.
- [ ] Backup created for current requirements/dependencies files (e.g., `requirements.txt`, `Pipfile`, `pyproject.toml`).
- [ ] Review Flask 3.x [changelog](https://flask.palletsprojects.com/en/3.0.x/changes/) for relevant breaking changes.
- [ ] Confirm compatibility of key Flask extensions (e.g., flask_sqlalchemy, flask_login) with Flask 3.x.

## Environment Setup

### Local Environment Preparation

```bash
# (Optional, recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Backup current dependencies
cp requirements.txt requirements.txt.bak

# Upgrade pip and setuptools to avoid install issues
pip install --upgrade pip setuptools wheel
```

### CI Environment Preparation

- Ensure CI image/runtime supports Python ≥3.8.
- Update dependency cache settings if necessary.
- Confirm test and deployment scripts allow for updated dependencies.

## Step-by-Step Migration Procedure

1. **Update Flask Version in Dependency File**
   - **Action:** Change `Flask` version in `requirements.txt` (or `Pipfile`/`pyproject.toml`) to `Flask>=3.0,<4.0`.
   - **Expected Outcome:** Dependency file references Flask 3.x.
   - **Verification Command:**
     ```bash
     grep Flask requirements.txt
     ```
   - **Rollback:** Revert to backup dependency file.

2. **Upgrade Flask and Dependencies**
   - **Action:** Install upgraded Flask and update dependencies.
     ```bash
     pip install --upgrade -r requirements.txt
     ```
   - **Expected Outcome:** Flask 3.x and compatible packages are installed.
   - **Verification Command:**
     ```bash
     python -c "import flask; print(flask.__version__)"
     ```
   - **Rollback:** Re-activate backup virtual env or reinstall from `requirements.txt.bak`.

3. **Check Flask Extension Compatibility**
   - **Action:** Review and upgrade Flask extensions as needed.
     ```bash
     pip list | grep Flask
     ```
     Upgrade any primary extensions (example):
     ```bash
     pip install --upgrade flask_sqlalchemy flask_login flask_wtf
     ```
   - **Expected Outcome:** All extensions are up to date and compatible.
   - **Verification Command:**
     ```bash
     pip check
     ```
   - **Rollback:** Downgrade any problematic extension or revert extension specs to previous versions.

4. **Run Tests Locally**
   - **Action:** Run all local tests to check for compatibility issues.
     ```bash
     pytest
     ```
   - **Expected Outcome:** All tests pass cleanly.
   - **Verification Command:** Review test output (should be green/no failures).
   - **Rollback:** Investigate and fix test regressions, or revert to previous environment.

5. **Check for Deprecated/Removed Flask APIs**
   - **Action:** Search codebase for use of removed/deprecated Flask APIs per [Flask 3.0 Porting Guide](https://flask.palletsprojects.com/en/3.0.x/porting/).
   - **Expected Outcome:** Code does not use removed interfaces or deprecated patterns.
   - **Verification Command:**
     ```bash
     grep -rnw . -e 'flask.ext' -e 'app.errorhandler(Exception)' -e 'app.env'
     ```
   - **Rollback:** Refactor code or revert changes that require more time.

6. **Deploy to Staging Environment**
   - **Action:** Promote updated code to a staging/pre-production environment.
   - **Expected Outcome:** Application starts and behaves as expected.
   - **Verification Command:** Access app endpoints, check logs for Flask startup messages, monitor error logs.
   - **Rollback:** Revert deployment to previous release.

7. **Deploy to Production**
   - **Action:** Merge and deploy to production.
   - **Expected Outcome:** Production application uses Flask 3.x, no critical errors.
   - **Verification Command:** Monitor production for traffic, error rates, and log anomalies.
   - **Rollback:** Initiate rollback procedure (see below).

## Verification & Smoke Tests

- **Functional Verification:**  
  - Run basic user scenarios (login, API endpoints, pages).
- **Automated Tests:**  
  ```bash
  pytest
  ```
- **Health Endpoint:**  
  ```bash
  curl -f http://localhost:5000/health
  ```
- **Logs:**  
  - Examine server logs for exceptions on startup or while handling requests.

## Rollback Procedure

1. **Restore Previous Dependency File**
   - Replace updated `requirements.txt` with `requirements.txt.bak` (or earlier lockfile).

2. **Reinstall Dependencies**
   ```bash
   pip install --force-reinstall -r requirements.txt.bak
   ```

3. **Redeploy Application**
   - Deploy the reverted code and dependencies to staging/production as needed.

4. **Verify Rollback**
   - Run tests and smoke checks to confirm the application is functioning as before.

5. **Monitor**
   - Observe metrics and logs to ensure rollback success.

## Post-Migration Monitoring

- **Metrics to Watch (24-48h):**
  - Error rate (5xx, exceptions in logs)
  - Application startup errors
  - User-reported issues (support desk, sentry/rollbar, etc.)
- **Log Monitoring:**
  - New stack traces or "ImportError"/"AttributeError"
  - Flask-specific warnings/errors at startup/runtime
- **Alerts:**
  - Uptime/health check failures
  - Latency spikes

## Known Issues & Workarounds

- If using `flask.ext.*` imports:  
  - **Workaround:** Change to explicit imports via actual extension module (e.g., `import flask_sqlalchemy`).
- Extensions not compatible with Flask 3.x may fail to import or break:  
  - **Workaround:** Pin extension versions as per their Flask 3.x compatibility docs, or wait for maintainers to support Flask 3.x.
- Removed APIs (e.g., `app.env`, certain error handling signatures):  
  - **Workaround:** Refactor affected code as per [Flask 3.x porting guide](https://flask.palletsprojects.com/en/3.0.x/porting/).

---

_N/A — not applicable to this task._ (for any sections not listed above)