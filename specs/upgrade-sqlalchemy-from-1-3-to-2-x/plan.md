# PLAN: SQLAlchemy 1.3 to 2.x Upgrade

## Overview

**Migration Strategy: Strangler-Fig**

Given the medium risk and moderate effort noted in the upgrade option, a strangler-fig approach is most appropriate. SQLAlchemy 2.x introduces significant breaking changes, especially in the ORM and Query APIs, meaning portions of the codebase may need progressive adaptation and careful validation. This strategy allows us to incrementally refactor query and ORM usage, minimizing risk, and simplifying rollback compared to a big-bang upgrade.

## Phases

| Phase | Description                                                | Dependencies                 | Estimated Effort      |
|-------|------------------------------------------------------------|------------------------------|-----------------------|
| 1     | Audit and catalog SQLAlchemy usage across codebase         | None                         | 5 person-days         |
| 2     | Update core dependencies and lock to SQLAlchemy 2.x        | Phase 1                      | 2 person-days         |
| 3     | Refactor deprecated APIs, migrate connection/transaction usage, update queries | Phase 2            | 13 person-days        |
| 4     | Regression and performance testing, CI pipeline verification| Phase 3                      | 5 person-days         |

*Total effort: 25 person-days (as implied by moderate option).*

## Component Changes

**Component: Data Access Layer (DAL) / Models**
- **Structural Changes:** 
  - Replace `session.query()` patterns with 2.x-compatible syntax.
  - Refactor explicit use of `session.execute()` and Core APIs where required.
  - Address all deprecated constructs (e.g., implicit transactional state, legacy ORM query patterns).
- **Affected Files:** 
  - All files where `sqlalchemy` is imported or where ORM models are declared.
  - Files that invoke Session, Engine, or direct query construction.
  - *e.g.,* `models.py`, `database.py`, `repository.py` (actual file names per context).
- **Modified APIs:**
  - `Session.query()` calls → 2.x idioms.
  - Raw SQL text execution/signatures.
  - Transaction/context manager usage, e.g., `session.begin()`, `session.commit()`.
  - Type checking and engine creation (`create_engine()`).

**Component: Tests**
- Update fixtures and mocks for any changes to session/transaction handling.
- Ensure all DAL/ORM tests reflect new error handling and SQLAlchemy 2.x API signatures.

## Dependency Upgrade Plan

| Dependency   | Current Version | Target Version | Breaking Changes                                                        | Migration Notes                  |
|--------------|----------------|---------------|-------------------------------------------------------------------------|----------------------------------|
| SQLAlchemy   | 1.3            | 2.x           | Major ORM and query syntax changes; session/query APIs deprecated/changed| Refactor all affected usages     |

*No other dependencies mentioned in context.*

## Infrastructure Changes

N/A — not applicable to this task

## Rollback Strategy

**Phase 2 and 3 are reversible independently.**

- **After Phase 2:**  
  - Rollback updated dependency in requirements file (e.g., revert `requirements.txt` or lockfile changes from SQLAlchemy 2.x to 1.3).
  - Re-install dependencies to re-pin SQLAlchemy to 1.3.

- **After Phase 3:**  
  - Revert code changes in repository affecting model, query, and session handling.
  - Rollback any test changes related to updated API usage.
  - Revert requirements to SQLAlchemy 1.3 if any regressions observed.

- **Always:**  
  - Maintain branch isolation until all phases and integration tests pass.
  - Document all code and dependency changes for clear reversible commits.

## Testing Strategy

**Test Pyramid:**

- **Unit Tests:**  
  - Tool: pytest (if contextually used; update as per stack)  
  - Target: ≥90% coverage on models, query helpers, and migration-affected code  
  - CI Gate: Fail build if coverage drops below threshold.

- **Integration Tests:**  
  - Tool: pytest or relevant framework  
  - Target: All database interaction flows, CRUD operations, transaction/rollback scenarios.

- **Regression Tests:**  
  - Run full suite before and after migration; compare outputs/side effects for anomalies.

- **Performance Tests:**  
  - Tool: pytest-benchmark or similar (if in use)  
  - Target: Ensure no performance regressions >10% in critical query paths.

**CI Gates:**  
- All tests pass against SQLAlchemy 2.x before merging.
- No unhandled deprecation warnings related to SQLAlchemy.

## Timeline

| Milestone                            | Phase   | Estimated Completion | Owner      |
|--------------------------------------|---------|---------------------|------------|
| Complete usage audit                 | 1       | +5 days             | TODO       |
| Dependency and lock upgrade applied  | 2       | +7 days             | TODO       |
| All code and tests refactored        | 3       | +20 days            | TODO       |
| All testing, stabilization complete  | 4       | +25 days            | TODO       |

---

*Only the SQLAlchemy upgrade is covered; all other aspects are marked N/A per requirements.*