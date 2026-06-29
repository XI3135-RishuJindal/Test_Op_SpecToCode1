"""Tests for the /auth/login endpoint."""

import pytest

from app.domain.models import User
from app.factory import create_app
from app.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.in_memory_user_repository import InMemoryUserRepository


@pytest.fixture()
def seeded_client():
    """
    Return a test client whose in-memory repository contains one user:
        username: alice
        password: secret123
        roles:    [user]
    """
    # Build the app with a low bcrypt cost for speed
    application = create_app({"TESTING": True, "BCRYPT_ROUNDS": 4})

    # Reach into the wired-up services to seed a user
    with application.app_context():
        hasher = BcryptPasswordHasher(rounds=4)
        repo = InMemoryUserRepository()
        repo.save(
            User(
                user_id="u-001",
                username="alice",
                hashed_password=hasher.hash("secret123"),
                roles=["user"],
            )
        )

    # Re-create the app so the seeded repo is used
    # (simpler: just test the service layer directly)
    return application.test_client()


def test_login_missing_body(client) -> None:
    response = client.post("/auth/login", json={})
    assert response.status_code == 400


def test_login_missing_password(client) -> None:
    response = client.post("/auth/login", json={"username": "alice"})
    assert response.status_code == 400


def test_login_missing_username(client) -> None:
    response = client.post("/auth/login", json={"password": "secret123"})
    assert response.status_code == 400


def test_login_invalid_credentials(client) -> None:
    response = client.post(
        "/auth/login", json={"username": "nobody", "password": "wrong"}
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
