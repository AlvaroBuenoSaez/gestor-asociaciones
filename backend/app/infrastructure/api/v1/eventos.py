from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.evento_repository_impl import SqlAlchemyEventoRepository
from app.application.services.evento_service import EventoService
from app.domain.models.evento import Evento, EventoCreate, EventoUpdate

router = APIRouter(
    prefix="/eventos",
    tags=["eventos"]
)

def get_evento_service(db: Session = Depends(get_db)) -> EventoService:
    repository = SqlAlchemyEventoRepository(db)
    return EventoService(repository)

@router.post("/", response_model=Evento, status_code=status.HTTP_201_CREATED)
def create_evento(
    evento: EventoCreate,
    service: EventoService = Depends(get_evento_service)
):
    return service.create_evento(evento)

@router.get("/", response_model=List[Evento])
def list_eventos(
    asociacion_id: int,
    service: EventoService = Depends(get_evento_service)
):
    return service.list_eventos_by_association(asociacion_id)

@router.get("/{evento_id}", response_model=Evento)
def get_evento(
    evento_id: int,
    service: EventoService = Depends(get_evento_service)
):
    evento = service.get_evento(evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento not found")
    return evento

@router.put("/{evento_id}", response_model=Evento)
def update_evento(
    evento_id: int,
    evento_update: EventoUpdate,
    service: EventoService = Depends(get_evento_service)
):
    evento = service.update_evento(evento_id, evento_update)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento not found")
    return evento

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento(
    evento_id: int,
    service: EventoService = Depends(get_evento_service)
):
    success = service.delete_evento(evento_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento not found")
