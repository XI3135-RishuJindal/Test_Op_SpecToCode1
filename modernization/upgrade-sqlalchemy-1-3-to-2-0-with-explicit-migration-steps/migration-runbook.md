# Migration Runbook: SQLAlchemy 1.3 to 2.0 Upgrade

---

## Pre-Migration Checklist

_All items must be ✅ prior to proceeding with the migration._

- [ ] ✅ All automated tests (unit, integration, e2e) are passing on current SQLAlchemy 1.3 code.
- [ ] ✅ Project dependencies (`requirements.txt`, `pyproject.toml`, or `Pipfile`) are under version control.
- [ ] ✅ All usage of deprecated APIs in SQLAlchemy 1.3 is identified and documented (see [Migration Procedure]).
- [ ] ✅ All developers are notified of a feature freeze during the upgrade window.
- [ ] ✅ A production backup of the database is completed and verified.
- [ ] ✅ Rollback plan is documented and tested in staging.
- [ ] ✅ All environment variables and credentials are current and available for local, CI, and production.
- [ ] ✅ A maintenance window is scheduled (if required).

---

## Environment Setup

_Commands / steps to prepare local and CI environments for the upgrade._

### 1. Update Local Environment

```bash
# Create/activate a virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Remove old SQLAlchemy and install 2.x
pip uninstall sqlalchemy  # if installed
pip install "SQLAlchemy>=2.0,<2.1"
```

### 2. Update Dependency Lockfile

If using a lockfile (such as `requirements.txt`):

```bash
pip freeze > requirements.txt
# or
poetry add "SQLAlchemy@^2.0"
# or
pipenv install "SQLAlchemy>=2.0,<2.1"
```

### 3. Update CI Configuration

- Ensure CI config uses Python 3.7+ (as required by SQLAlchemy 2.0).
- Confirm CI install step uses the updated dependency spec.

---

## Step-by-Step Migration Procedure

1. **Update SQLAlchemy Version in Dependency Files**
   - **Action:** Change minimum required SQLAlchemy version to `2.0` in all relevant files.
   - **Expected outcome:** Application installs SQLAlchemy 2.x on all environments.
   - **Verification command:**
     ```bash
     pip show sqlalchemy
     # Version should be 2.0.x or later
     ```
   - **Rollback action:** Restore previous dependency file and reinstall dependencies.

2. **Refactor Deprecated API Usage**
   - **Action:** Update codebase to replace removed/changed SQLAlchemy 1.3 APIs:
     - Change all `from sqlalchemy.ext.declarative import declarative_base` to `from sqlalchemy.orm import declarative_base`
     - Replace `session.query(...).get(pk)` with `session.get(Model, pk)`
     - Remove implicit session use and use explicit `Session()` context managers (where appropriate)
     - Prefix all SELECT/INSERT/UPDATE/DELETE Core queries with `select()`, `insert()`, etc.
     - Update any usage of removed functions/params per [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
   - **Expected outcome:** All source code is compatible with SQLAlchemy 2.0.
   - **Verification command:**
     ```bash
     pytest  # Or your test command
     ```
   - **Rollback action:** Revert all code changes.

3. **Test Migration in Local and CI**
   - **Action:** Run full test suite locally and in CI to catch any issues.
   - **Expected outcome:** All tests pass.
   - **Verification command:**
     ```bash
     pytest
     ```
   - **Rollback action:** Pin SQLAlchemy back to 1.3 in dependencies and revert code changes.

4. **Deploy To Staging**
   - **Action:** Deploy the upgraded code to staging/pre-production environment.
   - **Expected outcome:** Staging workflows using SQLAlchemy 2.0 function normally; no errors in logs.
   - **Verification command:**
     - Application-specific health checks
     - Review staging logs for SQLAlchemy errors.
   - **Rollback action:** Redeploy previous build; restore previous dependencies.

5. **Production Deployment**
   - **Action:** Deploy upgrade to production during maintenance window.
   - **Expected outcome:** Application operates normally with SQLAlchemy 2.0; no user-facing or backend errors.
   - **Verification command:** 
     - Application health monitoring
     - Critical workflows tested manually
     - `pip show sqlalchemy` on production
   - **Rollback action:** Follow [Rollback Procedure] below.

---

## Verification & Smoke Tests

_Run all of the following to confirm the upgrade is working:_

- Full test suite:
  ```bash
  pytest
  ```
- Manually verify:
  - Main CRUD operations in the application
  - Background jobs/tasks that involve the database
  - Any raw SQL execution points
- Check logs for SQLAlchemy deprecation or error messages (no warnings/errors should occur under normal operation)
- Query version in-app, if available (e.g., log `sqlalchemy.__version__` at startup)

---

## Rollback Procedure

_Full rollback steps in the event the upgrade must be undone:_

1. **Restore Previous Dependency Files**
   - Check out previous version of `requirements.txt` / `pyproject.toml` / `Pipfile` where SQLAlchemy 1.3.x is specified.

2. **Revert Code Changes**
   - Undo all SQLAlchemy 2.0 API migration commits (use `git revert` or restore from backup branch).

3. **Reinstall Dependencies**
   - Remove current virtualenv and create a new one:
     ```bash
     rm -rf venv/
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

4. **Repeat in CI/CD**
   - Ensure CI/CD pipeline uses older dependency spec and passes all tests.

5. **Redeploy Previous Release**
   - Deploy last known-good build to staging, then to production (following usual release process).

6. **Confirm Application Functionality**
   - Run verification & smoke tests as above; ensure system is operating as expected.

---

## Post-Migration Monitoring

**For 24–48 hours after deployment:**

- **Logs:** 
  - Review for any SQLAlchemy deprecation or error messages.
  - Monitor for exceptions like `AttributeError`, `TypeError`, or others related to ORM/session handling.
- **Metrics:** 
  - Database query latency and error rates.
  - Application error rates; alert on any spikes.
- **Alerts:** 
  - Error spike alerts for database or ORM transactions.
  - Application-level alerting on failed CRUD operations.

---

## Known Issues & Workarounds

- **Issue:** Silent failures due to implicit session usage removed in 2.0.
  - **Workaround:** Use explicit `with Session() as session:` blocks everywhere; audit code for missing session context.
- **Issue:** ORM APIs removed—`session.query(...).get(pk)` does not exist.
  - **Workaround:** Use `session.get(Model, pk)` instead.
- **Issue:** Core query construction syntax errors (e.g., positional arguments not allowed in filters).
  - **Workaround:** Refactor to use only keyword arguments and SQLAlchemy 2.x query styles.
- **Issue:** Third-party libraries not yet compatible with SQLAlchemy 2.0.
  - **Workaround:** Pin such dependencies, or abandon upgrade until compatible, as per [Pre-Migration Checklist].

---

_N/A — not applicable to this task sections have been omitted per instruction._