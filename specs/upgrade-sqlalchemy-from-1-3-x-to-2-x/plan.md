# PLAN: SQLAlchemy 1.3.x → 2.x Upgrade

## Overview

**Migration Strategy:** Feature-flag gated deployment

**Justification:**  
Based on the medium upgrade urgency and absence of explicit runtime/build tool context, a feature-flag approach balances risk and developer effort for this moderate upgrade. SQLAlchemy 2.x introduces significant API and behavioral changes, and a feature flag allows toggling between "1.3 compatibility mode" and "2.x native mode" for safer rollout and smoother rollback if regressions surface. This aligns with moderate effort and mitigates risk without requiring a full parallel or big-bang migration.

---

## Phases

| Phase   | Description                                                       | Dependencies               | Estimated Effort        |
|---------|-------------------------------------------------------------------|----------------------------|-------------------------|
| 1       | Static analysis & compatibility audit                             | None                       | 15% of total person-days |
| 2       | Update code for SQLAlchemy 2.x API changes (guarded by flag)      | Phase 1                    | 50% of total person-days |
| 3       | Integrate and test under feature flag                             | Phase 2                    | 25% of total person-days |
| 4       | Remove flag & deprecated patterns; full 2.x enablement            | Phase 3                    | 10% of total person-days |

> *Total effort must match "moderate" upgrade option person-days. Please specify or adjust as needed based on provided input in downstream planning.*

---

## Component Changes

| Component / File                  | Changes Required                                            |
|-----------------------------------|------------------------------------------------------------|
| Database model and DAL modules    | Refactor for 2.x API: eliminate deprecated patterns, migrate session and engine usage, update connection and transaction management. |
| Query code (e.g., repository.py)  | Replace legacy query methods, update result proxy usage, adjust for new Core/ORM division if present. |
| Migration scripts (if any)        | Update Alembic or direct migration code for new engine/bind patterns, update use of `MetaData`. |
| Configuration files (e.g., config.py) | Any SQLAlchemy config keys (pooling, isolation, etc.) may require changes for new settings or defaults. |
| All tests using SQLAlchemy mocks  | Update to new mock/fixture patterns if test harness interacts with SQLAlchemy internals. |

*Note: Actual class, function, and file names depend on codebase — review all code initializing SQLAlchemy engines, sessions, connections, or emitting raw SQL.*

---

## Dependency Upgrade Plan

| Dependency     | Current Version | Target Version | Breaking Changes                  | Migration Notes               |
|----------------|----------------|---------------|-----------------------------------|-------------------------------|
| SQLAlchemy     | 1.3.x          | 2.x           | Major API overhaul; dropped 1.x compatibility defaults | Remove usage of `session.query(Model).filter_by()`, refactor to 2.x style, revisit connection/string pattern, resolve all deprecated/removed API usage. |
| Alembic (if any) | unknown         | N/A           | N/A                              | N/A                          |

---

## Infrastructure Changes

N/A — not applicable to this task

---

## Rollback Strategy

- **Phase 1-2:**  
  - Revert feature flag to enforce legacy 1.3.x code path.
  - Rollback local changes to code interacting with SQLAlchemy if feature-flag rollback is insufficient.
  - Reinstall SQLAlchemy 1.3.x in the environment.

- **Phase 3:**  
  - If regressions appear with the flag enabled, revert to previous stable tag and re-enable legacy mode.
  - Restore config files and any scripts to pre-upgrade state.

- **Phase 4:**  
  - To undo full enablement, reintroduce the feature flag, revert breaking code, and downgrade dependency to 1.3.x.

---

## Testing Strategy

- **Unit Testing:**  
  - Update all unit tests for SQLAlchemy-using modules to hit at least 90% line and branch coverage.
  - Mock/stub DB sessions using the new SQLAlchemy 2.x patterns.

- **Integration Testing:**  
  - Run tests against ephemeral/test databases with 2.x enabled and with fallback to 1.3 compatibility.
  - Validate schema management, transactionality, and migration scripts.

- **Regression Testing:**  
  - Backwards-compatibility test runs with feature flag off to ensure no regressions in legacy mode.
  - End-to-end tests for all critical DB workflows.

- **Performance Testing:**  
  - Compare query performance and transaction times between 1.3.x and 2.x modes.

- **CI Gates:**  
  - Require all builds to pass with the feature flag in both states before merging.
  - Use code coverage tools compatible with Python (if Python is the language), e.g., pytest-cov.

---

## Timeline

| Milestone                   | Phase    | Estimated Completion | Owner          |
|-----------------------------|----------|---------------------|----------------|
| Compatibility Audit         | 1        | TODO                | TODO           |
| Code Updated Under Flag     | 2        | TODO                | TODO           |
| Integrated & Tests Passing  | 3        | TODO                | TODO           |
| Full 2.x Enabled, Cleanup   | 4        | TODO                | TODO           |

---

**End of PLAN**