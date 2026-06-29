"""Tests for the InMemorySecurityAdapter (JWT + API key)."""
from __future__ import annotations

from datetime import timedelta

import pytest

from src.adapters.in_memory_security import InMemorySecurityAdapter
from src.domain.security import ApiKey
from passlib.context import CryptContext

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = "test-secret"
JWT_ALGORITHM = "HS256"


@pytest.fixture()
def adapter() -> InMemorySecurityAdapter:
    return InMemorySecurityAdapter(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)


@pytest.mark.asyncio
class TestJwtValidation:
    async def test_valid_token_returns_claims(self, adapter: InMemorySecurityAdapter) -> None:
        token = adapter.create_jwt(subject="user-1", scopes=["read"])
        claims = await adapter.validate_jwt(token)
        assert claims is not None
        assert claims.subject == "user-1"
        assert "read" in claims.scopes

    async def test_expired_token_returns_none(self, adapter: InMemorySecurityAdapter) -> None:
        token = adapter.create_jwt(subject="user-1", expires_in=timedelta(seconds=-1))
        claims = await adapter.validate_jwt(token)
        # jose raises on expired tokens, so None is expected
        assert claims is None

    async def test_invalid_token_returns_none(self, adapter: InMemorySecurityAdapter) -> None:
        claims = await adapter.validate_jwt("not.a.valid.token")
        assert claims is None


@pytest.mark.asyncio
class TestApiKeyValidation:
    async def test_valid_key_returns_api_key(self, adapter: InMemorySecurityAdapter) -> None:
        raw_key = "super-secret-key"
        api_key = ApiKey(
            key_id="k-1",
            hashed_key=_pwd_ctx.hash(raw_key),
            consumer_id="consumer-1",
        )
        await adapter.store_api_key(api_key)
        result = await adapter.validate_api_key(raw_key)
        assert result is not None
        assert result.key_id == "k-1"

    async def test_invalid_key_returns_none(self, adapter: InMemorySecurityAdapter) -> None:
        result = await adapter.validate_api_key("wrong-key")
        assert result is None

    async def test_revoke_key(self, adapter: InMemorySecurityAdapter) -> None:
        raw_key = "revoke-me"
        api_key = ApiKey(
            key_id="k-2",
            hashed_key=_pwd_ctx.hash(raw_key),
            consumer_id="consumer-2",
        )
        await adapter.store_api_key(api_key)
        revoked = await adapter.revoke_api_key("k-2")
        assert revoked is True
        result = await adapter.validate_api_key(raw_key)
        assert result is None
