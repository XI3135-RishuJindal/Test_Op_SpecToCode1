# SQLAlchemy 2.x Modernization Design Document

## Architecture Overview

**Before:**  
- Application uses SQLAlchemy 1.x (exact minor version unknown).
- Mix of ORM and Core usage patterns.
- Reliance on implicit transaction handling and legacy session usage.
- Codebase assumes 1.x-style APIs (e.g., `session.query()` patterns, implicit engine bindings).

**After:**  
- Application uses SQLAlchemy 2.x (latest stable release targeted).
- All code follows 2.x APIs, including:
    - Use of `select()`, `update()`, `delete()` constructs instead of the legacy Query API.
    - Explicit use of engine/session in all database interactions.
    - Transaction handling refactored for 2.x best practices.
- Deprecated/removed patterns (e.g., `session.execute()` with legacy signature, implicit `autocommit`) eliminated.

## Migration Strategy

- **Approach:** Strangler Fig Pattern
    - Incrementally refactor components to the 2.x API while maintaining backwards compatibility as much as feasible.
    - Adopt hybrid mode/compatibility shims (as guided by SQLAlchemy docs) to facilitate gradual migration.
    - Migrate and test individual modules/subsystems before full switchover.
- Allow for parallel installs and testing (where feasible).
- Leverage feature flags to enable/disable new code paths if possible.

## Component Changes

| Component              | Changes                                                                           | Reason                     |
|------------------------|-----------------------------------------------------------------------------------|----------------------------|
| Database Models        | Update declarative base definitions as needed; ensure imports use 2.x APIs.       | Align with 2.x structure   |
| ORM Query Logic        | Replace `session.query()` with `select()` constructs and `scalars()`, `all()`.    | 2.x removal of `query()`   |
| Session Management     | Make session usage explicit; use context managers (e.g., `with Session()`).       | Required in 2.x            |
| Transactions           | Explicit transaction boundaries via `begin()` or `commit()` context managers.     | Implicit transactions gone |
| Core SQL Usage         | Replace use of legacy connection execution with explicitly bound statements.       | API signature changes      |
| Third-party Integrations| Audit and refactor for deprecated APIs (esp. Flask-SQLAlchemy, Alembic, etc.).   | Compatibility with 2.x     |

## Dependency Upgrade Plan

| Dependency         | Current Version | Target Version | Migration Notes                                               |
|--------------------|----------------|---------------|--------------------------------------------------------------|
| SQLAlchemy         | 1.x            | 2.x           | Major API changes; see above for required code changes.       |
| Alembic            | unknown        | Latest        | Must be at version compatible with SQLAlchemy 2.x.            |
| Flask-SQLAlchemy   | unknown        | Latest        | Confirm compatibility with SQLAlchemy 2.x; update if needed.  |
| Others (custom/DB) | N/A            | N/A           | Review/test for indirect SQLAlchemy usage.                   |

## CI/CD Pipeline Changes

- Update dependency installation steps (e.g., `requirements.txt`/`pyproject.toml`) to reference `SQLAlchemy>=2.0`.
- Extend test steps to include suite runs against both SQLAlchemy 1.x and 2.x (if parallel support is required during migration).
- Enforce lint/type-checking tools for deprecated API usage.
- Add migration-focused jobs to flag new SQLAlchemy warnings and errors.

## Infrastructure Changes

N/A — not applicable to this task.

## Rollback Plan

- Pin SQLAlchemy version back to previous (1.x) in dependency manifest (e.g., `requirements.txt`/`pyproject.toml`).
- Revert codebase to state prior to 2.x-specific changes (maintain a dedicated upgrade branch).
- If migration causes production issues, deploy the pre-migration artifact using the locked dependency set.
- Document breaking issues for post-mortem review.

## Testing Strategy

- **Unit Tests:** Update/migrate existing database-related tests to new API. Add coverage for refactored query/session patterns.
- **Integration Tests:** Exercise all DB migration, ORM, and raw SQL code through full application flows.
- **Regression Tests:** Validate data consistency and query correctness pre- and post-migration.
- **Performance Tests:** Benchmark ORM and Core patterns to ensure query performance is not degraded.
- **Compatibility Tests:** If parallel support is needed during migration, run key tests on both old and new code paths.

---

**Note:** Strict adherence to SQLAlchemy 2.x migration guides is required for detail work. See [SQLAlchemy 2.0 Migration Notes](https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#change-5289) for specifics.