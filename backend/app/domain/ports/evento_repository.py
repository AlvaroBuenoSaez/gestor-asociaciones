from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.evento import Evento, EventoCreate, EventoUpdate

class EventoRepository(ABC):
    @abstractmethod
    def get_by_id(self, evento_id: int) -> Optional[Evento]:
        pass

    @abstractmethod
    def list_by_association(self, asociacion_id: int) -> List[Evento]:
        pass

    @abstractmethod
    def create(self, evento: EventoCreate) -> Evento:
        pass

    @abstractmethod
    def update(self, evento_id: int, evento: EventoUpdate) -> Optional[Evento]:
        pass

    @abstractmethod
    def delete(self, evento_id: int) -> bool:
        pass
