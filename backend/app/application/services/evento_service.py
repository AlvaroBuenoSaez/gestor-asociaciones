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
            # Create LugarCreate object or similar, but Lugar domain model expects id.
            # We should probably use a specific method in repository or pass a dict/DTO.
            # For now, let's assume repository.save takes a Lugar-like object or we construct one.
            # Since Lugar domain model has id (int), we can't instantiate it easily without ID.
            # But wait, LugarCreate exists in domain/models/lugar.py? Let's check.
            from app.domain.models.lugar import LugarCreate
            lugar_create = LugarCreate(
                nombre=evento.lugar_nombre,
                direccion=evento.lugar_direccion,
                asociacion_id=evento.asociacion_id
            )
            self.lugar_repository.save(lugar_create)
        return self.evento_repository.create(evento)

    def get_evento(self, evento_id: int) -> Optional[Evento]:
        return self.evento_repository.get_by_id(evento_id)

    def list_eventos_by_association(self, asociacion_id: int) -> List[Evento]:
        return self.evento_repository.list_by_association(asociacion_id)

    def update_evento(self, evento_id: int, evento_update: EventoUpdate) -> Optional[Evento]:
        # We need asociacion_id to save the place. EventoUpdate might not have it.
        # We should fetch the event first to get asociacion_id if needed, or just pass what we have.
        # But EventoUpdate doesn't have asociacion_id usually.
        # Let's fetch the existing event.
        existing_evento = self.evento_repository.get_by_id(evento_id)
        if existing_evento and self.lugar_repository and evento_update.lugar_nombre and evento_update.lugar_direccion:
             from app.domain.models.lugar import LugarCreate
             lugar_create = LugarCreate(
                nombre=evento_update.lugar_nombre,
                direccion=evento_update.lugar_direccion,
                asociacion_id=existing_evento.asociacion_id
            )
             self.lugar_repository.save(lugar_create)
        return self.evento_repository.update(evento_id, evento_update)

    def delete_evento(self, evento_id: int) -> bool:
        return self.evento_repository.delete(evento_id)
