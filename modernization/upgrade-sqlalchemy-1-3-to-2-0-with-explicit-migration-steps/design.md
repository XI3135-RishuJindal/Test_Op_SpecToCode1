# SQLAlchemy 1.3 to 2.0 Upgrade — Design Document

## Architecture Overview

**Before:**  
- The application uses SQLAlchemy version 1.3 for its ORM and database interactions.
- Queries rely on legacy APIs (often non-async, implicit engine/bind patterns, e.g., `session.execute()` without explicit connections).
- Significant use of implicit transaction semantics and automatic commit/rollback.

**After:**  
- The application will use SQLAlchemy version 2.0, requiring explicit engine/bind usage, explicit transactions, and migrated API patterns.
- All code paths for data access are upgraded to the 2.0 API style. 
- Deprecated or removed APIs are replaced with new equivalents.

---

## Migration Strategy

**Chosen Approach:**  
Strangler Fig Pattern

**Rationale:**  
- The strangler fig approach allows incremental refactoring of individual modules/components without requiring a risky "big-bang" migration.
- Enables running 1.3 and 2.0 style code in parallel, swapping out portions progressively, testing as we go.

**Steps:**
1. Identify all code paths interacting with SQLAlchemy.
2. Introduce compatibility shims or wrappers where feasible to allow both 1.3 and 2.0 styles temporarily.
3. Migrate and test individual models/repositories/module clusters iteratively.
4. When all direct usages are migrated, upgrade the core SQLAlchemy dependency and remove shims.
5. Conduct system-wide validation and cut-over.

---

## Component Changes

| Component                     | Changes                                                                            | Rationale                                          |
|-------------------------------|-------------------------------------------------------------------------------------|----------------------------------------------------|
| ORM Model Definitions         | Review for deprecated constructs, e.g., `declarative_base`, and update syntax.      | SQLAlchemy 2.0 expects modern class-declared models|
| Query Execution               | Replace legacy `session.execute()` and similar APIs with 2.0 style usage.           | Explicit use of connections and select() API is mandated.|
| Transactions                  | Refactor to use explicit `with session.begin():` or context managers.               | 2.0 removes implicit transaction enforcement.       |
| Engine/Session Management     | Replace global binds with explicit session and engine passing.                      | New engine/session APIs require explicit scope.     |
| Raw SQL & Text Clause Usage   | Update `text()` and manual query usage as required.                                | Some query constructs have altered signatures/semantics.|
| Removed Legacy APIs           | Remove patterns like `Query.with_entities`, `session.query().filter()`, etc.       | Ensure code fully avoids deprecated patterns.       |

---

## Dependency Upgrade Plan

| Dependency             | Current Version | Target Version | Migration Notes                          |
|------------------------|----------------|---------------|------------------------------------------|
| SQLAlchemy             | 1.3.x          | 2.0.x         | API/behavior breaking changes; see ORM docs|
| sqlalchemy-utils       | [current]      | [latest]      | Ensure compatibility with SQLAlchemy 2.0  |
| alembic (if used)      | [current]      | [latest]      | Requires upgraded SQLAlchemy version      |
| DB driver (e.g. psycopg2, pymysql) | [current] | [latest] | Double-check for any required updates     |

_Note: "[current]" and "[latest]" to be replaced with actual versions from your environment._

---

## CI/CD Pipeline Changes

- **Build:**  
  Update requirements to pin to SQLAlchemy 2.0 and related dependencies.
- **Test:**  
  Add migration-specific integration test jobs to CI (run full test suite with both 1.3 and 2.0 in staging phase if possible).
  Enforce separate linting for new API usage.
- **Deploy:**  
  Tag deployments of modules migrated to 2.0, and coordinate deployment order if needed.

---

## Infrastructure Changes

N/A — not applicable to this task

---

## Rollback Plan

- Maintain a feature branch with the 1.3 codebase until migration is validated in staging/production.
- After each incremental migration step, tag release; enable a rollback by redeploying the previous tag if issues arise.
- For final cut-over, ensure all migration steps are reversible, or that core SQLAlchemy config can be changed via requirements files/environment variables to pin 1.3 temporarily.
- Database schema is *not* expected to change as part of this migration; only application logic is impacted.

---

## Testing Strategy

- **Unit Tests:**  
  Update/extend unit tests around all model, query, and repository code to ensure old and new APIs produce the same results.
- **Integration Tests:**  
  Run full integration tests using a real database backend with SQLAlchemy 2.0.
- **Regression Tests:**  
  Ensure all high-level application behaviors are captured in regression tests, especially transactional workflows, ORM querying, and connection handling.
- **Performance Tests:**  
  Compare performance pre- and post-migration on common query and transaction patterns to catch regressions.
- **Code Coverage:**  
  Track coverage of all DB code paths across tests, and enforce no significant drop post-migration.

---

