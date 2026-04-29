# SQLAlchemy 2.x Upgrade SPEC Document

## Current State
- **Interfaces**: The existing codebase primarily employs SQLAlchemy version 1.x interfaces, including session management (e.g., `Session()`, `session.query()`) and ORM (Object Relational Mapping) features (e.g., `declarative_base()`, `relationship()`).
- **APIs**: The code utilizes APIs such as `session.commit()`, `session.rollback()`, and the use of raw SQL execution via `session.execute()`.
- **Data Models**: The data models are defined using `Base` class from SQLAlchemy; relationships and types are defined following 1.x conventions.
- **Key Behaviours**: Key behaviours include lazy loading, eager loading, and data transaction handling through session lifecycle management.

## Target State
- **Interfaces**: Transition to SQLAlchemy 2.x requires usage of the new `select` construct instead of `session.query()` for querying, with updated methods like `Session.begin()` for transaction management.
- **APIs**: The `session.commit()` will now require context management (e.g., `with Session() as session:`) to handle transactions, enhancing safety and readability.
- **Data Models**: Data models will still utilize `declarative_base()`, but may need adjustments to relationships and loading strategies to conform to the new ORM behavior in 2.x.
- **Key Behaviours**: Support for asynchronous database operations and new approaches for eager/lazy loading will be incorporated.

## Compatibility & Breaking Changes
1. **Querying**:  
   - **Breaking Change**: Use of `session.query()` will lead to errors.  
   - **Migration Path**: Replace `session.query(MyModel)` with `select(MyModel)` and use `session.execute()` or `session.scalars()` to execute queries.

2. **Transaction Management**:  
   - **Breaking Change**: Direct usage of `Session.begin()` and `session.commit()` without context management will fail.  
   - **Migration Path**: Change transaction management to `with Session() as session:` and place commit within the context.

3. **Eager Loading**:  
   - **Breaking Change**: Existing eager loading techniques using `joinedload()` may be affected by deprecation of certain patterns.  
   - **Migration Path**: Update eager loading syntax to use the new `select()` and `load()` methods in the context of the updated ORM.

## Key Flows (before vs after)
1. **Querying Data**  
   - **Before**:  
     ```python
     session = Session()
     results = session.query(MyModel).filter(MyModel.id == 1).one()
     ```
   - **After**:  
     ```python
     with Session() as session:
         stmt = select(MyModel).where(MyModel.id == 1)
         results = session.execute(stmt).scalars().one()
     ```

2. **Handling Transactions**  
   - **Before**:  
     ```python
     session = Session()
     session.add(new_object)
     session.commit()
     session.close()
     ```
   - **After**:  
     ```python
     with Session() as session:
         session.add(new_object)
         session.commit()
     ```

## Data Model Changes
- **Table/Schema Updates**: N/A — No schema changes have been identified; only implementation logic changes to support SQLAlchemy 2.x's new features.

## Configuration Changes
- **N/A**: No changes to environment variables, feature flags, or configuration files are necessary for upgrading SQLAlchemy to 2.x.