"""Domain ports (interfaces) — inbound and outbound."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models import AuthResult, User


# ---------------------------------------------------------------------------
# Inbound ports (use-case interfaces driven by the outside world)
# ---------------------------------------------------------------------------


class AuthenticationPort(ABC):
    """Primary port: authenticate a user with username + password."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> AuthResult:
        """Validate credentials and return an AuthResult."""
        ...


class MFAPort(ABC):
    """Primary port: manage and verify multi-factor authentication."""

    @abstractmethod
    def verify_totp(self, user_id: str, token: str) -> bool:
        """Return True when the TOTP token is valid for the given user."""
        ...

    @abstractmethod
    def enable_mfa(self, user_id: str) -> str:
        """Enable MFA for a user and return the provisioning URI / secret."""
        ...


class RoleValidationPort(ABC):
    """Primary port: validate that a user holds a required role."""

    @abstractmethod
    def has_role(self, user_id: str, role: str) -> bool:
        """Return True when the user holds the specified role."""
        ...


# ---------------------------------------------------------------------------
# Outbound ports (interfaces implemented by infrastructure adapters)
# ---------------------------------------------------------------------------


class UserRepositoryPort(ABC):
    """Secondary port: persistence operations for User entities."""

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Return the User with the given username, or None."""
        ...

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Return the User with the given ID, or None."""
        ...

    @abstractmethod
    def save(self, user: User) -> None:
        """Persist (create or update) a User entity."""
        ...


class PasswordHasherPort(ABC):
    """Secondary port: password hashing and verification."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Return the hashed representation of *plain_password*."""
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Return True when *plain_password* matches *hashed_password*."""
        ...
