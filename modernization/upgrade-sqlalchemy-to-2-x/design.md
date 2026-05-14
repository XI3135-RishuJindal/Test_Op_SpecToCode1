# SQLAlchemy 2.x Upgrade Design Document

## Architecture Overview

_Previous State:_
- Application uses SQLAlchemy 1.x as its ORM/database toolkit.
- Codebase relies on 1.x APIs, including implicit execution, legacy session usage, and possibly deprecated query patterns.

_Target State (Post-Upgrade):_
- Application uses SQLAlchemy 2.x, taking advantage of the latest APIs and recommended idioms.
- Code updated to remove usage of deprecated or removed APIs, and to ensure compatibility with new transaction and session patterns.
- Codebase prepared for ongoing support and easier upgrades.

## Migration Strategy

- **Approach:** Strangler Fig Pattern
  - Incremental upgrade of components and code paths to SQLAlchemy 2.x compatibility, instead of a disruptive big-bang migration.
  - Update critical or simpler modules first, gradually expanding to whole codebase.
- Dual-support (compatibility code) if necessary, to allow fallback if critical issues are encountered before fully switching.
- Maintain extensive regression and integration testing throughout the migration.

## Component Changes

### ORM Models
- Update all Declarative base classes to use the new 2.x declarative base style where required.
- Update legacy mapper syntax to use modern style.

### Session and Transaction Management
- Refactor code to use 2.x "future" style session and `Session.begin` context managers.
- Migrate from autocommit/autoflush patterns to explicit transaction control.

### Query Patterns
- Rewrite queries using 2.x Core and ORM patterns, e.g. explicit statements, removal of implicit execution.
- Replace use of `session.query(Model)` with new-style `session.scalars(select(Model))` or `session.execute(select(...))`.

### Removed/Deprecated Features
- Replace all usages of previously available APIs now removed or deprecated in 2.x, such as:
   - `session.execute('raw SQL')` → use `text()` constructs.
   - Deprecated relationship patterns (e.g., `backref` without `back_populates`).
   - Deprecated query chaining (e.g., `.from_self()`).

## Dependency Upgrade Plan

| dependency   | current version | target version | migration notes                                                    |
|--------------|----------------|---------------|--------------------------------------------------------------------|
| SQLAlchemy   |   1.x          |    2.x        | Major API changes; see [2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html). Legacy APIs removed. |
| Alembic*     |   unknown      |   latest      | Ensure Alembic version is compatible with SQLAlchemy 2.x.           |

\* Only if Alembic is in use.

## CI/CD Pipeline Changes

- **Test Suites:** Ensure CI runs all test suites against SQLAlchemy 2.x.
- **Build Requirements:** Update build configuration files (e.g., `requirements.txt`, `pyproject.toml`) to require SQLAlchemy 2.x.
- **Static Analysis:** Enable SQLAlchemy 2.0 mode warnings if available.
- **Deployment Checks:** Add migration validation jobs to flag remaining legacy patterns.

## Infrastructure Changes

N/A — not applicable to this task

## Rollback Plan

- Retain branch/tag for pre-upgrade code and requirements.
- If post-upgrade deployment fails, revert:
  - Code to pre-upgrade commit.
  - Dependency locks (e.g., pin SQLAlchemy 1.x in requirements).
- Database schema remains unchanged; no destructive migrations associated.

## Testing Strategy

- **Unit Tests:** Run all existing unit tests to detect API breakages.
- **Integration Tests:** End-to-end tests covering all major database flows.
- **Regression Tests:** Ensure business logic/results identical to pre-upgrade.
- **Performance Tests:** Benchmark critical queries to detect regressions from 2.x migration.
- **Manual QA:** As a backup for automated coverage gaps, especially for forms or views using complex queries.

---

**Notes:**  
All direct and transitive dependencies relying on SQLAlchemy APIs (including plugins or extensions) must be checked for 2.x compatibility.  
All developers involved should read [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html) before starting.