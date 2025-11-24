from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.ports.socia_repository import SociaRepository
from app.domain.models.socia import Socia, SociaCreate, SociaUpdate
from app.infrastructure.persistence.models.socia_sql import SociaModel

class SqlAlchemySociaRepository(SociaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, socia_id: int) -> Optional[Socia]:
        db_socia = self.db.query(SociaModel).filter(SociaModel.id == socia_id).first()
        if db_socia:
            return Socia.model_validate(db_socia)
        return None

    def list_by_association(self, asociacion_id: int) -> List[Socia]:
        socias = self.db.query(SociaModel).filter(SociaModel.asociacion_id == asociacion_id).all()
        return [Socia.model_validate(socia) for socia in socias]

    def create(self, socia: SociaCreate) -> Socia:
        db_socia = SociaModel(**socia.model_dump())
        self.db.add(db_socia)
        self.db.commit()
        self.db.refresh(db_socia)
        return Socia.model_validate(db_socia)

    def update(self, socia_id: int, socia_update: SociaUpdate) -> Optional[Socia]:
        db_socia = self.db.query(SociaModel).filter(SociaModel.id == socia_id).first()
        if not db_socia:
            return None

        update_data = socia_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_socia, key, value)

        self.db.commit()
        self.db.refresh(db_socia)
        return Socia.model_validate(db_socia)

    def delete(self, socia_id: int) -> bool:
        db_socia = self.db.query(SociaModel).filter(SociaModel.id == socia_id).first()
        if db_socia:
            self.db.delete(db_socia)
            self.db.commit()
            return True
        return False
