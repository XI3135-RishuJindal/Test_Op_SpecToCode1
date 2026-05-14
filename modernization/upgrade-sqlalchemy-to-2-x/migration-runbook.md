# SQLAlchemy 2.x Migration Runbook

## Pre-Migration Checklist

All items must be ✅ before proceeding.

- [ ] ✅ Current test suite passes against latest 1.x SQLAlchemy version
- [ ] ✅ All direct `sqlalchemy` dependencies are specified in `requirements.txt`/`pyproject.toml`
- [ ] ✅ No use of SQLAlchemy APIs or patterns [removed or deprecated in v2.x](https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html)
- [ ] ✅ Complete codebase backup available (VCS branch, artifact backup, and database snapshot if applicable)
- [ ] ✅ Stakeholders notified about upgrade window/downtime

---

## Environment Setup

Follow these steps to prep for migration:

**Local:**
```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install existing dependencies
pip install -r requirements.txt

# (Optional) Pin SQLAlchemy to latest 1.x to validate baseline
pip install 'SQLAlchemy<2.0'
pytest  # Or your relevant test command
```

**CI:**
- Ensure clean build and test pipeline with pinned 1.x SQLAlchemy before migration.
- Confirm you can update CI scripts/config to allow SQLAlchemy 2.x.

---

## Step-by-Step Migration Procedure

1. **Bump SQLAlchemy to 2.x**

    - **Action:**  
      Update dependency specification to `SQLAlchemy>=2.0,<3.0`, e.g. in `requirements.txt` or `pyproject.toml`.
    - **Expected outcome:**  
      The environment now installs SQLAlchemy 2.x.
    - **Verification command:**  
      `pip freeze | grep SQLAlchemy`
    - **Rollback action:**  
      Revert dependency file and reinstall with `SQLAlchemy<2.0`.

2. **Upgrade Dependencies for SQLAlchemy 2.x Compatibility**

    - **Action:**  
      Upgrade or patch any ORM-related dependencies (e.g., Alembic, Flask-SQLAlchemy) that require support for SQLAlchemy 2.x.
    - **Expected outcome:**  
      All dependencies are up to date and compatible.
    - **Verification command:**  
      `pip check`
    - **Rollback action:**  
      Reinstall previous dependency versions.

3. **Update Codebase for 2.x API Changes**

    - **Action:**  
      Refactor the code to comply with 2.x syntax (see [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)), e.g.:
        - Use `select()` or `from sqlalchemy import select`
        - Avoid implicit legacy `session.query()`
        - Replace `engine.execute()` with new patterns
        - Address type and import changes
    - **Expected outcome:**  
      No deprecated or removed 1.x usage remains; code compiles/passes lint.
    - **Verification command:**  
      Run linter and static checks, e.g.:
      ```bash
      python -m compileall .
      flake8 .
      ```
    - **Rollback action:**  
      Restore code from backup or VCS.

4. **Run and Fix Tests**

    - **Action:**  
      Execute the automated test suite (`pytest`, `unitest`, etc.) and resolve breakages due to 2.x changes.
    - **Expected outcome:**  
      All tests pass under SQLAlchemy 2.x.
    - **Verification command:**  
      `pytest`
    - **Rollback action:**  
      Revert to backup branch, original dependency versions.

5. **Deploy to Staging and Validate Application**

    - **Action:**  
      Deploy upgraded code to staging/pre-production; run critical workflows.
    - **Expected outcome:**  
      Application runs without errors, database access is functional.
    - **Verification command:**  
      Application logs/health checks, key smoke tests (see next section).
    - **Rollback action:**  
      Revert deploy, restore backup dependencies/code.

---

## Verification & Smoke Tests

Run after staging deploy and initial production rollout:

```bash
# Confirm SQLAlchemy 2.x is installed
python -c 'import sqlalchemy; print(sqlalchemy.__version__)'

# Basic connectivity test
python -c 'from sqlalchemy import create_engine; create_engine("DB_URL").connect()'

# Run representative CRUD test case
pytest tests/test_db_integration.py

# Application-specific smoke checks
curl -f http://YOUR_APP/ping
curl -f http://YOUR_APP/some-db-backed-endpoint
```

Success: All checks pass, endpoints respond, no tracebacks in logs.

---

## Rollback Procedure

If migration fails at any point, execute these rollback steps:

1. Restore dependency file(s) to prior version (where SQLAlchemy is `<2.0`).
2. Reinstall production dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Restore application code from backup or revert the VCS branch/commit, as needed:

    ```bash
    git checkout <pre-migration-commit>
    ```

4. Re-deploy the application/service.
5. Confirm application health and database access as normal.
6. Verify logs to ensure normal operation.

---

## Post-Migration Monitoring

For 24-48 hours after deployment, monitor:

- **Application logs**: Look for SQLAlchemy-related errors, warnings.
- **Database logs/performance**: Monitor for increased errors, invalid queries, or performance degradation.
- **Key metrics**:
    - Error rates on database operations
    - Latency or timeout increases for DB-backed endpoints
    - ORM session/connection pool exhaustion
- **Alerts**: Set up temporary alerts for new SQLAlchemy error patterns (search for `sqlalchemy.exc`, `DeprecationWarning`, etc.)
- **Bug/incident intake**: Have an engineer on-call for rapid triage of new issues.

---

## Known Issues & Workarounds

- **Removed/Changed APIs**: Some methods (e.g., `engine.execute()`, legacy `session.query`) are removed or changed in 2.x. [Migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) provides code modernization tips.
- **Third-party Incompatibility**: Some libraries/plugins may require their own upgrades. Check their documentation.
- **Legacy Mode as Temporary Workaround**: To unblock migration, you may set `SQLALCHEMY_WARN_20=1` or use legacy mode ([docs](https://docs.sqlalchemy.org/en/20/glossary.html#term-legacy-mode)), but this is not recommended except as a last resort.

---
