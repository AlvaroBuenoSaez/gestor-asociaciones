from typing import List, Optional
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.domain.ports.user_repository import UserRepository
from app.domain.models.user import User, UserCreate, UserUpdate
from app.infrastructure.persistence.models.user_sql import UserModel, UserProfileModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return User.model_validate(db_user)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return User.model_validate(db_user)
        return None

    def list_by_association(self, asociacion_id: int) -> List[User]:
        # Join UserModel with UserProfileModel to filter by association
        users = (
            self.db.query(UserModel)
            .join(UserProfileModel)
            .filter(UserProfileModel.asociacion_id == asociacion_id)
            .all()
        )
        return [User.model_validate(user) for user in users]

    def create(self, user: UserCreate) -> User:
        try:
            # 1. Create Auth User
            hashed_password = pwd_context.hash(user.password)
            db_user = UserModel(
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                password=hashed_password,
                is_active=True,
                is_superuser=False,
                is_staff=False,
                date_joined=datetime.datetime.utcnow()
            )
            self.db.add(db_user)
            self.db.flush() # Flush to get db_user.id without committing

            # 2. Create User Profile
            db_profile = UserProfileModel(
                user_id=db_user.id,
                asociacion_id=user.asociacion_id,
                role=user.role,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            self.db.add(db_profile)

            self.db.commit()
            self.db.refresh(db_user)
            return User.model_validate(db_user)
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        try:
            # Update User fields
            if user_update.first_name is not None:
                db_user.first_name = user_update.first_name
            if user_update.last_name is not None:
                db_user.last_name = user_update.last_name
            if user_update.email is not None:
                db_user.email = user_update.email

            # Update Profile fields
            if db_user.profile:
                if user_update.role is not None:
                    db_user.profile.role = user_update.role
                if user_update.telefono is not None:
                    db_user.profile.telefono = user_update.telefono
                if user_update.direccion is not None:
                    db_user.profile.direccion = user_update.direccion

                db_user.profile.updated_at = datetime.datetime.utcnow()

            self.db.commit()
            self.db.refresh(db_user)
            return User.model_validate(db_user)
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            try:
                self.db.delete(db_user)
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
                return False
        return False
