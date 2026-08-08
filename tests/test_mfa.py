"""Tests for MFA endpoints (/auth/mfa/enable, /auth/mfa/verify)."""

import json

import pytest

from app.adapters.outbound.bcrypt_hasher import BcryptPasswordHasher
from app.adapters.outbound.in_memory_user_repo import InMemoryUserRepository
from app.domain.models import User
from app.domain.services import AuthenticationService, MFAService, RoleValidationService
from app.adapters.inbound.http_routes import create_auth_routes, health_bp
from flask import Flask


@pytest.fixture()
def mfa_client():
    """Isolated Flask test client with a single user for MFA tests."""
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher(rounds=4)
    repo.save(
        User(
            user_id="u-mfa",
            username="bob",
            hashed_password=hasher.hash("pass"),
            roles=["user"],
        )
    )

    auth_svc = AuthenticationService(repo, hasher)
    mfa_svc = MFAService(repo)
    role_svc = RoleValidationService(repo)

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(create_auth_routes(auth_svc, mfa_svc, role_svc))

    yield flask_app.test_client()


class TestMFAEnable:
    def test_enable_missing_user_id_returns_400(self, mfa_client):
        response = mfa_client.post("/auth/mfa/enable", json={})
        assert response.status_code == 400

    def test_enable_unknown_user_returns_404(self, mfa_client):
        response = mfa_client.post("/auth/mfa/enable", json={"user_id": "ghost"})
        assert response.status_code == 404

    def test_enable_known_user_returns_200(self, mfa_client):
        response = mfa_client.post("/auth/mfa/enable", json={"user_id": "u-mfa"})
        assert response.status_code == 200

    def test_enable_returns_mfa_secret(self, mfa_client):
        response = mfa_client.post("/auth/mfa/enable", json={"user_id": "u-mfa"})
        data = json.loads(response.data)
        assert "mfa_secret" in data
        assert len(data["mfa_secret"]) > 0


class TestMFAVerify:
    def test_verify_missing_fields_returns_400(self, mfa_client):
        response = mfa_client.post("/auth/mfa/verify", json={"user_id": "u-mfa"})
        assert response.status_code == 400

    def test_verify_invalid_token_returns_valid_false(self, mfa_client):
        # Enable MFA first
        mfa_client.post("/auth/mfa/enable", json={"user_id": "u-mfa"})
        response = mfa_client.post(
            "/auth/mfa/verify", json={"user_id": "u-mfa", "token": "000000"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["valid"] is False
