# SPEC: Migration for SQLAlchemy 2.x Compatibility

## Current State

The application utilizes SQLAlchemy 1.x APIs throughout its codebase. The following elements are affected:

- **Session Usage:** Sessions are typically created via `sessionmaker()` and are used without context managers. Common usage patterns:
    ```python
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.execute("SELECT * FROM my_table")
    ```
- **Querying:** The classic ORM querying style, e.g., `session.query(Model).filter(...)`.
- **Engine/Connection:** Direct engine-bound execution or deprecated connection patterns:
    ```python
    engine.execute(...)
    ```
- **Bindings:** Implicit engine or session bindings prevalent (e.g., `Base.metadata.create_all()` without explicit bind).
- **String SQL Execution:** Executing raw SQL as string arguments directly (e.g., `session.execute("SELECT ...")`).
- **Synchronous-Only Codebase:** No use of asynchronous SQLAlchemy features.
- **API/Interfaces:** Internal APIs and data models relying on above SQLAlchemy patterns.

## Target State

All database interactions and patterns are updated for compatibility with SQLAlchemy 2.x:

- **Session Usage:** Sessions are created and used via context managers, enforcing new-style usage:
    ```python
    Session = sessionmaker(bind=engine, future=True)
    with Session() as session:
        result = session.execute(text("SELECT * FROM my_table"))
    ```
- **Querying:** New ORM querying patterns (`select()` instead of `session.query(...)`):
    ```python
    stmt = select(Model).where(Model.id == 1)
    result = session.execute(stmt)
    ```
- **Engine/Connection:** Prohibit direct `engine.execute()`; use `Connection` or `Session` objects explicitly:
    ```python
    with engine.connect() as conn:
        result = conn.execute(text("..."))
    ```
- **Bindings:** All metadata operations require explicit bind.
- **String SQL Execution:** Use `sqlalchemy.text()` for textual SQL expressions.
- **API/Interfaces:** All application APIs updated to handle revised SQLAlchemy interfaces and result objects (e.g., no direct fetching from results of raw SQL).

## Compatibility & Breaking Changes

| Breaking Change | Migration Path |
|-----------------|---------------|
| `session.execute()` or `engine.execute()` disallows raw string queries | Always use `sqlalchemy.text(sql)` in queries: <br/>`session.execute(text("SELECT * FROM ..."))` |
| Deprecated `session.query(...)` pattern removed | Use `select()` construct: <br/>`stmt = select(Model).where(...)` |
| Sessions require context manager for proper transactional handling | Wrap session use in `with Session() as session:` blocks |
| Metadata operations require explicit bind | Specify bind explicitly: <br/>`Base.metadata.create_all(bind=engine)` |
| Return values and result proxy behavior changed | Use `.scalars()`, `.mappings()` or `.fetchone()` / `.fetchall()` appropriately, e.g.: <br/>`result = session.execute(stmt)` <br/>`rows = result.scalars().all()` |
| Removal of implicit engine/session binding | Refactor all code to always specify engine/session object explicitly |

## Key Flows (before vs after)

### Flow 1: Running a Raw SQL Query

**Before (1.x):**
1. Create session via `sessionmaker`.
2. Execute string SQL directly: `result = session.execute("SELECT ...")`
3. Fetch results from `result`.

**After (2.x):**
1. Create session via `sessionmaker` with `future=True` (or remove argument if using 2.x):
2. Use context manager: `with Session() as session:`
3. Execute query via `text()`: `result = session.execute(text("SELECT ..."))`
4. Fetch via `result.all()` or appropriate method.

---

### Flow 2: ORM Query

**Before (1.x):**
1. `query = session.query(User).filter(User.name == "Alice")`
2. `user = query.first()`

**After (2.x):**
1. `stmt = select(User).where(User.name == "Alice")`
2. `result = session.execute(stmt)`
3. `user = result.scalars().first()`

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

**Environment variables:**  
N/A — not applicable to this task

**Feature flags:**  
N/A — not applicable to this task

**Config files:**  
All places where `sqlalchemy` is pinned to `<2.0` must update requirements to `sqlalchemy>=2.0`.

- **Example:**  
  In `requirements.txt` or `pyproject.toml`:
  ```
  sqlalchemy>=2.0,<3.0
  ```

---

**End of Spec**