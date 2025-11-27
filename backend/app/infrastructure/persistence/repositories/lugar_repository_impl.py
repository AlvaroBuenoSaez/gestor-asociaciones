from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.lugar import Lugar, LugarCreate
from app.domain.repositories.lugar_repository import LugarRepository
from app.infrastructure.persistence.models.lugar_sql import LugarModel

class SqlAlchemyLugarRepository(LugarRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, nombre: str, asociacion_id: int) -> Optional[Lugar]:
        db_lugar = self.db.query(LugarModel).filter(
            LugarModel.nombre == nombre,
            LugarModel.asociacion_id == asociacion_id
        ).first()
        if db_lugar:
            return Lugar.model_validate(db_lugar)
        return None

    def search_by_name(self, query: str, asociacion_id: int) -> List[Lugar]:
        db_lugares = self.db.query(LugarModel).filter(
            LugarModel.nombre.ilike(f"%{query}%"),
            LugarModel.asociacion_id == asociacion_id
        ).all()
        return [Lugar.model_validate(l) for l in db_lugares]

    def save(self, lugar: LugarCreate) -> Lugar:
        # Check if exists first to avoid unique constraint error if logic fails elsewhere
        existing = self.find_by_name(lugar.nombre, lugar.asociacion_id)
        if existing:
            return existing

        db_lugar = LugarModel(
            nombre=lugar.nombre,
            direccion=lugar.direccion,
            asociacion_id=lugar.asociacion_id
        )
        self.db.add(db_lugar)
        self.db.commit()
        self.db.refresh(db_lugar)
        return Lugar.model_validate(db_lugar)
