from typing import List, Optional
from app.domain.models.transaccion import Transaccion, TransaccionCreate, TransaccionUpdate
from app.domain.ports.transaccion_repository import TransaccionRepository

class TransaccionService:
    def __init__(self, transaccion_repository: TransaccionRepository):
        self.transaccion_repository = transaccion_repository

    def create_transaccion(self, transaccion: TransaccionCreate) -> Transaccion:
        return self.transaccion_repository.create(transaccion)

    def get_transaccion(self, transaccion_id: int) -> Optional[Transaccion]:
        return self.transaccion_repository.get_by_id(transaccion_id)

    def list_transacciones_by_association(self, asociacion_id: int) -> List[Transaccion]:
        return self.transaccion_repository.list_by_association(asociacion_id)

    def update_transaccion(self, transaccion_id: int, transaccion_update: TransaccionUpdate) -> Optional[Transaccion]:
        return self.transaccion_repository.update(transaccion_id, transaccion_update)

    def delete_transaccion(self, transaccion_id: int) -> bool:
        return self.transaccion_repository.delete(transaccion_id)
