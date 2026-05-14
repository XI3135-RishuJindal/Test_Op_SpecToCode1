# Migration Runbook: SQLAlchemy 2.x Compatibility

## Pre-Migration Checklist

- [ ] ✅ Inventory all code paths that import or utilize SQLAlchemy APIs.
- [ ] ✅ Ensure test coverage for all ORM/database interactions.
- [ ] ✅ Freeze current production and development requirements.
- [ ] ✅ Backup all source code repositories and databases.
- [ ] ✅ Review SQLAlchemy 2.x [Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html).
- [ ] ✅ Communicate maintenance window and migration plan to stakeholders.
- [ ] ✅ Confirm all developers are aware of migration and have a rollback plan.

## Environment Setup

1. **Update Local Environment**
    - Create and activate a new virtual environment (if applicable).
    - Upgrade pip:
      ```sh
      pip install --upgrade pip
      ```
    - Backup the requirements file:
      ```sh
      cp requirements.txt requirements.txt.pre-sqlalchemy2
      ```

2. **Update SQLAlchemy Package**
    ```sh
    pip install 'sqlalchemy>=2.0,<2.1'
    ```

3. **Update CI Configuration**
    - Update your CI pipeline to use SQLAlchemy 2.x.
    - Example for requirements:
      ```
      sqlalchemy>=2.0,<2.1
      ```

    - If applicable, update Docker or environment specifications accordingly.

4. **Dependencies Audit**
    - Audit and update any libraries or ORMs that depend on SQLAlchemy to their SQLAlchemy 2.x-compatible versions.

## Step-by-Step Migration Procedure

1. **Update Imports and Engine/Session Usage**
    - **Action:** Refactor all imports to use modern locations (e.g., `from sqlalchemy.orm import sessionmaker`), update engine and session creation to follow SQLAlchemy 2.x patterns.
    - **Expected outcome:** No deprecated import/module access; all session and engine usage conforms to 2.x API.
    - **Verification command:**
      ```sh
      grep -RI "from sqlalchemy.ext.declarative" . # Should return no results
      ```
    - **Rollback:** Revert source code files to previous commit.

2. **Replace Deprecated `session.query()` Syntax**
    - **Action:** Refactor queries to use `select()` and session execution where applicable. Example:
      ```python
      # Before
      session.query(User).filter_by(id=1).first()
      # After
      session.execute(select(User).filter_by(id=1)).scalar_one_or_none()
      ```
    - **Expected outcome:** No usage of deprecated query patterns.
    - **Verification command:**
      ```sh
      grep -RI "session.query" .
      ```
    - **Rollback:** Undo changes, restore previous query code.

3. **Adopt Explicit Transaction Blocks**
    - **Action:** Replace implicit transaction scopes with `with Session.begin():` blocks where needed.
    - **Expected outcome:** All DB writes are within explicit transaction blocks.
    - **Verification command:**
      ```sh
      grep -RI "with Session" .
      ```
    - **Rollback:** Revert affected files.

4. **Remove Deprecated `commit()` on Connections**
    - **Action:** Remove `commit()` calls on connections (should only be on session).
    - **Expected outcome:** No direct commits on connections.
    - **Verification command:**
      ```sh
      grep -RI "connection.commit" .
      ```
    - **Rollback:** Restore previous DB transaction usage.

5. **Update All Custom Declarative Base Usages**
    - **Action:** Use `sqlalchemy.orm.declarative_base` instead of legacy import.
    - **Expected outcome:** All model base classes use the new import path.
    - **Verification command:**
      ```sh
      grep -RI "declarative_base" .
      ```
    - **Rollback:** Revert to old base definition.

6. **Run and Fix Application Test Suite**
    - **Action:** Execute all automated tests; fix any broken due to migration.
    - **Expected outcome:** All tests pass under SQLAlchemy 2.x.
    - **Verification command:**
      ```sh
      pytest  # or relevant test command
      ```
    - **Rollback:** Analyze test output, revert relevant code.

## Verification & Smoke Tests

- **Run basic database connectivity check:**
  ```sh
  python -c "from your_app import Session; with Session() as session: session.execute('SELECT 1')"
  ```
- **Execute core functional tests:**
  ```sh
  pytest tests/
  ```
- **Manual UI smoke test:** (if applicable)
    - Log in, create, update and delete representative records.
- **API test:** (if applicable)
    - Invoke endpoints that exercise database reads/writes.

## Rollback Procedure

1. **Deactivate migrated environment:**
    ```sh
    deactivate  # If using virtualenv/venv
    ```

2. **Restore backup requirements:**
    ```sh
    mv requirements.txt.pre-sqlalchemy2 requirements.txt
    pip install -r requirements.txt
    ```

3. **Revert source code changes:**
    ```sh
    git checkout <last-known-good-commit>
    ```

4. **Restart application/services as needed.**

5. **Verify application is operational and database access functions as pre-migration:**
    ```sh
    pytest
    ```

## Post-Migration Monitoring

- **Key Metrics:**
  - DB query error rates (e.g., via APM)
  - Application exception/error logs referencing SQLAlchemy
  - Application performance latency for DB-bound endpoints

- **Logs/Alerts:**
  - Monitor for log entries containing SQLAlchemy warnings or errors
  - Enable and watch for alerts on DB connection errors or failed migrations

- **Recommended Duration:**  
  - Closely monitor for 24–48 hours post-deployment

## Known Issues & Workarounds

- **Issue:** Some third-party libraries may not yet fully support SQLAlchemy 2.x.
   - **Workaround:** Pin those packages to compatible versions, or delay upgrade until upstream support is available.

- **Issue:** Object session handling semantics have changed; unexpected lazy loading failures.
    - **Workaround:** Wrap DB modifications in explicit `with Session.begin()` blocks; review SQLAlchemy 2.x docs for session state handling.

- **Issue:** Legacy string-based queries (`session.execute("SELECT * FROM table")`) require `text()` wrapper.
    - **Workaround:** Use `from sqlalchemy import text` and wrap queries as `session.execute(text("SELECT * FROM table"))`.

---

**End of Runbook**
