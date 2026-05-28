# CONSTITUTION
## Flask 1.x → 3.1 Upgrade & Application Factory Adoption

---

## Project Identity

**Name:** Flask Modernization — v1.x to 3.1  
**Purpose:** Upgrade the application's Flask dependency from version 1.x to 3.1 and refactor the codebase to use the application factory pattern.  
**High-Level Goal:** Eliminate reliance on an outdated Flask release, resolve associated security and compatibility debt, and establish a maintainable, testable application structure via the factory pattern.

---

## Guiding Principles

1. **Prefer Flask 3.1 APIs over deprecated 1.x APIs** because Flask 2.x and 3.x removed several globals, helpers, and behaviours present in 1.x; retaining old call-sites will cause runtime errors.
2. **Prefer the application factory pattern (`create_app()`) over module-level app instantiation** because a single global `app` object prevents proper test isolation and makes configuration-per-environment impossible.
3. **Prefer incremental, branch-based migration over a single big-bang merge** because the moderate effort ceiling limits rework capacity; smaller changesets reduce regression risk.
4. **Prefer explicit extension initialisation inside the factory over import-time side effects** because Flask 3.x tightens application context rules and implicit initialisation is a known source of `RuntimeError` during testing.
5. **Prefer pinning Flask to `>=3.1,<4.0` over an unpinned dependency** because future major Flask releases may introduce further breaking changes outside this project's scope.

---

## Constraints

| Category | Constraint |
|---|---|
| **Effort ceiling** | Moderate option — treat as a fixed, time-boxed effort. No scope creep beyond Flask upgrade and factory refactor. |
| **Target version** | Flask **3.1.x** (minimum). No downgrade below 3.1 permitted after cutover. |
| **Python runtime** | TODO — minimum Python version must be confirmed; Flask 3.1 requires Python ≥ 3.9. Verify and pin accordingly. |
| **Dependency compatibility** | All Flask extensions (e.g. Flask-SQLAlchemy, Flask-Login, Flask-WTF) must be upgraded to versions compatible with Flask 3.1 before merge. |
| **Scope freeze** | Database schema changes, business logic refactors, and frontend changes are **out of scope**. |
| **Breaking-change window** | TODO — confirm whether a maintenance window or feature freeze is required during cutover. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test coverage** | Existing test suite must pass at 100% on Flask 3.1 before merge. Net-new factory-related code must have ≥ 80% line coverage. |
| **Regression gate** | CI pipeline must execute the full test suite against Flask 3.1; no merge permitted with failing tests. |
| **Deprecation warnings** | Zero Flask deprecation warnings (`DeprecationWarning`, `PendingDeprecationWarning`) in the test run output after migration. |
| **Code review** | Every PR touching the factory pattern or Flask version pin requires at least one reviewer approval. |
| **Documentation** | `README` or equivalent must document the `create_app()` entry point, supported configuration keys, and how to run the app locally after the refactor. |
| **Dependency audit** | `pip-audit` (or equivalent) must report no known CVEs in Flask or its direct dependencies at merge time. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Upgrade target is Flask **3.1** (not 2.x) | Jumping to the current stable release avoids a two-step upgrade and immediately resolves all 1.x EOL risk. | Accepted |
| ADR-002 | Adopt the **application factory pattern** (`create_app()`) as part of this upgrade | Flask 3.x best-practice; required for proper extension init and test isolation; low additional cost when already touching app bootstrap code. | Accepted |
| ADR-003 | Keep all other framework/library upgrades **out of scope** unless required for Flask 3.1 compatibility | Preserves effort budget; unrelated upgrades introduce unrelated risk. | Accepted |
| ADR-004 | Minimum Python version — **TODO** | Flask 3.1 requires Python ≥ 3.9; actual runtime version must be confirmed from the deployment environment before work begins. | Proposed |