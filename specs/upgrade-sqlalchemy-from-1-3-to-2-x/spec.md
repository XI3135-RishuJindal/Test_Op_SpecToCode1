## Summary

This spec covers the upgrade of SQLAlchemy from version 1.3 to the latest 2.x release. The expected outcome is to bring all usages of SQLAlchemy within the project up to date with 2.x compatibility, addressing breaking changes and deprecations. This upgrade is intended to ensure long-term maintainability, improve compliance with CVE mitigation, and prepare the codebase for ongoing support and new features in the SQLAlchemy ecosystem.

## Motivation

- **End of Life (EOL)**: SQLAlchemy 1.3 is no longer maintained, with security and bug fixes only available in later 1.4 and 2.x branches.
- **Security (CVE) Coverage**: Only SQLAlchemy 1.4+ receives security patches. Upgrading mitigates risk from unpatched vulnerabilities.
- **Modern API Adoption**: SQLAlchemy 2.x introduces a fully "2.0" style API, deprecates legacy behaviors, and mandates clearer separation between core and ORM features.
- **Compliance Requirements**: Staying current with dependencies is often a requirement for regulated environments and audit readiness.
- **Upgrade Urgency**: Medium, per tech analysis—should be prioritized within the next cycle.

## Current State

- **SQLAlchemy Version**: 1.3.x in current use across the codebase.
- **Interface Usage**:
  - Use of `session.query()`, legacy-style querying and execution.
  - Possible reliance on `engine.execute()` for direct SQL execution.
  - Configuration using SQLAlchemy 1.3 patterns.
  - Data models and ORM mappings defined for 1.3 API.
- **Config Keys**: N/A — not applicable to this task.
- **Schema Elements**: Usage of SQLAlchemy ORM models compatible with 1.3.
- **APIs/Classes**: 
  - `Session`, `sessionmaker`, `engine`, `MetaData`, declarative base models.
- **Key Behaviors**:
  - Implicit connection closure, implicit transaction handling, and 1.3-specific transaction API patterns.
  - Potential implicit commit/rollback semantics.

## Proposed Changes

| Component           | Before (1.3.x)                                                                 | After (2.x)                                                                  | Breaking? |
|---------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------------------|-----------|
| ORM Querying        | `session.query()`, possibly auto-executing, 1.x-style queries                  | 2.x-style querying, explicit execution, use of `select()` and `Session.execute()` | Y         |
| Engine Execution    | `engine.execute()` across the codebase                                         | `engine.execute()` removed; must use connections and explicit execution APIs      | Y         |
| Transaction API     | Implicit and legacy transaction patterns allowed                                | Transaction patterns strictly enforced—must use commit/rollback context, scopes  | Y         |
| Model Declarative   | 1.3-style declarative base, possibly using `Base = declarative_base()`          | 2.0-style declarative base and possible use of new field typing requirements     | Y         |
| Session Management  | `sessionmaker` invocations with legacy/implicit patterns                       | Revised session management patterns and explicit configuration                   | Y         |
| Deprecated Imports  | May use imports or call patterns removed in 2.x                                | Only supported 2.x API; all deprecated features removed                         | Y         |

## Compatibility & Breaking Changes

| Breaking Change                                              | Migration Path / Notes          |
|-------------------------------------------------------------|---------------------------------|
| Removal of `engine.execute()`                               | Use Connection object and explicit execution; update all usages accordingly. |
| ORM Query interface changed: `session.query()` patterns      | Use `select()` constructs and `Session.execute()`.                           |
| Transaction demarcation is stricter, requires explicitness   | Refactor to explicit commit/rollback/context managers as per 2.x guidance.   |
| Legacy declarative and config APIs removed/changed           | Update all declarative class definitions and usage to 2.x idioms.            |
| Possible removal of mutable column defaults, operators, etc. | TODO — Identify and enumerate any 1.3 features in use that are removed in 2.x |

## Acceptance Criteria

1. Given the codebase using SQLAlchemy 1.3, when all direct and transitive dependencies are upgraded to SQLAlchemy 2.x, then all automated tests must pass on a clean CI run.
2. Given an attempt to use `engine.execute()` or other removed APIs, when running the application, then a migration must exist updating code to supported 2.x patterns with no runtime errors.
3. Given all ORM queries, when run in local or CI environment, then they must use 2.x-compatible patterns (`select()`, `Session.execute()`) and yield correct results.
4. Given the database session and transaction boundaries, when application transactions are started and completed, then they must exhibit the correct ACID behavior with explicit commit/rollback, verified by automated tests.
5. Given usage of declarative base classes and ORM models, when declared, then no 1.3-deprecated or removed features are present and model mapping functions as expected under 2.x, confirmed by tests.
6. Given compliance scans or dependency audit tools are run after the upgrade, then they must report SQLAlchemy at 2.x with no flagged EOL CVEs or maintenance blockers.

## Open Questions

| #  | Question                                                                 | Owner (or TODO) | Due Date (or TODO) |
|----|--------------------------------------------------------------------------|-----------------|-------------------|
| 1  | What language/runtime is the project implemented in?                     | TODO            | TODO              |
| 2  | Which files/modules rely on removed APIs (e.g., `engine.execute()`)?     | TODO            | TODO              |
| 3  | Are there 1.3-specific ORM configuration or feature usages unaccounted for? | TODO            | TODO              |
| 4  | Are there environment-specific constraints (build tools, CI) that restrict SQLAlchemy 2.x? | TODO            | TODO              |