from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.transaccion_repository_impl import SqlAlchemyTransaccionRepository
from app.application.services.transaccion_service import TransaccionService
from app.domain.models.transaccion import Transaccion, TransaccionCreate, TransaccionUpdate

router = APIRouter(
    prefix="/finanzas",
    tags=["finanzas"]
)

def get_transaccion_service(db: Session = Depends(get_db)) -> TransaccionService:
    repository = SqlAlchemyTransaccionRepository(db)
    return TransaccionService(repository)

@router.post("/", response_model=Transaccion, status_code=status.HTTP_201_CREATED)
def create_transaccion(
    transaccion: TransaccionCreate,
    service: TransaccionService = Depends(get_transaccion_service)
):
    return service.create_transaccion(transaccion)

@router.get("/", response_model=List[Transaccion])
def list_transacciones(
    asociacion_id: int,
    service: TransaccionService = Depends(get_transaccion_service)
):
    return service.list_transacciones_by_association(asociacion_id)

@router.get("/{transaccion_id}", response_model=Transaccion)
def get_transaccion(
    transaccion_id: int,
    service: TransaccionService = Depends(get_transaccion_service)
):
    transaccion = service.get_transaccion(transaccion_id)
    if not transaccion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaccion not found")
    return transaccion

@router.put("/{transaccion_id}", response_model=Transaccion)
def update_transaccion(
    transaccion_id: int,
    transaccion_update: TransaccionUpdate,
    service: TransaccionService = Depends(get_transaccion_service)
):
    transaccion = service.update_transaccion(transaccion_id, transaccion_update)
    if not transaccion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaccion not found")
    return transaccion

@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaccion(
    transaccion_id: int,
    service: TransaccionService = Depends(get_transaccion_service)
):
    success = service.delete_transaccion(transaccion_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaccion not found")
