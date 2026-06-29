"""Tests for role validation endpoint (/auth/roles/check)."""

import json

import pytest

from app.adapters.outbound.bcrypt_hasher import BcryptPasswordHasher
from app.adapters.outbound.in_memory_user_repo import InMemoryUserRepository
from app.domain.models import User
from app.domain.services import AuthenticationService, MFAService, RoleValidationService
from app.adapters.inbound.http_routes import create_auth_routes, health_bp
from flask import Flask


@pytest.fixture()
def role_client():
    """Isolated Flask test client for role-check tests."""
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher(rounds=4)
    repo.save(
        User(
            user_id="u-role",
            username="carol",
            hashed_password=hasher.hash("pass"),
            roles=["user", "editor"],
        )
    )

    auth_svc = AuthenticationService(repo, hasher)
    mfa_svc = MFAService(repo)
    role_svc = RoleValidationService(repo)

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(create_auth_routes(auth_svc, mfa_svc, role_svc))

    yield flask_app.test_client()


class TestRoleCheck:
    def test_missing_fields_returns_400(self, role_client):
        response = role_client.post("/auth/roles/check", json={"user_id": "u-role"})
        assert response.status_code == 400

    def test_user_has_assigned_role(self, role_client):
        response = role_client.post(
            "/auth/roles/check", json={"user_id": "u-role", "role": "editor"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["has_role"] is True

    def test_user_does_not_have_unassigned_role(self, role_client):
        response = role_client.post(
            "/auth/roles/check", json={"user_id": "u-role", "role": "admin"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["has_role"] is False

    def test_unknown_user_has_no_role(self, role_client):
        response = role_client.post(
            "/auth/roles/check", json={"user_id": "ghost", "role": "user"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["has_role"] is False
