"""Tests for the AuthenticationService use-case."""

import pytest

from app.application.auth_service import AuthenticationService
from app.domain.models import User
from app.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.in_memory_user_repository import InMemoryUserRepository


@pytest.fixture()
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture()
def hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher(rounds=4)


@pytest.fixture()
def service(repo, hasher) -> AuthenticationService:
    return AuthenticationService(repo, hasher)


@pytest.fixture()
def alice(repo, hasher) -> User:
    user = User(
        user_id="u-001",
        username="alice",
        hashed_password=hasher.hash("secret123"),
        roles=["user"],
    )
    repo.save(user)
    return user


def test_authenticate_valid_credentials(service, alice) -> None:
    result = service.authenticate("alice", "secret123")
    assert result.success is True
    assert result.user_id == "u-001"
    assert "user" in result.roles


def test_authenticate_wrong_password(service, alice) -> None:
    result = service.authenticate("alice", "wrongpassword")
    assert result.success is False
    assert result.error == "Invalid credentials"


def test_authenticate_unknown_user(service) -> None:
    result = service.authenticate("ghost", "anything")
    assert result.success is False
    assert result.error == "Invalid credentials"


def test_authenticate_mfa_flag(repo, hasher, service) -> None:
    user = User(
        user_id="u-002",
        username="bob",
        hashed_password=hasher.hash("pass"),
        roles=["admin"],
        mfa_enabled=True,
    )
    repo.save(user)
    result = service.authenticate("bob", "pass")
    assert result.success is True
    assert result.requires_mfa is True
