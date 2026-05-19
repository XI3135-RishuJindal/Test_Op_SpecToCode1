import pytest
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session, declarative_base
import sys

TARGET_SQLALCHEMY_VERSION_PREFIX = "2."

# Basic model for ORM path
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)

def get_engine():
    # Use in-memory SQLite DB for test
    return create_engine("sqlite:///:memory:")

def test_sqlalchemy_exact_version():
    # Verify SQLAlchemy 2.x is active (not just installed, but loaded)
    assert sqlalchemy.__version__.startswith(TARGET_SQLALCHEMY_VERSION_PREFIX), (
        f"Expected SQLAlchemy version to start with {TARGET_SQLALCHEMY_VERSION_PREFIX}, "
        f"got {sqlalchemy.__version__}"
    )

def test_orm_crud_path_works():
    engine = get_engine()
    Base.metadata.create_all(engine)
    # 2.x requires use of new-style session usage
    with Session(engine) as session:
        user = User(name="Bob")
        session.add(user)
        session.commit()
        stmt = sqlalchemy.select(User).where(User.name == "Bob")
        result = session.execute(stmt).scalar_one()
        assert result.name == "Bob"
        # Update
        result.name = "Alice"
        session.commit()
        stmt2 = sqlalchemy.select(User).where(User.name == "Alice")
        assert session.execute(stmt2).scalar_one().name == "Alice"
        # Delete
        session.delete(result)
        session.commit()
        assert session.execute(sqlalchemy.select(User)).first() is None

def test_core_execution_path_works():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE t (id INTEGER PRIMARY KEY, val TEXT)"))
        conn.execute(text("INSERT INTO t (val) VALUES ('x')"))
        result = conn.execute(text("SELECT val FROM t")).first()
        assert result[0] == 'x'

def test_legacy_deprecated_apis_absent():
    engine = get_engine()
    # Engine.execute is removed in SQLAlchemy 2.x
    with pytest.raises(AttributeError):
        # This should raise, as engine.execute() is removed in 2.x
        engine.execute(text("SELECT 1"))
    # Session.execute supports only SQLAlchemy 2.x API, so check calling with future flag fails
    # (No future flag anymore: in 2.x future=True is default/gone)
    with pytest.raises(TypeError):
        Session(engine, future=True)

def test_new_config_keys_supported():
    # Example: 'engine.echo_pool' is new in 2.0 (https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#engine-echo-pool)
    engine = create_engine("sqlite:///:memory:", echo=True, echo_pool=True)
    # validate database works fine with that flag
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        # No error, configuration accepted

def test_inspect_session_api():
    # Session has new 2.x APIs ("get", etc.), validate availability and usage
    engine = get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(name="Charlie"))
        session.commit()
        obj = session.get(User, 1)
        assert obj is not None
        assert isinstance(obj, User)
        assert obj.name == "Charlie"