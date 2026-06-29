"""Shared pytest fixtures."""

import pytest

from app.factory import create_app


@pytest.fixture()
def app():
    """Create a test application with a fast bcrypt cost factor."""
    application = create_app({"TESTING": True, "BCRYPT_ROUNDS": 4})
    yield application


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()
