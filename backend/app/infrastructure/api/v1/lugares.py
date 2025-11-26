from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.lugar_repository_impl import SqlAlchemyLugarRepository
from app.domain.models.lugar import Lugar

router = APIRouter(
    prefix="/lugares",
    tags=["lugares"]
)

@router.get("/buscar", response_model=List[Lugar])
def buscar_lugares(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    repo = SqlAlchemyLugarRepository(db)
    return repo.search_by_name(q)
