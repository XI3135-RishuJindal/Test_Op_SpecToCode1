from .user import User

class UserService:
    def create_user(self, user_id: int, name: str, email: str) -> User:
        return User(user_id=user_id, name=name, email=email)

    def get_user(self, user_id: int) -> User:
        # Placeholder for actual retrieval logic
        pass
