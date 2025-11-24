from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
import datetime

class UserModel(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(128))
    last_login = Column(DateTime, nullable=True)
    is_superuser = Column(Boolean, default=False)
    username = Column(String(150), unique=True, index=True)
    first_name = Column(String(150))
    last_name = Column(String(150))
    email = Column(String(254))
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("UserProfileModel", back_populates="user", uselist=False)

class AsociacionVecinalModel(Base):
    __tablename__ = "core_asociacionvecinal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200))
    direccion = Column(Text, nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(254), nullable=True)
    numero_registro = Column(String(50), unique=True)
    drive_folder_id = Column(String(100), nullable=True)
    drive_credentials = Column(Text, nullable=True)  # Store JSON credentials
    distrito = Column(String(100), nullable=True)
    provincia = Column(String(100), nullable=True)
    codigo_postal = Column(String(10), nullable=True)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    profiles = relationship("UserProfileModel", back_populates="asociacion")

class UserProfileModel(Base):
    __tablename__ = "users_userprofile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth_user.id"), unique=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=True)
    role = Column(String(10), default='member')
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    ocupacion = Column(String(100), nullable=True)
    fecha_ingreso = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("UserModel", back_populates="profile")
    asociacion = relationship("AsociacionVecinalModel", back_populates="profiles")
