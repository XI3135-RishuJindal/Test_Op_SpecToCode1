# SQLAlchemy 2.x Upgrade Specification

## Current State

- **SQLAlchemy Version:** < 2.0 (commonly 1.4.x or earlier)
- **Interfaces/APIs:**
  - Use of _legacy_ query API: `session.query(Model)`, `.filter()`, etc.
  - Engine creation via `create_engine(connection_string)` with implicit connection pooling.
  - Transaction management using `session.begin()`, `session.commit()`, etc., often without the `with` context manager.
  - Direct use of `engine.execute()` and `session.execute()` for raw SQL.
  - Data model classes inherit from `declarative_base()` (from `sqlalchemy.ext.declarative`).
  - Type checking and reflection using legacy methods.
- **Behaviors:**
  - Implicit coercion between text and SQL expressions.
  - Transparent connection closing; some leaks possible.
  - ORM queries constructed with non-keyword arguments.
  - Bound metadata to an engine (sometimes as `MetaData(bind=engine)`).

## Target State

- **SQLAlchemy Version:** 2.x (e.g., 2.0.30)
- **Interfaces/APIs:**
  - **Modern query API:** Use `session.scalars(select(Model))` or `session.execute(select(Model))` instead of `session.query()`.
  - **Engine creation:** Same, but all query/transaction APIs updated.
  - **Context Manager Transactions:** All transactions use `with Session.begin():` or `with session.begin():` context.
  - **Deprecation of `engine.execute()`**: Use `Connection.execute()`, always from a connection/transaction context.
  - **Declarative models:** Import from `sqlalchemy.orm.declarative_base`.
  - **Use of keyword arguments** for all ORM/API calls.
  - **No `MetaData(bind=...)`**: Engine binding must be explicit.
- **Behaviors:**
  - Stricter typing and error handling.
  - Explicit management of connections/transactions.
  - Clear separation of textual SQL and SQLAlchemy Core constructs.

## Compatibility & Breaking Changes

| Breaking Change   | Description | Migration Path |
|-------------------|-------------|---------------|
| `session.query()` | Removed/unsupported; all queries must use `select()` and `session.execute()` or `session.scalars()` | Replace instances of `session.query(Model)` with `session.execute(select(Model))` or `session.scalars(select(Model))` |
| `engine.execute()` and `session.execute()` (raw SQL) | Removed/raises; must use a `Connection` object for `execute()` calls; ORM queries must use `select()` construct | Refactor all raw SQL executions to be performed within `with engine.connect() as conn:` blocks |
| Use of `MetaData(bind=...)` | `bind` argument removed; binding metadata to engine disallowed | Pass engine explicitly when constructing/reflecting metadata, e.g., `metadata.create_all(engine)` |
| ORM queries with non-keyword arguments | Only keyword arguments allowed for filter/constructors | Refactor all such calls to use keyword arguments |
| Import path for `declarative_base` | Moved from `sqlalchemy.ext.declarative` to `sqlalchemy.orm` | Change import to `from sqlalchemy.orm import declarative_base` |
| Transaction context | Implicit transactions/commits deprecated | Use explicit `with Session.begin():` transaction blocks everywhere |

## Key Flows (before vs after)

**1. ORM Querying**  
**Before:**  
```python
session.query(User).filter(User.id == 5).all()
```
**After:**  
```python
from sqlalchemy import select
session.scalars(select(User).where(User.id == 5)).all()
```

**2. Executing Raw SQL**  
**Before:**  
```python
result = engine.execute("SELECT id FROM users")
```
**After:**  
```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT id FROM users"))
```

**3. Transaction Management**  
**Before:**  
```python
session = Session()
session.add(obj)
session.commit()
```
**After:**  
```python
with Session.begin() as session:
    session.add(obj)
```

**4. Declarative Base Import**  
**Before:**  
```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
```
**After:**  
```python
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

N/A — not applicable to this task