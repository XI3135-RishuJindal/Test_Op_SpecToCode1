import sys
import importlib
import pytest

import flask
import sqlalchemy

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    SQLAlchemy = None

@pytest.fixture(scope="session")
def app():
    # Import the app following common factory patterns for Flask
    try:
        from app import create_app  # If the app uses a factory
        app = create_app(test_config=True)
    except ImportError:
        from app import app
    yield app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def db(app):
    # Assumes that SQLAlchemy instance is initialized as 'db' in app/__init__.py
    from app import db
    yield db

def test_flask_version():
    # Assert Flask version is 3.x
    assert flask.__version__.startswith("3."), f"Active Flask version is not 3.x: {flask.__version__}"

def test_sqlalchemy_version():
    # Assert SQLAlchemy version is 2.x
    assert sqlalchemy.__version__.startswith("2."), f"Active SQLAlchemy version is not 2.x: {sqlalchemy.__version__}"

def test_critical_path_root(client):
    # Test the root or health endpoint (critical path)
    response = client.get("/")
    assert response.status_code == 200

def test_critical_path_model_create_read(client, db, app):
    # Assumes a model called 'User' exists, and there is a route to create/read user
    with app.app_context():
        # Dynamically import User model
        try:
            from app.models import User
        except ImportError:
            pytest.skip("User model not found; adjust test_critical_path_model_create_read as needed.")

        # Remove all users first
        db.session.query(User).delete()
        db.session.commit()

        # Create user via ORM to ensure SQLAlchemy 2.x API works
        user = User(username="upgrade_test", email="upgrade@example.com")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Check getting the user (SQLAlchemy 2.x: session.get())
        fetched = db.session.get(User, user_id)
        assert fetched is not None
        assert fetched.username == "upgrade_test"

        # Clean up
        db.session.delete(fetched)
        db.session.commit()

def test_no_deprecated_imports():
    # Ensure 'flask.ext.sqlalchemy' is not importable anymore
    with pytest.raises(ImportError):
        importlib.import_module("flask.ext.sqlalchemy")

def test_session_get_used(db, app):
    # Ensure SQLAlchemy 2.x session.get() is usable and .query.get() is gone
    with app.app_context():
        from app.models import User
        # Create a dummy user
        user = User(username="session_get_user", email="session_get@example.com")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # SQLAlchemy 2.x: Use session.get()
        retrieved = db.session.get(User, user_id)
        assert retrieved is not None

        # Ensure .query.get() is not present
        assert not hasattr(User.query, 'get'), (
            "User.query.get() should not exist; legacy API must be removed"
        )

        db.session.delete(retrieved)
        db.session.commit()

def test_flask_request_get_json(client):
    # Ensure that request.get_json() works and request.json is absent
    # We'll need to define a simple test route if not present
    from flask import request, jsonify
    try:
        from app import app as current_app
    except ImportError:
        pytest.skip("Flask app not importable directly.")
    route_url = "/_test_get_json"

    @current_app.route(route_url, methods=["POST"])
    def _test_get_json():
        payload = request.get_json()
        # Confirm that request.json is gone in Flask 3.x
        assert not hasattr(request, 'json'), "request.json must not exist in Flask 3.x"
        return jsonify({"received": payload})

    test_client = current_app.test_client()
    response = test_client.post(route_url, json={"foo": "bar"})
    assert response.status_code == 200
    assert response.get_json()["received"] == {"foo": "bar"}

def test_new_config_keys_load(app):
    # Example: Flask 3 introduced SERVER_NAME as a required config key by default
    # SQLAlchemy 2.x may require or expose new config keys
    # This test checks for at least one known new config key in each
    flask_new_keys = ["ENV", "SERVER_NAME"]
    for key in flask_new_keys:
        assert hasattr(app.config, key), f"Flask config key {key} missing."

    # SQLAlchemy config: check for 2.x engine-style config where appropriate
    sqlalchemy_new_keys = ["SQLALCHEMY_ENGINE_OPTIONS"]
    for key in sqlalchemy_new_keys:
        assert hasattr(app.config, key), f"SQLAlchemy config key {key} missing."

def test_sqlalchemy_future_flag_gone(app):
    # SQLAlchemy 2.x removes 'future=True' config; ensure it's not present
    assert 'SQLALCHEMY_ENGINE_OPTIONS' not in app.config or \
        'future' not in app.config['SQLALCHEMY_ENGINE_OPTIONS'], \
        "'future' option must not be set in SQLALCHEMY_ENGINE_OPTIONS under SQLAlchemy 2.x"