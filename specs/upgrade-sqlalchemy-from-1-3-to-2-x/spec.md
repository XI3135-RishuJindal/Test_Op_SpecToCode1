## Summary

This spec covers the upgrade of SQLAlchemy from version 1.3 to the 2.x series. The goal is to ensure the codebase is compatible with SQLAlchemy 2.x, removing all deprecated interfaces and usages that were allowed in 1.3. The expected outcome is a system free from SQLAlchemy 1.3-specific constructs, leveraging the modern APIs and patterns required in SQLAlchemy 2.x.

## Motivation

The primary drivers for this upgrade are medium urgency technical debt reduction and long-term support. SQLAlchemy 1.3 is considered legacy, and missing continued maintenance increases the risk of unpatched security vulnerabilities (CVE exposure), compatibility issues with database backends, and inability to leverage recent performance and stability improvements. Ensuring forward compatibility and compliance with newer ecosystem libraries is only possible on SQLAlchemy 2.x. 

## Current State

- SQLAlchemy version: 1.3
- Existing interfaces: N/A — not enough context provided
- APIs used: N/A — not enough context provided
- Data models: N/A — not enough context provided
- Key behaviours: Application uses SQLAlchemy 1.3-style ORM and/or Core API constructs; may rely on legacy engine patterns and session management behaviors.

## Proposed Changes

| Component      | Before (SQLAlchemy 1.3)                        | After (SQLAlchemy 2.x)                      | Breaking? |
|----------------|------------------------------------------------|---------------------------------------------|-----------|
| ORM API usage  | 1.3 syntax, deprecated constructs may exist    | 2.x syntax, all legacy API usages removed   | Y         |
| Core engine    | 1.3 engine and connection API                  | 2.x engine and connection API               | Y         |
| Session usage  | 1.3 session and transaction patterns           | 2.x session and transaction patterns        | Y         |
| Import paths   | Compatible with 1.3-only module paths          | Compatible with 2.x-imports                 | Y         |

## Compatibility & Breaking Changes

| Breaking Change                   | Migration Path             |
|-----------------------------------|----------------------------|
| Deprecated APIs removed in 2.x    | TODO (requires code audit) |
| Legacy engine/session patterns    | TODO (requires code audit) |
| Import path differences           | TODO (requires code audit) |

## Acceptance Criteria

1. Given the codebase with SQLAlchemy 2.x installed, when the application is started, then no ImportError or AttributeError due to missing/removed SQLAlchemy 1.3 APIs occurs.
2. Given automated test suite execution under SQLAlchemy 2.x, when tests are run, then all tests pass with no SQLAlchemy deprecation or warning messages.
3. Given invocation of main application workflows (CRUD, batch processing, queries), when operating under SQLAlchemy 2.x, then all workflows complete successfully and produce the same externally observable results as with SQLAlchemy 1.3.
4. Given any use of import paths referencing removed modules or names in SQLAlchemy 2.x, when these are exercised, then the application does not raise an ImportError.

## Open Questions

| # | Question                                                                                | Owner (or TODO) | Due Date (or TODO) |
|---|-----------------------------------------------------------------------------------------|-----------------|--------------------|
| 1 | Which specific API usages in the codebase are incompatible with SQLAlchemy 2.x?         | TODO            | TODO               |
| 2 | What integration points exist with other libraries that may depend on SQLAlchemy 1.3?   | TODO            | TODO               |
| 3 | Is there comprehensive test coverage for all workflow paths using SQLAlchemy?           | TODO            | TODO               |
| 4 | Which import paths require updates for 2.x compatibility?                              | TODO            | TODO               |