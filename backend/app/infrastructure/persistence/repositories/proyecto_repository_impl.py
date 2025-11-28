from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.ports.proyecto_repository import ProyectoRepository
from app.domain.models.proyecto import Proyecto, ProyectoCreate, ProyectoUpdate
from app.infrastructure.persistence.models.proyecto_sql import ProyectoModel

class SqlAlchemyProyectoRepository(ProyectoRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, proyecto_id: int) -> Optional[Proyecto]:
        db_proyecto = self.db.query(ProyectoModel).filter(ProyectoModel.id == proyecto_id).first()
        if db_proyecto:
            return Proyecto.model_validate(db_proyecto)
        return None

    def list_by_association(self, asociacion_id: int) -> List[Proyecto]:
        proyectos = self.db.query(ProyectoModel).filter(ProyectoModel.asociacion_id == asociacion_id).order_by(ProyectoModel.fecha_inicio.desc()).all()
        return [Proyecto.model_validate(p) for p in proyectos]

    def create(self, proyecto: ProyectoCreate) -> Proyecto:
        db_proyecto = ProyectoModel(**proyecto.model_dump())
        self.db.add(db_proyecto)
        self.db.commit()
        self.db.refresh(db_proyecto)
        return Proyecto.model_validate(db_proyecto)

    def update(self, proyecto_id: int, proyecto_update: ProyectoUpdate) -> Optional[Proyecto]:
        db_proyecto = self.db.query(ProyectoModel).filter(ProyectoModel.id == proyecto_id).first()
        if not db_proyecto:
            return None

        update_data = proyecto_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_proyecto, key, value)

        self.db.commit()
        self.db.refresh(db_proyecto)
        return Proyecto.model_validate(db_proyecto)

    def delete(self, proyecto_id: int) -> bool:
        db_proyecto = self.db.query(ProyectoModel).filter(ProyectoModel.id == proyecto_id).first()
        if db_proyecto:
            self.db.delete(db_proyecto)
            self.db.commit()
            return True
        return False
