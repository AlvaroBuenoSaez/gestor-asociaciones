from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

class AsociacionVecinal(BaseModel):
    id: int
    nombre: str
    numero_registro: str
    drive_folder_id: Optional[str] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    role: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    ocupacion: Optional[str] = None
    asociacion_id: Optional[int] = None

    class Config:
        from_attributes = True

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: datetime
    profile: Optional[UserProfile] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "member"
    asociacion_id: int

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
