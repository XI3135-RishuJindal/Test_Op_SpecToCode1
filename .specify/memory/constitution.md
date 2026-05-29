# CONSTITUTION
## Flask 1.x → 3.1 Modernization & Application Factory Adoption

---

## Project Identity

**Name:** Flask Modernization — v1.x to 3.1  
**Purpose:** Upgrade the application's Flask dependency from 1.x to 3.1 and refactor the codebase to use the application factory pattern.  
**High-Level Goal:** Eliminate Flask 1.x (end-of-life, unsupported) as a dependency, resolve associated security and compatibility debt, and establish a maintainable, testable application structure via the factory pattern — without breaking existing functionality.

---

## Guiding Principles

1. **Prefer incremental, verifiable migration steps over a single big-bang upgrade** because Flask 1.x → 3.1 spans multiple breaking-change releases; each step must leave the application in a runnable state.
2. **Prefer the application factory pattern (`create_app()`) over module-level app instantiation** because global app objects block testability, prevent multiple configurations, and are incompatible with modern Flask extension initialization.
3. **Prefer explicit extension initialization inside the factory over implicit global state** because Flask 3.x tightens application context rules and relying on global `app` references causes runtime errors.
4. **Prefer preserving existing external API contracts (routes, response shapes) over refactoring unrelated behavior** because scope is bounded to the upgrade; unrelated changes increase regression risk.
5. **Prefer updating deprecated or removed APIs immediately upon discovery** because Flask 2.x and 3.x removed several 1.x APIs (e.g., `before_first_request`, `flask.json` module paths); leaving them in place causes silent or hard failures.
6. **Prefer environment-based configuration loading inside the factory over hardcoded config** because the factory pattern's primary value is environment-specific app construction (test, dev, prod).

---

## Constraints

- **Effort ceiling:** Moderate option — scope is limited to the Flask upgrade and factory refactor only. No unrelated infrastructure, database, or frontend changes are in scope.
- **Technology mandates:**
  - Target framework: **Flask 3.1** (pinned).
  - Python runtime: **TODO** — minimum Python version must be confirmed; Flask 3.1 requires Python ≥ 3.9. Verify and document the project's current runtime before proceeding.
  - All Flask extensions in use must be upgraded to versions compatible with Flask 3.1 before cutover.
- **Scope freeze:** No new features, no route additions, no ORM or database changes during this modernization window.
- **Build/packaging tooling:** **TODO** — confirm whether the project uses `pip`/`requirements.txt`, `Poetry`, or `pip-tools`; dependency pinning strategy must match existing tooling.

---

## Quality Standards

- **Test coverage:** All existing passing tests must continue to pass post-migration. Net-new unit tests must cover the `create_app()` factory for at minimum: default config, test config, and missing-config error paths.
- **No broken imports:** CI must run a full import check (`python -c "from app import create_app"`) as a mandatory gate.
- **Dependency audit:** A `pip check` (or equivalent) must pass with zero conflicts before any PR is merged.
- **Code review:** Every PR touching the factory refactor or Flask version pin requires at least one reviewer approval.
- **Deprecation warnings:** The test suite must be run with `PYTHONWARNINGS=error::DeprecationWarning`; zero unresolved Flask deprecation warnings are permitted at merge.
- **Documentation:** The project README must be updated to document the factory entry point and how to run the app in each environment (dev/test/prod) before the milestone is closed.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Upgrade target is Flask 3.1 (not an intermediate version) | Task specifies Flask 3.1 as the end state; stopping at 2.x would require a second migration cycle | Accepted |
| ADR-002 | Adopt `create_app()` application factory as the sole app entry point | Required for Flask 3.x best practices, testability, and extension compatibility | Accepted |
| ADR-003 | All Flask extensions must be upgraded to Flask 3.1-compatible versions in the same PR/branch as the Flask upgrade | Mixed-version extensions cause subtle runtime failures; atomic upgrade reduces debugging surface | Accepted |
| ADR-004 | Python minimum version to be confirmed before work begins | Flask 3.1 drops support for Python < 3.9; current runtime is unknown | Proposed — TODO |
| ADR-005 | Dependency management tooling to be confirmed before updating lock files | Unknown build tool; wrong tooling produces inconsistent environments | Proposed — TODO |