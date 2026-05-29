# CONSTITUTION
## SQLAlchemy Query API Migration

---

## Project Identity

**Name:** SQLAlchemy Query API Migration

**Purpose:** Migrate all legacy SQLAlchemy Query API calls (e.g., `session.query(Model).filter(...)`) to the modern `Session.execute(select())` style introduced in SQLAlchemy 2.0.

**High-Level Goal:** Eliminate all usage of the deprecated Query API across the codebase, replacing it with the 2.0-style `select()` + `Session.execute()` pattern, ensuring the application is compatible with SQLAlchemy 2.0+ and free of legacy ORM query debt.

---

## Guiding Principles

1. **Prefer `Session.execute(select())` over `session.query()` because** the Query API is fully removed in SQLAlchemy 2.0 and continued use creates a hard runtime breakage risk at the next major upgrade.
2. **Prefer incremental, file-by-file migration over a single big-bang rewrite because** smaller changesets reduce regression risk and allow targeted testing at each step.
3. **Prefer preserving existing query semantics over refactoring business logic because** this migration's scope is API style only — behavioral changes introduce unquantified risk outside the mandate.
4. **Prefer explicit `scalars()` / `scalar_one()` / `all()` result handling over implicit result unpacking because** SQLAlchemy 2.0 returns `Row` objects by default, and incorrect result handling is the most common source of silent regressions in this migration.
5. **Prefer running the full test suite after each logical batch of changes because** the absence of a type-safe compile step means tests are the primary regression gate.

---

## Constraints

- **Scope freeze:** Changes are limited strictly to replacing Query API call sites with `Session.execute(select())` equivalents. No schema changes, no model restructuring, no business-logic refactoring.
- **Timeline/Effort:** Moderate effort ceiling (exact person-days TODO — not provided in upgrade option). Work must be scoped and batched to fit within this envelope without scope creep.
- **Technology mandate:** All migrated code must be compatible with SQLAlchemy 2.0+ `select()` API. No new Query API call sites may be introduced after migration begins.
- **Runtime/Language:** TODO — runtime version and language not specified in tech analysis. Confirm Python version compatibility with SQLAlchemy 2.0 (requires Python 3.7+) before starting.
- **No breaking changes to external interfaces:** Public APIs, return types visible to callers, and serialization behavior must remain unchanged.

---

## Quality Standards

- **Test coverage:** Every migrated module must have its existing test coverage passing at 100% before the PR is merged. No net reduction in test coverage is acceptable.
- **Code review:** Each PR touching migrated query call sites requires at least one reviewer who can verify SQLAlchemy 2.0 result-handling correctness (`scalars()`, `scalar_one_or_none()`, etc.).
- **Regression gate:** CI must execute the full test suite on every PR. No merge is permitted with failing tests.
- **Migration tracking:** A checklist of all identified Query API call sites must be maintained and updated as each site is migrated. Done means zero remaining `session.query(` occurrences in production code (verified by automated grep/linting rule).
- **Linting rule:** A lint check (e.g., a `flake8` plugin or `grep`-based CI step) must be added to prohibit reintroduction of `session.query(` after the migration is complete.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Migrate to `Session.execute(select())` style | Query API is deprecated in SQLAlchemy 1.4 and removed in 2.0; medium urgency upgrade risk identified in tech analysis | Accepted |
| ADR-002 | Scope limited to Query API call-site replacement only | Upgrade option is "moderate"; broader refactoring would exceed effort ceiling and introduce unscoped risk | Accepted |
| ADR-003 | Add CI lint gate to ban `session.query(` post-migration | Prevents regression without relying solely on code review vigilance | Accepted |
| ADR-004 | Exact Python runtime version | TODO — not provided in tech analysis; must be confirmed to validate SQLAlchemy 2.0 compatibility | Proposed |