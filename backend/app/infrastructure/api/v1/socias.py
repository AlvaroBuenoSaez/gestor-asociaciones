from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.socia_repository_impl import SqlAlchemySociaRepository
from app.application.services.socia_service import SociaService
from app.domain.models.socia import Socia, SociaCreate, SociaUpdate

router = APIRouter(
    prefix="/socias",
    tags=["socias"]
)

def get_socia_service(db: Session = Depends(get_db)) -> SociaService:
    repository = SqlAlchemySociaRepository(db)
    return SociaService(repository)

@router.post("/", response_model=Socia, status_code=status.HTTP_201_CREATED)
def create_socia(
    socia: SociaCreate,
    service: SociaService = Depends(get_socia_service)
):
    return service.create_socia(socia)

@router.get("/", response_model=List[Socia])
def list_socias(
    asociacion_id: int,
    service: SociaService = Depends(get_socia_service)
):
    return service.list_socias_by_association(asociacion_id)

@router.get("/{socia_id}", response_model=Socia)
def get_socia(
    socia_id: int,
    service: SociaService = Depends(get_socia_service)
):
    socia = service.get_socia(socia_id)
    if not socia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Socia not found")
    return socia

@router.put("/{socia_id}", response_model=Socia)
def update_socia(
    socia_id: int,
    socia_update: SociaUpdate,
    service: SociaService = Depends(get_socia_service)
):
    socia = service.update_socia(socia_id, socia_update)
    if not socia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Socia not found")
    return socia

@router.delete("/{socia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_socia(
    socia_id: int,
    service: SociaService = Depends(get_socia_service)
):
    success = service.delete_socia(socia_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Socia not found")
