"""Tests for the RoleValidationService use-case."""

import pytest

from app.application.role_service import RoleValidationService
from app.domain.models import User
from app.infrastructure.in_memory_user_repository import InMemoryUserRepository


@pytest.fixture()
def repo() -> InMemoryUserRepository:
    r = InMemoryUserRepository()
    r.save(User(user_id="u-1", username="alice", hashed_password="x", roles=["admin", "user"]))
    return r


@pytest.fixture()
def service(repo) -> RoleValidationService:
    return RoleValidationService(repo)


def test_has_role_returns_true_for_existing_role(service) -> None:
    assert service.has_role("u-1", "admin") is True


def test_has_role_returns_false_for_missing_role(service) -> None:
    assert service.has_role("u-1", "superuser") is False


def test_has_role_returns_false_for_unknown_user(service) -> None:
    assert service.has_role("unknown", "admin") is False
