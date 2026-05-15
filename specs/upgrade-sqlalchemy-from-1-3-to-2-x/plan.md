# PLAN: Upgrade SQLAlchemy from 1.3 to 2.x

## Overview

**Strategy:** Big-bang migration

**Justification:**  
Given that this upgrade is limited to a single library (SQLAlchemy) and that significant breaking changes are introduced moving from the 1.3 to 2.x release lines, applying a big-bang approach is appropriate to manage migration risk and avoid hybrid incompatibilities. The risk score is moderate, per the upgrade option, and the scope is isolated to SQLAlchemy ORM and SQL API usage. A big-bang migration, executed in a dedicated upgrade branch, minimizes interim maintenance overhead and testing complexity.  

## Phases

| Phase         | Description                                           | Dependencies    | Estimated Effort |
|---------------|------------------------------------------------------|-----------------|------------------|
| Assessment    | Audit codebase for SQLAlchemy 1.3 usage, inventory incompatible patterns | None            | 10 person-days   |
| Refactoring   | Update code patterns for SQLAlchemy 2.x compliance (ORM, session, query, API) | Assessment      | 15 person-days   |
| Dependency Upgrade | Bump SQLAlchemy from 1.3 to 2.x and address breaking changes            | Refactoring     | 5 person-days    |
| Regression Testing | Full regression suite, verification of functionality post-upgrade      | Dependency Upgrade | 5 person-days  |

**Total estimated effort:** 35 person-days (as moderate per upgrade option).

## Component Changes

**Note:** File/class/method names cannot be listed due to lack of provided code context. The following applies to any files in the codebase that import and use SQLAlchemy.

- Update all import statements from SQLAlchemy to ensure compatibility with 2.x, especially those using old APIs (`from sqlalchemy.ext.declarative import declarative_base`, etc.).
- Replace `session.query(Model)` with the 2.x-style ORM usage (`Session.execute(select(Model))`).
- Update connection and engine creation patterns as per the 2.x API.
- Update ORM configuration and mapping declarations as required by new declarative mapping styles.
- Identify and refactor uses of `Query`, `.get()`, `session.connection()`, legacy transaction patterns, and direct SQL execution for 2.x compatibility.
- Modify all usage of removed/changed features (e.g., from `session.execute()` to 2.x-compliant method signatures and results handling).
- Update configuration files or code locations where SQLAlchemy version is referenced, if any.

**Affected Files:**  
- All files importing `sqlalchemy`, using ORM base, sessions, transactions, or executing SQL commands.
- All test files referencing SQLAlchemy ORM constructs.

**APIs Modified:**  
- All direct and indirect usages of SQLAlchemy ORM, session, and database APIs.

## Dependency Upgrade Plan

| Dependency   | Current Version | Target Version | Breaking Changes                                    | Migration Notes                   |
|--------------|----------------|---------------|-----------------------------------------------------|-----------------------------------|
| SQLAlchemy   | 1.3            | 2.x           | Extensive: import paths, ORM method signatures, session/query API overhaul, result objects | Audit and rewrite all usages. See [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#migration-guide) for reference. |

## Infrastructure Changes

- **Docker base image changes:**  
  N/A — not applicable to this task

- **Kubernetes manifest changes:**  
  N/A — not applicable to this task

- **CI/CD pipeline changes:**  
  N/A — not applicable to this task

- **IaC updates:**  
  N/A — not applicable to this task

- **Other:**  
  TODO: If build/install pinning exists, update from `sqlalchemy==1.3.*` to `sqlalchemy==2.*` in `requirements.txt` or equivalent locations.

## Rollback Strategy

**Phase 1 (Assessment):**  
- No rollback required (read-only activity).

**Phase 2 (Refactoring):**  
- Use version control branches. All changes must be committed on a feature branch. Rollback is possible via branch deletion or revert.

**Phase 3 (Dependency Upgrade):**  
- Revert requirements/dependency pin to `sqlalchemy==1.3.*` and reverse any 2.x-specific code changes via git revert, if issues are encountered.

**Phase 4 (Regression Testing):**  
- If new regressions are encountered, revert code and dependency to 1.3 baseline.

Rollback is independently reversible at every phase by reverting to the previous commit, branch, or dependency version.

## Testing Strategy

**Test Pyramid:**

- **Unit:**  
  - Ensure all ORM models, custom queries, and session/scoped session logic have direct unit test coverage.
  - Target: >85% coverage on domain modules using SQLAlchemy.
  - Tools: pytest + coverage.py or equivalent.

- **Integration:**  
  - Execute integration tests validating database CRUD, transactionality, and isolation under SQLAlchemy 2.x.
  - CI gate: All integration tests must pass with SQLAlchemy 2.x.

- **Regression:**  
  - Run complete regression suite across all business flows involving database persistence and queries.
  - CI gate: No regressions permitted.

- **Performance:**  
  - Compare before/after performance metrics for major ORM queries.
  - Tooling: pytest-benchmark or equivalent.

- **Continuous Integration:**  
  - PRs must trigger unit, integration, and regression tests for all supported Python versions.
  - Upgrade branch cannot be merged until all CI checks pass.

## Timeline

| Milestone            | Phase              | Estimated Completion | Owner           |
|----------------------|--------------------|---------------------|-----------------|
| Complete Audit       | Assessment         | Day 10              | TODO            |
| Core Refactor Done   | Refactoring        | Day 25              | TODO            |
| Dependency Upgraded  | Dependency Upgrade | Day 30              | TODO            |
| All Tests Passed     | Regression Testing | Day 35              | TODO            |

---

**Note:**  
All estimates and steps strictly map to the upgrade of SQLAlchemy from 1.3 to 2.x as per context. No additional features or infrastructural changes are included. Any missing file, class, or config names are due to lack of context and must be filled during phase execution.