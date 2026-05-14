# SQLAlchemy 2.x Migration Runbook

## Pre-Migration Checklist

- [ ] ✅ All application dependencies are compatible with SQLAlchemy 2.x (check libraries like Alembic, Flask-SQLAlchemy, etc.)
- [ ] ✅ Complete codebase search for deprecated 1.x patterns (see [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html))
- [ ] ✅ Ensure latest, passing full suite of automated tests
- [ ] ✅ Backup of current production database and migration scripts
- [ ] ✅ Rollback procedure is reviewed and tested on staging
- [ ] ✅ Change is approved per standard SDLC processes

---

## Environment Setup

- Update SQLAlchemy in your local environment:

  ```sh
  pip install --upgrade "SQLAlchemy>=2.0,<3.0"
  ```

- In CI (add/update requirements):

  ```
  # requirements.txt
  SQLAlchemy>=2.0,<3.0
  ```

  _OR_ in `pyproject.toml`:

  ```toml
  [project.dependencies]
  SQLAlchemy = ">=2.0,<3.0"
  ```

- Clean install after updating dependencies:

  ```sh
  pip install -r requirements.txt
  # OR
  pip install .
  ```

  _Verify version:_

  ```sh
  python -c "import sqlalchemy; print(sqlalchemy.__version__)"
  ```

---

## Step-by-Step Migration Procedure

1. **Upgrade SQLAlchemy version**

   - Action: Bump SQLAlchemy dependency to `>=2.0,<3.0` in project config.
   - Expected outcome: SQLAlchemy 2.x is installed.
   - Verification command:
     ```sh
     python -c "import sqlalchemy; print(sqlalchemy.__version__)"
     # Output should start with '2.'
     ```
   - Rollback: Revert dependency to previous 1.x version and re-install.

2. **Update code for 2.x API breaking changes**

   - Action: Refactor code to comply with SQLAlchemy 2.x patterns:
     - Change `session.execute(text("..."))` to follow new style.
     - Replace deprecated ORM/query interfaces (e.g., `.execute`, `.scalar`, `.first` are now methods on `Session`).
     - Use Core-style “future” connection/session patterns.
     - Remove deprecated imports/usages.
     - Ensure engine/session/context managers use `with` blocks.
   - Expected outcome: Codebase does not reference deprecated 1.x-only APIs; all syntax is compatible with 2.x.
   - Verification command:
     ```sh
     pytest
     # or your test runner
     ```
   - Rollback: Revert source code changes to previous branch/commit.

3. **Upgrade and test migration scripts (if applicable)**

   - Action: Ensure Alembic or other migration tool scripts work with SQLAlchemy 2.x.
   - Expected outcome: Migration scripts run without error; new migrations can be generated and applied.
   - Verification command:
     ```sh
     alembic upgrade head
     # or equivalent
     ```
   - Rollback: Pin Alembic and/or revert to tool versions compatible with SQLAlchemy 1.x.

4. **Deploy to staging and validate application**

   - Action: Deploy the updated branch to a staging environment which uses SQLAlchemy 2.x.
   - Expected outcome: Application starts, connects to database; all DB interactions work as expected.
   - Verification command:
     - Application-specific smoke tests, e.g.:
       ```sh
       curl -f http://staging-app/health
       ```
     - Endpoints that trigger DB CRUD (create/read/update/delete).
   - Rollback: Redeploy previous artifact/environment with SQLAlchemy 1.x.

5. **Deploy to production**

   - Action: Deploy with change when all staging checks pass.
   - Expected outcome: Production system using SQLAlchemy 2.x with no functional regression.
   - Verification command:
     - Automated smoke/health checks, monitor errors, run regression suite.
   - Rollback: Redeploy previous production release and dependency versions.

---

## Verification & Smoke Tests

- Run all existing unit, integration, and end-to-end tests:

  ```sh
  pytest
  # or
  nosetests
  # or your test runner
  ```

- Manual or automated smoke tests:
  - Validate key DB interactions (list, create, update, delete).
  - Example HTTP check:
    ```sh
    curl -f http://<app-url>/health
    ```
  - Application logs: Ensure no warnings/errors from SQLAlchemy.

---

## Rollback Procedure

1. **Revert dependency changes**
   - Roll back to previous SQLAlchemy 1.x version in all environment files.

     ```sh
     pip install "SQLAlchemy<2.0"
     ```

2. **Revert code changes**
   - If code was refactored for 2.x and is incompatible with 1.x, revert source code from VCS to stable pre-migration commit or branch.

     ```sh
     git checkout <pre-migration-commit>
     ```

3. **Redeploy previous builds/artifacts**
   - Build and deploy prior app version (pre-migration) to staging/production using CI/CD as standard.

4. **Verify application**
   - Run health checks and DB operations to confirm functionality has returned to normal.

5. **Monitor for residual issues**
   - Check logs for migration/caching/connection pool warnings or errors.
   - Run targeted regression tests.

---

## Post-Migration Monitoring

- **Metrics to monitor:**
  - Application error rate (especially DB exceptions)
  - Latency for DB operations (CRUD)
  - Connection pool/server errors

- **Logs:**
  - Application logs for SQLAlchemy errors, deprecation warnings, or stack traces
  - Database logs for connection errors or transaction issues

- **Alerts:**
  - Automated alerts on increased error/exception rates
  - Alert on database connection exhaustion/exceptions

  _Monitor for at least 24–48 hours post-deployment._

---

## Known Issues & Workarounds

- **Deprecation Warnings:** Review logs for deprecation warnings; some APIs are removed entirely in 2.x, not just deprecated—review [2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html).
- **Third-Party Compatibility:** Some related libraries (e.g., Flask-SQLAlchemy <3.0, Alembic <1.8) may not support 2.x—upgrade these as needed.
- **Python Version:** SQLAlchemy 2.x requires Python 3.7+.
- **Implicit Execution:** “Implicit” connections/transactions are not supported; all DB activity must occur within explicit connection/session scope.
- **Old Query Patterns:** Legacy `session.query().from_self()` and some ORM chaining may be broken—refactor to recommended 2.x style per [docs](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#orm-query-usage).

---

For further troubleshooting, consult the [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html).