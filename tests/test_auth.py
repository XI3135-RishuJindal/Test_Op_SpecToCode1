"""Tests for the /auth/login endpoint."""

import json

import pytest

from app.adapters.outbound.in_memory_user_repo import InMemoryUserRepository
from app.domain.models import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_user(app, user_id: str, username: str, plain_password: str) -> None:
    """Insert a user into the in-memory repo via the app's hasher."""
    # Re-create the hasher to hash the password the same way the app does
    from app.adapters.outbound.bcrypt_hasher import BcryptPasswordHasher

    hasher = BcryptPasswordHasher(rounds=4)  # low rounds for speed in tests
    hashed = hasher.hash(plain_password)
    user = User(user_id=user_id, username=username, hashed_password=hashed, roles=["user"])

    # Access the repo through the app context
    # We rebuild a minimal app with a known repo for isolation
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def seeded_client(app, client):
    """Client backed by an app that has one pre-seeded user."""
    # Patch the app's user repo with a known user
    from app.adapters.outbound.bcrypt_hasher import BcryptPasswordHasher
    from app.adapters.outbound.in_memory_user_repo import InMemoryUserRepository
    from app.domain.models import User
    from app.domain.services import AuthenticationService, MFAService, RoleValidationService
    from app.adapters.inbound.http_routes import create_auth_routes, health_bp
    from flask import Flask

    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher(rounds=4)
    hashed = hasher.hash("correct-password")
    repo.save(User(user_id="u-1", username="alice", hashed_password=hashed, roles=["user", "admin"]))

    auth_svc = AuthenticationService(repo, hasher)
    mfa_svc = MFAService(repo)
    role_svc = RoleValidationService(repo)

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(create_auth_routes(auth_svc, mfa_svc, role_svc))

    yield flask_app.test_client()


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


class TestLoginEndpoint:
    def test_login_missing_body_returns_400(self, client):
        response = client.post("/auth/login", json={})
        assert response.status_code == 400

    def test_login_missing_password_returns_400(self, client):
        response = client.post("/auth/login", json={"username": "alice"})
        assert response.status_code == 400

    def test_login_unknown_user_returns_401(self, client):
        response = client.post(
            "/auth/login", json={"username": "nobody", "password": "x"}
        )
        assert response.status_code == 401

    def test_login_wrong_password_returns_401(self, seeded_client):
        response = seeded_client.post(
            "/auth/login", json={"username": "alice", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_login_correct_credentials_returns_200(self, seeded_client):
        response = seeded_client.post(
            "/auth/login",
            json={"username": "alice", "password": "correct-password"},
        )
        assert response.status_code == 200

    def test_login_response_contains_user_id(self, seeded_client):
        response = seeded_client.post(
            "/auth/login",
            json={"username": "alice", "password": "correct-password"},
        )
        data = json.loads(response.data)
        assert data["user_id"] == "u-1"

    def test_login_response_contains_roles(self, seeded_client):
        response = seeded_client.post(
            "/auth/login",
            json={"username": "alice", "password": "correct-password"},
        )
        data = json.loads(response.data)
        assert "user" in data["roles"]
        assert "admin" in data["roles"]

    def test_login_response_requires_mfa_false_by_default(self, seeded_client):
        response = seeded_client.post(
            "/auth/login",
            json={"username": "alice", "password": "correct-password"},
        )
        data = json.loads(response.data)
        assert data["requires_mfa"] is False
