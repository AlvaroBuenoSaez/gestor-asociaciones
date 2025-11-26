from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.lugar import Lugar

class LugarRepository(ABC):
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[Lugar]:
        pass

    @abstractmethod
    def search_by_name(self, query: str) -> List[Lugar]:
        pass

    @abstractmethod
    def save(self, lugar: Lugar) -> Lugar:
        pass
