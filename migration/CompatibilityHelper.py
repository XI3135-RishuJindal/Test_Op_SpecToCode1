from sqlalchemy import create_engine, select, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from typing import Any, Generator

Base = declarative_base()

# Create a factory function for the SQLAlchemy engine
def get_engine(database_url: str) -> Any:
    return create_engine(database_url)

# Define a function to create a database session
def get_session(database_url: str) -> Generator:
    engine = get_engine(database_url)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    
    # Automatic session management with context
    with Session() as session:
        yield session

# Example model illustrating new typing
class MyModel(Base):
    __tablename__ = 'my_model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)

# TODO: Refactor any existing queries to use the new SQLAlchemy 2.x methods
# Replace sessions.query(MyModel).filter(...) with the appropriate select() construct
# e.g., session.execute(select(MyModel).filter(MyModel.id == some_id)).scalars().all()

# TODO: Update all session.commit() usages for context management compliance
# Ensure to commit only when changes have been made in the context

# Example of running a query with the new structure
def get_model_by_id(database_url: str, some_id: int) -> Any:
    with get_session(database_url) as session:
        result = session.execute(select(MyModel).filter(MyModel.id == some_id)).scalars().one_or_none()
        return result

# TODO: Ensure any necessary migrations related to schema changes are accounted for in the database upgrader
# Example data interactions should be reviewed and updated to reflect the 2.x API changes across the application.