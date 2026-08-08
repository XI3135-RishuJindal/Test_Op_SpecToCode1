"""Application service: MFA management use-case."""

import secrets

from app.domain.ports import MFAPort, UserRepositoryPort


class MFAService(MFAPort):
    """Handles TOTP-based multi-factor authentication."""

    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self._users = user_repository

    def verify_totp(self, user_id: str, token: str) -> bool:
        """
        Verify a TOTP *token* for *user_id*.

        TODO: integrate a real TOTP library (e.g. pyotp) and compare
              the token against the user's stored secret.
        """
        user = self._users.find_by_id(user_id)
        if user is None or not user.mfa_enabled or user.mfa_secret is None:
            return False
        # Placeholder — replace with: pyotp.TOTP(user.mfa_secret).verify(token)
        return False  # pragma: no cover

    def enable_mfa(self, user_id: str) -> str:
        """
        Enable MFA for *user_id* and return the provisioning secret.

        TODO: generate a real TOTP provisioning URI with pyotp and
              persist the secret on the User entity.
        """
        user = self._users.find_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id!r} not found")

        secret = secrets.token_hex(20)
        user.mfa_enabled = True
        user.mfa_secret = secret
        self._users.save(user)
        # TODO: return pyotp.totp.TOTP(secret).provisioning_uri(user.username)
        return secret
