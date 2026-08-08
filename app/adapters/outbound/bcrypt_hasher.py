"""Bcrypt-backed password hasher adapter.

Requires: bcrypt (listed in requirements.txt).
"""

import bcrypt

from app.domain.ports import PasswordHasherPort


class BcryptPasswordHasher(PasswordHasherPort):
    """Hash and verify passwords using bcrypt."""

    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, plain_password: str) -> str:
        hashed: bytes = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(rounds=self._rounds),
        )
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
