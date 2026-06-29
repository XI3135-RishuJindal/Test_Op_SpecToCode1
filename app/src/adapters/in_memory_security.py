"""In-memory security adapter (for testing; replace with a real store in production)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.domain.security import ApiKey, JwtClaims
from src.ports.outbound import SecurityPort

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InMemorySecurityAdapter(SecurityPort):
    """JWT validation and API-key management backed by in-memory storage.

    .. warning::
        This adapter is intended for development and testing only.
        Use a persistent, distributed store in production.
    """

    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256") -> None:
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._api_keys: dict[str, ApiKey] = {}  # key_id → ApiKey

    # ── API Key ──────────────────────────────────────────────────────────────

    async def validate_api_key(self, raw_key: str) -> Optional[ApiKey]:
        """Return the matching :class:`ApiKey` if *raw_key* is valid."""
        for api_key in self._api_keys.values():
            if _pwd_ctx.verify(raw_key, api_key.hashed_key):
                return api_key
        return None

    async def store_api_key(self, api_key: ApiKey) -> None:
        self._api_keys[api_key.key_id] = api_key

    async def revoke_api_key(self, key_id: str) -> bool:
        if key_id in self._api_keys:
            del self._api_keys[key_id]
            return True
        return False

    # ── JWT ──────────────────────────────────────────────────────────────────

    async def validate_jwt(self, token: str) -> Optional[JwtClaims]:
        """Decode and validate *token*; return ``None`` on any error."""
        try:
            payload = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=[self._jwt_algorithm],
            )
        except JWTError:
            return None

        subject = payload.get("sub", "")
        exp = payload.get("exp")
        if not subject or exp is None:
            return None

        expires_at = datetime.utcfromtimestamp(exp)
        scopes_raw = payload.get("scopes", payload.get("scope", ""))
        scopes: frozenset[str] = (
            frozenset(scopes_raw.split()) if isinstance(scopes_raw, str) else frozenset(scopes_raw)
        )

        extra = {k: v for k, v in payload.items() if k not in {"sub", "exp", "iss", "scopes", "scope"}}

        return JwtClaims(
            subject=subject,
            scopes=scopes,
            expires_at=expires_at,
            issuer=payload.get("iss", ""),
            extra=extra,
        )

    def create_jwt(
        self,
        subject: str,
        scopes: list[str] | None = None,
        expires_in: timedelta | None = None,
    ) -> str:
        """Helper: create a signed JWT (useful in tests and dev tooling)."""
        now = datetime.utcnow()
        exp = now + (expires_in or timedelta(hours=1))
        payload: dict = {
            "sub": subject,
            "iat": now,
            "exp": exp,
            "scopes": " ".join(scopes or []),
        }
        return jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)
