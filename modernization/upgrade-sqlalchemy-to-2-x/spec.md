# SPEC: Upgrade SQLAlchemy to 2.x

## Current State

- **ORM Version:** SQLAlchemy 1.3.x (assumed; versions prior to 2.x)
- **APIs Used:**  
  - `session.query()` style ORM queries  
  - Implicit connection management with context-free statements  
  - Use of legacy `MetaData.bind`  
  - Use of models inheriting from `declarative_base()`  
  - Raw SQL executed via `engine.execute()`  
- **Data Models:**  
  - Python classes inheriting from SQLAlchemy's `declarative_base()`  
  - Columns using standard datatypes (e.g., `String`, `Integer`)  
- **Behaviours:**  
  - Synchronous ORM sessions  
  - Global session/engine usage  
  - Autocommit patterns are present  
- **Interface Surface:**  
  - Data access via ORM models  
  - Modular access to the DB via session objects  
  - Widespread usage of implicit transactions

## Target State

- **ORM Version:** SQLAlchemy 2.x (e.g., 2.0.30)
- **APIs Used:**  
  - Use of `select()` constructs rather than direct `session.query()`  
  - Explicit connections and sessions (context-managed, i.e., `with Session() as session:`)  
  - No use of deprecated APIs (e.g., `MetaData(bind=...)`, `engine.execute()`)  
  - Full use of 2.x declarative system (Unified model construction, e.g., `Base = declarative_base()`)  
  - Updated SQL execution methods (e.g., session.execute(select(...)))
  - Encourage use of async patterns where applicable (optional)
- **Data Models:**  
  - Classes continue to use `declarative_base()`  
  - Type annotations are optional but encouraged  
- **Behaviours:**  
  - Explicit transaction scoping  
  - No legacy/implicit autocommit  
  - Removal of deprecated imports/syntax  
- **Interface Surface:**  
  - Data access via ORM models (as before)  
  - Modular, context-managed session usage  
  - Explicit transactions

## Compatibility & Breaking Changes

| Breaking Change                               | Description                                                                                                  | Migration Path                                                                                               |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `session.query()` deprecated                  | Cannot use `session.query(User)` in 2.x; must switch to `select(User)` and use `session.execute()`           | Refactor all calls: `session.query(Model)` → `session.execute(select(Model))`                               |
| Removal of `engine.execute()`                 | `engine.execute()` is removed                                                                                | Use `session.execute()` or context-managed connections, e.g., `with engine.connect() as conn: ...`          |
| Autocommit mode removed                      | Implicit autocommit removed; explicit transactions are required                                               | Use explicit `with session.begin():` blocks for transactions                                                |
| `MetaData(bind=engine)` deprecated           | Binding metadata directly to engine is not allowed                                                           | Use `metadata.create_all(engine)` or pass engine explicitly when needed                                     |
| No more implicit transaction/commit          | DDL and DML operations require explicit transactons                                                          | Always call `session.commit()` or use context managers                                                      |
| Changed import paths for declarative base     | Old: `from sqlalchemy.ext.declarative import declarative_base` — New: `from sqlalchemy.orm import declarative_base` | Update imports and ensure base created from `sqlalchemy.orm`                                                |
| Changed query results: Scalar/Rows           | Many query results now return `Result` objects instead of plain lists/objects                                | Use `.scalars()`, `.all()`, and `.one()` methods as appropriate                                             |

## Key Flows (before vs after)

### User Retrieval Example

**Before (SQLAlchemy 1.x):**
```python
session = Session()
user = session.query(User).filter(User.id == user_id).one()
```
**After (SQLAlchemy 2.x):**
```python
from sqlalchemy import select
with Session() as session:
    user = session.execute(
        select(User).filter_by(id=user_id)
    ).scalar_one()
```

---

### Raw SQL Execution Example

**Before:**
```python
result = engine.execute("SELECT * FROM user WHERE id=:id", id=5)
```
**After:**
```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM user WHERE id=:id"), {"id": 5})
```

---

### Transaction/Commit Example

**Before:**
```python
session = Session()
user = User(name="foo")
session.add(user)
session.commit()
```
**After:**
```python
with Session.begin() as session:
    user = User(name="foo")
    session.add(user)
```

## Data Model Changes

- **Tables/Schema:** No changes at the DB schema level are required.
- **ORM Models:** Only import and declaration pattern may change, not field definitions.

**Example Change:**

| From (before)                                                      | To (after)                                       |
|--------------------------------------------------------------------|--------------------------------------------------|
| `from sqlalchemy.ext.declarative import declarative_base`           | `from sqlalchemy.orm import declarative_base`     |

No field/type changes required just for the SQLAlchemy upgrade.

## Configuration Changes

N/A — not applicable to this task