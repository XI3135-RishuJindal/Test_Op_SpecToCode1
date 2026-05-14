# SQLAlchemy 2.x Migration Runbook

## Pre-Migration Checklist

All items below must be **✅** before proceeding:

- [ ] All project dependencies that require SQLAlchemy are compatible with v2.x  
- [ ] Application test suite passes with SQLAlchemy 1.4.x in “2.0 compatibility mode” (`future=True`)  
- [ ] Database schema migrations are up-to-date and tested  
- [ ] All deprecated APIs (e.g., `session.query`, use of string-based relationships) have been refactored  
- [ ] Verified that no unsupported dialects/extensions are in use  
- [ ] Recent backup of database and application source is available  
- [ ] CI/CD pipeline is green and ready to test the upgrade  
- [ ] Rollback plan is prepared and reviewed  
- [ ] Stakeholders have been notified of migration window

## Environment Setup

_Commands and steps to prepare upgrade test and deploy environments._

1. **Update Dependency Specification**

   Update the SQLAlchemy version constraint in your dependency file:

   - `requirements.txt`:  
     ```
     SQLAlchemy>=2.0,<3.0
     ```
   - `pyproject.toml` (for Poetry):  
     ```toml
     sqlalchemy = ">=2.0,<3.0"
     ```
   - `setup.py`:  
     ```python
     install_requires=["SQLAlchemy>=2.0,<3.0"]
     ```

2. **Install/Upgrade SQLAlchemy in Local Env**

   ```sh
   pip install --upgrade 'SQLAlchemy>=2.0,<3.0'
   ```
   
3. **Install in CI Environment**

   Update your CI workflow to ensure it pulls the latest requirements:

   ```sh
   pip install --upgrade -r requirements.txt
   ```

## Step-by-Step Migration Procedure

1. ### **Update Project Dependency**

   - **Action**: Pin SQLAlchemy version as specified above and run dependency installation locally and in CI.
   - **Expected Outcome**: SQLAlchemy 2.x is installed; `pip freeze | grep SQLAlchemy` outputs a 2.x version.
   - **Verification Command**:
     ```sh
     python -c 'import sqlalchemy; print(sqlalchemy.__version__)'
     ```
   - **Rollback**: Revert dependency file change and reinstall previous version (`pip install 'SQLAlchemy<2.0'`).

2. ### **Run Full Test Suite**

   - **Action**: Execute all unit, integration, and end-to-end tests.
   - **Expected Outcome**: All tests pass; no SQLAlchemy deprecation or usage errors.
   - **Verification Command**:
     ```sh
     pytest  # or your test runner
     ```
   - **Rollback**: Restore previous dependency file and revert code changes as needed.

3. ### **Codebase Refactor (If Needed)**

   - **Action**: Refactor legacy usage patterns; update to SQLAlchemy 2.x API (see [2.x migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)).
     - Replace `.query()` with `select()` constructs.
     - Replace `session.execute(text())` usages as needed.
     - Switch to `async` APIs where appropriate.
     - Remove usage of string relationship references.
   - **Expected Outcome**: Code uses SQLAlchemy 2.x APIs only. No warnings or errors during import/run.
   - **Verification Command**:
     ```sh
     pytest  # confirm no failures, review logs for deprecation warnings
     ```
   - **Rollback**: Use version control to revert problematic refactor commits.

4. ### **Deploy to Staging**

   - **Action**: Deploy updated code and dependencies to staging.
   - **Expected Outcome**: Application starts and functions without SQLAlchemy errors.
   - **Verification Command**:
     ```sh
     curl -f http://staging/healthz
     grep -i sqlalchemy /var/log/app.log
     ```
   - **Rollback**: Redeploy previous staging build/environment.

5. ### **Production Deploy**

   - **Action**: During scheduled window, deploy upgrade to production following normal release protocol.
   - **Expected Outcome**: Production system runs with SQLAlchemy 2.x; no regressions observed.
   - **Verification Command**:
     ```sh
     curl -f http://production/healthz
     tail -n 100 /var/log/app.log | grep -i sqlalchemy
     ```
   - **Rollback**: Initiate rollback playbook below.


## Verification & Smoke Tests

_Perform these after deploying to staging and production:_

- **Basic application health check:**
  ```sh
  curl -f http://<service>/healthz
  ```
- **Database connectivity test:**
  - Trigger a read/write operation via the application
- **Application log review:**
  ```sh
  tail -n 200 /var/log/app.log | grep -i 'sqlalchemy\|error' 
  ```
- **Critical path functional tests:**
  - Run automated smoke tests if available:
    ```sh
    pytest tests/smoke/
    ```

## Rollback Procedure

1. **Revert Dependency Change**

   ```sh
   # In all relevant environments:
   pip install 'SQLAlchemy<2.0'
   ```

2. **Revert Code Refactors**

   ```sh
   git checkout <last-known-good-commit>
   ```

3. **Re-run Test Suite**

   ```sh
   pytest
   ```

4. **Redeploy and Restart Application**

   Redeploy with previous configuration and restart services.

5. **Verify Restoration**

   Perform all health, smoke, and functional tests to confirm full operation.

## Post-Migration Monitoring

- **Metrics:**  
  - Application error rate (500s, exceptions)
  - Database latency and connections
  - Throughput of key endpoints

- **Logs:**  
  - Application/service logs for SQLAlchemy errors, warnings, or exceptions
  - SQLAlchemy connection pool logs

- **Alerts:**  
  - Trigger if abnormal error rates or repeated exceptions matching `sqlalchemy.*` patterns

- **Duration:**  
  Monitor intensively for at least 24–48 hours after deployment

## Known Issues & Workarounds

- **Breaking changes on legacy APIs:**  
  - See [migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
  - Refactor to explicitly use new style queries and session management

- **Old extensions/plugins not compatible:**  
  - Verify that all SQLAlchemy extensions in use support 2.x; if not, seek alternatives or updates

- **Async support changes:**  
  - Review and refactor any async code per [docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

_N/A — not applicable to this task_ for any section not listed above.