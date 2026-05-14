# SPEC: Upgrade SQLAlchemy to 2.x

## Current State

- **SQLAlchemy Version:** 1.3.x (assumed; code using legacy patterns and APIs)
- **Session Usage:** Uses `session.query()`, often in conjunction with `.get()` and `.filter_by()`.
- **ORM API Usage:** Implicit execution patterns, with widespread usage of deprecated behavior such as:
    - `session.commit()` outside context managers.
    - `Query.get()`
    - Calling `engine.execute()` directly.
    - Using `session.execute()` with string SQL.
    - Mixing synchronous and asynchronous patterns (if any async code).
- **Declarative Base:** Custom base via `declarative_base()` without explicit typing.
- **Configuration:** No use of SQLAlchemy 2.x style engine/session configuration or [future] flag.
- **Imports:** Mix of `sqlalchemy` and `sqlalchemy.orm` imports, sometimes referencing moved or deprecated APIs.
- **Type Annotations:** Largely absent or inconsistent.
- **Key Behaviours Affected:** All database interaction flows, including querying and transaction management, may rely on 1.3.x/1.4.x legacy APIs.

## Target State

- **SQLAlchemy Version:** 2.x (e.g., 2.0.30+)
- **Session Usage:** Uses new-style patterns:
    - Prefer `select()`, `session.scalars()`, `session.execute()`
    - `.get()` is used from the session, e.g., `session.get(Model, id)`
- **ORM API Usage:** 
    - Use context managers with sessions, e.g., `with Session(engine) as session: ...`
    - No use of `Query` objects where possible.
    - All queries use `select()`, `update()`, `delete()` constructs.
    - No use of deprecated `engine.execute()`; engine used for connections only.
    - If async: ensure separation of sync and async workflows.
- **Declarative Base:** Use `DeclarativeBase` (`from sqlalchemy.orm import DeclarativeBase`)
- **Configuration:** Use explicit 2.x engine/session configuration.
- **Imports:** Use fully supported 2.x import paths and API signatures.
- **Type Annotations:** Follow SQLAlchemy 2.x recommendations.
- **Key Behaviours:** All database access flows, migrations, and model definitions work with and follow 2.x idioms.

## Compatibility & Breaking Changes

| Breaking Change                                                                 | Migration Path                                                                                                                                         |
|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `session.query().get(id)` removed                                               | Change to `session.get(Model, id)`                                                                                                                     |
| Direct use of `engine.execute()` is removed                                     | Use `Session.execute()` or explicit connection (`engine.connect()`) with compile                              |
| Use of legacy-style ORM querying                                                | Migrate to core-style `select()`, `session.execute(select(...))`                                                                                      |
| No implicit commit/rollback; session auto-flush behavior changes                | Ensure explicit use of context managers and `commit()` as needed.                                                                                      |
| Use of `declarative_base()` (from `sqlalchemy.ext.declarative`) is deprecated   | Use `from sqlalchemy.orm import DeclarativeBase` and `class Base(DeclarativeBase): ...`                                                               |
| Synchronous/async ambiguity in APIs                                             | Audit all flows to cleanly separate synchronous and asynchronous usage.                                                                                |
| String SQL in `session.execute()` is restricted                                | Use SQLAlchemy text() or, preferably, Core expressions.                                                                                                |
| Changed defaults for some relationships, schema arguments                       | Audit `relationship()`, `ForeignKey()`, and others for updated argument/behavior changes.                                                             |
| Changed import locations for commonly-used symbols (e.g., `inspect`, `declarative_base`) | Update all imports to match 2.x documented locations.                                                                                         |

## Key Flows (before vs after)

### 1. Retrieve Object by Primary Key

**Before:**
```python
session.query(User).get(user_id)
```
**After:**
```python
session.get(User, user_id)
```

---

### 2. Basic Query

**Before:**
```python
users = session.query(User).filter_by(is_active=True).all()
```
**After:**
```python
stmt = select(User).filter_by(is_active=True)
users = session.scalars(stmt).all()
```

---

### 3. Engine Direct Execution

**Before:**
```python
result = engine.execute("SELECT * FROM users WHERE active=1")
```
**After:**
```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE active=1"))
```
or, preferably:
```python
stmt = select(User).where(User.active == True)
with Session(engine) as session:
    users = session.scalars(stmt).all()
```

---

### 4. Session Management

**Before:**
```python
session = Session()
# ... do work ...
session.commit()
session.close()
```
**After:**
```python
with Session(engine) as session:
    # ... do work ...
    session.commit()
# session automatically closed
```

## Data Model Changes

- **Declarative Base:**  
    - **Before:**  
        ```python
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
        ```
    - **After:**  
        ```python
        from sqlalchemy.orm import DeclarativeBase
        class Base(DeclarativeBase):
            pass
        ```

- **No further table/field changes required** unless related API signature requires updates (e.g., arguments to relationships).

## Configuration Changes

- **Engine/Session Construction:**
    - **Before:**  
        ```python
        engine = create_engine(DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        ```
    - **After:**  
        ```python
        engine = create_engine(DB_URL)
        # or, for async:
        # from sqlalchemy.ext.asyncio import create_async_engine
        # engine = create_async_engine(DB_URL)
        Session = sessionmaker(engine)
        with Session() as session:
            ...
        ```

- **No required new environment variables, feature flags, or config files** unless custom logic is present. Check custom config loaders for string SQL or engine/session pattern customizations.

---

**N/A — not applicable to this task:**  
- Language, Runtime, Build tool, Environment-specific configs (not SQLAlchemy concerned)
- Application-layer logic and frameworks beyond SQLAlchemy upgrade scope

---

**End of document.**