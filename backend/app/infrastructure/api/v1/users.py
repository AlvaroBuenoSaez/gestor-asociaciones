from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.user_repository_impl import SqlAlchemyUserRepository
from app.application.services.user_service import UserService
from app.domain.models.user import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = SqlAlchemyUserRepository(db)
    return UserService(repository)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[User])
def list_users(
    asociacion_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.list_users_by_association(asociacion_id)

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    user = service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
