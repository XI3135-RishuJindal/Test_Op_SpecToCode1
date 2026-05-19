# Constitution: Flask 3.x & SQLAlchemy 2.x Modernization

## Project Identity

**Name:**  
Flask/SQLAlchemy Modernization Refactor

**Purpose:**  
Refactor existing application code to become compatible with Flask 3.x and SQLAlchemy 2.x, addressing all relevant breaking changes.

**High-Level Goal:**  
Ensure the application runs without errors or regressions on Flask 3.x and SQLAlchemy 2.x by updating code patterns and dependencies in accordance with the latest frameworks.

---

## Guiding Principles

1. **Prefer code compatibility with Flask 3.x and SQLAlchemy 2.x over legacy practices because breaking changes render older code non-functional.**
2. **Prefer source changes that minimize scope and complexity over broad rewrites because the stated goal is targeted refactoring.**
3. **Prefer explicit error-checking for deprecated/removed APIs over silent failure because breaking changes may cause runtime failures.**

---

## Constraints

- **Timeline and Effort Ceiling:**  
  Must not exceed the moderate person-days estimate defined in the selected upgrade option.

- **Technology Mandates:**  
  - All modernized code must target Flask 3.x and SQLAlchemy 2.x compatibility.
  - No assumptions on runtime, language, or cloud provider (TODO: clarify if/when known).

- **Budget or Scope Freezes:**  
  - Scope limited strictly to updating for Flask 3.x and SQLAlchemy 2.x breaking changes.

---

## Quality Standards

- **Testing:**  
  - Minimum: All existing tests must pass after refactor.
  - New or updated code must be covered by tests—no less than the pre-refactor coverage percentage.

- **Code Review:**  
  - All modernization commits must undergo peer code review for compatibility and safety.

- **Documentation:**  
  - Update README or equivalent onboarding/reference docs to reflect new framework/ORM versions and any changed execution commands.

- **Deployment Gates:**  
  - Do not promote to production until passing all relevant test suites on Flask 3.x and SQLAlchemy 2.x.

---

## Decision Log

| ID   | Decision                                                | Rationale                                                               | Status    |
|------|---------------------------------------------------------|-------------------------------------------------------------------------|-----------|
| 1    | Refactor strictly for Flask 3.x and SQLAlchemy 2.x      | Breaking changes require targeted updates; explicit modernization goal   | accepted  |
| 2    | Limit changes to code affected by breaking changes only | Align with effort ceiling and scope freeze of 'moderate' upgrade option | accepted  |
| 3    | Enforce testing pass post-upgrade                       | Prevent regressions during framework/ORM migration                      | accepted  |

---

**End of Constitution**