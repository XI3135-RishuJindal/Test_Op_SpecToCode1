# SPEC: Upgrade SQLAlchemy from 1.3 to 2.x

## Summary

This spec details the required changes to upgrade the SQLAlchemy library from version 1.3 to 2.x in our codebase. The upgrade aims to bring the project current with supported releases, address known technical debt, and ensure ongoing supportability of ORM/database access code. The primary outcome is to replace all SQLAlchemy 1.3 interfaces, patterns, and dependencies with equivalents compatible with 2.x, without altering application logic.

## Motivation

- **End of Life (EOL):** SQLAlchemy 1.3 is end-of-life and no longer receives updates or security patches.
- **Security:** Continued use of EOL versions carries risk of unpatched CVEs (none specified, but 1.3 is out of support).
- **Compliance:** Staying current with actively supported versions helps meet compliance and security requirements.
- **Tech Debt:** Outdated APIs and behaviors increase maintenance effort.
- **Upgrade Urgency:** Medium, per technical analysis: project not blocked, but upgrade required to avoid accumulating further technical debt.

## Current State

- **Key Dependency:** The application directly depends on SQLAlchemy 1.3.
- **Usage Patterns:** Existing code may use 1.3-specific APIs, including:
  - `session.execute()` with legacy behaviors.
  - Implicit connections/binds (`engine.execute()`, etc.).
  - Legacy ORM Query API and constructor patterns.
  - Legacy import paths and config defaults.
- **Schema Models & Queries:** ORM model usage, session configuration, engine setup, and raw SQL execution rely on 1.3 idioms.
- **Configuration:** SQLAlchemy version is set to 1.3.x in project dependency management.
- **Explicit Affected Artifacts:** Specific classes, config keys, or schema elements are **TODO** as they are not detailed in the provided context.

## Proposed Changes

| Component              | Before (1.3)                                | After (2.x)                                      | Breaking? |
|------------------------|---------------------------------------------|--------------------------------------------------|-----------|
| SQLAlchemy dependency  | Version 1.3                                 | Version 2.x                                      | Y         |
| Session patterns       | Legacy `session.execute()`, implicit binds  | 2.x usage: explicit execution, new Session API   | Y         |
| Engine & connection    | Legacy `engine.execute()`                   | 2.x: move to `connection.execute()` only         | Y         |
| ORM Query usage        | Legacy Query API                            | Updated 2.x Query API patterns                   | Y         |
| Import paths           | Deprecated/older import locations           | 2.x import paths                                 | Y         |
| Declarative base/model | Legacy Base class patterns                  | 2.x declarative usage                            | Y         |
| Configuration keys     | Defaults for 1.3 behaviors                  | Adjusted for 2.x where defaults have changed     | Y         |
| Custom TypeDecorator   | Legacy binding/processing methods           | Updated methods as required by 2.x               | Y         |
| (Others as found)      | TODO                                        | TODO                                             | TODO      |

## Compatibility & Breaking Changes

| Change Area              | What Breaks              | Migration Path                        |
|-------------------------|--------------------------|---------------------------------------|
| Dependency version      | 1.3-only APIs unsupported| Update all code and dependencies to use 2.x-compatible SQLAlchemy APIs |
| Session methods         | Old context manager and execution idioms break | Refactor to new Session usage required in 2.x                           |
| Engine/connection       | `engine.execute()` removed| Use `connection.execute()`; refactor all call sites                      |
| ORM Query API           | Incompatible behavioral changes | Refactor to use 2.x-compliant query building and execution               |
| Import paths            | Deprecated imports break  | Update import paths to 2.x structure                                    |
| Configuration           | 1.3 default behaviors     | Review and update config keys to match 2.x defaults                     |
| Custom types            | TypeDecorator changes     | Update custom types as per 2.x API requirements                         |
| Application code using legacy patterns | Broad incompatibility | Manual migration required at usage points (TODO: enumerate locations)   |
| (Others as analyzed)    | TODO                     | TODO                                                                      |

## Acceptance Criteria

1. Given the upgrade to SQLAlchemy 2.x, when running project dependency checks, then all references to SQLAlchemy 1.3 must be removed from dependency metadata.
2. Given all tests previously passing under SQLAlchemy 1.3, when running the full CI/CD test suite under SQLAlchemy 2.x, then all tests must pass with no failures or errors due to API changes.
3. Given valid SQLAlchemy 2.x coding patterns, when inspecting all ORM model definitions and session usage, then no deprecated or legacy SQLAlchemy 1.3 APIs must remain.
4. Given the existing migration and seed scripts, when running database migrations, then no errors or warnings related to SQLAlchemy version incompatibility are logged.
5. Given the application is executed in its primary runtime modes, when interacting with all database code-paths, then behavior matches pre-upgrade functional correctness, as verified by test data and assertions.
6. Given static analysis (e.g., linting or mypy as configured), when scanning the codebase, then no SQLAlchemy-related warnings about deprecated or removed 1.3 APIs are reported.

## Open Questions

| # | Question                                                                | Owner         | Due Date   |
|---|------------------------------------------------------------------------|---------------|------------|
| 1 | What specific code modules/classes interact directly with SQLAlchemy?   | TODO          | TODO       |
| 2 | Are there any third-party dependencies/plugins relying on SQLAlchemy 1.3 APIs? | TODO          | TODO       |
| 3 | What integration tests or system tests explicitly exercise database edge cases? | TODO          | TODO       |
| 4 | Are there any configuration overrides that rely on 1.3 behaviors?       | TODO          | TODO       |
| 5 | Has the application been pinned to avoid later SQLAlchemy 2.x minors due to plugin compatibility? | TODO          | TODO       |

---

_N/A sections below_

## N/A — not applicable to this task

N/A. All sections above relate directly to the SQLAlchemy upgrade as scoped. No additional unrelated concerns included.