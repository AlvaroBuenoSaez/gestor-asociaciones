from typing import List, Optional
from app.domain.models.socia import Socia, SociaCreate, SociaUpdate
from app.domain.ports.socia_repository import SociaRepository

class SociaService:
    def __init__(self, socia_repository: SociaRepository):
        self.socia_repository = socia_repository

    def create_socia(self, socia: SociaCreate) -> Socia:
        return self.socia_repository.create(socia)

    def get_socia(self, socia_id: int) -> Optional[Socia]:
        return self.socia_repository.get_by_id(socia_id)

    def list_socias_by_association(self, asociacion_id: int) -> List[Socia]:
        return self.socia_repository.list_by_association(asociacion_id)

    def update_socia(self, socia_id: int, socia_update: SociaUpdate) -> Optional[Socia]:
        return self.socia_repository.update(socia_id, socia_update)

    def delete_socia(self, socia_id: int) -> bool:
        return self.socia_repository.delete(socia_id)
