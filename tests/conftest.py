"""Shared pytest fixtures."""

import pytest

from app.factory import create_app


@pytest.fixture()
def app():
    """Create a Flask test application instance."""
    flask_app = create_app()
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()
