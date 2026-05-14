# SPEC: Migrate Application Code for SQLAlchemy 2.x Compatibility

## Current State

- **SQLAlchemy Version**: <2.x (likely 1.3.x or 1.4.x)
- **Session Usage**: Majority of session operations use session methods not as context managers (e.g., `session = Session(); session.query(...); session.commit()`)
- **Query Interface**: Code relies heavily on the legacy `Query` interface, for example via `session.query(Model).filter(Model.foo == bar)`
- **Connection Execution**: Uses `engine.execute()`, `connection.execute(sql_text("..."))`, or ORM `session.execute()` without explicit statements.
- **Implicit Bindings**: Frequent use of string SQL, relying on engine/connection for implicit text execution.
- **Data Models**: ORM mapped classes using `declarative_base`, with sometimes Model class methods making queries directly via `session.query`.
- **Transactions**: Transactions may be implicitly managed or left out in some cases, depending on autocommit defaults.
- **API Usage**: Some hybrid mix of "1.x legacy" and "2.x style", including positional arguments in some query/execute methods.
- **Import Paths**: Some imports of now-deprecated aliases or locations (e.g., `from sqlalchemy.ext.declarative import declarative_base`).

## Target State

- **SQLAlchemy Version**: 2.x (>=2.0.0)
- **Session Usage**: Sessions are used as context managers: `with Session() as session: ...`
- **Query Interface**: Direct use of `select()`, `insert()`, etc., from SQLAlchemy Core for queries: `session.execute(select(Model).where(...))`
- **Connection Execution**: Use only explicit SQL expressions or textual SQL via `text()`; `engine.execute` removed.
- **No Implicit Bindings**: Always use explicit statement execution with `session.execute(statement)`.
- **Data Models**: ORM-mapped classes continue as before; queries and class methods updated to use new patterns.
- **Transactions**: Explicit transaction blocks as context managers where necessary: `with session.begin(): ...`
- **API Usage**: Only "2.x style" API calls; no use of legacy/removed patterns.
- **Import Paths**: All imports updated to new canonical locations (e.g., `from sqlalchemy.orm import declarative_base`).

## Compatibility & Breaking Changes

| Breaking Change | Migration Path |
|-----------------|---------------|
| Removal of `engine.execute()` | Replace all usage with explicit connections or sessions: `with engine.connect() as conn: conn.execute(...)` |
| Removal of `session.execute()` with raw SQL string | Use `text()` to wrap SQL: `session.execute(text("SELECT ..."))` |
| No implicit autocommit on execute | Surround changes/updates with `with session.begin(): ...` or explicit `session.commit()` |
| `session.query()` discouraged/removed | Replace with `select()` statements: `session.execute(select(Model).where(...))` |
| Old-style transaction handling | Use context managers: `with session.begin(): ...` |
| Deprecated imports | Update imports to canonical locations, e.g., `from sqlalchemy.orm import declarative_base` |
| Legacy ORM query returns lists, Result is now used | Handle `Result` object (e.g. `.scalars()`, `.all()`) instead of expecting lists/rows |
| Connectionless execution APIs removed | Use explicit `engine.connect()` or `Session` objects |

## Key Flows (before vs after)

**User Query Flow**

*Before (SQLAlchemy 1.4.x)*

1. Create a session: `session = Session()`
2. Query: `results = session.query(User).filter(User.id == user_id).all()`
3. Close session: `session.close()`

*After (SQLAlchemy 2.x)*

1. Create session as context manager: `with Session() as session:`
2. Query: `results = session.execute(select(User).where(User.id == user_id)).scalars().all()`
3. Session automatically closed.

---

**Transaction/Write Flow**

*Before*

1. `session = Session()`
2. `user = User(name="Alice")`
3. `session.add(user)`
4. `session.commit()`
5. `session.close()`

*After*

1. `with Session() as session:`
2. `with session.begin():`
3. `    user = User(name="Alice")`
4. `    session.add(user)`
5. Session automatically committed and closed.

---

**Raw SQL Execution**

*Before*

1. `results = session.execute("SELECT * FROM users")`

*After*

1. `results = session.execute(text("SELECT * FROM users"))`

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

N/A — not applicable to this task