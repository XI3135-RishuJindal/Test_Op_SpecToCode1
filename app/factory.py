"""Flask application factory."""

import os

from flask import Flask

from app.adapters.auth_routes import create_auth_blueprint
from app.adapters.health import health_bp
from app.application.auth_service import AuthenticationService
from app.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.in_memory_user_repository import InMemoryUserRepository


def create_app(config: dict | None = None) -> Flask:
    """
    Create and configure the Flask application.

    *config* is an optional dict of overrides (useful in tests).
    """
    app = Flask(__name__)

    # ------------------------------------------------------------------ config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["BCRYPT_ROUNDS"] = int(os.getenv("BCRYPT_ROUNDS", "12"))
    app.config["ENV"] = os.getenv("FLASK_ENV", "production")

    if config:
        app.config.update(config)

    # --------------------------------------------------------- dependency wiring
    user_repo = InMemoryUserRepository()
    password_hasher = BcryptPasswordHasher(rounds=app.config["BCRYPT_ROUNDS"])
    auth_service = AuthenticationService(user_repo, password_hasher)

    # ---------------------------------------------------------------- blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(create_auth_blueprint(auth_service))

    return app
