from typing import List, Optional
from app.domain.models.evento import Evento, EventoCreate, EventoUpdate
from app.domain.ports.evento_repository import EventoRepository

class EventoService:
    def __init__(self, evento_repository: EventoRepository):
        self.evento_repository = evento_repository

    def create_evento(self, evento: EventoCreate) -> Evento:
        return self.evento_repository.create(evento)

    def get_evento(self, evento_id: int) -> Optional[Evento]:
        return self.evento_repository.get_by_id(evento_id)

    def list_eventos_by_association(self, asociacion_id: int) -> List[Evento]:
        return self.evento_repository.list_by_association(asociacion_id)

    def update_evento(self, evento_id: int, evento_update: EventoUpdate) -> Optional[Evento]:
        return self.evento_repository.update(evento_id, evento_update)

    def delete_evento(self, evento_id: int) -> bool:
        return self.evento_repository.delete(evento_id)
