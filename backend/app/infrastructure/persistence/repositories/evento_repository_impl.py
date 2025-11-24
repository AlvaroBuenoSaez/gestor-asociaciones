from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import timedelta
from app.domain.ports.evento_repository import EventoRepository
from app.domain.models.evento import Evento, EventoCreate, EventoUpdate
from app.infrastructure.persistence.models.evento_sql import EventoModel

class SqlAlchemyEventoRepository(EventoRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_evento: EventoModel) -> Evento:
        # Convert BigInt microseconds to timedelta for domain
        duracion_td = None
        if db_evento.duracion is not None:
            duracion_td = timedelta(microseconds=db_evento.duracion)

        return Evento(
            id=db_evento.id,
            asociacion_id=db_evento.asociacion_id,
            responsable_id=db_evento.responsable_id,
            nombre=db_evento.nombre,
            descripcion=db_evento.descripcion,
            lugar=db_evento.lugar,
            fecha=db_evento.fecha,
            duracion=duracion_td,
            colaboradores=db_evento.colaboradores,
            evaluacion=db_evento.evaluacion,
            observaciones=db_evento.observaciones
        )

    def get_by_id(self, evento_id: int) -> Optional[Evento]:
        db_evento = self.db.query(EventoModel).filter(EventoModel.id == evento_id).first()
        if db_evento:
            return self._to_domain(db_evento)
        return None

    def list_by_association(self, asociacion_id: int) -> List[Evento]:
        eventos = self.db.query(EventoModel).filter(EventoModel.asociacion_id == asociacion_id).all()
        return [self._to_domain(evento) for evento in eventos]

    def create(self, evento: EventoCreate) -> Evento:
        try:
            # Convert timedelta to microseconds for DB
            duracion_us = None
            if evento.duracion:
                duracion_us = int(evento.duracion.total_seconds() * 1_000_000)

            db_evento = EventoModel(
                asociacion_id=evento.asociacion_id,
                responsable_id=evento.responsable_id,
                nombre=evento.nombre,
                descripcion=evento.descripcion,
                lugar=evento.lugar,
                fecha=evento.fecha,
                duracion=duracion_us,
                colaboradores=evento.colaboradores,
                evaluacion=evento.evaluacion,
                observaciones=evento.observaciones
            )
            self.db.add(db_evento)
            self.db.commit()
            self.db.refresh(db_evento)
            return self._to_domain(db_evento)
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, evento_id: int, evento_update: EventoUpdate) -> Optional[Evento]:
        db_evento = self.db.query(EventoModel).filter(EventoModel.id == evento_id).first()
        if not db_evento:
            return None

        try:
            update_data = evento_update.model_dump(exclude_unset=True)

            # Handle duration conversion
            if 'duracion' in update_data:
                duracion = update_data.pop('duracion')
                if duracion is not None:
                    db_evento.duracion = int(duracion.total_seconds() * 1_000_000)
                else:
                    db_evento.duracion = None

            for key, value in update_data.items():
                setattr(db_evento, key, value)

            self.db.commit()
            self.db.refresh(db_evento)
            return self._to_domain(db_evento)
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, evento_id: int) -> bool:
        db_evento = self.db.query(EventoModel).filter(EventoModel.id == evento_id).first()
        if db_evento:
            try:
                self.db.delete(db_evento)
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
                return False
        return False
