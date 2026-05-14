# Migration Runbook: Migrate Application Code for SQLAlchemy 2.x Compatibility

---

## Pre-Migration Checklist

- [ ] ✅ Inventory all application entry points that use SQLAlchemy.
- [ ] ✅ Identify direct and transitive dependencies on SQLAlchemy (including plugins and extensions).
- [ ] ✅ Verify database access credentials and backup current database(s).
- [ ] ✅ Confirm test suite covers all database interactions.
- [ ] ✅ Document all SQLAlchemy usage patterns in the codebase (ORM, Core/Engine, custom queries, etc).
- [ ] ✅ Install SQLAlchemy 2.x in a development environment.
- [ ] ✅ Review official [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migration) for breaking changes relevant to your codebase.
- [ ] ✅ Communicate planned migration and windows to all stakeholders.
- [ ] ✅ Validate rollback plan readiness.

---

## Environment Setup

1. **Clone the repository and create a new feature branch**
   ```bash
   git checkout -b sqlalchemy2-migration
   ```

2. **Update SQLAlchemy to 2.x in your dependency manifest. Example:**
   - `requirements.txt`
     ```
     SQLAlchemy>=2.0,<3.0
     ```
   - Or, for other languages/build tools, adapt accordingly.

3. **(Optional, but recommended) Set up a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. **Install updated dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **In CI/CD pipeline config:**  
   - Update the build image/client to ensure SQLAlchemy 2.x is installed.
   - Run tests with `--fail-fast` to catch migration issues early.

---

## Step-by-Step Migration Procedure

1. **Update Import Statements**
   - **Action:** Ensure all usage imports from `sqlalchemy` and `sqlalchemy.orm` use newer patterns (no deprecated `sqlalchemy.ext.*`, etc).
   - **Expected outcome:** Code runs without ImportError/DeprecationWarnings.
   - **Verification command:**  
     ```bash
     grep "sqlalchemy.ext" -R your_project/
     ```
   - **Rollback:** Revert import statement changes.

2. **Update Engine & Session Usage**
   - **Action:** Refactor `Session` instantiation to use `Session(engine)` instead of legacy patterns like `sessionmaker()` without binding.
   - **Expected outcome:** Session usage aligns with 2.x API.
   - **Verification command:**  
     ```bash
     grep -R "sessionmaker" your_project/
     ```
   - **Rollback:** Restore original session creation logic.

3. **Refactor Transaction Patterns**
   - **Action:** Update legacy transaction blocks (`session.begin()`, explicit commits) to use context managers:
     ```python
     with Session(engine) as session:
         with session.begin():
             ...
     ```
   - **Expected outcome:** Database writes/reads work as expected using the context manager.
   - **Verification command:**  
     Run tests covering commits and rollbacks.
   - **Rollback:** Revert to pre-migration transaction handling.

4. **Update Query API**
   - **Action:** Replace deprecated `.execute()`, `.scalar()`, `.first()`, `.all()` usages per [2.0 Query API](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#orm-query-api).
   - **Expected outcome:** Query logic works and does not raise deprecation warnings or errors.
   - **Verification command:**  
     ```bash
     grep -n "execute\|scalar\|first\|all" your_project/
     ```
   - **Rollback:** Restore original query logic.

5. **Replace ORM Bulk Methods**
   - **Action:** Replace deprecated ORM bulk methods (`bulk_save_objects`, `bulk_insert_mappings`, etc.) with supported alternatives or Core-level bulk operations.
   - **Expected outcome:** Bulk operations perform as expected.
   - **Verification command:**  
     Run relevant test cases.
   - **Rollback:** Restore previous bulk operation code.

6. **Address Deprecated/Removed Features**
   - **Action:** Remove or refactor usage of features removed in 2.x (e.g., `convert_unicode`, implicit autocommit, etc).
   - **Expected outcome:** Application runs without errors or removed feature usage.
   - **Verification command:**  
     Run application and observe logs for `DeprecationWarning` or `RemovedIn20Warning`.
   - **Rollback:** Restore code and dependencies to pre-migration versions.

7. **Run Full Test Suite**
   - **Action:** Execute all automated tests (unit, integration, e2e).
   - **Expected outcome:** All tests pass.
   - **Verification command:**  
     ```bash
     pytest
     # or other project-specific test command
     ```
   - **Rollback:** Revert all code and dependency changes.

---

## Verification & Smoke Tests

- **Run all automated tests:**
  ```bash
  pytest
  # or equivalent
  ```
- **Start the application and perform manual smoke tests:**
  - Basic DB CRUD flows (create, read, update, delete).
  - Application startup: should succeed with no SQLAlchemy deprecation/fatal errors in logs.
  - If API, hit endpoints that rely on DB access.

- **Check logs for any SQLAlchemy-related tracebacks or backward-compatibility warnings**
  - Example:
    ```bash
    grep "sqlalchemy" logs/app.log
    ```

---

## Rollback Procedure

1. **Checkout main branch**
   ```bash
   git checkout main
   ```

2. **Revert SQLAlchemy version in dependency manifest to pre-migration version**
   - Example: In `requirements.txt`, set specific previous version.
     ```
     SQLAlchemy==<previous_version>
     ```

3. **Re-install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Revert source code changes**
   ```bash
   git reset --hard <last-known-good-commit>
   ```

5. **Run test suite to confirm stability**
   ```bash
   pytest
   ```

6. **Re-deploy previous, stable build/package to production**
   - Use existing CI/CD procedures.

7. **Notify stakeholders of rollback completion.**

---

## Post-Migration Monitoring

- **Metrics to watch:**
  - Application error rates, especially DB-related exceptions.
  - Response times for DB-backed endpoints/workloads.
- **Logs:**
  - SQLAlchemy stack traces or warnings in application logs.
- **Alerts:**
  - Increased DB error rates (e.g., connection errors, transaction failures).
  - User-reported issues related to data access or save operations.

Monitor for at least 24-48 hours post-deployment.

---

## Known Issues & Workarounds

- **Removed/Modified APIs:** Certain APIs removed or changed in 2.x; see [SQLAlchemy What's New 2.0](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html).
  - **Workaround:** Use official migration guide for code conversion examples.
- **Extensions/Plugins Compatibility:** Some third-party extensions may not be 2.x-compatible.
  - **Workaround:** Pin extension versions or search for compatible forks/upgrades.
- **Legacy Transaction Handling:** Legacy transaction functions (`session.commit()` outside of context managers) may fail.
  - **Workaround:** Refactor to use context managers (`with session.begin()`).

---

