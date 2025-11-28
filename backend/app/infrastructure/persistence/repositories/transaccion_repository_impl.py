from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.ports.transaccion_repository import TransaccionRepository
from app.domain.models.transaccion import Transaccion, TransaccionCreate, TransaccionUpdate
from app.infrastructure.persistence.models.transaccion_sql import TransaccionModel

class SqlAlchemyTransaccionRepository(TransaccionRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaccion_id: int) -> Optional[Transaccion]:
        db_transaccion = self.db.query(TransaccionModel).filter(TransaccionModel.id == transaccion_id).first()
        if db_transaccion:
            return Transaccion.model_validate(db_transaccion)
        return None

    def list_by_association(self, asociacion_id: int) -> List[Transaccion]:
        transacciones = self.db.query(TransaccionModel).filter(TransaccionModel.asociacion_id == asociacion_id).order_by(TransaccionModel.fecha_transaccion.desc()).all()
        return [Transaccion.model_validate(t) for t in transacciones]

    def create(self, transaccion: TransaccionCreate) -> Transaccion:
        db_transaccion = TransaccionModel(**transaccion.model_dump())
        self.db.add(db_transaccion)
        self.db.commit()
        self.db.refresh(db_transaccion)
        return Transaccion.model_validate(db_transaccion)

    def update(self, transaccion_id: int, transaccion_update: TransaccionUpdate) -> Optional[Transaccion]:
        db_transaccion = self.db.query(TransaccionModel).filter(TransaccionModel.id == transaccion_id).first()
        if not db_transaccion:
            return None

        update_data = transaccion_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transaccion, key, value)

        self.db.commit()
        self.db.refresh(db_transaccion)
        return Transaccion.model_validate(db_transaccion)

    def delete(self, transaccion_id: int) -> bool:
        db_transaccion = self.db.query(TransaccionModel).filter(TransaccionModel.id == transaccion_id).first()
        if db_transaccion:
            self.db.delete(db_transaccion)
            self.db.commit()
            return True
        return False
