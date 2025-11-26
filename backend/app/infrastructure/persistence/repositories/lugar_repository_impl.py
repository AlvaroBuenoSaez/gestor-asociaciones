from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.lugar import Lugar
from app.domain.repositories.lugar_repository import LugarRepository
from app.infrastructure.persistence.models.lugar_sql import LugarModel

class SqlAlchemyLugarRepository(LugarRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, nombre: str) -> Optional[Lugar]:
        db_lugar = self.db.query(LugarModel).filter(LugarModel.nombre == nombre).first()
        if db_lugar:
            return Lugar.model_validate(db_lugar)
        return None

    def search_by_name(self, query: str) -> List[Lugar]:
        db_lugares = self.db.query(LugarModel).filter(LugarModel.nombre.ilike(f"%{query}%")).all()
        return [Lugar.model_validate(l) for l in db_lugares]

    def save(self, lugar: Lugar) -> Lugar:
        # Check if exists first to avoid unique constraint error if logic fails elsewhere
        existing = self.find_by_name(lugar.nombre)
        if existing:
            return existing

        db_lugar = LugarModel(nombre=lugar.nombre, direccion=lugar.direccion)
        self.db.add(db_lugar)
        self.db.commit()
        self.db.refresh(db_lugar)
        return Lugar.model_validate(db_lugar)
