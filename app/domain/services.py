"""Domain services — core business logic, framework-agnostic."""

from app.domain.models import AuthResult
from app.domain.ports import (
    AuthenticationPort,
    MFAPort,
    PasswordHasherPort,
    RoleValidationPort,
    UserRepositoryPort,
)


class AuthenticationService(AuthenticationPort):
    """Authenticate users against stored credentials."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def authenticate(self, username: str, password: str) -> AuthResult:
        user = self._user_repo.find_by_username(username)
        if user is None:
            return AuthResult(success=False, error="Invalid credentials")

        if not self._password_hasher.verify(password, user.hashed_password):
            return AuthResult(success=False, error="Invalid credentials")

        return AuthResult(
            success=True,
            user_id=user.user_id,
            roles=user.roles,
            requires_mfa=user.mfa_enabled,
        )


class MFAService(MFAPort):
    """Manage and verify TOTP-based multi-factor authentication."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def verify_totp(self, user_id: str, token: str) -> bool:
        """Verify a TOTP token for the given user.

        TODO: integrate a real TOTP library (e.g. pyotp) here.
        """
        user = self._user_repo.find_by_id(user_id)
        if user is None or not user.mfa_enabled or user.mfa_secret is None:
            return False
        # TODO: replace stub with pyotp.TOTP(user.mfa_secret).verify(token)
        return False

    def enable_mfa(self, user_id: str) -> str:
        """Enable MFA for a user and return the provisioning URI.

        TODO: generate a real TOTP secret and provisioning URI.
        """
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id!r} not found")
        # TODO: generate secret with pyotp.random_base32()
        secret = "JBSWY3DPEHPK3PXP"  # placeholder
        user.mfa_secret = secret
        user.mfa_enabled = True
        self._user_repo.save(user)
        return secret


class RoleValidationService(RoleValidationPort):
    """Validate user roles."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def has_role(self, user_id: str, role: str) -> bool:
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            return False
        return role in user.roles
