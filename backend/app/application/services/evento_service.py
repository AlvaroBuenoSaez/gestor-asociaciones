from typing import List, Optional
from app.domain.models.evento import Evento, EventoCreate, EventoUpdate
from app.domain.ports.evento_repository import EventoRepository
from app.domain.repositories.lugar_repository import LugarRepository
from app.domain.models.lugar import Lugar

class EventoService:
    def __init__(self, evento_repository: EventoRepository, lugar_repository: LugarRepository = None):
        self.evento_repository = evento_repository
        self.lugar_repository = lugar_repository

    def create_evento(self, evento: EventoCreate) -> Evento:
        if self.lugar_repository and evento.lugar_nombre and evento.lugar_direccion:
            self.lugar_repository.save(Lugar(nombre=evento.lugar_nombre, direccion=evento.lugar_direccion))
        return self.evento_repository.create(evento)

    def get_evento(self, evento_id: int) -> Optional[Evento]:
        return self.evento_repository.get_by_id(evento_id)

    def list_eventos_by_association(self, asociacion_id: int) -> List[Evento]:
        return self.evento_repository.list_by_association(asociacion_id)

    def update_evento(self, evento_id: int, evento_update: EventoUpdate) -> Optional[Evento]:
        if self.lugar_repository and evento_update.lugar_nombre and evento_update.lugar_direccion:
            self.lugar_repository.save(Lugar(nombre=evento_update.lugar_nombre, direccion=evento_update.lugar_direccion))
        return self.evento_repository.update(evento_id, evento_update)

    def delete_evento(self, evento_id: int) -> bool:
        return self.evento_repository.delete(evento_id)
