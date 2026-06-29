"""Flask application factory."""

from flask import Flask

from app.adapters.inbound.http_routes import create_auth_routes, health_bp
from app.adapters.outbound.bcrypt_hasher import BcryptPasswordHasher
from app.adapters.outbound.in_memory_user_repo import InMemoryUserRepository
from app.domain.services import (
    AuthenticationService,
    MFAService,
    RoleValidationService,
)


def create_app() -> Flask:
    """Compose the application and return a configured Flask instance."""
    flask_app = Flask(__name__)

    # ------------------------------------------------------------------
    # Outbound adapters (infrastructure)
    # ------------------------------------------------------------------
    user_repo = InMemoryUserRepository()
    password_hasher = BcryptPasswordHasher()

    # ------------------------------------------------------------------
    # Domain services (use-cases)
    # ------------------------------------------------------------------
    auth_service = AuthenticationService(user_repo, password_hasher)
    mfa_service = MFAService(user_repo)
    role_service = RoleValidationService(user_repo)

    # ------------------------------------------------------------------
    # Inbound adapters (HTTP)
    # ------------------------------------------------------------------
    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(
        create_auth_routes(auth_service, mfa_service, role_service)
    )

    return flask_app
