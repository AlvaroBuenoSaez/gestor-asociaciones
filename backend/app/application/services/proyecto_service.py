from typing import List, Optional
from app.domain.models.proyecto import Proyecto, ProyectoCreate, ProyectoUpdate
from app.domain.ports.proyecto_repository import ProyectoRepository

class ProyectoService:
    def __init__(self, proyecto_repository: ProyectoRepository):
        self.proyecto_repository = proyecto_repository

    def create_proyecto(self, proyecto: ProyectoCreate) -> Proyecto:
        return self.proyecto_repository.create(proyecto)

    def get_proyecto(self, proyecto_id: int) -> Optional[Proyecto]:
        return self.proyecto_repository.get_by_id(proyecto_id)

    def list_proyectos_by_association(self, asociacion_id: int) -> List[Proyecto]:
        return self.proyecto_repository.list_by_association(asociacion_id)

    def update_proyecto(self, proyecto_id: int, proyecto_update: ProyectoUpdate) -> Optional[Proyecto]:
        return self.proyecto_repository.update(proyecto_id, proyecto_update)

    def delete_proyecto(self, proyecto_id: int) -> bool:
        return self.proyecto_repository.delete(proyecto_id)
