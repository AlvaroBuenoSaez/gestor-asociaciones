from typing import List, Optional
from app.domain.models.user import User, UserCreate, UserUpdate
from app.domain.ports.user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: UserCreate) -> User:
        # Check if username already exists
        if self.user_repository.get_by_username(user.username):
            raise ValueError(f"Username {user.username} already exists")

        return self.user_repository.create(user)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)

    def list_users_by_association(self, asociacion_id: int) -> List[User]:
        return self.user_repository.list_by_association(asociacion_id)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        return self.user_repository.update(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repository.delete(user_id)
