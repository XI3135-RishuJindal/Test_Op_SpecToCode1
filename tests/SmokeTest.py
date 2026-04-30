import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from myapp.models import MyModel  # Adjust import according to your application structure
from myapp.database import get_database_url  # Function to get your database URL

@pytest.fixture(scope='module')
def db_engine():
    engine = create_engine(get_database_url())
    yield engine
    engine.dispose()

@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    connection.close()

def test_database_connection(db_engine):
    with db_engine.connect() as connection:
        assert connection is not None

def test_query_my_model(db_session):
    # Assuming you have an entry in MyModel to query
    results = db_session.execute(select(MyModel)).scalars().all()
    assert isinstance(results, list)

def test_filter_my_model(db_session):
    # Replace 'some_id' with a valid id in your database for the test
    some_id = 1
    result = db_session.execute(select(MyModel).where(MyModel.id == some_id)).scalars().first()
    assert result is not None
    assert result.id == some_id

def test_insert_my_model(db_session):
    new_instance = MyModel(name='Test Name')  # Adjust fields as necessary
    db_session.add(new_instance)
    db_session.commit()
    
    # Verify that it has been inserted
    result = db_session.execute(select(MyModel).where(MyModel.name == 'Test Name')).scalars().first()
    assert result is not None
    assert result.name == 'Test Name'
    
    # Clean up by deleting the inserted record
    db_session.delete(result)
    db_session.commit()