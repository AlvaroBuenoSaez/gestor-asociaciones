from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.user import User, UserCreate, UserUpdate

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_by_association(self, asociacion_id: int) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> User:
        pass

    @abstractmethod
    def update(self, user_id: int, user: UserUpdate) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass
