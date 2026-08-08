"""In-memory user repository adapter (suitable for testing / local dev)."""

from typing import Dict, Optional

from app.domain.models import User
from app.domain.ports import UserRepositoryPort


class InMemoryUserRepository(UserRepositoryPort):
    """Stores User entities in a plain Python dict."""

    def __init__(self) -> None:
        self._store: Dict[str, User] = {}

    # ------------------------------------------------------------------
    # UserRepositoryPort implementation
    # ------------------------------------------------------------------

    def find_by_username(self, username: str) -> Optional[User]:
        for user in self._store.values():
            if user.username == username:
                return user
        return None

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    def save(self, user: User) -> None:
        self._store[user.user_id] = user
