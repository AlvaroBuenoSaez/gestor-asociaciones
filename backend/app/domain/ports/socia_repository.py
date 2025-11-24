from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.socia import Socia, SociaCreate, SociaUpdate

class SociaRepository(ABC):
    @abstractmethod
    def get_by_id(self, socia_id: int) -> Optional[Socia]:
        pass

    @abstractmethod
    def list_by_association(self, asociacion_id: int) -> List[Socia]:
        pass

    @abstractmethod
    def create(self, socia: SociaCreate) -> Socia:
        pass

    @abstractmethod
    def update(self, socia_id: int, socia: SociaUpdate) -> Optional[Socia]:
        pass

    @abstractmethod
    def delete(self, socia_id: int) -> bool:
        pass
