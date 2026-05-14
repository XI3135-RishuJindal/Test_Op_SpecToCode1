# SQLAlchemy 2.x Compatibility Migration Design Document

## Architecture Overview

### Before Migration
- The application uses SQLAlchemy version 1.x.
- SQLAlchemy APIs are called in **imperative mode** (session management, query APIs, etc.).
- Implicit execution binding is common (e.g., `engine.execute()`).
- Synchronous ORM interfaces are predominantly used.
- Transactions and connections may be handled implicitly.

### After Migration
- The application uses SQLAlchemy version 2.x.
- APIs utilize the **2.0 style** (major breaking changes, including explicit connection/session management, changed query construction, and execution).
- No reliance on deprecated patterns (such as `engine.execute` or implicit database connections).
- Code is prepared for future async adoption but remains synchronous unless otherwise specified.
- Complete removal of patterns and symbols depreciated or removed in SQLAlchemy 2.x.

---

## Migration Strategy

**Chosen Approach:** Strangler Fig Pattern

- Incrementally update modules/components to the 2.x-style APIs.
- Maintain test coverage and deploy in phases to reduce risk.
- All code paths interacting with SQLAlchemy must be upgraded before full 2.x version switch.
- CI ensures no regressions or use of deprecated features at each migration step.

---

## Component Changes

| Component               | Change Description | Rationale |
|--------------------------|--------------------------|-----------|
| **Database Session Management** | Refactor all code to use explicit session objects, leveraging `Session()` context managers. Remove use of `session.begin(subtransactions=True)`, `session.autocommit` etc. | SQLAlchemy 2.x requires explicit session and transaction hierarchies. |
| **Query Construction** | Replace all usage of `Query` objects with direct use of `select`, `update`, `delete` constructs. Modify result handling: replace `query.first()`/`query.one()` with updated equivalents. | 2.x enforces Core style constructs and changes ORM query mechanisms. |
| **Session/Engine Execution** | Remove all `engine.execute()` and `connection.execute()` in favor of `Session.execute()` or explicit connections. | Deprecated in SQLAlchemy 2.x. |
| **Bindings & Reflection** | Remove or update `bind` parameters, move reflection to current idioms, e.g., `inspect(engine)`. | `bind` is removed; central connection patterns have changed. |
| **Row/Result Handling** | Change result handling to use `scalars()`, `mappings()`, or `all()` as required by the new Result API. | New result proxy object in 2.x differs from previous tuple behavior. |
| **Declarative Base** | Update `declarative_base()` import paths, prefer `from sqlalchemy.orm import declarative_base`. | Module locations moved in 2.x. |
| **Autocommit/Autoflush** | Remove usage of `autocommit` mode (no longer supported). Ensure transactions are explicit. | NO autocommit/implicit transactions in 2.x. |

---

## Dependency Upgrade Plan

| Dependency     | Current Version | Target Version | Migration Notes |
|----------------|----------------|---------------|----------------|
| SQLAlchemy     | 1.x            | 2.x           | Needs codebase refactor for incompatible API changes. |
| Alembic        | (If applicable) existing | Latest compatible | Update for compatibility with SQLAlchemy 2.x; may require migration script adjustments. |
| Any ORM Plugins| unknown        | Latest compatible | Audit for SQLAlchemy 2.x support and upgrade or replace as needed. |

---

## CI/CD Pipeline Changes

- **Static Checks:**  
  Add tools/scripts to scan for deprecated SQLAlchemy 1.x idioms (such as `engine.execute`).
- **Dependencies:**  
  Update dependency management (requirements.txt, requirements.in, setup.py, etc.) to require SQLAlchemy >=2.0,<3.0.
- **Tests:**  
  Run the full test suite against SQLAlchemy 2.x. Fail the build if deprecated or removed APIs are detected.
- **Optional:**  
  Add a job to run tests for both 1.x and 2.x during migration phase for increased safety.

---

## Infrastructure Changes

N/A — not applicable to this task

---

## Rollback Plan

- Ensure all migration code is committed in feature branches and releases are tracked/tagged.
- If errors or regressions are found after SQLAlchemy 2.x deployment:
    - Roll back application code to pre-migration tag.
    - Revert SQLAlchemy version pin to 1.x in dependency management files.
    - Redeploy using approved CI/CD pipeline with the known-good (1.x-compatible) artifact.
- Maintain a parallel requirements file for SQLAlchemy 1.x for immediate rollback if necessary.

---

## Testing Strategy

- **Unit Tests:**  
  Ensure all data access and ORM logic are adequately covered. Update or replace tests failing due to API changes.
- **Integration Tests:**  
  Test all data flows end-to-end with an actual or in-memory database using SQLAlchemy 2.x to ensure functional correctness.
- **Regression Tests:**  
  Compare behavior/outputs between SQLAlchemy 1.x and 2.x code paths to confirm compatibility.
- **Performance Tests:**  
  Benchmark database-heavy endpoints to detect regressions due to ORM-level changes.
- **Code Review:**  
  Enforce peer review for all SQLAlchemy-related code changes to verify no deprecated patterns remain.

---