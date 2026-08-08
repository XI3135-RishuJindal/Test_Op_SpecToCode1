"""Application service: user authentication use-case."""

from app.domain.models import AuthResult
from app.domain.ports import AuthenticationPort, PasswordHasherPort, UserRepositoryPort


class AuthenticationService(AuthenticationPort):
    """Orchestrates credential validation against the user repository."""

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._users = user_repository
        self._hasher = password_hasher

    def authenticate(self, username: str, password: str) -> AuthResult:
        """Validate *username* / *password* and return an AuthResult."""
        user = self._users.find_by_username(username)
        if user is None:
            return AuthResult(success=False, error="Invalid credentials")

        if not self._hasher.verify(password, user.hashed_password):
            return AuthResult(success=False, error="Invalid credentials")

        return AuthResult(
            success=True,
            user_id=user.user_id,
            roles=user.roles,
            requires_mfa=user.mfa_enabled,
        )
