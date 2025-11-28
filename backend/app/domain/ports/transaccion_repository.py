from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.transaccion import Transaccion, TransaccionCreate, TransaccionUpdate

class TransaccionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaccion_id: int) -> Optional[Transaccion]:
        pass

    @abstractmethod
    def list_by_association(self, asociacion_id: int) -> List[Transaccion]:
        pass

    @abstractmethod
    def create(self, transaccion: TransaccionCreate) -> Transaccion:
        pass

    @abstractmethod
    def update(self, transaccion_id: int, transaccion: TransaccionUpdate) -> Optional[Transaccion]:
        pass

    @abstractmethod
    def delete(self, transaccion_id: int) -> bool:
        pass
