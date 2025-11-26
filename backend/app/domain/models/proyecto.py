from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProyectoBase(BaseModel):
    nombre: str
    responsable: str
    involucrados: Optional[str] = None
    descripcion: Optional[str] = None
    materiales: Optional[str] = None
    lugar: Optional[str] = None
    fecha_inicio: date
    fecha_final: Optional[date] = None
    recursivo: bool = False

class ProyectoCreate(ProyectoBase):
    asociacion_id: int

class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = None
    responsable: Optional[str] = None
    involucrados: Optional[str] = None
    descripcion: Optional[str] = None
    materiales: Optional[str] = None
    lugar: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_final: Optional[date] = None
    recursivo: Optional[bool] = None

class Proyecto(ProyectoBase):
    id: int
    asociacion_id: int
    fecha_creacion: datetime
    fecha_modificacion: datetime

    class Config:
        from_attributes = True
