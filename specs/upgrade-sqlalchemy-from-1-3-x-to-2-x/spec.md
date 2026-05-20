# SPEC: Upgrade SQLAlchemy from 1.3.x to 2.x

## Summary
This specification covers the upgrade of SQLAlchemy from version 1.3.x to 2.x across the codebase. The objective is to align with current supported versions, address future compatibility, and take advantage of improvements present in SQLAlchemy 2.x. The expected outcome is that all SQLAlchemy interfaces, ORM usages, and database integration points operate correctly under SQLAlchemy 2.x, with all deprecated and EOL (End-of-Life) features replaced or refactored as mandated by the new major version.

## Motivation
Upgrading to SQLAlchemy 2.x is required due to the following business and technical drivers:
- **End-of-life of 1.3.x**: SQLAlchemy 1.3.x is no longer maintained, leading to exposure to unpatched security vulnerabilities and lack of support.
- **New CVE coverage**: Running a supported version ensures ongoing CVE (Common Vulnerabilities and Exposures) coverage.
- **Compliance requirements**: Current compliance standards demand use of supported, non-EOL third-party dependencies.
- **Performance and feature improvements**: SQLAlchemy 2.x introduces both bug fixes and performance improvements potentially beneficial to our application.
- **Upgrade urgency**: Classified as "medium" per tech analysis; though not immediately blocking, proactive completion reduces compounding tech debt and compliance risk.

## Current State
- **SQLAlchemy Version**: All database access uses SQLAlchemy 1.3.x and its associated ORM patterns.
- **Interfaces/APIs Impacted**: 
    - Session management (use of `sessionmaker`, context patterns potentially using legacy approaches).
    - ORM query API and model definitions.
    - Engine/resource configuration via ORM and Core (e.g., `create_engine`).
    - Transactions, connection handling (may use legacy patterns deprecated/removed in 2.x).
    - Any custom type definitions or event handlers dependent on 1.3.x API signatures.
    - Code may utilize implicit execution patterns (removed in 2.x).
    - Data model classes may not use updated declarative base practices.
- **Config Keys or Schema Elements Involved**: N/A — No specific configs or schema elements are referenced in the provided context.
- **Known 1.3.x Only Usages**: Use of legacy `session.query`, lack of explicit execution context, and possible use of deprecated API points.
- **Language, Runtime, Build Tool**: Unknown (information not provided).
  
## Proposed Changes

| Component                        | Before (1.3.x)                  | After (2.x)                                            | Breaking? (Y/N) |
|-----------------------------------|----------------------------------|--------------------------------------------------------|-----------------|
| SQLAlchemy Core/ORM API           | 1.3.x API & patterns             | 2.x API using explicit execution & new query syntax    | Y               |
| Session usage                     | Implicit transaction mgmt, etc.  | Explicit context management required                   | Y               |
| Query construction                | `session.query()` pattern        | New select/ORM filter syntax required                  | Y               |
| Model base definition             | Classic Base maybe               | New declarative base import required                   | Y               |
| Type decorators/events            | 1.3.x signatures                 | Updated signatures as required by 2.x                  | Y               |
| Implicit execution                | May be present                   | Must switch to explicit execution                      | Y               |

## Compatibility & Breaking Changes

| Breaking Change                                                     | Migration Path                                                      |
|---------------------------------------------------------------------|---------------------------------------------------------------------|
| Removal of implicit execution (autocommit/execute in session/query) | Refactor to use explicit connections/transactions as per 2.x docs   |
| Deprecated query API (`session.query()`)                            | Rewrite queries using new 2.x ORM querying constructs               |
| ORM session/transaction context handling                            | Refactor to use `with Session.begin()` or equivalent 2.x pattern    |
| Declarative base changes                                            | Update model definitions to use the new declarative base API        |
| Custom event/type handler signature changes                         | Adjust custom code to match new signature requirements              |
| Other unknown upstream incompatibilities                            | TODO — Review and document as encountered during upgrade/testing    |

## Acceptance Criteria

1. **Given**: A clean environment with only SQLAlchemy 2.x installed,  
   **when**: the test suite is executed,  
   **then**: all tests that previously passed under 1.3.x pass without error.

2. **Given**: Application is run in a staging environment configured to use SQLAlchemy 2.x,  
   **when**: core user workflows involving database read/write operations are exercised,  
   **then**: no unexpected exceptions or regressions occur compared to the 1.3.x baseline.

3. **Given**: All direct imports and usage of 1.3.x legacy APIs are scanned and audited,  
   **when**: static/code quality checks are run,  
   **then**: no deprecated or removed SQLAlchemy 1.3.x API usage patterns are found.

4. **Given**: Any custom events, type decorators, or external plugin hooks in the codebase,  
   **when**: the relevant usage is tested,  
   **then**: signatures conform to 2.x requirements and behave as expected.

## Open Questions

| # | Question                                                                         | Owner (or TODO) | Due Date (or TODO) |
|---|----------------------------------------------------------------------------------|-----------------|-------------------|
| 1 | What language/runtime/build tool is used, and does it impact SQLAlchemy 2.x use? | TODO            | TODO              |
| 2 | Are there external integrations or plugins that are not compatible with 2.x?      | TODO            | TODO              |
| 3 | Are there patterns or legacy features unique to our codebase requiring discovery? | TODO            | TODO              |

