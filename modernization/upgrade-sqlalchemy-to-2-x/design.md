# Design Document: SQLAlchemy Upgrade to 2.x

## Architecture Overview

### Before
- The application uses SQLAlchemy version 1.x for its ORM and database tooling.
- Codebase relies on SQLAlchemy's 1.x query/api style (e.g., classic `session.query()`, implicit execution, legacy connection use).
- Some features may use deprecated legacy patterns.

### After
- The application will use SQLAlchemy 2.x as its ORM and database toolkit.
- Code is updated to use the 2.x API:
  - Prefer explicit `select()` constructs.
  - Prefer `Session.execute()` over legacy `.query()`.
  - Avoid implicit engine/disconnect patterns.
  - Removed/updated features that have been removed or changed in 2.x.

## Migration Strategy

- **Strangler Fig Pattern:**
  - Individual modules/components refactored incrementally to use 2.x idioms.
  - Codebase runs with SQLAlchemy 2.x once module changes validated and merged, but tests and staging validate correctness at every phase.
  - Brief parallel run where possible using test environments with both 1.x and 2.x for verification prior to production switchover.

## Component Changes

| Component                  | Change Description                                                      |
|----------------------------|------------------------------------------------------------------------|
| Data Access Layer          | Refactor all ORM queries to use new 2.x style (core select, execute).  |
| Session Management         | Explicit use of `Session`, avoid deprecated/bare engine connections.    |
| Raw SQL Usage & Migrations | Update any raw connection APIs or migration scripts incompatible with 2.x.|
| Transaction Handling       | Adopt context-managed session/engine patterns as per 2.x guidance.      |
| Configuration              | Update settings if any changed between 1.x and 2.x (e.g., echo).        |
| 3rd-party integrations     | Check and update (or pin) integrations for tools using SQLAlchemy APIs. |

## Dependency Upgrade Plan

| dependency     | current version | target version | migration notes                                                    |
|----------------|----------------|---------------|-------------------------------------------------------------------|
| SQLAlchemy     | 1.x            | 2.x           | Major API and behavior changes; see release notes/migration guide.|
| alembic        | N/A or old     | latest        | Update only if dependency on SQLAlchemy API changes.              |
| any SA plugins | unknown        | N/A or latest | Evaluate compatibility with 2.x, update/pin or remove as needed.  |

## CI/CD Pipeline Changes

- Update requirements.txt/pyproject.toml to specify SQLAlchemy >=2.0.
- Add/expand tests to check for ORM errors related to breaking changes in 2.x.
- Enable stricter linting/static analysis to catch deprecated/legacy usage.
- Monitor CI on new SQLAlchemy 2.x for failures; address test breakage promptly.

## Infrastructure Changes

N/A — not applicable to this task

## Rollback Plan

- Pin requirements.txt/pyproject.toml back to SQLAlchemy 1.x version.
- Revert code changes to former 1.x patterns using version control (git).
- Rollback can be performed via standard deployment rollback mechanisms.

## Testing Strategy

- **Unit Tests:** All existing and new data-access unit tests must pass under 2.x.
- **Integration Tests:** Full end-to-end tests covering actual database operations with new SQLAlchemy.
- **Regression Tests:** Compare behavior and outputs with the 1.x version to detect any changes.
- **Performance Tests:** (Optional but recommended) Run DB-intensive benchmarks to identify regressions, as query compilation/execution code has changed.
- **Manual Verification:** Key workflows exercised in staging prior to production deployment.

---

_Note: See official [SQLAlchemy 1.x-to-2.x Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) and [2.x Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html) as primary resources._