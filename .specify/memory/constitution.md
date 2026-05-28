# CONSTITUTION
## psycopg2 → psycopg3 Migration Project

---

## Project Identity

**Name:** psycopg2 Upgrade / psycopg3 Migration

**Purpose:** Upgrade the project's PostgreSQL database adapter from `psycopg2` to either the latest stable `psycopg2` release or migrate fully to `psycopg3` (`psycopg` ≥ 3.x), eliminating accumulated driver-level tech debt and ensuring continued compatibility with current PostgreSQL server versions and Python runtimes.

**High-Level Goal:** Deliver a working, tested database adapter upgrade with no regressions in database connectivity, query behaviour, or transaction semantics — at moderate effort and without expanding scope beyond the adapter layer.

---

## Guiding Principles

1. **Prefer psycopg3 (`psycopg`) over staying on psycopg2 where feasible**, because psycopg2 is in maintenance-only mode and receives no new features; psycopg3 is the actively maintained successor.
2. **Prefer minimal surface-area changes over broad refactoring**, because the upgrade urgency is medium and scope must remain bounded to the adapter layer only.
3. **Prefer explicit connection and cursor management over implicit patterns**, because psycopg3 changes several defaults (e.g. autocommit behaviour, binary protocol) that can silently alter runtime behaviour if not addressed deliberately.
4. **Prefer validating behaviour through tests over assuming API compatibility**, because psycopg3 is not a drop-in replacement — type handling, `%s`/`%(name)s` parameter syntax, and `copy` APIs have breaking changes.
5. **Prefer documenting every API difference encountered over leaving tribal knowledge implicit**, because runtime and language versions are currently unknown (see Constraints), increasing the risk of environment-specific surprises.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate (exact person-days not specified — TODO: confirm with project lead before work begins) |
| **Scope freeze** | Changes are limited to the database adapter layer (`psycopg2` → `psycopg`/`psycopg2` latest). No ORM upgrades, schema changes, or infrastructure work in scope. |
| **Python runtime** | TODO: confirm minimum Python version. psycopg3 requires Python ≥ 3.7; async features require ≥ 3.8. |
| **PostgreSQL server version** | TODO: confirm target server version. psycopg3 supports PostgreSQL ≥ 10. |
| **Dependency conflicts** | TODO: audit whether any pinned transitive dependencies (e.g. SQLAlchemy, Django, asyncpg) constrain the adapter version. |
| **Build/packaging toolchain** | TODO: unknown — confirm whether `psycopg[binary]` or source build is required for the deployment environment. |

---

## Quality Standards

- **Test coverage:** All existing database integration tests must pass without modification to test assertions. Net-new tests must cover any psycopg3-specific code paths introduced (e.g. `AsyncConnection`, binary copy). Coverage must not decrease from the pre-upgrade baseline.
- **Regression gate:** A full integration test run against a real PostgreSQL instance (not mocked) must pass before the PR is mergeable.
- **Code review:** Minimum one reviewer with familiarity with the project's database layer must approve. Reviewer must explicitly confirm transaction semantics are preserved.
- **Documentation:** A `MIGRATION_NOTES.md` file must be committed alongside the change, listing every psycopg API difference encountered and how it was resolved.
- **Dependency manifest:** `requirements.txt` / `pyproject.toml` (whichever applies) must pin the new adapter to a specific minor version (e.g. `psycopg[binary]>=3.1,<4`).
- **No silent failures:** Any connection error, type coercion change, or behavioural difference discovered during migration must be resolved explicitly — not suppressed or worked around with compatibility shims unless documented.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Evaluate psycopg3 as the primary migration target before falling back to psycopg2-latest | psycopg2 is maintenance-only; psycopg3 is the strategic successor and reduces future upgrade debt | Accepted |
| ADR-002 | Limit scope strictly to the adapter layer | Upgrade urgency is medium; broader refactoring would exceed the moderate effort ceiling | Accepted |
| ADR-003 | Confirm Python and PostgreSQL runtime versions before finalising adapter choice | Both are unknown at constitution time; psycopg3 has hard runtime minimums that may affect the decision | Proposed — TODO: resolve before sprint start |
| ADR-004 | Require integration tests against a live PostgreSQL instance as a merge gate | Mocked DB tests cannot catch type-handling and protocol-level regressions introduced by the adapter change | Accepted |