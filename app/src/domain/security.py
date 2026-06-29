"""Security domain entities (API keys, JWT claims)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ApiKey:
    """Represents an API key credential.

    Attributes:
        key_id: Unique identifier for the key.
        hashed_key: Bcrypt-hashed value of the raw key.
        consumer_id: Owning consumer / tenant identifier.
        scopes: Allowed permission scopes.
        expires_at: Optional expiry timestamp (UTC).
        enabled: Whether the key is active.
    """

    key_id: str
    hashed_key: str
    consumer_id: str
    scopes: frozenset[str] = field(default_factory=frozenset)
    expires_at: Optional[datetime] = None
    enabled: bool = True

    def is_expired(self) -> bool:
        """Return ``True`` if the key has passed its expiry date."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass(frozen=True)
class JwtClaims:
    """Decoded and validated JWT claims.

    Attributes:
        subject: ``sub`` claim — typically a user or service identifier.
        scopes: Permission scopes extracted from the token.
        expires_at: Token expiry timestamp (UTC).
        issuer: ``iss`` claim.
        extra: Any additional claims present in the token.
    """

    subject: str
    scopes: frozenset[str]
    expires_at: datetime
    issuer: str = ""
    extra: dict = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Return ``True`` if the token has expired."""
        return datetime.utcnow() > self.expires_at
