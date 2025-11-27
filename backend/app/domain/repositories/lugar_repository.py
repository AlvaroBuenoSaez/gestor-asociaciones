from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.lugar import Lugar, LugarCreate

class LugarRepository(ABC):
    @abstractmethod
    def find_by_name(self, nombre: str, asociacion_id: int) -> Optional[Lugar]:
        pass

    @abstractmethod
    def search_by_name(self, query: str, asociacion_id: int) -> List[Lugar]:
        pass

    @abstractmethod
    def save(self, lugar: LugarCreate) -> Lugar:
        pass
