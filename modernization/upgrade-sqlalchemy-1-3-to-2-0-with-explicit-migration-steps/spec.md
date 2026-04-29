# SPEC: Upgrade SQLAlchemy 1.3 to 2.0

## Current State

### Interfaces & APIs

- **SQLAlchemy Version:** 1.3.x (exact patch may vary)
- **Session Usage:** 
  - Session objects generally constructed using `session = Session()`
  - Calls use implicit I/O (e.g., `session.execute(...)`, `.query(...)`, and `session.commit()`)
- **Queries:** 
  - Use of `session.query(SomeModel).filter_by(...)`
  - Strings passed to `Query.filter()` (e.g., `session.query(User).filter("name = 'foo'")`)
- **Connection Handling:**
  - Engine connects using `engine.connect()` and `engine.execute()` directly
- **ORM Mappings:**
  - Use of classic mapping and/or `declarative_base()`
- **Transaction Handling:**
  - Implicit via session scope; explicit via `session.begin(subtransactions=True)` in some flows

### Data Models

- SQLAlchemy ORM mapping using either classic or declarative base syntax
- Explicit or implicit table definition matching SQLAlchemy 1.3 conventions

### Key Behaviours

- Application runs with old SQLAlchemy 1.3 APIs (synchronous only)
- Reliance on implicit transactional management and context behavior

---

## Target State

### Interfaces & APIs

- **SQLAlchemy Version:** 2.0.x
- **Session Usage:** 
  - Sessions created with explicit context management:  
    ```python
    from sqlalchemy.orm import Session

    with Session(engine) as session:
        ...
    ```
  - No implicit commits outside explicit session blocks
- **Queries:** 
  - Replacement of `session.query()` with SQL 2.0 Core and ORM constructs, e.g.,
    ```python
    session.execute(select(User).where(User.name == "foo"))
    ```
  - Removal of string-based filters and old-style queries
- **Connection Handling:**
  - Direct Engine usage (`engine.execute()`) removed; now through Session or Connectors
  - Use of `engine.begin()`, `with engine.begin() as conn:` for transactional blocks
- **ORM Mappings:**
  - Standardized on `declarative_base()` or `DeclarativeBase` / `Mapped`
- **Transaction Handling:**
  - No support for `subtransactions` or nested transactions as in 1.3
  - Use of explicit scoping with context managers

### Data Models

- ORM Models may use SQLAlchemy 2.0 `Mapped` type hints (optional)
- Table definitions updated as needed for compatibility

### Key Behaviours

- Code uses explicit context blocks for session/transaction management
- All code updated for SQLAlchemy 2.0 deprecations and removals

---

## Compatibility & Breaking Changes

### Breaking Change: Session Usage and Query Syntax

- **Change:** `session.query()` is soft-deprecated; use `session.execute(select(...))` or ORM select constructs.
- **Migration Path:**
  1. Replace all `session.query(Model)` with `session.execute(select(Model))`.
  2. Adapt filters: `.filter_by(name="foo")` becomes `.where(Model.name == "foo")`.

### Breaking Change: Engine Connection & Execution

- **Change:** `engine.execute()` removed
- **Migration Path:**
  1. Use `with engine.connect() as conn:` and `conn.execute(...)`.
  2. For ORM, prefer `session.execute`.

### Breaking Change: Transaction Handling

- **Change:** `subtransactions` and `session.begin(subtransactions=True)` no longer supported.
- **Migration Path:** 
  - Use explicit context-managed transactions (`with session.begin(): ...`).

### Breaking Change: String-Based Filters

- **Change:** Passing strings to `filter()` deprecated/removed.
- **Migration Path:** 
  - Always use SQL expressions: `.filter(User.name == "foo")`.

### Breaking Change: Implicit I/O

- **Change:** Implicit loader/debugging behaviour removed; explicit loading now required in most places.
- **Migration Path:** 
  - Use loader options or explicit execution as per 2.0 documentation.

---

## Key Flows (before vs after)

### Example: Basic Query (Before)

1. Obtain session: `session = Session()`
2. Query: `users = session.query(User).filter_by(active=True).all()`
3. Use results

#### After

1. Obtain session via context manager:
    ```python
    with Session(engine) as session:
        result = session.execute(select(User).where(User.active == True))
        users = result.scalars().all()
    ```

### Example: Transaction Handling

#### Before

```python
session = Session()
session.begin(subtransactions=True)
# do some db work
session.commit()
```

#### After

```python
with Session(engine) as session:
    with session.begin():
        # do some db work
        ...
```

---

## Data Model Changes

- **Optionally**: Add type annotations (`Mapped[]`) and SQLAlchemy 2.x declarative base classes for ORM models
    - e.g.,
      ```python
      from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
      class User(Base):
          id: Mapped[int] = mapped_column(primary_key=True)
      ```
- **Existing classic models** remain compatible with only minor changes; full migration to type-hinted ORM is **optional**.

---

## Configuration Changes

- Update `requirements.txt` or relevant dependency management files:
  - `sqlalchemy>=2.0.0,<2.1.0`
- Environment variables, feature flags, or config files related to SQLAlchemy version or ORM configuration must be updated accordingly if present.
- **If using Alembic:** Ensure Alembic is upgraded for SQLAlchemy 2.0 compatibility.

---

## N/A Sections

- Language/Runtime-specific details: **N/A — not applicable to this task**
- Build Tool-specific steps: **N/A — not applicable to this task**
- Unrelated frameworks/tools: **N/A — not applicable to this task**