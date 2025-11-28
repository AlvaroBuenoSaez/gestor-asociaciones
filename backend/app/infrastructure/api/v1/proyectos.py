from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.proyecto_repository_impl import SqlAlchemyProyectoRepository
from app.application.services.proyecto_service import ProyectoService
from app.domain.models.proyecto import Proyecto, ProyectoCreate, ProyectoUpdate

router = APIRouter(
    prefix="/proyectos",
    tags=["proyectos"]
)

def get_proyecto_service(db: Session = Depends(get_db)) -> ProyectoService:
    repository = SqlAlchemyProyectoRepository(db)
    return ProyectoService(repository)

@router.post("/", response_model=Proyecto, status_code=status.HTTP_201_CREATED)
def create_proyecto(
    proyecto: ProyectoCreate,
    service: ProyectoService = Depends(get_proyecto_service)
):
    return service.create_proyecto(proyecto)

@router.get("/", response_model=List[Proyecto])
def list_proyectos(
    asociacion_id: int,
    service: ProyectoService = Depends(get_proyecto_service)
):
    return service.list_proyectos_by_association(asociacion_id)

@router.get("/{proyecto_id}", response_model=Proyecto)
def get_proyecto(
    proyecto_id: int,
    service: ProyectoService = Depends(get_proyecto_service)
):
    proyecto = service.get_proyecto(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto not found")
    return proyecto

@router.put("/{proyecto_id}", response_model=Proyecto)
def update_proyecto(
    proyecto_id: int,
    proyecto_update: ProyectoUpdate,
    service: ProyectoService = Depends(get_proyecto_service)
):
    proyecto = service.update_proyecto(proyecto_id, proyecto_update)
    if not proyecto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto not found")
    return proyecto

@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proyecto(
    proyecto_id: int,
    service: ProyectoService = Depends(get_proyecto_service)
):
    success = service.delete_proyecto(proyecto_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto not found")
