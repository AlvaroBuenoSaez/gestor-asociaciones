from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.proyecto import Proyecto, ProyectoCreate, ProyectoUpdate

class ProyectoRepository(ABC):
    @abstractmethod
    def get_by_id(self, proyecto_id: int) -> Optional[Proyecto]:
        pass

    @abstractmethod
    def list_by_association(self, asociacion_id: int) -> List[Proyecto]:
        pass

    @abstractmethod
    def create(self, proyecto: ProyectoCreate) -> Proyecto:
        pass

    @abstractmethod
    def update(self, proyecto_id: int, proyecto: ProyectoUpdate) -> Optional[Proyecto]:
        pass

    @abstractmethod
    def delete(self, proyecto_id: int) -> bool:
        pass
