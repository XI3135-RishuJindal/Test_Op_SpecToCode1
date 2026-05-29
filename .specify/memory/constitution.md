# CONSTITUTION — psycopg2 → psycopg3 Modernization

## Project Identity

**Name:** psycopg2 Upgrade / psycopg3 Migration

**Purpose:** Upgrade the project's PostgreSQL database adapter from psycopg2 to either the latest stable psycopg2 release or migrate fully to psycopg3 (psycopg), eliminating accumulated driver-level tech debt and ensuring continued compatibility with current PostgreSQL and Python ecosystems.

**High-Level Goal:** Deliver a stable, tested database adapter upgrade with no regression in database connectivity, query behaviour, or application functionality.

---

## Guiding Principles

1. **Prefer psycopg3 (psycopg) over a psycopg2 patch upgrade** because psycopg3 is the actively maintained successor; psycopg2 receives only critical fixes and carries medium-urgency EOL risk.
2. **Prefer an incremental, branch-based migration over a big-bang swap** because the adapter touches all database I/O paths, making a phased approach safer to test and roll back.
3. **Prefer explicit connection/cursor lifecycle management over implicit patterns** because psycopg3 changes context-manager and connection semantics; silent behavioural differences must be surfaced early.
4. **Prefer running the existing test suite against the new adapter before merging** because adapter-level changes can silently alter type coercion, transaction handling, and error classes.
5. **Prefer pinning the new adapter version in dependency manifests** because floating dependencies introduce non-deterministic breakage across environments.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option selected; treat as ≤ 5 person-days total. No scope expansion beyond adapter replacement. |
| **Scope freeze** | Only the database adapter layer is in scope. Application features, schema changes, and ORM upgrades are explicitly out of scope. |
| **Target adapter** | psycopg3 (`psycopg` ≥ latest stable) preferred; psycopg2 latest stable is the fallback if migration blockers are found. |
| **Python runtime** | TODO — confirm minimum Python version in use (psycopg3 requires Python ≥ 3.7; binary extras require ≥ 3.8). |
| **PostgreSQL version** | TODO — confirm server version to validate driver compatibility. |
| **Dependency manifest** | The new adapter version must be pinned (exact or bounded) in whatever dependency file the project uses (requirements.txt, pyproject.toml, etc.). |
| **No downtime** | Deployment must not require a database restart or application downtime beyond a normal rolling/restart deploy. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test coverage** | All existing database-layer tests must pass against the new adapter before merge. No net reduction in passing test count. |
| **Regression gate** | A dedicated integration test connecting to a real (or containerised) PostgreSQL instance must execute successfully in CI. |
| **Code review** | Minimum one peer review approval required before merging the adapter change. |
| **Dependency audit** | Any transitive dependency that pins psycopg2 must be identified and resolved or explicitly documented as a known blocker. |
| **Documentation** | A brief migration note (CHANGELOG entry or PR description) must record: old version → new version, any API changes handled, and any known behavioural differences. |
| **Rollback plan** | The PR must include or reference instructions for reverting to psycopg2 if a production issue is detected post-deploy. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Target psycopg3 as the primary migration path | psycopg2 is in maintenance-only mode; psycopg3 is the upstream-recommended successor and reduces future EOL risk | Accepted |
| ADR-002 | Fallback to psycopg2 latest stable if psycopg3 migration blockers exist within effort ceiling | Effort is capped at moderate; a hard blocker (e.g., incompatible dependency) must not cause the project to exceed the ceiling | Accepted |
| ADR-003 | Scope limited strictly to adapter replacement | Tech analysis shows no other upgrade targets in this option; expanding scope risks exceeding the effort ceiling | Accepted |
| ADR-004 | Python runtime version compatibility to be confirmed before work begins | Runtime is listed as unknown in tech analysis; psycopg3 has a hard Python version floor | Proposed — TODO |