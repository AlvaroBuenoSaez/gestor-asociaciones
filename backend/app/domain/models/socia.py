from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class SociaBase(BaseModel):
    numero_socia: str
    nombre: str
    apellidos: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    escalera: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = "España"
    nacimiento: Optional[date] = None
    pagado: bool = False
    descripcion: Optional[str] = None

class SociaCreate(SociaBase):
    asociacion_id: int

class SociaUpdate(BaseModel):
    numero_socia: Optional[str] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    escalera: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None
    nacimiento: Optional[date] = None
    pagado: Optional[bool] = None
    descripcion: Optional[str] = None

class Socia(SociaBase):
    id: int
    asociacion_id: int
    fecha_inscripcion: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
