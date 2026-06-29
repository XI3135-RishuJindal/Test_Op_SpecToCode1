"""Application service: role-validation use-case."""

from app.domain.ports import RoleValidationPort, UserRepositoryPort


class RoleValidationService(RoleValidationPort):
    """Checks whether a user holds a required role."""

    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self._users = user_repository

    def has_role(self, user_id: str, role: str) -> bool:
        """Return True when *user_id* holds *role*."""
        user = self._users.find_by_id(user_id)
        if user is None:
            return False
        return role in user.roles
