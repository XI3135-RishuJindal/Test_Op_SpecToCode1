"""Authentication HTTP adapter (REST endpoints)."""

from flask import Blueprint, Response, jsonify, request
from typing import Tuple

from app.application.auth_service import AuthenticationService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def create_auth_blueprint(auth_service: AuthenticationService) -> Blueprint:
    """Factory that wires the blueprint to a concrete AuthenticationService."""

    @auth_bp.post("/login")
    def login() -> Tuple[Response, int]:
        """Authenticate a user and return a result payload."""
        body = request.get_json(silent=True) or {}
        username: str = body.get("username", "")
        password: str = body.get("password", "")

        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        result = auth_service.authenticate(username, password)
        if not result.success:
            return jsonify({"error": result.error}), 401

        return (
            jsonify(
                {
                    "user_id": result.user_id,
                    "roles": result.roles,
                    "requires_mfa": result.requires_mfa,
                }
            ),
            200,
        )

    return auth_bp
