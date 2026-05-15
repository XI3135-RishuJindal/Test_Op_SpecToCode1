# PLAN: SQLAlchemy 1.3→2.x Upgrade

## Overview

**Migration Strategy**: Feature-flag gated incremental migration with code compatibility shims.

**Justification**:  
Given the medium risk and moderate effort (as per the upgrade option), a feature-flag or incremental approach is best. SQLAlchemy 2.x introduces significant API changes, many of which are not backward-compatible. An all-at-once migration (big-bang) is riskier given potential runtime errors, while a strangler-fig or parallel-run is not feasible for library-level upgrades unless dual-stack shims are used. Feature-flags will allow us to enable/disable new codepaths and mitigate risk.

---

## Phases

| Phase                       | Description                                                                                     | Dependencies                  | Estimated Effort      |
|-----------------------------|------------------------------------------------------------------------------------------------|-------------------------------|-----------------------|
| 1. Compatibility Analysis   | Audit code for 1.3-specific usage. Identify breaking changes and migration points.             | None                          | 2 person-days         |
| 2. Shim Preparation         | Introduce backward-compatibility shims for imports and API changes.                            | Phase 1                       | 2 person-days         |
| 3. Code Migration           | Update code to new 2.x APIs, refactor deprecated calls, update session/engine use, etc.        | Phases 1,2                    | 5 person-days         |
| 4. Dependency Upgrade       | Bump SQLAlchemy to 2.x in dependency files (e.g., requirements.txt, setup.py, pyproject.toml). | Phase 3                       | 0.5 person-days       |
| 5. Integration/Regression   | Run tests, check integrations, resolve any issues.                                             | Phase 4                       | 2.5 person-days       |
| 6. Feature-flag Remove      | Remove feature-flags and shims, finalize the migration.                                        | Phase 5 successful            | 1 person-day          |

**Total Effort**: 13 person-days

---

## Component Changes

### ALL ORM/Database modules
- **Structural Changes**:  
  - Refactor all files that import or use SQLAlchemy ORM, Engine, Session.
  - Update deprecated APIs (e.g., `.execute()`, query conventions).
  - Replace direct engine-bound execution with connection-based patterns.
- **Affected Files (examples):**
  - `models.py`: Update declarative base and model definitions.
  - `database.py`: Refactor session and engine creation.
  - `repositories/*.py`: Refactor query patterns.
- **APIs Modified:**
  - `Session.query`, `engine.execute`, `Model.query`, etc., as per SQLAlchemy 2.x API changes.

---

## Dependency Upgrade Plan

| Dependency   | Current Version | Target Version | Breaking Changes                                   | Migration Notes                                                |
|--------------|----------------|---------------|----------------------------------------------------|---------------------------------------------------------------|
| SQLAlchemy   | 1.3            | 2.x           | Major API deprecations/changes, removed features   | Most ORM/core methods have new patterns for Session/Execution. |

---

## Infrastructure Changes

N/A — not applicable to this task

---

## Rollback Strategy

| Phase/Step             | Rollback Action                                                                              |
|------------------------|---------------------------------------------------------------------------------------------|
| After Code Migration   | Revert changed code to previous state using VCS.                                            |
| After Dependency Bump  | Roll back dependency version in requirements/setup/pyproject. Reinstall previous env.       |
| After Integration      | Revert feature flags to previous state, re-enable 1.3 compatibility shims.                  |
| After Shim Removal     | Restore shims/flags from VCS or abort removal.                                              |

All rollback actions are independently reversible through version control.

---

## Testing Strategy

**Test Pyramid**:
- **Unit Tests**: Refactor and run all tests involving database models, query logic, sessions.  
  - **Tooling**: pytest (assumed standard for Python/SQLAlchemy projects)
  - **Coverage Target**: 90% for DB interaction code (models, repositories, services)
  - **CI Gate**: All CI builds must pass with SQLAlchemy 2.x; feature-flag disables new code for fallback.
- **Integration Tests**: Verify ORM behavior, transactions, migrations, raw queries.
- **Regression Tests**: Validate critical flows, ensure parity with pre-upgrade behaviors.
- **Performance Tests**: N/A — not applicable to this task (unless regressions are observed).

---

## Timeline

| Milestone                  | Phase                   | Estimated Completion | Owner        |
|----------------------------|------------------------ |---------------------|--------------|
| Code Audit Complete        | Phase 1                 | +2 days             | TODO         |
| Shims Introduced           | Phase 2                 | +4 days             | TODO         |
| Code Refactored            | Phase 3                 | +9 days             | TODO         |
| Dependency Upgraded        | Phase 4                 | +9.5 days           | TODO         |
| Regression Tested          | Phase 5                 | +12 days            | TODO         |
| Flags/Shims Removed        | Phase 6                 | +13 days            | TODO         |

---

**End of PLAN**