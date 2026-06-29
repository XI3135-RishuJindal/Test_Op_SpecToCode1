"""Flask inbound adapter — health-check and authentication routes."""

from flask import Blueprint, jsonify, request

from app.domain.ports import AuthenticationPort, MFAPort, RoleValidationPort

health_bp = Blueprint("health", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Return service liveness status."""
    return jsonify({"status": "ok", "service": "authentication-service"}), 200


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------


def create_auth_routes(
    auth_service: AuthenticationPort,
    mfa_service: MFAPort,
    role_service: RoleValidationPort,
) -> Blueprint:
    """Wire domain services into the auth blueprint and return it."""

    @auth_bp.route("/login", methods=["POST"])
    def login():
        """Authenticate a user with username and password."""
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

    @auth_bp.route("/mfa/enable", methods=["POST"])
    def enable_mfa():
        """Enable MFA for a user and return the provisioning secret."""
        body = request.get_json(silent=True) or {}
        user_id: str = body.get("user_id", "")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        try:
            secret = mfa_service.enable_mfa(user_id)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 404

        return jsonify({"user_id": user_id, "mfa_secret": secret}), 200

    @auth_bp.route("/mfa/verify", methods=["POST"])
    def verify_mfa():
        """Verify a TOTP token for a user."""
        body = request.get_json(silent=True) or {}
        user_id: str = body.get("user_id", "")
        token: str = body.get("token", "")

        if not user_id or not token:
            return jsonify({"error": "user_id and token are required"}), 400

        valid = mfa_service.verify_totp(user_id, token)
        return jsonify({"valid": valid}), 200

    @auth_bp.route("/roles/check", methods=["POST"])
    def check_role():
        """Check whether a user holds a specific role."""
        body = request.get_json(silent=True) or {}
        user_id: str = body.get("user_id", "")
        role: str = body.get("role", "")

        if not user_id or not role:
            return jsonify({"error": "user_id and role are required"}), 400

        has = role_service.has_role(user_id, role)
        return jsonify({"user_id": user_id, "role": role, "has_role": has}), 200

    return auth_bp
