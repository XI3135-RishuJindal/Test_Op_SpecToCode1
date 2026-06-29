"""Domain models for the Authentication Service."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class User:
    """Core user entity."""

    user_id: str
    username: str
    hashed_password: str
    roles: List[str] = field(default_factory=list)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None


@dataclass
class AuthResult:
    """Result returned after an authentication attempt."""

    success: bool
    user_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    requires_mfa: bool = False
    error: Optional[str] = None
