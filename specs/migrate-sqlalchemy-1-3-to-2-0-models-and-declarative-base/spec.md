# Spec: Migrate SQLAlchemy 1.3 to 2.0 — Models and Declarative Base

## Summary

This spec covers the migration of SQLAlchemy from version 1.3 to version 2.0, scoped specifically to the ORM model definitions and declarative base configuration. The upgrade replaces the legacy `declarative_base()` factory pattern with the new `DeclarativeBase` class-based approach, updates model column declarations to use the 2.0-style `mapped_column()` and `Mapped` type annotations, and removes or replaces all 1.x-only APIs that are absent from SQLAlchemy 2.0. The expected outcome is a codebase that runs cleanly under SQLAlchemy 2.0 with no legacy shim dependencies, passing all existing data-layer tests.

---

## Motivation

- **EOL / Compatibility:** SQLAlchemy 1.3 reached end-of-life and no longer receives bug fixes or security patches. SQLAlchemy 1.4 served as a transitional release; SQLAlchemy 2.0 is the current stable major version.
- **Security:** Unpatched versions accumulate CVEs over time. Remaining on 1.3 blocks the ability to apply upstream security fixes.
- **Upgrade Urgency:** Rated **medium** — the project is not in immediate crisis, but continued delay increases migration complexity as the gap between installed and current versions widens.
- **Technical Debt:** The 1.3 declarative API (`declarative_base()`, untyped `Column()` declarations, implicit autoflush/autocommit behaviours) is incompatible with SQLAlchemy 2.0's strict typing model and new session semantics. Leaving these patterns in place blocks adoption of Python type-checking tooling (mypy, pyright) against ORM models.
- **Ecosystem Alignment:** Libraries that depend on SQLAlchemy (e.g., Alembic, FastAPI integrations, async drivers) are increasingly dropping 1.x support in their own current releases.

---

## Current State

The following describes the existing patterns affected by this migration. Specific identifiers are noted where inferable from standard SQLAlchemy 1.3 usage; project-specific names are marked **TODO** where source context was not provided.

### Declarative Base
- A module-level `Base` object is created via `declarative_base()` from `sqlalchemy.ext.declarative`.
- All ORM model classes inherit from this `Base`.

### Model Column Declarations
- Columns are declared using `Column(Type, ...)` directly on model classes without `Mapped` type annotations.
- Relationship declarations use `relationship()` without `Mapped` generic typing.
- Primary keys, nullable constraints, defaults, and foreign keys are expressed as positional/keyword arguments to `Column()`.

### Session Configuration
- Sessions are created via `sessionmaker` bound to an engine.
- `Session.execute()` calls may use string SQL or legacy `Query` API (`session.query(Model)`).
- `autocommit` and `autoflush` behaviours rely on 1.x defaults.

### Key Identifiers (TODO — confirm against actual source)
| Identifier | Type | Location |
|---|---|---|
| `Base` | Declarative base instance | TODO |
| Model classes (e.g., `User`, `Order`, …) | ORM models | TODO |
| `Column` imports | `sqlalchemy.Column` | TODO |
| `relationship()` calls | `sqlalchemy.orm.relationship` | TODO |
| `sessionmaker` configuration | TODO | TODO |

---

## Proposed Changes

### Overview

For each affected component, the table below describes the before state (SQLAlchemy 1.3), the after state (SQLAlchemy 2.0), and whether the change is breaking to callers outside the data layer.

| Component | Before (1.3) | After (2.0) | Breaking? |
|---|---|---|---|
| Declarative base creation | `Base = declarative_base()` from `sqlalchemy.ext.declarative` | `class Base(DeclarativeBase): pass` from `sqlalchemy.orm` | Y — all model class hierarchies must re-inherit |
| Column declaration style | `column_name = Column(Type, ...)` | `column_name: Mapped[type] = mapped_column(...)` | Y — attribute access semantics change under strict typing |
| Relationship declaration style | `rel = relationship("Model")` | `rel: Mapped[List["Model"]] = relationship(...)` | N — runtime behaviour preserved; typing improves |
| Import source for `declarative_base` | `sqlalchemy.ext.declarative` | Removed in 2.0; replaced by `sqlalchemy.orm.DeclarativeBase` | Y — import paths must change |
| `Query` API (`session.query()`) | Supported natively | Legacy; removed from 2.0 core (available via `sqlalchemy.orm.Query` shim in 2.0 with warning) | Y — callers using `session.query()` must migrate to `select()` statements |
| `Boolean` / `String` column without explicit length | Accepted silently | May raise or warn depending on dialect | N (runtime), Y (strict mode) |
| `__tablename__` and `__table_args__` | Unchanged | Unchanged | N |
| Metadata access via `Base.metadata` | `Base.metadata` | `Base.metadata` (same attribute, different base class) | N |
| `autocommit=True` on Session | Supported | Removed | Y — callers relying on autocommit must use explicit `begin()` |

### Specific Changes

1. **Declarative Base:** Replace the `declarative_base()` call with a `DeclarativeBase` subclass. All model classes that currently inherit from the old `Base` must be updated to inherit from the new `Base`.

2. **Column Declarations:** Replace bare `Column(...)` assignments with `Mapped[<type>]`-annotated `mapped_column(...)` declarations on all model classes. Optional columns must use `Mapped[Optional[<type>]]`.

3. **Relationship Declarations:** Add `Mapped` generic annotations to all `relationship()` fields. One-to-many relationships use `Mapped[List["TargetModel"]]`; many-to-one use `Mapped["TargetModel"]`; optional use `Mapped[Optional["TargetModel"]]`.

4. **Import Cleanup:** Remove all imports from `sqlalchemy.ext.declarative`. Consolidate ORM imports to `sqlalchemy.orm`.

5. **Legacy Query Removal:** Any use of `session.query(Model)` must be replaced with `select(Model)` executed via `session.execute()`. This is scoped to query sites that originate from or are tightly coupled to model definitions; broader query migration is **out of scope** for this spec unless co-located with model files.

6. **`autocommit` Session Flag:** Remove `autocommit=True` from any `sessionmaker` calls. Replace with explicit transaction management.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `declarative_base()` removed | All model files that call this function will fail to import | Replace with `class Base(DeclarativeBase): pass`; update all model inheritance |
| `sqlalchemy.ext.declarative` import path removed | ImportError at startup | Change import to `from sqlalchemy.orm import DeclarativeBase` |
| Untyped `Column()` declarations | Not a hard runtime error in 2.0 but triggers deprecation warnings; incompatible with `mapped_column` style on same class | Migrate all columns on a given model atomically to `mapped_column` + `Mapped` |
| `session.query()` API | Emits `LegacyAPIWarning` in 2.0; targeted for removal in future | Replace with `select()` + `session.execute()` |
| `autocommit=True` on Session | Raises error in 2.0 | Remove flag; wrap operations in explicit `with session.begin():` blocks |
| `relationship()` without `Mapped` annotation | Works at runtime but breaks static type checking | Add `Mapped[...]` annotations; no runtime behaviour change expected |
| `Column` with `Integer` primary key and no `autoincrement` hint | Behaviour unchanged but explicit annotation required for type safety | Add `Mapped[int]` with `mapped_column(primary_key=True)` |
| Mixed 1.x / 2.0 column styles on same model | Not supported; will raise `InvalidRequestError` | Migrate all columns on each model in a single pass — no partial migration per model |

---

## Acceptance Criteria

1. **Given** the application dependencies are updated to SQLAlchemy 2.0, **when** the application process starts, **then** no `LegacyAPIWarning` or `MovedIn20Warning` warnings are emitted from any model or declarative base module.

2. **Given** the migrated codebase, **when** a static type checker (mypy or pyright) is run against all model files, **then** no type errors are reported that originate from ORM column or relationship declarations.

3. **Given** the updated `Base` class, **when** `Base.metadata.create_all(engine)` is called against a fresh in-memory SQLite database, **then** all tables are created without error and the resulting schema matches the schema produced by the 1.3 version of the same models.

4. **Given** a model with a `Mapped` primary key column, **when** a new instance is inserted and the session is committed, **then** the primary key attribute is populated on the instance without requiring an explicit refresh call.

5. **Given** a model with a `relationship()` declaration annotated with `Mapped[List[...]]`, **when** the related collection is accessed after a query, **then** the collection is returned as the correct Python type and no `SAWarning` is emitted.

6. **Given** any code path that previously used `session.query(Model)`, **when** that code path is executed after migration, **then** it uses `select(Model)` with `session.execute()` and returns equivalent results with no `LegacyAPIWarning`.

7. **Given** the full test suite, **when** it is executed against SQLAlchemy 2.0, **then** all tests that passed under SQLAlchemy 1.3 continue to pass (zero regression).

8. **Given** a `sessionmaker` configuration, **when** the configuration is inspected, **then** no `autocommit=True` flag is present and all transactions are managed explicitly.

9. **Given** the migrated model files, **when** they are imported, **then** no imports from `sqlalchemy.ext.declarative` are present anywhere in the model or base modules.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What are the exact names and locations of all model classes and the `Base` definition in the project? | TODO | TODO |
| 2 | Are there any models using SQLAlchemy's `concrete` or `joined` table inheritance that require special handling in 2.0? | TODO | TODO |
| 3 | Are there any models using `@declared_attr` that need to be verified for 2.0 compatibility? | TODO | TODO |
| 4 | Does the project use Alembic for migrations? If so, does the Alembic version in use support SQLAlchemy 2.0, and does `env.py` need updating? | TODO | TODO |
| 5 | Are there any async session usages (`AsyncSession`) that interact with these models and require separate migration steps? | TODO | TODO |
| 6 | Is the `session.query()` API used outside of model-adjacent files (e.g., in service or repository layers)? If so, is that broader migration in scope? | TODO | TODO |
| 7 | Are there custom `TypeDecorator` or `UserDefinedType` subclasses attached to model columns that need 2.0 compatibility review? | TODO | TODO |
| 8 | What is the target Python version? SQLAlchemy 2.0 requires Python 3.7+; `Mapped` with PEP 604 union syntax (`X \| None`) requires Python 3.10+. | TODO | TODO |